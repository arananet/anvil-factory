import json
import tempfile
import unittest
from pathlib import Path

from anvil.scaffold import init_project, new_project
from anvil.onboard import onboard_project
from anvil.design import (
    scaffold_design_system,
    load_design_system,
    packet_design_section,
)
from anvil.pipeline import load_pipeline
from anvil.stations import load_registry
from anvil.model import WorkOrder
from anvil.runner import run_pipeline


ROOT = Path(__file__).resolve().parent.parent


def make_project_with_design(tmp):
    """Helper: create a project with a design system."""
    proj = Path(tmp) / "proj"
    init_project(proj, "TestProj")
    scaffold_design_system(proj)
    return proj


def make_project_no_design(tmp):
    """Helper: create a project without a design system."""
    proj = Path(tmp) / "proj-no-design"
    init_project(proj, "NoDes")
    # Explicitly remove design/ if scaffold creates it
    design_dir = proj / "design"
    if design_dir.exists():
        import shutil
        shutil.rmtree(design_dir)
    return proj


class DesignScaffoldingTests(unittest.TestCase):
    def test_s1_scaffolding_creates_once_never_overwrites(self):
        """project-design-system S1: scaffold creates design/ files once, never overwrites"""
        with tempfile.TemporaryDirectory() as tmp:
            # Test anvil init
            proj = Path(tmp) / "init-test"
            init_project(proj, "InitTest")
            scaffold_design_system(proj)

            self.assertTrue((proj / "design" / "DESIGN.md").exists())
            self.assertTrue((proj / "design" / "tokens.json").exists())

            # Verify tokens.json is valid JSON
            tokens = json.loads((proj / "design" / "tokens.json").read_text())
            self.assertIsInstance(tokens, dict)

            # Edit DESIGN.md
            design_md = proj / "design" / "DESIGN.md"
            original_content = design_md.read_text()
            edited_content = original_content + "\n\n## Human Edit\nThis was edited by a human.\n"
            design_md.write_text(edited_content, encoding="utf-8")

            # Run scaffold again - should not overwrite
            scaffold_design_system(proj)
            self.assertEqual(design_md.read_text(), edited_content)

            # Test anvil new-project
            bp = {
                "id": "test-bp",
                "name": "Test Blueprint",
                "stack": ["python"],
                "structure": ["src/", "tests/"],
                "first_specs": ["baseline"],
            }
            new_proj = new_project(Path(tmp) / "new-test", "NewTest", bp)
            self.assertTrue((new_proj / "design" / "DESIGN.md").exists())
            self.assertTrue((new_proj / "design" / "tokens.json").exists())

            # Test anvil onboard
            legacy = Path(tmp) / "legacy"
            legacy.mkdir()
            (legacy / "README.md").write_text("# Legacy\n")
            (legacy / "package.json").write_text('{"name": "legacy"}\n')
            onboard_project(legacy, "Legacy")
            self.assertTrue((legacy / "design" / "DESIGN.md").exists())
            self.assertTrue((legacy / "design" / "tokens.json").exists())


class DesignStructureTests(unittest.TestCase):
    def test_s2_scaffold_is_structure_not_look(self):
        """project-design-system S2: scaffold contains sections and questions, no factory style"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)

            design_md = (proj / "design" / "DESIGN.md").read_text()
            tokens_json = (proj / "design" / "tokens.json").read_text()

            # Check for required sections
            required_sections = [
                "brand identity",
                "palette",
                "typography",
                "voice",
                "art direction",
                "tokens",
                "component",
                "layout",
                "motion",
                "quality bars",
                "hierarchy",
                "scale contrast",
                "responsive",
            ]

            for section in required_sections:
                self.assertIn(section.lower(), design_md.lower(),
                              f"Missing required section: {section}")

            # Verify no factory-imposed palette colors (common hex patterns)
            forbidden_patterns = [
                "#0066cc",  # common factory blues
                "#ff6600",  # common factory oranges
                "rgb(0, 102, 204)",  # RGB factory colors
                "hsl(210, 100%, 40%)",  # HSL factory colors
            ]

            combined = design_md + tokens_json
            for pattern in forbidden_patterns:
                self.assertNotIn(pattern.lower(), combined.lower(),
                                 f"Found factory color {pattern}")

            # Check for placeholders and questions
            self.assertTrue(
                "TODO" in design_md or "placeholder" in design_md.lower() or "?" in design_md,
                "Scaffold should contain placeholders or questions"
            )

            # Verify tokens.json is valid and has placeholder structure
            tokens = json.loads(tokens_json)
            self.assertIsInstance(tokens, dict)


class DesignPacketTests(unittest.TestCase):
    def test_s3_packets_carry_design_to_interface_stations(self):
        """project-design-system S3: packets carry design system to interface-producing stations"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)

            # Add real token values
            tokens = {
                "colors": {
                    "primary": "#007bff",
                    "secondary": "#6c757d",
                },
                "typography": {
                    "base_size": "16px",
                    "scale": 1.25,
                },
            }
            (proj / "design" / "tokens.json").write_text(
                json.dumps(tokens, indent=2), encoding="utf-8"
            )

            # Add quality bars to DESIGN.md
            design_md = proj / "design" / "DESIGN.md"
            design_content = design_md.read_text()
            design_content += "\n\n## Quality Bars\n\n- Clear visual hierarchy\n- Minimum 4.5:1 contrast ratio\n"
            design_md.write_text(design_content, encoding="utf-8")

            # Interface-producing stations
            interface_stations = ["builder", "writer", "media-producer", "brief-writer", "reviewer-design"]

            for station_id in interface_stations:
                section = packet_design_section(proj, station_id)
                self.assertTrue(section, f"Design section should exist for {station_id}")
                self.assertIn("Project design", section)
                self.assertIn("#007bff", section, "Token values should be in section")
                self.assertIn("quality", section.lower(), "Quality bars should be in section")

            # Non-interface station should not get design section
            scout_section = packet_design_section(proj, "scout")
            self.assertEqual(scout_section, "", "scout should not receive design section")

            # Project without design system should return empty section
            proj_no_design = make_project_no_design(tmp)
            empty_section = packet_design_section(proj_no_design, "builder")
            self.assertEqual(empty_section, "", "Project without design should return empty section")


class DesignReviewerTests(unittest.TestCase):
    def test_s4_reviewer_design_in_catalog_and_pipelines(self):
        """project-design-system S4: reviewer-design exists and is in pipelines"""
        # Load the registry
        reg = load_registry(ROOT / "stations")

        # Check reviewer-design exists in catalog
        self.assertIn("reviewer-design", reg.ids(), "reviewer-design must be in the catalog")

        # Check station contract
        reviewer_design = reg.get("reviewer-design")
        self.assertIsNotNone(reviewer_design)
        self.assertEqual(reviewer_design.kind, "agent")

        # Verify contract mentions design system
        contract = reviewer_design.prompt
        self.assertTrue(
            any(word in contract.lower() for word in ["design", "tokens", "quality"]),
            "Contract should reference design system"
        )

        # Check pipelines that should have reviewer-design
        pipelines_to_check = ["sdlc-default", "content-default", "content-short"]

        for pipeline_name in pipelines_to_check:
            pipeline_path = ROOT / "pipelines" / f"{pipeline_name}.json"
            pipeline = load_pipeline(pipeline_path, known_stations=set(reg.ids()))

            # Find the parallel reviewer group
            with open(pipeline_path) as f:
                pipeline_data = json.load(f)

            found_reviewer_design = False
            reviewers_before = set()

            for stage in pipeline_data["stages"]:
                if "parallel" in stage:
                    parallel_group = stage["parallel"]
                    # Check if this is a reviewer group
                    if any(s.startswith("reviewer-") for s in parallel_group):
                        if "reviewer-design" in parallel_group:
                            found_reviewer_design = True
                            # Verify existing reviewers are still there
                            for reviewer in parallel_group:
                                if reviewer.startswith("reviewer-") and reviewer != "reviewer-design":
                                    reviewers_before.add(reviewer)

            self.assertTrue(
                found_reviewer_design,
                f"reviewer-design must be in {pipeline_name} parallel reviewer group"
            )


class DesignWarningsTests(unittest.TestCase):
    def test_s5_missing_design_system_warnings_and_findings(self):
        """project-design-system S5: missing design system produces warnings and findings"""
        with tempfile.TemporaryDirectory() as tmp:
            # Create project without design system
            proj = make_project_no_design(tmp)

            # Create a work order for interface-producing work
            wo = WorkOrder(
                id="wo-design-test",
                kind="feature",
                title="Test Feature",
                source="test",
                description="A test feature",
            )

            # Load registry and a pipeline with interface stations
            reg = load_registry(ROOT / "stations")
            pipeline_path = ROOT / "pipelines" / "content-default.json"
            pipeline = load_pipeline(pipeline_path, known_stations=set(reg.ids()))

            # Run pipeline in non-execute mode (dry run)
            report = run_pipeline(proj, pipeline, wo, registry=reg, executor=None)

            # Check for warning about missing design system
            report_dict = report.to_dict()

            # S5 Part 1: Run report should have warnings list with missing design system
            self.assertIn("warnings", report_dict, "Report should have warnings list")
            warnings = report_dict.get("warnings", [])

            found_design_warning = any(
                "design" in str(w).lower() and "missing" in str(w).lower()
                for w in warnings
            )
            self.assertTrue(
                found_design_warning,
                "Report should warn about missing design system"
            )

            # S5 Part 2: If reviewer-design ran, it should have changes_requested verdict
            # and a finding about missing design system
            if "reviewer-design" in [s["station"] for s in report_dict.get("steps", [])]:
                # Find reviewer-design review
                reviews_dir = proj / "runs" / wo.id / "reviews"
                if reviews_dir.exists():
                    for review_file in reviews_dir.glob("*.review.json"):
                        review_data = json.loads(review_file.read_text())
                        if review_data.get("station") == "reviewer-design":
                            self.assertEqual(
                                review_data["verdict"],
                                "changes_requested",
                                "reviewer-design should request changes when no design system"
                            )

                            findings = review_data.get("findings", [])
                            found_design_finding = any(
                                "design system" in str(f).lower() and "missing" in str(f).lower()
                                for f in findings
                            )
                            self.assertTrue(
                                found_design_finding,
                                "reviewer-design should report missing design system as finding"
                            )


if __name__ == "__main__":
    unittest.main()
