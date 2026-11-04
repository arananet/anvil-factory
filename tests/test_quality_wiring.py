"""Integration tests for quality standard wiring into the runner.

Tests verify the requirements from gate loopback round 2, item 5:
- Visual run's generating and reviewing packets contain charter and anchor sections
- Visual run with no anchors produces report warning
- Non-visual run contains no charter text anywhere (S3)
- reviewer-design dual-section output validates against contract
- Traversal paths in new WorkOrder fields are rejected
"""

import json
import tempfile
import unittest
from pathlib import Path

from anvil.scaffold import init_project
from anvil.design import scaffold_design_system
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.stations import load_registry
from anvil.runner import run_pipeline
from anvil.quality import (
    validate_reviewer_quality_section,
)


ROOT = Path(__file__).resolve().parent.parent


def make_test_project(tmp, with_anchors=True):
    """Helper: create a test project with design system."""
    proj = Path(tmp) / "proj"
    init_project(proj, "TestProj")
    scaffold_design_system(proj)

    if with_anchors:
        # Create fixture anchor images
        anchor_dir = proj / "design" / "reference"
        anchor_dir.mkdir(parents=True, exist_ok=True)
        (anchor_dir / "product-photoreal.jpg").write_bytes(b"FAKE_PHOTOREAL_IMAGE")

    return proj


class QualityWiringIntegrationTests(unittest.TestCase):
    """Integration tests proving quality charter and anchor wiring into runner."""

    def test_visual_run_packets_contain_charter_and_anchor_sections(self):
        """Visual run: generating and reviewing packets contain charter and anchor sections"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_test_project(tmp, with_anchors=True)

            # Create visual work order with anchors
            wo = WorkOrder(
                id="wo-visual-wiring",
                kind="feature",
                title="Product render",
                surfaces=["ui"],
                description="Physical product rendering",
                anchors=["design/reference/product-photoreal.jpg"]
            )

            # Load registry and pipeline
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(
                ROOT / "pipelines" / "sdlc-default.json",
                known_stations=set(reg.ids())
            )

            # Run pipeline in packets-only mode
            report = run_pipeline(proj, pipe, wo, registry=reg)

            # Check that packets were generated
            runs_dir = proj / "runs" / wo.id
            self.assertTrue(runs_dir.exists())

            # Check generating station packets contain charter and anchors
            generating_stations = ["builder", "media-producer"]
            for station_id in generating_stations:
                packet_path = runs_dir / f"{station_id}.packet.md"
                if packet_path.exists():
                    packet_text = packet_path.read_text()

                    # Charter section must be present
                    self.assertIn("Quality Charter", packet_text,
                                f"{station_id} packet missing Quality Charter section")
                    self.assertIn("Observable criteria", packet_text,
                                f"{station_id} packet missing criteria")

                    # Physical product criteria
                    packet_lower = packet_text.lower()
                    self.assertIn("materials", packet_lower)
                    self.assertIn("light", packet_lower)
                    self.assertIn("contact", packet_lower)
                    self.assertIn("scale", packet_lower)

                    # Anchor section must be present
                    self.assertIn("Reference Anchors", packet_text,
                                f"{station_id} packet missing Reference Anchors section")
                    self.assertIn("design/reference/product-photoreal.jpg", packet_text,
                                f"{station_id} packet missing anchor citation")

            # Check reviewer-design packet contains charter and anchors
            reviewer_packet = runs_dir / "reviewer-design.packet.md"
            if reviewer_packet.exists():
                packet_text = reviewer_packet.read_text()

                self.assertIn("Quality Charter", packet_text,
                            "reviewer-design packet missing Quality Charter section")
                self.assertIn("Reference Anchors", packet_text,
                            "reviewer-design packet missing Reference Anchors section")

    def test_visual_run_without_anchors_produces_warning(self):
        """Visual run with no anchors: report contains visible warning"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_test_project(tmp, with_anchors=False)

            # Remove design/reference directory entirely
            import shutil
            ref_dir = proj / "design" / "reference"
            if ref_dir.exists():
                shutil.rmtree(ref_dir)

            # Create visual work order with no anchors
            wo = WorkOrder(
                id="wo-no-anchors",
                kind="feature",
                title="Product render without anchors",
                surfaces=["ui"],
                description="Physical product rendering"
            )

            # Load registry and pipeline
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(
                ROOT / "pipelines" / "sdlc-default.json",
                known_stations=set(reg.ids())
            )

            # Run pipeline
            report = run_pipeline(proj, pipe, wo, registry=reg)

            # Check that warning is in report
            self.assertIn("warnings", report.to_dict())
            warnings = report.to_dict()["warnings"]

            # Should have a warning about missing anchors
            has_anchor_warning = any(
                "no reference anchors" in w.lower() or "missing anchors" in w.lower()
                for w in warnings
            )
            self.assertTrue(has_anchor_warning,
                          "Report missing warning about no reference anchors")

            # Check packets still have charter (floor) but warn about missing anchors
            runs_dir = proj / "runs" / wo.id
            reviewer_packet = runs_dir / "reviewer-design.packet.md"
            if reviewer_packet.exists():
                packet_text = reviewer_packet.read_text()

                # Charter should still be present (charter floor)
                self.assertIn("Quality Charter", packet_text)

                # Warning about missing anchors should be visible
                self.assertIn("WARNING", packet_text)
                self.assertIn("no reference anchors", packet_text.lower())

    def test_non_visual_run_never_receives_charter(self):
        """S3: Non-visual run contains no charter text in any packet or report"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_test_project(tmp)

            # Create non-visual work order (API only)
            wo = WorkOrder(
                id="wo-non-visual",
                kind="feature",
                title="API endpoint",
                surfaces=["api"],
                description="Add new API endpoint"
            )

            # Load registry and pipeline
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(
                ROOT / "pipelines" / "sdlc-default.json",
                known_stations=set(reg.ids())
            )

            # Run pipeline
            report = run_pipeline(proj, pipe, wo, registry=reg)

            # Check that NO packet contains charter text
            runs_dir = proj / "runs" / wo.id

            # Check all generated packets
            for packet_path in runs_dir.glob("*.packet.md"):
                packet_text = packet_path.read_text()

                # Charter section header must NOT be present (as injected data)
                # Note: Station prompts may mention "Quality Charter" in documentation,
                # but the actual "## Quality Charter" section should not be injected
                lines = packet_text.split("\n")
                for line in lines:
                    if line.startswith("## "):
                        self.assertNotIn("Quality Charter", line,
                                       f"{packet_path.name} has Quality Charter section header")
                        self.assertNotIn("Reference Anchor", line,
                                       f"{packet_path.name} has Reference Anchors section header")

                # Observable criteria section content should not appear
                # (This would indicate the charter was actually injected)
                self.assertNotIn("Observable criteria:", packet_text,
                               f"{packet_path.name} contains injected quality criteria")

            # Report should make no mention of quality standard
            report_dict = report.to_dict()
            report_json = json.dumps(report_dict)

            # Quality standard terms should not appear in report
            self.assertNotIn("quality charter", report_json.lower())
            self.assertNotIn("quality standard", report_json.lower())


class ReviewerDualSectionValidationTests(unittest.TestCase):
    """Tests for reviewer-design dual-section (compliance + quality) contract."""

    def test_dual_section_output_validates(self):
        """reviewer-design dual-section review validates correctly"""
        # Valid dual-section review
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
                    "Materials: Surface reads as plastic, anchor shows metal",
                    "Light: Missing shadow complexity from anchor"
                ],
                "anchor": "design/reference/product.jpg"
            }
        }

        # Should validate successfully
        is_valid = validate_reviewer_quality_section(review)
        self.assertTrue(is_valid, "Valid dual-section review should validate")

        # Verify both sections are distinct
        self.assertIn("compliance", review)
        self.assertIn("quality", review)
        self.assertEqual(review["compliance"]["verdict"], "pass")
        self.assertEqual(review["quality"]["verdict"], "fail")

    def test_dual_section_pass_compliance_fail_quality(self):
        """Review can pass compliance but fail quality"""
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
                    "Contact: Objects float above surfaces (charter floor gap)"
                ],
                "anchor": "design/reference/stylized.jpg"
            }
        }

        is_valid = validate_reviewer_quality_section(review)
        self.assertTrue(is_valid)

    def test_dual_section_requires_quality_anchor_citation(self):
        """Quality section findings must cite anchor"""
        review = {
            "station": "reviewer-design",
            "verdict": "fail",
            "quality": {
                "verdict": "fail",
                "findings": ["Generic quality issue without anchor"]
                # Missing anchor field
            }
        }

        # Should fail validation - no anchor cited
        is_valid = validate_reviewer_quality_section(review)
        self.assertFalse(is_valid, "Quality section without anchor should fail validation")

    def test_dual_section_quality_findings_cite_criteria(self):
        """Quality findings must name specific criteria categories"""
        review = {
            "station": "reviewer-design",
            "verdict": "fail",
            "quality": {
                "verdict": "fail",
                "findings": [
                    "Materials: Surfaces read as molded plastic instead of metal shown in anchor",
                    "Light: Single flat light, missing studio lighting from anchor",
                    "Scale: Product reads as toy-sized instead of full-scale",
                    "Contact: Objects meet surfaces correctly per anchor"
                ],
                "anchor": "design/reference/product.jpg"
            }
        }

        is_valid = validate_reviewer_quality_section(review)
        self.assertTrue(is_valid)

        # Check that criteria categories are named
        findings = review["quality"]["findings"]
        categories = ["Materials", "Light", "Scale", "Contact"]
        found_categories = [c for c in categories if any(c in f for f in findings)]
        self.assertGreater(len(found_categories), 0,
                         "Quality findings should cite specific criteria")


class PathValidationTests(unittest.TestCase):
    """Tests for path traversal validation in WorkOrder quality fields."""

    def test_anchors_rejects_parent_traversal(self):
        """anchors field rejects parent directory traversal"""
        with self.assertRaises(ValueError) as ctx:
            WorkOrder(
                id="wo-bad-anchor",
                kind="feature",
                title="Bad anchor path",
                surfaces=["ui"],
                anchors=["../../../etc/passwd"]
            )

        self.assertIn("..", str(ctx.exception).lower())

    def test_anchors_rejects_absolute_paths(self):
        """anchors field rejects absolute paths"""
        with self.assertRaises(ValueError) as ctx:
            WorkOrder(
                id="wo-abs-anchor",
                kind="feature",
                title="Absolute anchor path",
                surfaces=["ui"],
                anchors=["/etc/passwd"]
            )

        self.assertIn("absolute", str(ctx.exception).lower())

    def test_identity_reference_rejects_traversal(self):
        """identity_reference field rejects path traversal"""
        with self.assertRaises(ValueError) as ctx:
            WorkOrder(
                id="wo-bad-ref",
                kind="feature",
                title="Bad identity reference",
                surfaces=["ui"],
                identity_reference="../../../etc/passwd"
            )

        self.assertIn("..", str(ctx.exception).lower())

    def test_deliverable_set_rejects_traversal(self):
        """deliverable_set field rejects path traversal in any item"""
        with self.assertRaises(ValueError) as ctx:
            WorkOrder(
                id="wo-bad-deliverable",
                kind="feature",
                title="Bad deliverable path",
                surfaces=["ui"],
                deliverable_set=[
                    "renders/product-front.png",
                    "../../../etc/passwd"  # Malicious path
                ]
            )

        self.assertIn("..", str(ctx.exception).lower())

    def test_valid_relative_paths_accepted(self):
        """Valid relative paths are accepted"""
        # Should not raise
        wo = WorkOrder(
            id="wo-good-paths",
            kind="feature",
            title="Good paths",
            surfaces=["ui"],
            anchors=["design/reference/product.jpg"],
            identity_reference="renders/product-canonical.png",
            deliverable_set=["renders/product-front.png", "renders/product-side.png"]
        )

        self.assertEqual(wo.anchors, ["design/reference/product.jpg"])
        self.assertEqual(wo.identity_reference, "renders/product-canonical.png")
        self.assertEqual(len(wo.deliverable_set), 2)

    def test_from_dict_validates_paths(self):
        """WorkOrder.from_dict validates quality field paths"""
        # Parent traversal in anchors
        with self.assertRaises(ValueError) as ctx:
            WorkOrder.from_dict({
                "id": "wo-dict-bad",
                "kind": "feature",
                "title": "Bad from dict",
                "surfaces": ["ui"],
                "anchors": ["../../etc/passwd"]
            })

        self.assertIn("..", str(ctx.exception).lower())

    def test_from_dict_backslash_traversal(self):
        """from_dict rejects backslash path traversal (Windows-style)"""
        with self.assertRaises(ValueError) as ctx:
            WorkOrder.from_dict({
                "id": "wo-backslash",
                "kind": "feature",
                "title": "Backslash traversal",
                "surfaces": ["ui"],
                "identity_reference": "..\\..\\windows\\system32"
            })

        error_msg = str(ctx.exception).lower()
        self.assertTrue("\\" in str(ctx.exception) or "dangerous" in error_msg)


if __name__ == "__main__":
    unittest.main()
