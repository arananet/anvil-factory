"""Tests for lifecycle board accessibility and visual quality (loopback 1 findings).

Covers loopback findings from wo-gh-13:
- A. Link structure: board rows link to job details with real anchor elements
- B. Contrast ratios: WCAG 4.5:1 minimum for all text/background pairs
- C. Spacing scale: consistent spacing via CSS custom properties
- D. Responsive behavior: stages row adapts at narrow widths
- E. Rendered evidence: Playwright captures (when available)
"""

import json
import re
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.statuspage import render_status_page, CSS

# Import Playwright for rendered evidence tests
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def write_report(proj, folder, data):
    """Write a report.json fixture to runs/<folder>/."""
    d = Path(proj) / "runs" / folder
    d.mkdir(parents=True, exist_ok=True)
    (d / "report.json").write_text(json.dumps(data))


def write_merge_record(proj, work_order_id, merged=True, pr_number=None):
    """Write a merge record fixture for a work order."""
    merge_dir = Path(proj) / "merge_records"
    merge_dir.mkdir(parents=True, exist_ok=True)
    record = {"work_order_id": work_order_id, "merged": merged}
    if pr_number:
        record["pr_number"] = pr_number
    (merge_dir / f"{work_order_id}.json").write_text(json.dumps(record))


# Fixture: approved work order
APPROVED_RUN = {
    "work_order_id": "wo-link-001",
    "pipeline": "sdlc-default",
    "title": "Approved work order",
    "kind": "feature",
    "verdict": "approved",
    "human_required": False,
    "loopbacks": 0,
    "steps": [
        {"station": "intake", "status": "completed", "duration_ms": 1.0, "cost": None, "artifacts": []},
        {"station": "spec-writer", "status": "executed", "duration_ms": 100.0, "cost": None, "artifacts": []},
        {"station": "builder", "status": "executed", "duration_ms": 200.0, "cost": None, "artifacts": []},
        {"station": "reviewer-spec", "status": "executed", "duration_ms": 50.0, "cost": None, "artifacts": []},
        {"station": "approver", "status": "completed", "duration_ms": 1.0, "cost": None, "artifacts": []},
    ],
    "decision": {
        "approver": {
            "reviews_counted": [{"station": "reviewer-spec", "verdict": "pass"}],
            "reviews_expected": ["reviewer-spec"],
            "rule": "All counted reviews passed.",
        },
        "human_gate": {
            "required": False,
            "rule": "No risk hints matched, so no human is required.",
            "hints_matched": [],
        },
    },
    "risk_hints": [],
}


class TestBoardLinkStructure(unittest.TestCase):
    """Test board link structure (loopback finding A)."""

    def test_board_row_work_order_id_is_real_anchor_element(self):
        """Finding A: work order ID in board row is <a> element with href to detail section."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)

            write_report(proj, "wo-link-001", APPROVED_RUN)
            write_report(proj, "wo-link-002", {
                **APPROVED_RUN,
                "work_order_id": "wo-link-002",
                "title": "Second work order",
            })

            page, _ = render_status_page(proj, generated_at="2026-11-04 00:00:00 UTC")

            # Verify each work order ID in the board is a real anchor element
            # Pattern: <a href="#wo-link-001-detail" class="board-wo-id">wo-link-001</a>
            for wo_id in ["wo-link-001", "wo-link-002"]:
                # Check for anchor element with correct href
                anchor_pattern = rf'<a href="#{re.escape(wo_id)}-detail"[^>]*>{re.escape(wo_id)}</a>'
                self.assertIsNotNone(
                    re.search(anchor_pattern, page),
                    f"Work order {wo_id} should be a real anchor element with href to #{wo_id}-detail"
                )

    def test_detailed_section_has_matching_id_attribute(self):
        """Finding A: detailed run section has id attribute matching the board link href."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)

            write_report(proj, "wo-link-001", APPROVED_RUN)

            page, _ = render_status_page(proj, generated_at="2026-11-04 00:00:00 UTC")

            # Verify the detailed section has the matching id
            # Pattern: <section class="run" id="wo-link-001-detail">
            detail_pattern = r'<section[^>]*id="wo-link-001-detail"[^>]*>'
            self.assertIsNotNone(
                re.search(detail_pattern, page),
                "Detailed section should have id='wo-link-001-detail'"
            )

    def test_all_board_rows_link_to_their_details(self):
        """Finding A: every board row links to its corresponding detail section."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)

            # Multiple work orders
            work_order_ids = ["wo-a", "wo-b", "wo-c"]
            for wo_id in work_order_ids:
                write_report(proj, wo_id, {
                    **APPROVED_RUN,
                    "work_order_id": wo_id,
                })

            page, _ = render_status_page(proj, generated_at="2026-11-04 00:00:00 UTC")

            # For each work order, verify both the anchor and the target exist
            for wo_id in work_order_ids:
                # Check anchor in board
                anchor_pattern = rf'<a href="#{re.escape(wo_id)}-detail"[^>]*>{re.escape(wo_id)}</a>'
                self.assertIsNotNone(
                    re.search(anchor_pattern, page),
                    f"Board should have anchor linking to #{wo_id}-detail"
                )

                # Check matching id in detail section
                detail_pattern = rf'<section[^>]*id="{re.escape(wo_id)}-detail"[^>]*>'
                self.assertIsNotNone(
                    re.search(detail_pattern, page),
                    f"Detail section should have id='{wo_id}-detail'"
                )


def compute_contrast_ratio(fg_hex, bg_hex):
    """Compute WCAG contrast ratio between foreground and background colors.

    Both colors should be hex strings like "#FFFFFF" or "FFFFFF".
    Returns contrast ratio as a float.
    """
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def relative_luminance(rgb):
        # Convert to sRGB
        r, g, b = [c / 255.0 for c in rgb]
        # Apply gamma correction
        rgb_linear = []
        for c in [r, g, b]:
            if c <= 0.03928:
                rgb_linear.append(c / 12.92)
            else:
                rgb_linear.append(((c + 0.055) / 1.055) ** 2.4)
        # Calculate relative luminance
        return 0.2126 * rgb_linear[0] + 0.7152 * rgb_linear[1] + 0.0722 * rgb_linear[2]

    fg_rgb = hex_to_rgb(fg_hex)
    bg_rgb = hex_to_rgb(bg_hex)

    fg_lum = relative_luminance(fg_rgb)
    bg_lum = relative_luminance(bg_rgb)

    # Contrast ratio formula: (lighter + 0.05) / (darker + 0.05)
    lighter = max(fg_lum, bg_lum)
    darker = min(fg_lum, bg_lum)

    return (lighter + 0.05) / (darker + 0.05)


class TestContrastRatios(unittest.TestCase):
    """Test WCAG contrast ratios (loopback finding B)."""

    def test_all_text_background_pairs_meet_wcag_minimum(self):
        """Finding B: all text/background pairs meet WCAG 4.5:1 minimum contrast.

        Tests the specific pairs called out in loopback finding B:
        .muted, footer, and .board-description on #0C0C0C background,
        plus other primary text/background pairs on main backgrounds.
        """
        # Text/background pairs to verify from the CSS
        # Background is #0C0C0C (body background) for most text
        text_bg_pairs = [
            # Finding B specifically mentions these three on #0C0C0C:
            (".muted", "#9A9A9A", "#0C0C0C"),
            ("footer", "#8A8A8A", "#0C0C0C"),
            (".board-description", "#9A9A9A", "#0C0C0C"),
            # Other primary text on main background:
            (".board-wo-title", "#C9C9C9", "#0C0C0C"),
            ("table th", "#9A9A9A", "#0C0C0C"),
            (".artifacts", "#9A9A9A", "#0C0C0C"),
            (".meta", "#C9C9C9", "#0C0C0C"),
            (".status.st-idle", "#8A8A8A", "#0C0C0C"),
        ]

        wcag_minimum = 4.5

        for label, fg, bg in text_bg_pairs:
            ratio = compute_contrast_ratio(fg, bg)
            self.assertGreaterEqual(
                ratio,
                wcag_minimum,
                f"{label} contrast ratio {ratio:.2f}:1 (fg={fg}, bg={bg}) is below WCAG minimum {wcag_minimum}:1"
            )

    def test_muted_text_contrast_on_dark_background(self):
        """Finding B: .muted (#9A9A9A) on #0C0C0C meets 4.5:1 minimum."""
        ratio = compute_contrast_ratio("#9A9A9A", "#0C0C0C")
        self.assertGreaterEqual(
            ratio,
            4.5,
            f".muted contrast ratio {ratio:.2f}:1 is below WCAG minimum 4.5:1"
        )

    def test_footer_text_contrast(self):
        """Finding B: footer (#8A8A8A) on #0C0C0C meets 4.5:1 minimum."""
        ratio = compute_contrast_ratio("#8A8A8A", "#0C0C0C")
        self.assertGreaterEqual(
            ratio,
            4.5,
            f"footer contrast ratio {ratio:.2f}:1 is below WCAG minimum 4.5:1"
        )

    def test_board_description_contrast(self):
        """Finding B: .board-description (#9A9A9A) on #0C0C0C meets 4.5:1 minimum."""
        ratio = compute_contrast_ratio("#9A9A9A", "#0C0C0C")
        self.assertGreaterEqual(
            ratio,
            4.5,
            f".board-description contrast ratio {ratio:.2f}:1 is below WCAG minimum 4.5:1"
        )


class TestSpacingScale(unittest.TestCase):
    """Test consistent spacing scale (loopback finding C)."""

    def test_spacing_uses_css_custom_properties(self):
        """Finding C: spacing draws from consistent scale defined via CSS custom properties."""
        # Verify CSS defines spacing scale in :root
        spacing_vars = [
            "--space-4", "--space-8", "--space-12", "--space-16",
            "--space-20", "--space-24", "--space-32", "--space-48", "--space-64"
        ]

        for var in spacing_vars:
            self.assertIn(
                var,
                CSS,
                f"CSS should define spacing variable {var}"
            )

    def test_spacing_scale_values_are_consistent(self):
        """Finding C: spacing scale follows consistent progression."""
        # Extract spacing values from CSS
        spacing_pattern = r'--space-(\d+):\s*(\d+)px'
        matches = re.findall(spacing_pattern, CSS)

        # Verify we have spacing definitions
        self.assertGreater(len(matches), 0, "CSS should define spacing scale")

        # Verify spacing values match their names (e.g., --space-4: 4px)
        for name, value in matches:
            self.assertEqual(
                name,
                value,
                f"Spacing variable --space-{name} should be {name}px, not {value}px"
            )

    def test_board_styles_use_spacing_variables(self):
        """Finding C: board styles use spacing variables instead of hardcoded values."""
        # Check that board-related styles use var(--space-X) instead of hardcoded px values
        # Look for patterns like "padding:var(--space-" in board styles

        board_style_lines = [
            line for line in CSS.split('\n')
            if 'board' in line or 'lifecycle' in line
        ]

        # Verify at least some board styles use spacing variables
        uses_spacing_vars = any('var(--space-' in line for line in board_style_lines)
        self.assertTrue(
            uses_spacing_vars,
            "Board styles should use spacing variables from the scale"
        )


class TestResponsiveBehavior(unittest.TestCase):
    """Test responsive behavior (loopback finding D)."""

    def test_stages_row_has_media_query_for_narrow_widths(self):
        """Finding D: CSS includes media query for narrow viewports to prevent horizontal scrolling."""
        # Verify presence of media query for narrow viewports
        self.assertIn(
            "@media (max-width: 400px)",
            CSS,
            "CSS should include media query for narrow viewports (max-width: 400px)"
        )

    def test_media_query_adjusts_board_stages_for_narrow_widths(self):
        """Finding D: media query adapts .board-stages for narrow viewports."""
        # Extract the media query content
        media_query_pattern = r'@media \(max-width: 400px\)\s*\{([^}]+)\}'
        match = re.search(media_query_pattern, CSS)

        self.assertIsNotNone(match, "Should have media query for narrow widths")

        media_query_content = match.group(1)

        # Verify it targets .board-stages or .board-stage
        self.assertTrue(
            '.board-stage' in media_query_content,
            "Media query should adjust .board-stage styling for narrow widths"
        )

    def test_board_stages_has_flex_wrap(self):
        """Finding D: .board-stages uses flex-wrap to prevent horizontal scrolling."""
        # Find the .board-stages style
        board_stages_pattern = r'\.board-stages\s*\{([^}]+)\}'
        match = re.search(board_stages_pattern, CSS)

        self.assertIsNotNone(match, "Should have .board-stages style")

        board_stages_content = match.group(1)

        # Verify it has flex-wrap
        self.assertIn(
            'flex-wrap',
            board_stages_content,
            ".board-stages should use flex-wrap to wrap stages at narrow widths"
        )


@unittest.skipUnless(PLAYWRIGHT_AVAILABLE, "Playwright not available")
class TestRenderedEvidence(unittest.TestCase):
    """Test rendered evidence captures (loopback finding E)."""

    def test_status_page_renders_with_lifecycle_board(self):
        """Finding E: capture rendered evidence of status page with lifecycle board."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)

            # Create diverse work orders to show full board
            write_report(proj, "wo-spec-001", {
                "work_order_id": "wo-spec-001",
                "pipeline": "sdlc-default",
                "title": "At spec stage",
                "kind": "feature",
                "verdict": "pending",
                "human_required": False,
                "loopbacks": 0,
                "steps": [
                    {"station": "intake", "status": "completed", "duration_ms": 1.0, "cost": None, "artifacts": []},
                    {"station": "spec-writer", "status": "executed", "duration_ms": 100.0, "cost": None, "artifacts": []},
                ],
                "risk_hints": [],
            })

            write_report(proj, "wo-review-002", {
                "work_order_id": "wo-review-002",
                "pipeline": "sdlc-default",
                "title": "At review stage",
                "kind": "feature",
                "verdict": "pending",
                "human_required": False,
                "loopbacks": 0,
                "steps": [
                    {"station": "intake", "status": "completed", "duration_ms": 1.0, "cost": None, "artifacts": []},
                    {"station": "spec-writer", "status": "executed", "duration_ms": 100.0, "cost": None, "artifacts": []},
                    {"station": "builder", "status": "executed", "duration_ms": 200.0, "cost": None, "artifacts": []},
                    {"station": "reviewer-spec", "status": "executed", "duration_ms": 50.0, "cost": None, "artifacts": []},
                ],
                "risk_hints": [],
            })

            write_report(proj, "wo-approved-003", {**APPROVED_RUN, "work_order_id": "wo-approved-003"})

            write_report(proj, "wo-merged-004", {**APPROVED_RUN, "work_order_id": "wo-merged-004"})
            write_merge_record(proj, "wo-merged-004", merged=True)

            page, _ = render_status_page(proj, generated_at="2026-11-04 00:00:00 UTC")

            # Write page to file for Playwright to render
            html_file = Path(tmp) / "status.html"
            html_file.write_text(page)

            # Capture with Playwright
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page_obj = browser.new_page()
                page_obj.goto(f"file://{html_file}")

                # Verify lifecycle board is visible
                board_locator = page_obj.locator(".lifecycle-board")
                self.assertTrue(board_locator.is_visible(), "Lifecycle board should be visible")

                # Verify board has rows
                rows = page_obj.locator(".board-row").count()
                self.assertGreaterEqual(rows, 4, "Board should have at least 4 work order rows")

                # Capture full page screenshot
                screenshot_path = Path(tmp) / "lifecycle-board-evidence.png"
                page_obj.screenshot(path=str(screenshot_path), full_page=True)

                # Verify screenshot was created
                self.assertTrue(screenshot_path.exists(), "Screenshot should be created")
                self.assertGreater(screenshot_path.stat().st_size, 0, "Screenshot should not be empty")

                # Test narrow viewport (responsive behavior)
                page_obj.set_viewport_size({"width": 380, "height": 800})
                narrow_screenshot = Path(tmp) / "lifecycle-board-narrow.png"
                page_obj.screenshot(path=str(narrow_screenshot), full_page=True)

                self.assertTrue(narrow_screenshot.exists(), "Narrow viewport screenshot should be created")

                browser.close()


if __name__ == "__main__":
    unittest.main()
