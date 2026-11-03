import json, os, re, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = ROOT / "benchmarks" / "model-benchmark"


class TestModelBenchmark(unittest.TestCase):
    def test_ground_truth_and_fixture_match_s1(self):
        """model-benchmark S1: ground truth has exactly 10 entries V1-V10 mapping to K1-K10, and fixture page carries each planted value"""
        ground_truth_path = BENCHMARK / "fixture" / "ground-truth.json"
        self.assertTrue(ground_truth_path.exists(), "ground-truth.json must exist")

        with open(ground_truth_path, encoding="utf-8") as f:
            ground_truth = json.load(f)

        self.assertEqual(len(ground_truth), 10, "ground truth must have exactly 10 entries")

        expected_ids = [f"V{i}" for i in range(1, 11)]
        expected_checks = [f"K{i}" for i in range(1, 11)]
        actual_ids = [entry["id"] for entry in ground_truth]
        actual_checks = [entry["scorer_check"] for entry in ground_truth]

        self.assertEqual(actual_ids, expected_ids, "ground truth must have entries V1 to V10")
        self.assertEqual(actual_checks, expected_checks, "ground truth must map to K1 to K10")

        for entry in ground_truth:
            self.assertIn("element", entry, f"{entry['id']} must name an element")
            self.assertIn("property", entry, f"{entry['id']} must name a property")
            self.assertIn("planted_value", entry, f"{entry['id']} must state the planted value")
            self.assertIn("documented_expectation", entry, f"{entry['id']} must state the documented expectation")
            self.assertIn("description", entry, f"{entry['id']} must have a description")

        fixture_page_path = BENCHMARK / "fixture" / "src" / "page.html"
        self.assertTrue(fixture_page_path.exists(), "fixture page must exist")

        with open(fixture_page_path, encoding="utf-8") as f:
            page_html = f.read()

        for entry in ground_truth:
            element_id = entry["element"]
            prop = entry["property"]
            planted = str(entry["planted_value"])

            self.assertIn(f'id="{element_id}"', page_html,
                         f"{entry['id']}: element {element_id} must exist in fixture page")

            if prop == "missing_rule":
                self.assertNotIn(":focus-visible", page_html,
                                f"{entry['id']}: :focus-visible rule must be absent")
            elif planted:
                planted_normalized = planted.strip().lower()
                page_normalized = page_html.lower()
                self.assertIn(planted_normalized, page_normalized,
                             f"{entry['id']}: planted value '{planted}' for {prop} must be present in fixture page")

    def test_scorer_convicts_fixture_and_acquits_compliant_s2(self):
        """model-benchmark S2: scorer fails K1-K10 and passes K11-K12 on fixture, passes 12/12 on compliant page"""
        scorer_path = BENCHMARK / "tools" / "scorer.py"
        self.assertTrue(scorer_path.exists(), "scorer.py must exist")

        fixture_page_path = BENCHMARK / "fixture" / "src" / "page.html"
        self.assertTrue(fixture_page_path.exists(), "fixture page must exist")

        result = subprocess.run(
            [sys.executable, str(scorer_path), str(fixture_page_path)],
            capture_output=True,
            text=True,
            cwd=ROOT
        )
        self.assertEqual(result.returncode, 0, f"scorer must run successfully: {result.stderr}")

        try:
            score = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            self.fail(f"scorer output must be valid JSON: {e}\n{result.stdout}")

        self.assertIn("passed", score, "scorer output must include passed count")
        self.assertIn("total", score, "scorer output must include total count")
        self.assertIn("checks", score, "scorer output must include checks array")

        self.assertEqual(score["total"], 12, "scorer must report 12 total checks")
        self.assertEqual(score["passed"], 2, "scorer must pass exactly 2 checks (K11, K12) on fixture")

        checks_by_id = {c["check_id"]: c for c in score["checks"]}

        for i in range(1, 11):
            check_id = f"K{i}"
            self.assertIn(check_id, checks_by_id, f"{check_id} must be present in scorer output")
            self.assertFalse(checks_by_id[check_id]["passed"], f"{check_id} must fail on fixture page")

        self.assertTrue(checks_by_id["K11"]["passed"], "K11 must pass on fixture page")
        self.assertTrue(checks_by_id["K12"]["passed"], "K12 must pass on fixture page")

        compliant_page = self._create_compliant_page()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(compliant_page)
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                [sys.executable, str(scorer_path), tmp_path],
                capture_output=True,
                text=True,
                cwd=ROOT
            )
            self.assertEqual(result.returncode, 0, f"scorer must run successfully on compliant page: {result.stderr}")

            score = json.loads(result.stdout)
            self.assertEqual(score["passed"], 12, "scorer must pass all 12 checks on compliant page")
            self.assertEqual(score["total"], 12, "scorer must report 12 total checks")

            for check in score["checks"]:
                self.assertTrue(check["passed"], f"{check['check_id']} must pass on compliant page")
        finally:
            os.unlink(tmp_path)

    def test_tokens_agree_across_design_files_s3(self):
        """model-benchmark S3: tokens.json and DESIGN.md agree on every token value"""
        tokens_path = BENCHMARK / "fixture" / "design" / "tokens.json"
        design_path = BENCHMARK / "fixture" / "design" / "DESIGN.md"

        self.assertTrue(tokens_path.exists(), "tokens.json must exist")
        self.assertTrue(design_path.exists(), "DESIGN.md must exist")

        with open(tokens_path, encoding="utf-8") as f:
            tokens = json.load(f)

        with open(design_path, encoding="utf-8") as f:
            design_text = f.read()

        self.assertIn("colors", tokens, "tokens.json must have colors")
        for color_name, color_hex in tokens["colors"].items():
            normalized_hex = color_hex.upper()
            self.assertIn(normalized_hex, design_text.upper(),
                         f"color {color_name} {color_hex} from tokens.json must appear in DESIGN.md")

        self.assertIn("type_scale", tokens, "tokens.json must have type_scale")
        for size in tokens["type_scale"]:
            self.assertIn(str(size), design_text,
                         f"type scale value {size} from tokens.json must appear in DESIGN.md")

        self.assertIn("radius", tokens, "tokens.json must have radius")
        for radius in tokens["radius"]:
            self.assertIn(str(radius), design_text,
                         f"radius token {radius} from tokens.json must appear in DESIGN.md")

        self.assertIn("line_heights", tokens, "tokens.json must have line_heights")
        for context, height in tokens["line_heights"].items():
            self.assertIn(str(height), design_text,
                         f"line height {height} for {context} from tokens.json must appear in DESIGN.md")

        if "spacing_rhythm" in tokens:
            self.assertIn(str(tokens["spacing_rhythm"]), design_text,
                         f"spacing rhythm {tokens['spacing_rhythm']} from tokens.json must appear in DESIGN.md")

    def _create_compliant_page(self):
        """Create a minimal compliant page in the fixture contract shape"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meridian Patch</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Inter, sans-serif; background: #FAFAF6; color: #14201B; }
        #page { padding: 0; }
        #hero-title { font-family: "Space Grotesk", sans-serif; font-size: 56px; line-height: 1.2; color: #14201B; }
        #hero-sub { font-size: 20px; line-height: 1.5; color: #53685C; }
        #cta-primary { background: #0E7C66; color: #FAFAF6; padding: 16px 32px; border-radius: 8px; border: none; font-size: 16px; cursor: pointer; transition: opacity 0.2s; }
        #price-badge { background: #FF6B4A; color: #FAFAF6; padding: 8px 16px; border-radius: 999px; font-size: 14px; }
        #section { padding-top: 64px; padding-bottom: 64px; }
        #heading-2 { font-family: "Space Grotesk", sans-serif; font-size: 32px; line-height: 1.2; color: #14201B; margin-bottom: 16px; }
        #body-text { font-size: 16px; line-height: 1.5; color: #14201B; }
        #caption { font-size: 12px; line-height: 1.5; color: #53685C; }
        #link-inline { color: #0E7C66; text-decoration: underline; }
        #card { background: #FAFAF6; border: 1px solid #E3E6DF; border-radius: 12px; padding: 24px; }
        a:focus-visible, button:focus-visible { outline: 2px solid #0E7C66; outline-offset: 2px; }
        @media (prefers-reduced-motion: reduce) {
            * { transition: none !important; animation: none !important; }
        }
    </style>
</head>
<body>
    <div id="page">
        <h1 id="hero-title">Meridian Patch</h1>
        <p id="hero-sub">A revolutionary product</p>
        <button id="cta-primary">Get Started</button>
        <span id="price-badge">$99</span>
        <section id="section">
            <h2 id="heading-2">Features</h2>
            <p id="body-text">This is body text that meets all requirements.</p>
            <p id="caption">This is a caption with proper contrast.</p>
            <a href="#" id="link-inline">Learn more</a>
            <div id="card">Card content</div>
        </section>
    </div>
</body>
</html>"""


if __name__ == "__main__":
    unittest.main()
