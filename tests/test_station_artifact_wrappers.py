"""Station artifact contract S4a/S4b at the channel wrapper (tools/codex_station.py).

The two observed reviewer losses came from the wrapper, not the reviewer:
  S4a  empty captured stdout made the wrapper exit 3 although a valid
       review.json had been written;
  S4b  the wrapper's own transcript (runs/<wo>/<station>.output.md) tripped
       its reviewer tree guard ("changed files outside its review file").
A reviewer touching code outside its run namespace still fails the guard
(see test_codex_reviewer_guard.py, unchanged).
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
    {"station": "reviewer-design", "verdict": "changes_requested", "findings": ["real finding"]}))
if os.environ.get("FAKE_NOTES"):
    (d / "reviewer-design.notes.output.md").write_text("working notes")
sys.stdout.write(os.environ.get("FAKE_STDOUT", ""))
'''


class TestWrapperArtifactContract(unittest.TestCase):
    def _run(self, stdout="", notes=False, output_in_run_tree=False):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        bindir = Path(tmp) / "bin"
        bindir.mkdir()
        fake = bindir / "codex"
        fake.write_text(FAKE)
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        wo = "wo-artifact-wrap-" + os.path.basename(tmp)
        run_dir = ROOT / "runs" / wo
        self.addCleanup(shutil.rmtree, run_dir, True)
        packet = Path(tmp) / "p.md"
        packet.write_text(f"# Task packet: reviewer-design\n\n- id: {wo}\n\nReview.\n")
        out = (run_dir / "reviewer-design.output.md") if output_in_run_tree else (Path(tmp) / "o.md")
        env = {k: v for k, v in os.environ.items() if k != "CF_AIG_TOKEN"}
        env.update({"PATH": str(bindir) + os.pathsep + str(Path(sys.executable).parent),
                    "ANVIL_CONFIGURED_MODEL": "openai/gpt-6.1-sol", "CF_AIG_TOKEN": "t",
                    "ANTHROPIC_BASE_URL": "https://gw.example.test/v1/a/g/anthropic",
                    "FAKE_WO": wo, "FAKE_STDOUT": stdout})
        if notes:
            env["FAKE_NOTES"] = "1"
        run_dir.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run([sys.executable, str(CODEX), str(packet), str(out)],
                              env=env, capture_output=True, text=True, timeout=60)
        return proc, run_dir

    def test_empty_stdout_with_valid_review_is_not_fatal_s4a(self):
        proc, run_dir = self._run(stdout="")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        review = json.loads((run_dir / "reviewer-design.review.json").read_text())
        self.assertEqual(review["verdict"], "changes_requested")

    def test_own_namespace_files_do_not_trip_the_guard_s4b(self):
        proc, _ = self._run(stdout="done", notes=True, output_in_run_tree=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("outside its review file", proc.stderr)

    def test_violation_set_allows_own_namespace_only_s4b(self):
        import codex_station
        before = {}
        after = {"runs/w/reviewer-ux.review.json": ("??", "1"),
                 "runs/w/reviewer-ux.output.md": ("??", "2"),
                 "runs/w/reviewer-ux.scratch.output.md": ("??", "3"),
                 "runs/w/reviewer-spec.output.md": ("??", "4"),
                 "runs/w/reviewer-ux.x/deep.md": ("??", "5"),
                 "src/app.py": (" M", "6")}
        self.assertEqual(codex_station.reviewer_tree_violations(
            before, after, ["runs/w/reviewer-ux.review.json"], own_prefix="runs/w/reviewer-ux."),
            ["runs/w/reviewer-spec.output.md", "runs/w/reviewer-ux.x/deep.md", "src/app.py"])


if __name__ == "__main__":
    unittest.main()
