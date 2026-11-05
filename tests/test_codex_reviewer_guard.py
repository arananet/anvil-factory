"""wo-gh-29 round 5, Part B: the Codex wrapper's reviewer tree guard (model-migration R4, R12).

Codex 0.166 offers no setting that drops its apply_patch edit tool short of
replacing the whole model catalog, so non-write stations get no-edit developer
instructions and a reviewer is additionally held to the producer contract after
the run: it may change exactly its own review file, or the station fails loudly.
"""
import json, os, shutil, stat, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODEX = ROOT / "tools" / "codex_station.py"
sys.path.insert(0, str(ROOT / "tools"))

FAKE = '''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
d = Path(os.getcwd()) / "runs" / os.environ["FAKE_WO"]
d.mkdir(parents=True, exist_ok=True)
(d / "reviewer-design.review.json").write_text(json.dumps(
    {"station": "reviewer-design", "verdict": "pass", "findings": []}))
if os.environ.get("FAKE_STRAY"):
    Path(os.environ["FAKE_STRAY"]).write_text("a reviewer must not write this")
with open(os.environ["FAKE_ARGV"], "w") as fh:
    json.dump(sys.argv[1:], fh)
print("codex did some work")
'''


class TestReviewerTreeGuard(unittest.TestCase):
    def _run(self, stray, station="reviewer-design"):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        bindir = Path(tmp) / "bin"
        bindir.mkdir()
        fake = bindir / "codex"
        fake.write_text(FAKE)
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        wo = "wo-codex-guard-" + os.path.basename(tmp)
        self.addCleanup(shutil.rmtree, ROOT / "runs" / wo, True)
        packet = Path(tmp) / "p.md"
        packet.write_text(f"# Task packet: {station}\n\n- id: {wo}\n\nReview.\n")
        env = {k: v for k, v in os.environ.items() if k != "CF_AIG_TOKEN"}
        env.update({"PATH": str(bindir) + os.pathsep + str(Path(sys.executable).parent),
                    "ANVIL_CONFIGURED_MODEL": "openai/gpt-6.1-sol", "CF_AIG_TOKEN": "t",
                    "ANTHROPIC_BASE_URL": "https://gw.example.test/v1/a/g/anthropic",
                    "FAKE_WO": wo, "FAKE_ARGV": str(Path(tmp) / "argv.json")})
        if stray:
            # a new non-ignored file in the tree under judgment (runs/ is git-ignored)
            target = ROOT / ("codex-guard-stray-" + os.path.basename(tmp) + ".txt")
            self.addCleanup(lambda: target.unlink(missing_ok=True))
            env["FAKE_STRAY"] = str(target)
        proc = subprocess.run([sys.executable, str(CODEX), str(packet), str(Path(tmp) / "o.md")],
                              env=env, capture_output=True, text=True, timeout=60)
        argv = json.loads((Path(tmp) / "argv.json").read_text())
        return proc, argv

    def test_reviewer_writing_only_its_review_file_passes(self):
        proc, argv = self._run(stray=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(any(a.startswith("developer_instructions=") and "apply_patch" in a
                            for a in argv))

    def test_reviewer_changing_another_file_fails_loudly(self):
        proc, _ = self._run(stray=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("codex-guard-stray-", proc.stderr)
        self.assertIn("outside its review file", proc.stderr)

    def test_violation_set_ignores_preexisting_and_allowed_changes(self):
        import codex_station
        before = {"a.py": (" M", "1"), "runs/w/x.txt": ("??", "2")}
        after = {"a.py": (" M", "1"), "runs/w/x.txt": ("??", "2"),
                 "runs/w/reviewer-ux.review.json": ("??", "3"), "b.py": (" M", "4")}
        self.assertEqual(codex_station.reviewer_tree_violations(
            before, after, ["runs/w/reviewer-ux.review.json"]), ["b.py"])
        after["a.py"] = (" M", "changed")
        self.assertEqual(codex_station.reviewer_tree_violations(
            before, after, ["runs/w/reviewer-ux.review.json"]), ["a.py", "b.py"])


if __name__ == "__main__":
    unittest.main()
