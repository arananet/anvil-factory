"""Tests for S7 same-subject test duty in quality standard.

Tests verify gate loopback round 4, item 3: when a work order declares
identity_reference and deliverable_set, the same-subject test duty appears
in the reviewer-design packet, instructing the reviewer to perform cross-set
comparison against the identity reference on enumerated traits.
"""

import tempfile
import unittest
from pathlib import Path

from anvil.scaffold import init_project
from anvil.design import scaffold_design_system
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.stations import load_registry
from anvil.runner import run_pipeline


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


class SameSubjectTestDutyTests(unittest.TestCase):
    """Tests for S7 same-subject test duty packet injection."""

    def test_same_subject_duty_injected_when_identity_reference_declared(self):
        """When work order has identity_reference and deliverable_set, packet contains same-subject test duty"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_test_project(tmp, with_anchors=True)

            # Create visual work order with identity_reference and deliverable_set
            wo = WorkOrder(
                id="wo-same-subject",
                kind="feature",
                title="Product asset set",
                surfaces=["ui"],
                description="Physical product rendering set",
                anchors=["design/reference/product-photoreal.jpg"],
                identity_reference="renders/product-canonical.png",
                identity_traits=["finish", "detail_colors", "mounting", "proportions", "markings"],
                deliverable_set=[
                    "renders/product-canonical.png",
                    "renders/product-front.png",
                    "renders/product-side.png",
                    "renders/product-back.png"
                ]
            )

            # Load registry and pipeline
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(
                ROOT / "pipelines" / "sdlc-default.json",
                known_stations=set(reg.ids())
            )

            # Run pipeline in packets-only mode
            report = run_pipeline(proj, pipe, wo, registry=reg)

            # Check reviewer-design packet contains same-subject test duty
            runs_dir = proj / "runs" / wo.id
            reviewer_packet = runs_dir / "reviewer-design.packet.md"

            self.assertTrue(reviewer_packet.exists(),
                          "reviewer-design packet should exist")

            packet_text = reviewer_packet.read_text()

            # Packet should mention same-subject test requirement
            self.assertIn("same-subject", packet_text.lower(),
                        "Packet missing same-subject test duty")

            # Packet should reference the identity reference
            self.assertIn("identity reference", packet_text.lower(),
                        "Packet missing identity reference concept")

            # Packet should mention deliverable set comparison
            self.assertIn("deliverable", packet_text.lower(),
                        "Packet missing deliverable set concept")

            # Packet should reference the identity traits to compare
            packet_lower = packet_text.lower()
            # At least some identity traits should be mentioned or the concept of traits
            has_trait_guidance = (
                "trait" in packet_lower or
                "finish" in packet_lower or
                "proportions" in packet_lower or
                "markings" in packet_lower
            )
            self.assertTrue(has_trait_guidance,
                          "Packet missing identity traits guidance")

    def test_same_subject_duty_absent_when_fields_not_declared(self):
        """When work order has no identity_reference/deliverable_set, packet has no same-subject duty"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_test_project(tmp, with_anchors=True)

            # Create visual work order WITHOUT identity_reference or deliverable_set
            wo = WorkOrder(
                id="wo-no-same-subject",
                kind="feature",
                title="Product render",
                surfaces=["ui"],
                description="Physical product rendering",
                anchors=["design/reference/product-photoreal.jpg"]
                # No identity_reference
                # No deliverable_set
            )

            # Load registry and pipeline
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(
                ROOT / "pipelines" / "sdlc-default.json",
                known_stations=set(reg.ids())
            )

            # Run pipeline in packets-only mode
            report = run_pipeline(proj, pipe, wo, registry=reg)

            # Check reviewer-design packet does NOT contain same-subject test duty
            runs_dir = proj / "runs" / wo.id
            reviewer_packet = runs_dir / "reviewer-design.packet.md"

            self.assertTrue(reviewer_packet.exists(),
                          "reviewer-design packet should exist")

            packet_text = reviewer_packet.read_text()

            # Packet should NOT mention same-subject test when fields absent
            # (This verifies the duty is conditional, not always injected)
            packet_lower = packet_text.lower()

            # If "same-subject" appears, it should NOT be in the context of a duty/requirement
            # Look for the absence of the specific duty language
            has_same_subject_duty = (
                "same-subject test" in packet_lower or
                "same subject test" in packet_lower or
                ("same-subject" in packet_lower and "perform" in packet_lower) or
                ("same subject" in packet_lower and "compare" in packet_lower and "set" in packet_lower)
            )

            self.assertFalse(has_same_subject_duty,
                           "Packet should not contain same-subject test duty when fields absent")

    def test_same_subject_duty_with_only_identity_reference(self):
        """Identity reference alone (no deliverable_set) does not trigger same-subject duty"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_test_project(tmp, with_anchors=True)

            # Create work order with identity_reference but NO deliverable_set
            wo = WorkOrder(
                id="wo-ref-only",
                kind="feature",
                title="Product with reference only",
                surfaces=["ui"],
                description="Physical product rendering",
                anchors=["design/reference/product-photoreal.jpg"],
                identity_reference="renders/product-canonical.png"
                # No deliverable_set - same-subject test needs both fields
            )

            # Load registry and pipeline
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(
                ROOT / "pipelines" / "sdlc-default.json",
                known_stations=set(reg.ids())
            )

            # Run pipeline
            report = run_pipeline(proj, pipe, wo, registry=reg)

            # Check packet
            runs_dir = proj / "runs" / wo.id
            reviewer_packet = runs_dir / "reviewer-design.packet.md"

            packet_text = reviewer_packet.read_text()
            packet_lower = packet_text.lower()

            # Should not have full same-subject test duty without deliverable_set
            has_cross_set_duty = (
                ("deliverable" in packet_lower and "set" in packet_lower) or
                ("across the set" in packet_lower) or
                ("whole set" in packet_lower)
            )

            self.assertFalse(has_cross_set_duty,
                           "Should not inject cross-set duty without deliverable_set")

    def test_same_subject_duty_with_only_deliverable_set(self):
        """Deliverable set alone (no identity_reference) does not trigger same-subject duty"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_test_project(tmp, with_anchors=True)

            # Create work order with deliverable_set but NO identity_reference
            wo = WorkOrder(
                id="wo-set-only",
                kind="feature",
                title="Product set without canonical reference",
                surfaces=["ui"],
                description="Physical product rendering",
                anchors=["design/reference/product-photoreal.jpg"],
                deliverable_set=[
                    "renders/product-front.png",
                    "renders/product-side.png"
                ]
                # No identity_reference - same-subject test needs both fields
            )

            # Load registry and pipeline
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(
                ROOT / "pipelines" / "sdlc-default.json",
                known_stations=set(reg.ids())
            )

            # Run pipeline
            report = run_pipeline(proj, pipe, wo, registry=reg)

            # Check packet
            runs_dir = proj / "runs" / wo.id
            reviewer_packet = runs_dir / "reviewer-design.packet.md"

            packet_text = reviewer_packet.read_text()
            packet_lower = packet_text.lower()

            # Should not have identity reference comparison duty without identity_reference
            has_identity_ref_duty = (
                "identity reference" in packet_lower and
                ("compare" in packet_lower or "against" in packet_lower)
            )

            self.assertFalse(has_identity_ref_duty,
                           "Should not inject identity reference duty without identity_reference field")

    def test_same_subject_duty_references_identity_traits(self):
        """When both fields present, packet references the specific identity traits to compare"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_test_project(tmp, with_anchors=True)

            # Create work order with identity_reference, deliverable_set AND identity_traits
            wo = WorkOrder(
                id="wo-with-traits",
                kind="feature",
                title="Product asset set with traits",
                surfaces=["ui"],
                description="Physical product rendering set",
                anchors=["design/reference/product-photoreal.jpg"],
                identity_reference="renders/product-canonical.png",
                identity_traits=["finish", "detail_colors", "mounting"],
                deliverable_set=[
                    "renders/product-canonical.png",
                    "renders/product-angle1.png",
                    "renders/product-angle2.png"
                ]
            )

            # Load registry and pipeline
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(
                ROOT / "pipelines" / "sdlc-default.json",
                known_stations=set(reg.ids())
            )

            # Run pipeline
            report = run_pipeline(proj, pipe, wo, registry=reg)

            # Check packet
            runs_dir = proj / "runs" / wo.id
            reviewer_packet = runs_dir / "reviewer-design.packet.md"

            packet_text = reviewer_packet.read_text()

            # Packet should reference traits in the same-subject duty context
            # Either by listing them or by mentioning "identity traits"
            packet_lower = packet_text.lower()

            has_trait_reference = (
                "identity trait" in packet_lower or
                "finish" in packet_lower or
                "detail" in packet_lower or
                "mounting" in packet_lower
            )

            self.assertTrue(has_trait_reference,
                          "Packet should reference identity traits when declared")


if __name__ == "__main__":
    unittest.main()
