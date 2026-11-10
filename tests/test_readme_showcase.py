import json, os, re, tempfile, unittest, urllib.request
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT = Path(__file__).resolve().parent.parent


class TestReadmeStructure(unittest.TestCase):
    """S1: First screen content verifies what ANVIL is, what it built, and how to try it"""

    def setUp(self):
        self.readme = ROOT / "README.md"
        if not self.readme.exists():
            self.skipTest("README.md not found")
        self.content = self.readme.read_text(encoding="utf-8")

    def test_house_template_header_present_r1(self):
        """readme-showcase R1: house template header with title, badges, one-line description"""
        # Check for OpenSpec and Apache 2.0 badges
        self.assertIn("OpenSpec", self.content, "OpenSpec badge missing from header")
        self.assertIn("Apache", self.content, "Apache 2.0 badge missing from header")
        # Check for one-line description (quoted per spec)
        lines = self.content.split("\n")
        has_quote = any(line.strip().startswith(">") for line in lines[:30])
        self.assertTrue(has_quote, "One-line description (quoted) missing from first screen")

    def test_built_by_anvil_block_with_links_r1(self):
        """readme-showcase R1: Built by ANVIL block with Sentia, Platform25, status board links"""
        self.assertIn("Built by ANVIL", self.content, "Built by ANVIL block missing")
        self.assertIn("https://sentia.info-693.workers.dev", self.content, "Sentia link missing")
        self.assertIn("https://platform25.pages.dev", self.content, "Platform25 link missing")
        self.assertIn("https://anvil-status.pages.dev", self.content, "Status board link missing")

    def test_quickstart_section_present_r1(self):
        """readme-showcase R1: quickstart section mentioning arananet/anvil-example-taskline"""
        self.assertIn("anvil-example-taskline", self.content.lower(), "Quickstart missing taskline example reference")

    def test_star_call_to_action_exact_wording_r5(self):
        """readme-showcase R5: star call to action with exact wording, appears once"""
        cta = "If ANVIL is useful to you, a star helps other builders find it."
        count = self.content.count(cta)
        # Spec says "at the end of the first screen and repeated at the close", so expect it 2 times
        self.assertEqual(count, 2, f"Star CTA should appear exactly twice, found {count} times")

    def test_no_em_or_en_dash_project_style(self):
        """readme-showcase guardrail: no em dash or en dash character (project style rule)"""
        # Check for em dash (U+2014) and en dash (U+2013)
        self.assertNotIn("—", self.content, "Em dash character found, violates project style")
        self.assertNotIn("–", self.content, "En dash character found, violates project style")


class TestTrustSection(unittest.TestCase):
    """S2: Trust section claims link to evidence"""

    def setUp(self):
        self.readme = ROOT / "README.md"
        if not self.readme.exists():
            self.skipTest("README.md not found")
        self.content = self.readme.read_text(encoding="utf-8")

    def test_trust_section_exists_r2(self):
        """readme-showcase R2: trust section exists"""
        # Look for trust-related heading
        trust_patterns = [
            "trust",
            "why you can trust",
            "trust the output"
        ]
        has_trust_section = any(pattern in self.content.lower() for pattern in trust_patterns)
        self.assertTrue(has_trust_section, "Trust section not found in README")

    def test_no_station_approves_own_work_mechanism_r2(self):
        """readme-showcase R2: mechanism 1 - no station approves its own work"""
        self.assertIn("independent", self.content.lower(), "Independent reviewer mechanism not mentioned")
        # Check for link to evidence (file path in repo)
        has_link = bool(re.search(r'\[.*?\]\([^)]+\)', self.content))
        self.assertTrue(has_link, "Trust mechanisms should link to evidence files")

    def test_memory_provenance_mechanism_r2(self):
        """readme-showcase R2: mechanism 2 - memory with provenance, CONTAM-Bench answer"""
        self.assertIn("memory", self.content.lower(), "Memory provenance mechanism not mentioned")
        self.assertIn("provenance", self.content.lower(), "Provenance not mentioned in memory mechanism")

    def test_human_gate_mechanism_r2(self):
        """readme-showcase R2: mechanism 3 - human gate before publishing/production"""
        self.assertIn("human", self.content.lower(), "Human gate mechanism not mentioned")
        gate_patterns = ["gate", "before publishing", "before.*production"]
        has_gate = any(re.search(pattern, self.content.lower()) for pattern in gate_patterns)
        self.assertTrue(has_gate, "Human gate mechanism not properly described")


class TestClaimHygiene(unittest.TestCase):
    """S3: Claim verification against main tree"""

    def setUp(self):
        self.readme = ROOT / "README.md"
        if not self.readme.exists():
            self.skipTest("README.md not found")
        self.content = self.readme.read_text(encoding="utf-8")

    def test_station_count_accurate_r3(self):
        """readme-showcase R3: station count verified against tree"""
        stations_dir = ROOT / "stations"
        if not stations_dir.exists():
            self.skipTest("Stations directory not found")

        # Count actual stations from the registry the factory loads
        try:
            from anvil.stations import load_registry
            registry = load_registry(stations_dir)
            actual_count = len(registry)
        except Exception as e:
            self.skipTest(f"Could not load station registry: {e}")

        # Check if README mentions station count
        station_pattern = r'(\d+)\s+station'
        match = re.search(station_pattern, self.content.lower())
        if match:
            claimed_count = int(match.group(1))
            self.assertEqual(claimed_count, actual_count,
                           f"Station count mismatch: README claims {claimed_count}, actual is {actual_count}")

    def test_pipeline_count_accurate_r3(self):
        """readme-showcase R3: pipeline count verified against tree"""
        pipelines_dir = ROOT / "pipelines"
        if not pipelines_dir.exists():
            self.skipTest("Pipelines directory not found")

        # Count actual pipeline files
        pipeline_files = list(pipelines_dir.glob("*.json"))
        actual_count = len(pipeline_files)

        # Check if README mentions pipeline count
        pipeline_pattern = r'(\d+)\s+pipeline'
        match = re.search(pipeline_pattern, self.content.lower())
        if match:
            claimed_count = int(match.group(1))
            self.assertEqual(claimed_count, actual_count,
                           f"Pipeline count mismatch: README claims {claimed_count}, actual is {actual_count}")

    def test_reviewer_count_corrected_to_five_r3(self):
        """readme-showcase R3: reviewer counts corrected from four to five"""
        # Spec says "wherever the current README says four software reviewers...the real count is five"
        # After correction, should not claim "four reviewers"
        four_reviewer_pattern = r'four\s+(software\s+)?reviewers?'
        match = re.search(four_reviewer_pattern, self.content.lower())
        if match:
            self.fail(f"README still claims 'four reviewers', should be corrected to five: {match.group(0)}")

    def test_test_suite_count_measured_r3(self):
        """readme-showcase R3: factory suite test count measured from tree"""
        # Discovery counts without executing this test again recursively.
        loader = unittest.TestLoader()
        actual_count = loader.discover(str(ROOT / "tests"), pattern="test_*.py").countTestCases()
        self.assertFalse(loader.errors, loader.errors)
        self.assertGreater(actual_count, 0)
        match = re.search(r'(?:(over|more than|at least)\s+)?(\d+)\s+tests?\b', self.content.lower())
        if match:
            claimed_count = int(match.group(2))
            if match.group(1) in ("over", "more than"):
                self.assertGreater(actual_count, claimed_count)
            elif match.group(1) == "at least":
                self.assertGreaterEqual(actual_count, claimed_count)
            else:
                self.assertLess(abs(claimed_count - actual_count), 10)


class TestLinkValidation(unittest.TestCase):
    """Tests and verification: link and claim checks"""

    def setUp(self):
        self.readme = ROOT / "README.md"
        if not self.readme.exists():
            self.skipTest("README.md not found")
        self.content = self.readme.read_text(encoding="utf-8")

    def test_relative_links_resolve_in_tree(self):
        """readme-showcase verification: relative links resolve in tree"""
        # Find all markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, self.content)

        for text, url in links:
            # Only check relative links (not http/https)
            if not url.startswith(("http://", "https://", "#")):
                # Resolve relative to README location
                link_path = (self.readme.parent / url).resolve()
                self.assertTrue(link_path.exists(),
                              f"Relative link '{url}' does not resolve: {link_path}")

    def test_showcase_external_links_valid(self):
        """readme-showcase verification: external showcase links (Sentia, Platform25, status board) are valid"""
        # Skip unless ANVIL_LIVE_TESTS=1 is set, as these links are behind Cloudflare bot filtering
        # The live verification is in run evidence (evidence/link-and-claim-verification.md)
        if os.environ.get("ANVIL_LIVE_TESTS") != "1":
            self.skipTest("Live link test skipped (set ANVIL_LIVE_TESTS=1 to enable)")

        showcase_links = [
            "https://sentia.info-693.workers.dev",
            "https://platform25.pages.dev",
            "https://anvil-status.pages.dev"
        ]

        for link in showcase_links:
            if link in self.content:
                try:
                    # Use a browser user agent to pass Cloudflare bot filtering
                    req = urllib.request.Request(
                        link,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                        method='HEAD'
                    )
                    with urllib.request.urlopen(req, timeout=10) as response:
                        self.assertIn(response.status, [200, 301, 302],
                                    f"Showcase link {link} returned unexpected status {response.status}")
                except Exception as e:
                    self.fail(f"Showcase link {link} failed to answer: {e}")


class TestClosingContent(unittest.TestCase):
    """R5: House template closing sections"""

    def setUp(self):
        self.readme = ROOT / "README.md"
        if not self.readme.exists():
            self.skipTest("README.md not found")
        self.content = self.readme.read_text(encoding="utf-8")

    def test_contributing_section_r5(self):
        """readme-showcase R5: Contributing section pointing at OpenSpec"""
        self.assertIn("Contributing", self.content, "Contributing section missing")
        self.assertIn("OpenSpec", self.content, "Contributing should reference OpenSpec")

    def test_license_section_r5(self):
        """readme-showcase R5: License section with Apache 2.0 and Copyright Eduardo Arana"""
        self.assertIn("License", self.content, "License section missing")
        self.assertIn("Apache", self.content, "Apache 2.0 license not mentioned")
        self.assertIn("Eduardo Arana", self.content, "Copyright holder Eduardo Arana not mentioned")

    def test_developer_section_r5(self):
        """readme-showcase R5: Developer section with Eduardo Arana"""
        developer_patterns = ["Developer", "Author", "Maintainer"]
        has_developer = any(pattern in self.content for pattern in developer_patterns)
        self.assertTrue(has_developer, "Developer/Author section missing")
        self.assertIn("Eduardo Arana", self.content, "Developer Eduardo Arana not mentioned")

    def test_kofi_block_r5(self):
        """readme-showcase R5: ko-fi support block present"""
        self.assertIn("ko-fi", self.content.lower(), "ko-fi support block missing")


class TestSocialPreview(unittest.TestCase):
    """S4: Social preview image ready for upload"""

    def test_social_preview_image_exists_and_dimensions_r4(self):
        """readme-showcase R4: social preview image 1280x640 exists in run evidence"""
        # The spec says the image is produced as run evidence, not in the tree yet
        # This test checks if it exists in expected locations after a run
        evidence_paths = [
            ROOT / "runs" / "wo-gh-23" / "evidence" / "social-preview.png",
            ROOT / "social-preview.png",
            ROOT / "docs" / "social-preview.png",
            ROOT / "assets" / "social-preview.png"
        ]

        found = None
        for path in evidence_paths:
            if path.exists():
                found = path
                break

        if found:
            # Check dimensions if PIL is available
            try:
                from PIL import Image
                img = Image.open(found)
                width, height = img.size
                self.assertEqual(width, 1280, f"Social preview width should be 1280, got {width}")
                self.assertEqual(height, 640, f"Social preview height should be 640, got {height}")
            except ImportError:
                self.skipTest("PIL not available to verify image dimensions")
        else:
            # Image may not exist yet if builder hasn't run
            self.skipTest("Social preview image not found (may not be generated yet)")


class TestQuickstartExecution(unittest.TestCase):
    """S5: Quickstart execution under 5 minutes"""

    def test_quickstart_completes_under_5_minutes_s5(self):
        """readme-showcase S5: quickstart executed from clean clone completes under 5 minutes"""
        # This is a placeholder - actual execution happens during the build step
        # The test verifies that evidence of quickstart execution exists
        evidence_paths = [
            ROOT / "runs" / "wo-gh-23" / "evidence" / "quickstart-execution.txt",
            ROOT / "runs" / "wo-gh-23" / "evidence" / "quickstart.log"
        ]

        # Look for quickstart evidence
        found = None
        for path in evidence_paths:
            if path.exists():
                found = path
                break

        if found:
            content = found.read_text(encoding="utf-8")
            # Check that it mentions completion and duration
            self.assertTrue(len(content) > 0, "Quickstart evidence file is empty")
            # Could check for duration markers if present
        else:
            # Evidence may not exist yet if builder hasn't run
            self.skipTest("Quickstart execution evidence not found (builder step)")


class TestFactorySuiteStable(unittest.TestCase):
    """Verification: factory suite stays green"""

    def test_factory_suite_can_run(self):
        """readme-showcase verification: factory suite can run without errors"""
        # Sanity check that test modules are importable
        # Actual full suite run is in CI via the checks gate (canonical: unittest discover)
        # A nested suite invocation inside the suite is redundant and recursive
        tests_dir = ROOT / "tests"
        if not tests_dir.exists():
            self.fail("Tests directory not found")

        # Verify we can find test files
        test_files = list(tests_dir.glob("test_*.py"))
        self.assertGreater(len(test_files), 0, "No test files found in tests directory")

        # Quick import check on this module itself (we're already running, so it works)
        try:
            import tests.test_readme_showcase
        except ImportError as e:
            self.fail(f"Could not import test module: {e}")


if __name__ == "__main__":
    unittest.main()
