"""Proven patterns: facts about this order's own run (spec: proven-patterns, work order wo-gh-50).

Every test in the RunEvidence class compares the tree with the base ref of
wo-gh-50 or names the files this order must produce or must not touch, so it
skips unless ANVIL_WORK_ORDER_ID is wo-gh-50 (decision 0018; the suite check
tests/test_run_evidence_scoping.py enforces the guard). The Permanent class
holds facts that stay true after the order merges.

Scenario map:
  S9 (R4.4, R5.4)   test_s9_default_init_equals_base_ref_init, test_s9_unmatched_run_equals_base_ref_run
  S10 (R7.2, R7.3, R8.1)  test_s10_base_ref_test_files_untouched, test_s10_protected_paths_untouched,
                    test_s10_produced_files_exist_without_dashes, test_s10_no_promoted_pattern_ships,
                    test_s10_builder_report_is_complete, test_s10_runner_never_says_retry,
                    test_s10_patterns_module_and_docs
"""
import json
import os
import re
import subprocess
import sys
import tarfile
import io
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures" / "patterns"
ORDER = "wo-gh-50"
BASE_REF = "13244db35475b9a19dbd041bc69cf6487d806a45"
DASHES = re.compile("[\u2013\u2014]")
PRODUCED = ["anvil/patterns.py", "patterns/README.md", "patterns/inbox/.gitkeep", "docs/PATTERNS.md",
            "brain/decisions/0020-proven-patterns.md"]
PROTECTED_PREFIXES = (".github/workflows/", "pipelines/", "blueprints/")
PROTECTED_FILES = ("anvil.json", "anvil/knowledge.py")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def changed_since_base():
    """(status, path) for every change of the working tree, tracked and untracked, against the base ref."""
    changes = []
    for line in git("diff", "--name-status", "--no-renames", BASE_REF).splitlines():
        status, path = line.split("\t", 1)
        changes.append((status, path))
    for path in git("ls-files", "--others", "--exclude-standard").splitlines():
        changes.append(("A", path))
    return changes


def snapshot(directory):
    return {str(p.relative_to(directory)): p.read_bytes() for p in sorted(Path(directory).rglob("*")) if p.is_file()}


@unittest.skipUnless(os.environ.get("ANVIL_WORK_ORDER_ID") == ORDER, "run evidence of wo-gh-50 only (decision 0018)")
class RunEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.base_tree = Path(cls._tmp.name) / "base"
        cls.base_tree.mkdir()
        archive = subprocess.run(["git", "archive", "--format=tar", BASE_REF], cwd=ROOT,
                                 capture_output=True, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(cls.base_tree)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def drive(self, tree, workdir, mode, *extra):
        done = subprocess.run([sys.executable, "-I", str(FIXTURES / "drive_line.py"), str(tree), str(workdir), mode, *extra],
                              capture_output=True, text=True, timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr[-3000:])
        return done.stdout

    def test_s9_default_init_equals_base_ref_init(self):
        """S9: init without --pattern writes the same tree and bytes as the default init at the base ref."""
        with tempfile.TemporaryDirectory() as work:
            work = Path(work)
            self.drive(self.base_tree, work, "init")
            base = snapshot(work / "project")
            import shutil
            shutil.rmtree(work / "project")
            self.drive(ROOT, work, "init")
            self.assertEqual(snapshot(work / "project"), base)
            self.assertTrue(base)

    def test_s9_unmatched_run_equals_base_ref_run(self):
        """S9: a run matching no pattern has the base ref packets, event kinds and report keys plus pattern."""
        for product_type in ("landing-page", None):
            with self.subTest(product_type=product_type), tempfile.TemporaryDirectory() as work:
                work = Path(work)
                extra = [product_type] if product_type else []
                base = json.loads(self.drive(self.base_tree, work, "run", *extra))
                import shutil
                shutil.rmtree(work / "project")
                now = json.loads(self.drive(ROOT, work, "run", *extra))
                self.assertEqual(now["packets"], base["packets"])
                self.assertEqual(now["events"], base["events"])
                self.assertEqual(sorted(set(now["report_keys"]) - {"pattern"}), base["report_keys"])
                self.assertIn("pattern", now["report_keys"])

    def test_s10_base_ref_test_files_untouched(self):
        """S10 (R7.3): no test file present at the base ref is modified or deleted."""
        touched = [(s, p) for s, p in changed_since_base() if p.startswith("tests/") and s != "A"]
        self.assertEqual(touched, [])

    def test_s10_protected_paths_untouched(self):
        """S10: workflows, pipelines, blueprints, anvil.json and the design knowledge loader are untouched."""
        touched = [(s, p) for s, p in changed_since_base()
                   if p.startswith(PROTECTED_PREFIXES) or p in PROTECTED_FILES]
        self.assertEqual(touched, [])

    def test_s10_new_tests_live_under_tests(self):
        """S10 (R7.1): the proven patterns tests are new files under tests/."""
        added = {p for s, p in changed_since_base() if s == "A"}
        new_tests = sorted(p for p in added if re.match(r"tests/test_proven_patterns\w*\.py$", p))
        self.assertGreaterEqual(len(new_tests), 4, new_tests)

    def test_s10_produced_files_exist_without_dashes(self):
        """S10: the produced files exist and carry no em dash or en dash."""
        scanned = ("anvil/", "patterns/", "docs/", "brain/", "tests/", "CHANGELOG.md")
        changed = [p for s, p in changed_since_base() if s != "D" and p.startswith(scanned)]
        for rel in PRODUCED:
            self.assertTrue((ROOT / rel).is_file(), rel)
        for rel in changed:
            path = ROOT / rel
            if path.is_file() and path.suffix in (".py", ".md", ".json", ".txt", ".yaml", ""):
                self.assertIsNone(DASHES.search(path.read_text(encoding="utf-8", errors="replace")), rel)

    def test_s10_no_promoted_pattern_ships(self):
        """S10 (scope): the order ships the mechanism and no promoted pattern; the inbox is empty."""
        entries = sorted(p.name for p in (ROOT / "patterns").iterdir())
        self.assertEqual(entries, ["README.md", "inbox"])
        self.assertEqual(sorted(p.name for p in (ROOT / "patterns" / "inbox").iterdir()), [".gitkeep"])

    def test_s10_builder_report_is_complete(self):
        """S10 (R8.1): the builder report names the strings, the base ref, the test count and new test files."""
        report = ROOT / "runs" / ORDER / "builder.output.md"
        if not report.is_file():
            self.skipTest("the builder report is not written yet")
        text = report.read_text(encoding="utf-8")
        for needle in ("proven-patterns", "promote-pattern", "dead-ends.json", "calibration.json", BASE_REF):
            self.assertIn(needle, text)
        self.assertRegex(text, r"\b\d{3,5}\b", "the exact full factory test count")
        self.assertIn("test_proven_patterns", text)


class Permanent(unittest.TestCase):
    def test_s10_runner_never_says_retry(self):
        """S10: the word "retry" does not occur in anvil/runner.py."""
        self.assertNotIn("retry", (ROOT / "anvil" / "runner.py").read_text(encoding="utf-8").lower())

    def test_s10_patterns_module_and_docs(self):
        """S10 (R1.5, R1.6): anvil/patterns.py exists and docs/PATTERNS.md documents the pack and its limits."""
        import importlib
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        importlib.import_module("anvil.patterns")
        doc = (ROOT / "docs" / "PATTERNS.md").read_text(encoding="utf-8")
        for needle in ("dead-ends.json", "calibration.json", "promote-pattern", "harvest", "check-patterns"):
            self.assertIn(needle, doc)
        self.assertRegex(doc.lower(), r"copy", "the docs say the validator does not detect product copy")

    def test_s10_no_dashes_in_drivers(self):
        """Project style rule for the fixture driver."""
        self.assertIsNone(DASHES.search((FIXTURES / "drive_line.py").read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
