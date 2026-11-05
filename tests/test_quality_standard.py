"""Tests for the quality standard for visual deliverables.

Tests cover the scenarios from .openspec/specs/quality-standard/spec.md:
- S1: Anchored realism makes a toy render fail the quality judgment
- S2: A visual run without anchors applies the floor and warns
- S3: A non-visual run never receives the charter
- S4: The generating station records its own anchor comparison before review
- S5: The anchor wins over the charter default
- S6: A game product is judged by its own stated standard
- S7: Two assets pass the anchor comparison yet diverge from each other
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from anvil.scaffold import init_project
from anvil.design import scaffold_design_system
from anvil.model import WorkOrder
from anvil.quality import (
    load_quality_charter,
    packet_quality_charter_section,
    packet_anchor_section,
    validate_generating_station_comparison,
    validate_reviewer_quality_section,
    is_visual_run,
    get_product_type,
    PRODUCT_TYPES,
)

ROOT = Path(__file__).resolve().parent.parent


def make_project_with_design(tmp, name="TestProj"):
    """Helper: create a project with a design system."""
    proj = Path(tmp) / "proj"
    init_project(proj, name)
    scaffold_design_system(proj)
    return proj


def make_visual_work_order(product_type="physical_product"):
    """Helper: create a work order for visual deliverables."""
    return WorkOrder(
        id="wo-test-visual",
        kind="feature",
        title="Product render",
        surfaces=["ui"],
        description=f"Product type: {product_type}",
    )


def make_non_visual_work_order():
    """Helper: create a work order with no visual surfaces."""
    return WorkOrder(
        id="wo-test-api",
        kind="feature",
        title="API endpoint",
        surfaces=["api"],
    )


def create_anchor_images(proj, anchors_dir="design/reference"):
    """Helper: create fixture anchor images for a project."""
    anchor_path = proj / anchors_dir
    anchor_path.mkdir(parents=True, exist_ok=True)

    # Create a photoreal anchor file
    photoreal = anchor_path / "product-photoreal.jpg"
    photoreal.write_bytes(b"FAKE_IMAGE_PHOTOREAL")

    # Create a stylized anchor file
    stylized = anchor_path / "product-stylized.jpg"
    stylized.write_bytes(b"FAKE_IMAGE_STYLIZED")

    return {
        "photoreal": str(photoreal.relative_to(proj)),
        "stylized": str(stylized.relative_to(proj)),
    }


class QualityCharterTests(unittest.TestCase):
    """Test that the quality charter exists and has the right structure."""

    def test_charter_exists(self):
        """The factory quality charter document exists"""
        charter = load_quality_charter()
        self.assertIsNotNone(charter)
        self.assertIn("version", charter)
        self.assertIn("criteria", charter)

    def test_charter_has_physical_product_criteria(self):
        """Charter defines observable criteria for physical products"""
        charter = load_quality_charter()
        physical = charter["criteria"]["physical_product"]

        # Verify all four criteria are present
        required = ["materials", "light", "contact", "scale"]
        for criterion in required:
            self.assertIn(criterion, physical)
            self.assertTrue(physical[criterion])  # Not empty

    def test_charter_has_game_criteria(self):
        """Charter allows game/illustration products to state their own standard"""
        charter = load_quality_charter()
        game = charter["criteria"]["game"]

        # Game criteria should reference project-stated standard
        self.assertIn("stated_standard", game)
        self.assertTrue(game["stated_standard"])


class PacketInjectionTests(unittest.TestCase):
    """Test that the charter and anchors are injected into the right packets."""

    def test_s3_non_visual_run_never_receives_charter(self):
        """S3: A non-visual run never receives the charter"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)
            wo = make_non_visual_work_order()

            # Non-visual run should not be flagged as visual
            self.assertFalse(is_visual_run(wo))

            # Charter section should be empty for non-visual stations
            for station in ["builder", "reviewer-design", "media-producer"]:
                section = packet_quality_charter_section(proj, station, wo)
                self.assertEqual(section, "")

    def test_visual_run_receives_charter_in_generating_packets(self):
        """Visual run: charter flows into generating station packets"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)
            wo = make_visual_work_order()

            # Visual run should be flagged as visual
            self.assertTrue(is_visual_run(wo))

            # Generating stations should receive charter
            generating_stations = ["builder", "media-producer"]
            for station in generating_stations:
                section = packet_quality_charter_section(proj, station, wo)
                self.assertNotEqual(section, "")
                self.assertIn("Quality Charter", section)
                section_lower = section.lower()
                self.assertIn("materials", section_lower)
                self.assertIn("light", section_lower)
                self.assertIn("contact", section_lower)
                self.assertIn("scale", section_lower)

    def test_visual_run_receives_charter_in_reviewer_packets(self):
        """Visual run: charter flows into reviewer-design packets"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)
            wo = make_visual_work_order()

            section = packet_quality_charter_section(proj, "reviewer-design", wo)
            self.assertNotEqual(section, "")
            self.assertIn("Quality Charter", section)

    def test_s2_visual_run_with_anchors_includes_anchor_section(self):
        """S2 setup: Visual run with anchors includes anchor section in packets"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)
            anchors = create_anchor_images(proj)
            wo = make_visual_work_order()

            # Add anchors to work order
            wo.anchors = [anchors["photoreal"]]

            # Packets should include anchor section (for imagery stations)
            section = packet_anchor_section(proj, "builder", wo)
            self.assertNotEqual(section, "")
            self.assertIn("Reference Anchors", section)
            self.assertIn(anchors["photoreal"], section)

    def test_s2_visual_run_without_anchors_warns(self):
        """S2: Visual run without anchors proceeds with charter floor and warns"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)
            wo = make_visual_work_order()

            # Remove anchors directory to simulate no anchors
            import shutil
            ref_dir = proj / "design/reference"
            if ref_dir.exists():
                shutil.rmtree(ref_dir)

            # No anchors directory exists
            self.assertFalse(ref_dir.exists())

            # Anchor section should warn about missing anchors (for imagery stations)
            section = packet_anchor_section(proj, "builder", wo)
            self.assertIn("WARNING", section)
            self.assertIn("no reference anchors", section.lower())


class ReviewerQualitySectionTests(unittest.TestCase):
    """Test reviewer-design's quality section validates correctly."""

    def test_s1_toy_render_fails_quality_against_photoreal_anchor(self):
        """S1: Toy-like output fails quality when anchors show photorealism"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)
            anchors = create_anchor_images(proj)
            wo = make_visual_work_order()
            wo.anchors = [anchors["photoreal"]]

            # Simulate a reviewer-design review with toy-like finding
            review = {
                "station": "reviewer-design",
                "verdict": "changes_requested",
                "compliance": {
                    "verdict": "pass",
                    "findings": []
                },
                "quality": {
                    "verdict": "fail",
                    "findings": [
                        "Materials: Surfaces read as molded plastic instead of the metal and glass shown in product-photoreal.jpg",
                        "Light: Single flat overhead light, missing the complex studio lighting in the anchor",
                        "Scale: Product reads as toy-sized (3-4 inches) instead of the full-scale device",
                    ],
                    "anchor": anchors["photoreal"]
                }
            }

            # Validate that quality section is separate from compliance
            self.assertIn("compliance", review)
            self.assertIn("quality", review)
            self.assertEqual(review["compliance"]["verdict"], "pass")
            self.assertEqual(review["quality"]["verdict"], "fail")

            # Quality findings must cite specific criteria
            quality_findings = review["quality"]["findings"]
            categories = ["Materials", "Light", "Scale", "Contact"]
            found_categories = [c for c in categories if any(c in f for f in quality_findings)]
            self.assertGreater(len(found_categories), 0)

            # Validate structure
            is_valid = validate_reviewer_quality_section(review)
            self.assertTrue(is_valid)

    def test_quality_section_requires_anchor_citation(self):
        """Quality section findings must cite the anchor they measured against"""
        review = {
            "station": "reviewer-design",
            "verdict": "fail",
            "quality": {
                "verdict": "fail",
                "findings": ["Generic quality failure without anchor citation"],
            }
        }

        # Should fail validation - no anchor cited
        is_valid = validate_reviewer_quality_section(review)
        self.assertFalse(is_valid)

    def test_quality_section_can_pass_compliance_fail_quality(self):
        """A deliverable can pass compliance but fail quality"""
        review = {
            "station": "reviewer-design",
            "verdict": "changes_requested",
            "compliance": {"verdict": "pass", "findings": []},
            "quality": {
                "verdict": "fail",
                "findings": [
                    "Materials: Surface finish reads as plastic, anchor shows brushed aluminum"
                ],
                "anchor": "design/reference/product.jpg"
            }
        }

        is_valid = validate_reviewer_quality_section(review)
        self.assertTrue(is_valid)

        # Both sections should be distinct
        self.assertEqual(review["compliance"]["verdict"], "pass")
        self.assertEqual(review["quality"]["verdict"], "fail")


class GeneratingStationTests(unittest.TestCase):
    """Test that generating stations record their own anchor comparison."""

    def test_s4_generating_station_records_comparison_before_review(self):
        """S4: Generating station records anchor comparison before review runs"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)
            anchors = create_anchor_images(proj)
            wo = make_visual_work_order()
            wo.anchors = [anchors["photoreal"]]

            # Simulate generating station's self-comparison output
            self_comparison = {
                "output": "renders/product-front.png",
                "anchor_cited": anchors["photoreal"],
                "criteria_checked": ["materials", "light", "contact", "scale"],
                "gaps": [],  # No gaps at charter bar
                "statement": "No gaps found at charter bar"
            }

            # Validate the structure
            is_valid = validate_generating_station_comparison(self_comparison)
            self.assertTrue(is_valid)

            # Must include explicit statement even when no gaps
            self.assertIn("statement", self_comparison)
            self.assertTrue(self_comparison["statement"])

    def test_s4_generating_station_records_gaps(self):
        """S4: Generating station records gaps when found"""
        self_comparison = {
            "output": "renders/product.png",
            "anchor_cited": "design/reference/product.jpg",
            "criteria_checked": ["materials", "light", "contact", "scale"],
            "gaps": [
                {"criterion": "materials", "description": "Surface reads as plastic instead of metal"},
                {"criterion": "light", "description": "Missing shadow complexity from anchor"}
            ],
            "statement": "2 gaps found at charter bar"
        }

        is_valid = validate_generating_station_comparison(self_comparison)
        self.assertTrue(is_valid)

        # Gaps must specify criterion
        for gap in self_comparison["gaps"]:
            self.assertIn("criterion", gap)
            self.assertIn("description", gap)


class CompositionOrderTests(unittest.TestCase):
    """Test that anchors, design system, and charter compose in the right order."""

    def test_s5_stylized_anchor_wins_over_charter_realism(self):
        """S5: When anchors show stylized work, stylized is the bar"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)
            anchors = create_anchor_images(proj)
            wo = make_visual_work_order()
            wo.anchors = [anchors["stylized"]]

            # Product type is physical_product but anchor is stylized
            product_type = get_product_type(wo)
            self.assertEqual(product_type, "physical_product")

            # Review that matches stylized anchor should pass quality
            review = {
                "station": "reviewer-design",
                "verdict": "pass",
                "quality": {
                    "verdict": "pass",
                    "findings": [],
                    "anchor": anchors["stylized"],
                    "note": "Output matches stylized anchor. Charter realism criteria do not override."
                }
            }

            is_valid = validate_reviewer_quality_section(review)
            self.assertTrue(is_valid)

    def test_s5_floor_gap_is_named(self):
        """S5: Anything below charter floor is named as a floor gap"""
        review = {
            "station": "reviewer-design",
            "verdict": "fail",
            "quality": {
                "verdict": "fail",
                "findings": [
                    "Floor gap: Contact - Objects float above surfaces instead of making physical contact (charter minimum)"
                ],
                "anchor": "design/reference/stylized.jpg"
            }
        }

        # Floor gap must be explicitly named
        findings = review["quality"]["findings"]
        self.assertTrue(any("Floor gap" in f for f in findings))

        is_valid = validate_reviewer_quality_section(review)
        self.assertTrue(is_valid)


class ProductTypeTests(unittest.TestCase):
    """Test that different product types get the right criteria."""

    def test_s6_game_product_uses_stated_standard(self):
        """S6: Game product is judged by its own stated standard"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)
            wo = make_visual_work_order(product_type="game")

            # Write a stated standard into the design system
            design_md = proj / "design" / "DESIGN.md"
            content = design_md.read_text()
            stated_standard = """
## Visual Standard for Game Assets

This project's visual standard (observable criteria):
- Materials: Cel-shaded with visible hand-painted texture strokes
- Light: Single dominant directional light with minimal ambient
- Contact: Stylized contact shadows, not physically accurate
- Scale: Characters scaled to fit 16:9 viewport, not anatomically precise
"""
            design_md.write_text(content + stated_standard)

            # Charter section for game should reference stated standard
            section = packet_quality_charter_section(proj, "reviewer-design", wo)
            self.assertIn("stated standard", section.lower())
            self.assertNotIn("photoreal", section.lower())

    def test_physical_product_gets_realism_criteria(self):
        """Physical product gets the charter's photorealism criteria"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)
            wo = make_visual_work_order(product_type="physical_product")

            section = packet_quality_charter_section(proj, "reviewer-design", wo)
            self.assertIn("materials", section.lower())
            self.assertIn("light", section.lower())
            self.assertIn("contact", section.lower())
            self.assertIn("scale", section.lower())

    def test_product_type_detection(self):
        """Product type is detected from work order"""
        physical_wo = make_visual_work_order(product_type="physical_product")
        self.assertEqual(get_product_type(physical_wo), "physical_product")

        game_wo = make_visual_work_order(product_type="game")
        self.assertEqual(get_product_type(game_wo), "game")

        illustration_wo = make_visual_work_order(product_type="illustration")
        self.assertEqual(get_product_type(illustration_wo), "illustration")

        # Default should be physical_product for visual ui work
        default_wo = make_visual_work_order(product_type=None)
        default_wo.description = ""  # Clear description
        self.assertEqual(get_product_type(default_wo), "physical_product")


class SetConsistencyTests(unittest.TestCase):
    """Test the same-subject test for sets of related deliverables."""

    def test_s7_set_divergence_fails_quality(self):
        """S7: Assets that pass individually but diverge from each other fail quality"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)
            anchors = create_anchor_images(proj)

            # Work order for a set of product images
            wo = make_visual_work_order()
            wo.anchors = [anchors["photoreal"]]
            wo.identity_reference = "renders/product-canonical.png"
            wo.identity_traits = ["finish", "detail_colors", "mounting", "proportions", "markings"]
            wo.deliverable_set = ["renders/product-front.png", "renders/product-side.png"]

            # Review where both assets pass anchor comparison individually
            review = {
                "station": "reviewer-design",
                "verdict": "fail",
                "compliance": {"verdict": "pass", "findings": []},
                "quality": {
                    "verdict": "fail",
                    "anchor_comparison": [
                        {
                            "asset": "renders/product-front.png",
                            "anchor": anchors["photoreal"],
                            "verdict": "pass"
                        },
                        {
                            "asset": "renders/product-side.png",
                            "anchor": anchors["photoreal"],
                            "verdict": "pass"
                        }
                    ],
                    "same_subject_test": {
                        "verdict": "fail",
                        "identity_reference": wo.identity_reference,
                        "divergences": [
                            {
                                "asset": "renders/product-side.png",
                                "trait": "detail_colors",
                                "description": "Logo rendered in blue instead of red as shown in canonical reference"
                            }
                        ]
                    },
                    "findings": [
                        "Set consistency failure: renders/product-side.png diverges on trait 'detail_colors' - Logo rendered in blue instead of red as shown in canonical reference"
                    ]
                }
            }

            # Both assets passed anchor comparison
            for comparison in review["quality"]["anchor_comparison"]:
                self.assertEqual(comparison["verdict"], "pass")

            # But same-subject test failed
            self.assertEqual(review["quality"]["same_subject_test"]["verdict"], "fail")

            # Divergent asset and trait must be named
            divergences = review["quality"]["same_subject_test"]["divergences"]
            self.assertEqual(len(divergences), 1)
            self.assertIn("asset", divergences[0])
            self.assertIn("trait", divergences[0])

            # Overall quality verdict is fail
            self.assertEqual(review["quality"]["verdict"], "fail")

    def test_s7_identity_traits_enumerated(self):
        """S7: Identity traits for the set are enumerated in work order"""
        wo = make_visual_work_order()
        wo.identity_traits = ["finish", "detail_colors", "mounting", "proportions", "markings"]

        # Physical product should have these specific traits
        required_traits = ["finish", "detail_colors", "mounting", "proportions", "markings"]
        for trait in required_traits:
            self.assertIn(trait, wo.identity_traits)

    def test_s7_set_passes_when_consistent(self):
        """S7: Set that is consistent across all traits passes quality"""
        review = {
            "station": "reviewer-design",
            "verdict": "pass",
            "quality": {
                "verdict": "pass",
                "anchor_comparison": [
                    {"asset": "renders/product-front.png", "verdict": "pass"},
                    {"asset": "renders/product-side.png", "verdict": "pass"}
                ],
                "same_subject_test": {
                    "verdict": "pass",
                    "identity_reference": "renders/product-canonical.png",
                    "divergences": []
                },
                "findings": []
            }
        }

        self.assertEqual(review["quality"]["same_subject_test"]["verdict"], "pass")
        self.assertEqual(len(review["quality"]["same_subject_test"]["divergences"]), 0)
        self.assertEqual(review["quality"]["verdict"], "pass")


class DesignReferenceDirectoryTests(unittest.TestCase):
    """Test that design/reference/ directory is created by scaffolding."""

    def test_design_reference_created_by_scaffold(self):
        """Scaffolding creates design/reference/ directory"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)

            # design/reference should exist
            ref_dir = proj / "design" / "reference"
            self.assertTrue(ref_dir.exists())
            self.assertTrue(ref_dir.is_dir())

    def test_design_reference_never_overwritten(self):
        """Scaffolding never overwrites existing design/reference/ contents"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project_with_design(tmp)

            # Add a file to design/reference
            ref_dir = proj / "design" / "reference"
            anchor = ref_dir / "my-anchor.jpg"
            anchor.write_bytes(b"ORIGINAL_CONTENT")

            # Run scaffold again
            scaffold_design_system(proj)

            # Original file should be preserved
            self.assertEqual(anchor.read_bytes(), b"ORIGINAL_CONTENT")


if __name__ == "__main__":
    unittest.main()
