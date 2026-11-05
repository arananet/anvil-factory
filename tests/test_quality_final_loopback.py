"""Tests for quality standard round 5 final loopback defects.

Tests verify:
1. stations/reviewer-design/PROMPT.md explicitly documents S7 same-subject test duty
2. Control character sanitization on identity_reference and identity_traits in packet output
"""

import re
import tempfile
import unittest
from pathlib import Path

from anvil.model import WorkOrder
from anvil.quality import packet_quality_charter_section


ROOT = Path(__file__).resolve().parent.parent


class PromptDocumentationTests(unittest.TestCase):
    """Tests verifying S7 same-subject test duty is documented in reviewer-design prompt."""

    def test_reviewer_design_prompt_documents_same_subject_test_duty(self):
        """reviewer-design PROMPT.md explicitly documents the S7 same-subject test duty"""
        prompt_path = ROOT / "stations" / "reviewer-design" / "PROMPT.md"
        self.assertTrue(prompt_path.exists(), "reviewer-design PROMPT.md must exist")

        prompt_text = prompt_path.read_text()

        # The prompt must explicitly document the same-subject test duty, not just
        # reference duties from the packet generically. Per round 5 finding F1:
        # "it applies when the work order declares both identity_reference and
        # deliverable_set; the reviewer performs a same-subject comparison across
        # the entire deliverable set against the identity reference on the enumerated
        # identity traits; any divergence is a quality failure that must be named in
        # the findings; the ruling and its evidence are recorded in the review's
        # quality section."

        # Check for explicit same-subject test documentation
        # The prompt must mention "same-subject" or "same subject" in context of the duty
        self.assertRegex(
            prompt_text.lower(),
            r'same[- ]subject',
            "Prompt must explicitly mention 'same-subject' or 'same subject' test"
        )

        # Must document that it applies when identity_reference and deliverable_set present
        # Look for mentions of identity_reference or deliverable_set in proximity to the duty
        has_identity_context = (
            "identity_reference" in prompt_text.lower() or
            "identity reference" in prompt_text.lower() or
            "deliverable_set" in prompt_text.lower() or
            "deliverable set" in prompt_text.lower()
        )
        self.assertTrue(
            has_identity_context,
            "Prompt must document when the same-subject test applies "
            "(identity_reference and deliverable_set)"
        )

        # Must document that comparison happens across the deliverable set
        # against the identity reference
        has_comparison_duty = (
            ("compar" in prompt_text.lower() and "set" in prompt_text.lower()) or
            ("across" in prompt_text.lower() and "deliverable" in prompt_text.lower())
        )
        self.assertTrue(
            has_comparison_duty,
            "Prompt must document comparison across deliverable set against identity reference"
        )

        # Must document that divergence is a quality failure
        has_divergence_handling = (
            "diverg" in prompt_text.lower() or
            "fail" in prompt_text.lower() or
            "quality" in prompt_text.lower()
        )
        self.assertTrue(
            has_divergence_handling,
            "Prompt must document that divergence is a quality failure"
        )

        # Must document that findings record the divergent asset and trait
        has_findings_requirement = (
            ("finding" in prompt_text.lower() or "record" in prompt_text.lower()) and
            "quality" in prompt_text.lower()
        )
        self.assertTrue(
            has_findings_requirement,
            "Prompt must document recording findings in quality section"
        )


class SanitizationTests(unittest.TestCase):
    """Tests verifying control character sanitization in quality packet sections."""

    def test_identity_reference_sanitizes_control_characters(self):
        """identity_reference field sanitizes control characters in packet output"""
        # Create work order with control characters in identity_reference
        # Using various control characters that should be removed
        malicious_ref = "design/ref\x00/prod\x1fuct.jpg"  # NULL and US (unit separator)

        wo = WorkOrder(
            id="wo-sanitize-test",
            kind="feature",
            title="Test sanitization",
            description="Test work order",
            surfaces=["ui"],  # Visual run
            identity_reference=malicious_ref,
            deliverable_set=["output1.jpg", "output2.jpg"],
            identity_traits=["color", "finish"]
        )

        # Generate quality charter section for reviewer-design
        # Use Path(".") as project since we only care about the text output
        charter_text = packet_quality_charter_section(Path("."), "reviewer-design", wo)

        # The control characters should be removed from the output
        # Original: "design/ref\x00/prod\x1fuct.jpg"
        # Sanitized: "design/ref/product.jpg"
        self.assertNotIn("\x00", charter_text, "NULL character must be sanitized")
        self.assertNotIn("\x1f", charter_text, "Unit separator must be sanitized")

        # Verify the cleaned version appears
        self.assertIn("design/ref/product.jpg", charter_text,
                     "Sanitized path should appear in output")

    def test_identity_traits_sanitize_control_characters(self):
        """identity_traits items sanitize control characters in packet output"""
        # Create work order with control characters in identity_traits
        malicious_traits = [
            "color\x08scheme",      # Backspace
            "finish\x1btexture",    # Escape
            "mounting\x7fdetails"   # Delete
        ]

        wo = WorkOrder(
            id="wo-sanitize-traits",
            kind="feature",
            title="Test traits sanitization",
            description="Test work order",
            surfaces=["ui"],  # Visual run
            identity_reference="design/ref/product.jpg",
            deliverable_set=["output1.jpg", "output2.jpg"],
            identity_traits=malicious_traits
        )

        # Generate quality charter section for reviewer-design
        charter_text = packet_quality_charter_section(Path("."), "reviewer-design", wo)

        # Control characters should be removed
        self.assertNotIn("\x08", charter_text, "Backspace must be sanitized")
        self.assertNotIn("\x1b", charter_text, "Escape must be sanitized")
        self.assertNotIn("\x7f", charter_text, "Delete must be sanitized")

        # Verify sanitized traits appear
        self.assertIn("colorscheme", charter_text, "Sanitized 'colorscheme' should appear")
        self.assertIn("finishtexture", charter_text, "Sanitized 'finishtexture' should appear")
        self.assertIn("mountingdetails", charter_text, "Sanitized 'mountingdetails' should appear")

    def test_all_quality_packet_interpolations_are_sanitized(self):
        """All work order strings interpolated into quality packet are sanitized"""
        # Create work order with control characters in all quality-related fields
        wo = WorkOrder(
            id="wo-full-sanitize",
            kind="feature",
            title="Full sanitization test",
            description="Test all fields",
            surfaces=["ui"],  # Visual run
            identity_reference="ref\x00with\x1fcontrols.jpg",
            deliverable_set=["out\x08put1.jpg", "out\x1bput2.jpg"],
            identity_traits=["trait\x7fone", "trait\x0etwo"]
        )

        # Generate quality charter section
        charter_text = packet_quality_charter_section(Path("."), "reviewer-design", wo)

        # Verify no control characters appear in output
        # Test for common dangerous control characters (excluding safe \n and \t)
        dangerous_controls = [
            "\x00",  # NULL
            "\x01", "\x02", "\x03", "\x04", "\x05", "\x06", "\x07",  # SOH-BEL
            "\x08",  # Backspace
            "\x0b",  # Vertical tab
            "\x0c",  # Form feed
            "\x0e", "\x0f",  # SO, SI
            "\x10", "\x11", "\x12", "\x13", "\x14", "\x15", "\x16", "\x17",
            "\x18", "\x19", "\x1a", "\x1b", "\x1c", "\x1d", "\x1e", "\x1f",  # Various controls
            "\x7f",  # DEL
        ]

        for ctrl_char in dangerous_controls:
            self.assertNotIn(
                ctrl_char,
                charter_text,
                f"Control character {repr(ctrl_char)} must be sanitized from quality packet"
            )

    def test_anchor_section_sanitizes_control_characters(self):
        """Anchor section output also sanitizes control characters from work order fields"""
        from anvil.quality import packet_anchor_section

        wo = WorkOrder(
            id="wo-anchor-sanitize",
            kind="feature",
            title="Anchor sanitization test",
            description="Test anchor section",
            surfaces=["ui"],  # Visual run
            anchors=["design/ref\x00/anchor\x1f.jpg"],
            identity_reference="identity\x08ref.jpg",
            deliverable_set=["output.jpg"],
            identity_traits=["trait\x1bone"]
        )

        # Generate anchor section
        anchor_text = packet_anchor_section(Path("/tmp"), "reviewer-design", wo)

        # Verify control characters are sanitized
        self.assertNotIn("\x00", anchor_text, "NULL must be sanitized in anchor section")
        self.assertNotIn("\x1f", anchor_text, "US must be sanitized in anchor section")
        self.assertNotIn("\x08", anchor_text, "Backspace must be sanitized in anchor section")
        self.assertNotIn("\x1b", anchor_text, "Escape must be sanitized in anchor section")


if __name__ == "__main__":
    unittest.main()
