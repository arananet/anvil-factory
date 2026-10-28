import json, tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.statuspage import generate_status_page, render_status_page

def write_report(proj, folder, data):
    d = Path(proj) / "runs" / folder
    d.mkdir(parents=True)
    (d / "report.json").write_text(json.dumps(data))

APPROVED_RUN = {
    "work_order_id": "wo-alpha-001", "pipeline": "sdlc-default",
    "title": "Add the export feature", "kind": "feature",
    "verdict": "approved", "human_required": False, "loopbacks": 0,
    "deployment_status": "deployed_verified",
    "risk_hints": [],
    "decision": {
        "approver": {
            "reviews_counted": [{"station": "reviewer-spec", "verdict": "pass"}],
            "reviews_expected": ["reviewer-spec", "reviewer-security"],
            "rule": "All counted reviews passed.",
        },
        "human_gate": {
            "required": False,
            "rule": ("Verdict approved and no risk hints matched (scanned: auth, payments, "
                     "data-deletion, production-deploy, secrets, publishing), so no human is required."),
            "hints_matched": [],
        },
    },
    "verify_results": [{"command": "run the tests", "status": "pass", "exit_code": 0, "output": ""}],
    "steps": [
        {"station": "intake", "status": "completed", "duration_ms": 1.5, "cost": None, "artifacts": ["runs/wo-alpha-001/report.json"]},
        {"station": "builder", "status": "executed", "duration_ms": 42.0, "cost": None, "artifacts": ["runs/wo-alpha-001/builder.output.md"]},
        {"station": "reviewer-spec", "status": "packet_ready", "duration_ms": 0.5, "cost": None, "artifacts": ["runs/wo-alpha-001/reviewer-spec.packet.md"]},
        {"station": "deployer", "status": "executed", "duration_ms": 900.0, "cost": None, "artifacts": ["runs/wo-alpha-001/deployer.output.md"]},
    ],
}

FAILED_RUN = {
    "work_order_id": "wo-beta-002", "pipeline": "hotfix",
    "title": "Fix the crash", "kind": "bug",
    "verdict": "rejected", "human_required": True, "loopbacks": 1,
    "deployment_status": None, "verify_results": [],
    "steps": [
        {"station": "intake", "status": "completed", "duration_ms": 1.0, "cost": None, "artifacts": []},
        {"station": "builder", "status": "failed", "duration_ms": 12.0, "cost": None, "artifacts": ["runs/wo-beta-002/builder.packet.md"]},
    ],
}

class TestStatusPage(unittest.TestCase):
    def make_project(self, tmp):
        proj = Path(tmp) / "proj"
        (proj / "runs").mkdir(parents=True)
        write_report(proj, "wo-alpha-001", APPROVED_RUN)
        write_report(proj, "wo-beta-002", FAILED_RUN)
        broken = proj / "runs" / "wo-broken-003"
        broken.mkdir(parents=True)
        (broken / "report.json").write_text("{ this is not json")
        (proj / "runs" / "wo-empty-004").mkdir(parents=True)
        return proj

    def test_page_contains_both_runs_and_statuses_s1_s2_s3(self):
        """status-page S1, S2, S3: every run, its facts, and each station with its status"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            page, summary = render_status_page(proj, generated_at="2026-10-28 00:00:00 UTC")
            self.assertEqual(summary["runs"], 2)
            for needle in ["wo-alpha-001", "wo-beta-002", "Add the export feature", "Fix the crash",
                           "sdlc-default", "hotfix", "approved", "rejected", "deployed_verified",
                           "builder", "reviewer-spec", "deployer", "intake",
                           "completed", "executed", "packet_ready", "failed"]:
                self.assertIn(needle, page)

    def test_snapshot_note_and_timestamp_s4(self):
        """status-page S4: the page states when it was generated and that it is a snapshot"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            page, _ = render_status_page(proj, generated_at="2026-10-28 00:00:00 UTC")
            self.assertIn("Snapshot generated from the run reports on disk", page)
            self.assertIn("2026-10-28 00:00:00 UTC", page)
            self.assertIn("not a live feed", page)

    def test_corrupt_and_missing_reports_skipped_and_noted_s5(self):
        """status-page S5: corrupt or missing report.json is skipped and noted in the footer"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            summary = generate_status_page(proj, Path(tmp) / "out")
            self.assertEqual(summary["runs"], 2)
            self.assertEqual(sorted(summary["skipped"]), ["wo-broken-003", "wo-empty-004"])
            page = (Path(tmp) / "out" / "index.html").read_text()
            self.assertIn("wo-broken-003", page)
            self.assertIn("wo-empty-004", page)
            self.assertTrue((Path(tmp) / "out" / "index.html").exists())

    def test_self_contained_and_arananet_style(self):
        """status-page requirements: inline CSS only, Arananet palette, no external assets"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            page, _ = render_status_page(proj, generated_at="2026-10-28 00:00:00 UTC")
            self.assertIn("#0C0C0C", page)
            self.assertIn("#1E1E1E", page)
            self.assertIn("#FF5C00", page)
            self.assertNotIn("http://", page.replace("http://www.w3.org", ""))
            self.assertNotIn("<link", page)
            self.assertNotIn("<script", page)

    def test_recorded_decision_sentences_render_s6(self):
        """status-page S6: a report with a decision object shows the runner's own rule sentences"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)
            write_report(proj, "wo-alpha-001", APPROVED_RUN)
            page, summary = render_status_page(proj, generated_at="2026-10-28 00:00:00 UTC")
            self.assertEqual(summary["runs"], 1)
            self.assertIn("All counted reviews passed.", page)
            self.assertIn("so no human is required.", page)
            self.assertNotIn("derived from the run record", page)

    def test_derived_decision_for_older_report_s6(self):
        """status-page S6: a report without a decision object gets a labeled derived explanation"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)
            write_report(proj, "wo-beta-002", FAILED_RUN)
            page, summary = render_status_page(proj, generated_at="2026-10-28 00:00:00 UTC")
            self.assertEqual(summary["runs"], 1)
            self.assertIn("derived from the run record", page)
            self.assertIn("verdict rejected is on record, but this report does not itemize the reviews behind it.", page)
            self.assertIn("a human was required for this run (verdict rejected)", page)

if __name__ == "__main__":
    unittest.main()
