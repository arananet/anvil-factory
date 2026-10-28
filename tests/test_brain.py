import io, json, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.brain import (check_brain, demote_learning, ensure_brain_memory,
                         parse_learnings, packet_learnings_section,
                         promote_learning, propose_learning)
from anvil.cli import main as cli_main
from anvil.model import WorkOrder
from anvil.onboard import onboard_project
from anvil.pipeline import load_pipeline
from anvil.runner import run_pipeline
from anvil.scaffold import init_project
from anvil.stations import load_registry

ROOT = Path(__file__).resolve().parent.parent

GOOD_CLAIM = "The store rejects empty titles with a 400"
BAD_CLAIM = "Whispered agent rumor with no run behind it"


def seed_run(proj, run_id="wo-seed-001", verdict="approved", verify=None):
    """Write a real run report and an artifact the provenance can point at."""
    run_dir = Path(proj) / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    report = {"work_order_id": run_id, "pipeline": "hotfix", "verdict": verdict,
              "human_required": False, "loopbacks": 0, "max_loopbacks": 2,
              "deployment_status": None, "verify_results": verify or [], "steps": []}
    (run_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (run_dir / "notes.md").write_text("run notes\n", encoding="utf-8")
    return run_id


class TestVerifiedMemory(unittest.TestCase):
    def make_project(self, tmp):
        proj = Path(tmp) / "proj"
        init_project(proj, "Demo")
        return proj

    def test_promotion_succeeds_with_real_support_s1(self):
        """verified-memory S1: a proposal whose provenance checks out becomes a verified entry"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            seed_run(proj)
            name = propose_learning(proj, GOOD_CLAIM, "wo-seed-001",
                                    "runs/wo-seed-001/notes.md", "verdict approved")
            entry_id = promote_learning(proj, name)
            self.assertEqual(entry_id, "L-1")
            entries = parse_learnings(proj)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["claim"], GOOD_CLAIM)
            self.assertEqual(entries[0]["run"], "wo-seed-001")
            self.assertFalse((proj / "brain" / "inbox" / name).exists())

    def test_promotion_with_verify_pass_evidence_s1(self):
        """verified-memory S1: a verify pass evidence claim is checked against verify_results"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            seed_run(proj, verify=[{"command": "run the tests", "status": "pass", "exit_code": 0}])
            name = propose_learning(proj, "Deployed copy passes the suite", "wo-seed-001",
                                    "runs/wo-seed-001/notes.md", "verify pass")
            self.assertEqual(promote_learning(proj, name), "L-1")

    def test_promotion_refused_when_run_missing_s2(self):
        """verified-memory S2: no run report, no promotion, and the reason names the missing report"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            name = propose_learning(proj, GOOD_CLAIM, "wo-ghost-999",
                                    "runs/wo-ghost-999/notes.md", "verdict approved")
            with self.assertRaises(ValueError) as cm:
                promote_learning(proj, name)
            self.assertIn("run report not found: runs/wo-ghost-999/report.json", str(cm.exception))
            self.assertEqual(parse_learnings(proj), [])
            self.assertTrue((proj / "brain" / "inbox" / name).exists())

    def test_promotion_refused_when_artifact_missing_s2(self):
        """verified-memory S2: a missing artifact refuses promotion with the artifact named"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            seed_run(proj)
            name = propose_learning(proj, GOOD_CLAIM, "wo-seed-001",
                                    "runs/wo-seed-001/absent.md", "verdict approved")
            with self.assertRaises(ValueError) as cm:
                promote_learning(proj, name)
            self.assertIn("artifact not found: runs/wo-seed-001/absent.md", str(cm.exception))
            self.assertEqual(parse_learnings(proj), [])

    def test_promotion_refused_when_evidence_contradicts_the_report_s2(self):
        """verified-memory S2: claiming verdict approved for a rejected run is refused"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            seed_run(proj, verdict="rejected")
            name = propose_learning(proj, GOOD_CLAIM, "wo-seed-001",
                                    "runs/wo-seed-001/notes.md", "verdict approved")
            with self.assertRaises(ValueError) as cm:
                promote_learning(proj, name)
            self.assertIn("evidence says verdict approved but run wo-seed-001 report verdict is rejected",
                          str(cm.exception))
            self.assertEqual(parse_learnings(proj), [])

    def test_check_brain_flags_a_stripped_provenance_s3(self):
        """verified-memory S3: a hand edited entry whose provenance was stripped fails the check"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            seed_run(proj)
            name = propose_learning(proj, GOOD_CLAIM, "wo-seed-001",
                                    "runs/wo-seed-001/notes.md", "verdict approved")
            promote_learning(proj, name)
            target = proj / "brain" / "learnings.md"
            stripped = "\n".join(ln for ln in target.read_text().splitlines()
                                 if not ln.startswith("Provenance:")) + "\n"
            target.write_text(stripped, encoding="utf-8")
            result = check_brain(proj)
            self.assertFalse(result["ok"])
            self.assertTrue(any("L-1" in p and "provenance" in p for p in result["problems"]))
            out = io.StringIO()
            with redirect_stdout(out):
                code = cli_main(["check-brain", str(proj)])
            self.assertEqual(code, 1)

    def test_inbox_items_are_quarantined_not_errors_s4(self):
        """verified-memory S4: inbox proposals are listed as quarantined and never fail check-brain"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            name = propose_learning(proj, BAD_CLAIM, "wo-ghost-999",
                                    "runs/wo-ghost-999/notes.md", "verdict approved")
            result = check_brain(proj)
            self.assertTrue(result["ok"])
            self.assertEqual(result["quarantined"], [name])
            out = io.StringIO()
            with redirect_stdout(out):
                code = cli_main(["check-brain", str(proj)])
            self.assertEqual(code, 0)
            self.assertIn("quarantined", out.getvalue())

    def test_packet_carries_verified_only_never_inbox_s5(self):
        """verified-memory S5: packets carry verified learnings; inbox claims never appear"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            seed_run(proj)
            good = propose_learning(proj, GOOD_CLAIM, "wo-seed-001",
                                    "runs/wo-seed-001/notes.md", "verdict approved")
            promote_learning(proj, good)
            propose_learning(proj, BAD_CLAIM, "wo-seed-001",
                             "runs/wo-seed-001/notes.md", "verdict approved")
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(ROOT / "pipelines" / "hotfix.json", known_stations=set(reg.ids()))
            wo = WorkOrder(id="wo-brain-001", kind="bug", title="Check the packets")
            run_pipeline(proj, pipe, wo, registry=reg)
            packets = list((proj / "runs" / "wo-brain-001").glob("*.packet.md"))
            self.assertTrue(packets)
            joined = "\n".join(p.read_text() for p in packets)
            self.assertIn("## Verified learnings", joined)
            self.assertIn(GOOD_CLAIM, joined)
            self.assertNotIn(BAD_CLAIM, joined)

    def test_demotion_marks_records_and_excludes_s6(self):
        """verified-memory S6: demotion marks the entry, writes a decision, removes it from packets"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            seed_run(proj)
            name = propose_learning(proj, GOOD_CLAIM, "wo-seed-001",
                                    "runs/wo-seed-001/notes.md", "verdict approved")
            promote_learning(proj, name)
            record = demote_learning(proj, "L-1", "The 400 came from validation order, not the store")
            entries = parse_learnings(proj)
            self.assertTrue(entries[0]["demoted"])
            text = Path(proj, record).read_text()
            self.assertIn("Demote learning L-1", text)
            self.assertIn("validation order", text)
            self.assertEqual(packet_learnings_section(proj), "")
            self.assertTrue(check_brain(proj)["ok"])
            with self.assertRaises(ValueError):
                demote_learning(proj, "L-1", "again")

    def test_scaffolding_creates_memory_layout_without_overwriting_s7(self):
        """verified-memory S7: init creates learnings.md and inbox; re-running scaffolding keeps content"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            self.assertTrue((proj / "brain" / "learnings.md").exists())
            self.assertTrue((proj / "brain" / "inbox").is_dir())
            target = proj / "brain" / "learnings.md"
            target.write_text("# Learnings\n\nHand kept content.\n", encoding="utf-8")
            self.assertEqual(ensure_brain_memory(proj), [])
            self.assertIn("Hand kept content.", target.read_text())

    def test_onboard_adds_memory_layout_and_keeps_existing_s7(self):
        """verified-memory S7: onboard creates the memory layout and never overwrites an existing store"""
        with tempfile.TemporaryDirectory() as tmp:
            legacy = Path(tmp) / "legacy"
            (legacy / "brain").mkdir(parents=True)
            (legacy / "brain" / "learnings.md").write_text("# Learnings\n\nPre existing store.\n", encoding="utf-8")
            (legacy / "app.py").write_text("print('hi')\n", encoding="utf-8")
            result = onboard_project(legacy)
            self.assertIn("brain/learnings.md", result["kept"])
            self.assertIn("Pre existing store.", (legacy / "brain" / "learnings.md").read_text())
            self.assertTrue((legacy / "brain" / "inbox").is_dir())

    def test_cli_promote_refusal_exits_1(self):
        """verified-memory S2: the CLI surfaces the refusal reason and exits 1"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            name = propose_learning(proj, GOOD_CLAIM, "wo-ghost-999",
                                    "runs/wo-ghost-999/notes.md", "verdict approved")
            out = io.StringIO()
            with redirect_stdout(out):
                code = cli_main(["promote-learning", str(proj), name])
            self.assertEqual(code, 1)
            self.assertIn("Promotion refused: run report not found", out.getvalue())


if __name__ == "__main__":
    unittest.main()
