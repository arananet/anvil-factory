"""Proven patterns: a new project born from a pattern (spec: proven-patterns, work order wo-gh-50).

The tests run the real command `anvil init <path> --name <name> --pattern <id>`
in process against a fixture promoted pack in a temporary patterns root named
by ANVIL_PATTERNS_DIR (see tests/fixtures/patterns/patterns_support.py), and
compare with the default init of the same code.

Scenario map:
  S8 (R5.4, R5.5)  test_s8_init_from_pattern, test_s8_check_command_runs, test_s8_raw_figures_are_skipped,
                   test_s8_unknown_pattern_refuses_before_writing, test_s8_new_project_config_loads
  S9 (R5.4)        test_s9_init_without_pattern_is_the_default_init,
                   test_s9_pattern_init_is_additive_to_default_init
"""
import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "fixtures" / "patterns"))
import patterns_support as ps  # noqa: E402


class InitFromPattern(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.root = self.tmp / "patterns"
        (self.root / "inbox").mkdir(parents=True)
        self.pack = ps.write_pack(self.root, "video-a", version="1", product_types=("explainer-video", "short-video"))
        self.new = self.tmp / "new"

    def tearDown(self):
        self._tmp.cleanup()

    def init(self, *extra, target=None):
        return ps.cli(["init", target or self.new, "--name", "New", *extra], self.root)

    def test_s8_init_from_pattern(self):
        """S8: brain/pattern.md, guardrails, the check command, the product type and the starting budgets."""
        code, out = self.init("--pattern", "video-a")
        self.assertEqual(code, 0, out)
        self.assertEqual((self.new / "brain" / "pattern.md").read_bytes(), (self.pack / "structure.md").read_bytes())
        copied = self.new / "guardrails" / "video-a" / "check_routes.py"
        self.assertEqual(copied.read_bytes(), (self.pack / "guardrails" / "check_routes.py").read_bytes())
        checks = json.loads((self.new / "anvil.json").read_text(encoding="utf-8")).get("checks")
        self.assertIsInstance(checks, list)
        running = [c for c in checks if "guardrails/video-a/check_routes.py" in str(c)]
        self.assertEqual(len(running), 1, checks)
        self.assertEqual(len(checks), 1, "one command per dead end enforced by a check, none for prompt ones")
        brain = (self.new / "brain" / "project.md").read_text(encoding="utf-8")
        self.assertIn("Product type: explainer-video", brain, "the first entry of product_types")
        self.assertNotIn("Product type: short-video", brain)
        config = json.loads((self.new / "anvil.yaml").read_text(encoding="utf-8"))
        efficiency = config["efficiency"]
        self.assertEqual(efficiency["station_budgets"]["builder"], 900000)
        self.assertEqual(efficiency["cache_read_weight"], 0.1)

    def test_s8_raw_figures_are_skipped(self):
        """S8: the intake raw token figure is not converted, not written, and init names it as skipped."""
        code, out = self.init("--pattern", "video-a")
        self.assertEqual(code, 0, out)
        budgets = json.loads((self.new / "anvil.yaml").read_text(encoding="utf-8"))["efficiency"]["station_budgets"]
        self.assertNotIn("intake", budgets)
        self.assertNotIn("master", budgets, "a stage that is not a station of the default pipeline is not a budget")
        skipped = [l for l in out.splitlines() if "intake" in l]
        self.assertTrue(skipped, out)
        self.assertRegex(" ".join(skipped).lower(), r"skip")
        self.assertRegex(" ".join(skipped).lower(), r"raw")

    def test_s8_check_command_runs(self):
        """S8: the appended check command really runs the copied guardrail in the new project."""
        code, out = self.init("--pattern", "video-a")
        self.assertEqual(code, 0, out)
        checks = json.loads((self.new / "anvil.json").read_text(encoding="utf-8"))["checks"]
        command = checks[0]
        self.assertIsInstance(command, str)
        argv = shlex.split(command)
        if argv and argv[0] in ("python", "python3"):
            argv[0] = sys.executable
        done = subprocess.run(argv, cwd=self.new, capture_output=True, text=True, timeout=60)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("routes ok", done.stdout)

    def test_s8_prompt_only_pattern_adds_no_check(self):
        """S8 (R5.4): a pack whose dead ends are all prompt text adds no check command."""
        ps.write_pack(self.root, "video-p", dead_ends=[dict(ps.CRT)], guardrails={})
        code, out = self.init("--pattern", "video-p")
        self.assertEqual(code, 0, out)
        checks = json.loads((self.new / "anvil.json").read_text(encoding="utf-8")).get("checks", [])
        self.assertEqual(checks, [])

    def test_s8_new_project_config_loads(self):
        """S8: the new project's anvil.yaml still loads with the factory's own reader."""
        from anvil.config import load_anvil_config, station_budget_settings
        code, out = self.init("--pattern", "video-a")
        self.assertEqual(code, 0, out)
        config = load_anvil_config(self.new / "anvil.yaml")
        budgets, _ = station_budget_settings(config)
        self.assertEqual(budgets.get("builder"), 900000)

    def test_s8_unknown_pattern_refuses_before_writing(self):
        """S8: --pattern nope exits 1 and the target does not exist."""
        code, out = self.init("--pattern", "nope")
        self.assertEqual(code, 1, out)
        self.assertIn("nope", out)
        self.assertFalse(self.new.exists())

    def test_s8_invalid_pack_refuses_before_writing(self):
        """S8 (R5.4): a promoted pack that fails validation is refused before anything is written."""
        ps.write_pack(self.root, "video-bad", dead_ends=[dict(ps.DITHER, evidence="")])
        code, out = self.init("--pattern", "video-bad")
        self.assertEqual(code, 1, out)
        self.assertFalse(self.new.exists())

    def test_s9_pattern_init_is_additive_to_default_init(self):
        """S9 (R5.4): init --pattern creates every file the default init creates."""
        default = self.tmp / "default"
        self.assertEqual(self.init(target=default)[0], 0)
        self.assertEqual(self.init("--pattern", "video-a")[0], 0)
        missing = sorted(set(ps.snapshot(default)) - set(ps.snapshot(self.new)))
        self.assertEqual(missing, [])

    def test_s9_init_without_pattern_is_the_default_init(self):
        """S9: init without --pattern equals scaffold.init_project, with patterns present or absent."""
        from anvil.scaffold import init_project
        reference = init_project(self.tmp / "same", "New")
        expected = ps.snapshot(reference)
        import shutil
        shutil.rmtree(reference)
        code, out = self.init(target=self.tmp / "same")
        self.assertEqual(code, 0, out)
        self.assertEqual(ps.snapshot(self.tmp / "same"), expected)
        self.assertFalse((self.tmp / "same" / "brain" / "pattern.md").exists())
        self.assertFalse((self.tmp / "same" / "guardrails").exists())


if __name__ == "__main__":
    unittest.main()
