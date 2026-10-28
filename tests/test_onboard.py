import tempfile
import unittest
from pathlib import Path

from anvil.onboard import analyze_project, onboard_project


def make_legacy_project(root):
    root.mkdir(parents=True)
    (root / "README.md").write_text("# Legacy Shop\n\nA small shop backend that predates the factory.\n")
    (root / "package.json").write_text('{"name": "legacy-shop", "version": "1.0.0"}\n')
    src = root / "src"
    src.mkdir()
    (src / "index.js").write_text("console.log('shop');\n")
    return root


class OnboardTests(unittest.TestCase):
    def test_s1_analysis_detects_what_exists(self):
        """existing-project-onboarding S1: stack, tests, specs, CI, file types"""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_legacy_project(Path(tmp) / "legacy")
            report = analyze_project(root)
            self.assertIn("node", report["stack"])
            self.assertFalse(report["has_tests"])
            self.assertFalse(report["has_specs"])
            self.assertFalse(report["has_ci"])
            self.assertTrue(report["has_readme"])
            self.assertIn(".js", report["file_types"])
            self.assertFalse((root / "anvil.json").exists())

    def test_s2_onboarding_adds_only_what_is_missing(self):
        """existing-project-onboarding S2: factory files created, existing untouched"""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_legacy_project(Path(tmp) / "legacy")
            readme_before = (root / "README.md").read_bytes()
            result = onboard_project(root)
            for rel in ("anvil.json", "anvil.yaml", "ONBOARDING.md", "brain/project.md", ".openspec/config.yaml"):
                self.assertTrue((root / rel).exists(), rel)
            self.assertEqual((root / "README.md").read_bytes(), readme_before)
            self.assertIn("README.md", result["kept"])

    def test_s3_baseline_spec_drafted(self):
        """existing-project-onboarding S3: draft baseline spec exists"""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_legacy_project(Path(tmp) / "legacy")
            onboard_project(root)
            spec = root / ".openspec" / "specs" / "existing-baseline" / "spec.md"
            self.assertTrue(spec.exists())
            self.assertIn("Status: draft", spec.read_text())

    def test_s4_double_onboarding_refused(self):
        """existing-project-onboarding S4: second run errors and changes nothing"""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_legacy_project(Path(tmp) / "legacy")
            onboard_project(root)
            marker = (root / "ONBOARDING.md").read_bytes()
            with self.assertRaises(ValueError):
                onboard_project(root)
            self.assertEqual((root / "ONBOARDING.md").read_bytes(), marker)

    def test_s5_gaps_become_suggested_work(self):
        """existing-project-onboarding S5: report lists gaps with suggested work orders"""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_legacy_project(Path(tmp) / "legacy")
            result = onboard_project(root)
            report = (root / "ONBOARDING.md").read_text()
            self.assertIn("no tests", report.lower())
            self.assertIn("no ci", report.lower())
            self.assertTrue(any("test" in s.lower() for s in result["suggested_work_orders"]))


if __name__ == "__main__":
    unittest.main()
