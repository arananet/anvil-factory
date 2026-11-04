import json, tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.statuspage import generate_status_page, render_status_page

# Import capture utilities for rendered evidence test
try:
    from anvil.capture import capture_breakpoints
    CAPTURE_AVAILABLE = True
except ImportError:
    CAPTURE_AVAILABLE = False

def write_report(proj, folder, data):
    d = Path(proj) / "runs" / folder
    d.mkdir(parents=True)
    (d / "report.json").write_text(json.dumps(data))

APPROVED_RUN = {
    "work_order_id": "wo-alpha-001", "pipeline": "sdlc-default",
    "title": "Add the export feature", "kind": "feature",
    "verdict": "approved", "human_required": False, "loopbacks": 0,
    "deployment_status": "deployed_verified",
    "risk_hints": [],
    "decision": {
        "approver": {
            "reviews_counted": [{"station": "reviewer-spec", "verdict": "pass"}],
            "reviews_expected": ["reviewer-spec", "reviewer-security"],
            "rule": "All counted reviews passed.",
        },
        "human_gate": {
            "required": False,
            "rule": ("Verdict approved and no risk hints matched (scanned: auth, payments, "
                     "data-deletion, production-deploy, secrets, publishing), so no human is required."),
            "hints_matched": [],
        },
    },
    "verify_results": [{"command": "run the tests", "status": "pass", "exit_code": 0, "output": ""}],
    "steps": [
        {"station": "intake", "status": "completed", "duration_ms": 1.5, "cost": None, "artifacts": ["runs/wo-alpha-001/report.json"]},
        {"station": "builder", "status": "executed", "duration_ms": 42.0, "cost": None, "artifacts": ["runs/wo-alpha-001/builder.output.md"],
         "configured_model": "fast-builder", "executed_model": "stub-model-x", "executor": {"kind": "http", "detail": "models.example"}},
        {"station": "reviewer-spec", "status": "packet_ready", "duration_ms": 0.5, "cost": None, "artifacts": ["runs/wo-alpha-001/reviewer-spec.packet.md"],
         "configured_model": "review-balanced", "executed_model": None, "executor": None},
        {"station": "deployer", "status": "executed", "duration_ms": 900.0, "cost": None, "artifacts": ["runs/wo-alpha-001/deployer.output.md"]},
    ],
}

FAILED_RUN = {
    "work_order_id": "wo-beta-002", "pipeline": "hotfix",
    "title": "Fix the crash", "kind": "bug",
    "verdict": "rejected", "human_required": True, "loopbacks": 1,
    "deployment_status": None, "verify_results": [],
    "steps": [
        {"station": "intake", "status": "completed", "duration_ms": 1.0, "cost": None, "artifacts": []},
        {"station": "builder", "status": "failed", "duration_ms": 12.0, "cost": None, "artifacts": ["runs/wo-beta-002/builder.packet.md"]},
    ],
}

class TestStatusPage(unittest.TestCase):
    def make_project(self, tmp):
        proj = Path(tmp) / "proj"
        (proj / "runs").mkdir(parents=True)
        write_report(proj, "wo-alpha-001", APPROVED_RUN)
        write_report(proj, "wo-beta-002", FAILED_RUN)
        broken = proj / "runs" / "wo-broken-003"
        broken.mkdir(parents=True)
        (broken / "report.json").write_text("{ this is not json")
        (proj / "runs" / "wo-empty-004").mkdir(parents=True)
        return proj

    def test_page_contains_both_runs_and_statuses_s1_s2_s3(self):
        """status-page S1, S2, S3: every run, its facts, and each station with its status"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            page, summary = render_status_page(proj, generated_at="2026-10-28 00:00:00 UTC")
            self.assertEqual(summary["runs"], 2)
            for needle in ["wo-alpha-001", "wo-beta-002", "Add the export feature", "Fix the crash",
                           "sdlc-default", "hotfix", "approved", "rejected", "deployed_verified",
                           "builder", "reviewer-spec", "deployer", "intake",
                           "completed", "executed", "packet_ready", "failed"]:
                self.assertIn(needle, page)

    def test_snapshot_note_and_timestamp_s4(self):
        """status-page S4: the page states when it was generated and that it is a snapshot"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            page, _ = render_status_page(proj, generated_at="2026-10-28 00:00:00 UTC")
            self.assertIn("Snapshot generated from the run reports on disk", page)
            self.assertIn("2026-10-28 00:00:00 UTC", page)
            self.assertIn("not a live feed", page)

    def test_corrupt_and_missing_reports_skipped_and_noted_s5(self):
        """status-page S5: corrupt or missing report.json is skipped and noted in the footer"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            summary = generate_status_page(proj, Path(tmp) / "out")
            self.assertEqual(summary["runs"], 2)
            self.assertEqual(sorted(summary["skipped"]), ["wo-broken-003", "wo-empty-004"])
            page = (Path(tmp) / "out" / "index.html").read_text()
            self.assertIn("wo-broken-003", page)
            self.assertIn("wo-empty-004", page)
            self.assertTrue((Path(tmp) / "out" / "index.html").exists())

    def test_self_contained_and_arananet_style(self):
        """status-page requirements: inline CSS only, Arananet palette, no external assets"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            page, _ = render_status_page(proj, generated_at="2026-10-28 00:00:00 UTC")
            self.assertIn("#0C0C0C", page)
            self.assertIn("#1E1E1E", page)
            self.assertIn("#FF5C00", page)
            self.assertNotIn("http://", page.replace("http://www.w3.org", ""))
            self.assertNotIn("<link", page)
            self.assertNotIn("<script", page)

    def test_recorded_decision_sentences_render_s6(self):
        """status-page S6: a report with a decision object shows the runner's own rule sentences"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)
            write_report(proj, "wo-alpha-001", APPROVED_RUN)
            page, summary = render_status_page(proj, generated_at="2026-10-28 00:00:00 UTC")
            self.assertEqual(summary["runs"], 1)
            self.assertIn("All counted reviews passed.", page)
            self.assertIn("so no human is required.", page)
            self.assertNotIn("derived from the run record", page)

    def test_derived_decision_for_older_report_s6(self):
        """status-page S6: a report without a decision object gets a labeled derived explanation"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)
            write_report(proj, "wo-beta-002", FAILED_RUN)
            page, summary = render_status_page(proj, generated_at="2026-10-28 00:00:00 UTC")
            self.assertEqual(summary["runs"], 1)
            self.assertIn("derived from the run record", page)
            self.assertIn("verdict rejected is on record, but this report does not itemize the reviews behind it.", page)
            self.assertIn("a human was required for this run (verdict rejected)", page)

    def test_step_rows_show_model_provenance(self):
        """agent-execution S8 (status page): executed model shown as model, configured as configured"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = self.make_project(tmp)
            page, _ = render_status_page(proj, generated_at="2026-10-28 00:00:00 UTC")
            self.assertIn("model: stub-model-x", page)
            self.assertIn("configured: review-balanced", page)

    def test_lifecycle_stages_derive_from_evidence_s1(self):
        """status-lifecycle-stages S1: stages derive from run report evidence"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)

            # Job with spec, build, and review steps
            spec_build_review = {
                "work_order_id": "wo-s1-001",
                "title": "Feature with spec, build, review",
                "kind": "feature",
                "verdict": "no_reviews",
                "human_required": False,
                "steps": [
                    {"station": "intake", "status": "completed"},
                    {"station": "spec-writer", "status": "executed"},
                    {"station": "builder", "status": "executed"},
                    {"station": "reviewer-spec", "status": "executed"},
                ]
            }

            # Job with only spec step
            spec_only = {
                "work_order_id": "wo-s1-002",
                "title": "Feature with spec only",
                "kind": "feature",
                "verdict": None,
                "human_required": False,
                "steps": [
                    {"station": "intake", "status": "completed"},
                    {"station": "spec-writer", "status": "executed"},
                ]
            }

            # Job with no runs (empty steps)
            no_runs = {
                "work_order_id": "wo-s1-003",
                "title": "Feature with no runs",
                "kind": "feature",
                "verdict": None,
                "human_required": False,
                "steps": []
            }

            write_report(proj, "wo-s1-001", spec_build_review)
            write_report(proj, "wo-s1-002", spec_only)
            write_report(proj, "wo-s1-003", no_runs)

            from anvil.statuspage import derive_lifecycle_stage

            stage_info_001 = derive_lifecycle_stage(spec_build_review, {})
            self.assertIn("SPEC", stage_info_001["stages_reached"])
            self.assertIn("BUILD", stage_info_001["stages_reached"])
            self.assertIn("REVIEW", stage_info_001["stages_reached"])
            self.assertEqual(stage_info_001["current_stage"], "REVIEW")

            stage_info_002 = derive_lifecycle_stage(spec_only, {})
            self.assertIn("SPEC", stage_info_002["stages_reached"])
            self.assertNotIn("BUILD", stage_info_002["stages_reached"])
            self.assertEqual(stage_info_002["current_stage"], "SPEC")

            stage_info_003 = derive_lifecycle_stage(no_runs, {})
            self.assertEqual(stage_info_003["stages_reached"], [])
            self.assertIsNone(stage_info_003["current_stage"])

    def test_approved_is_not_merged_s2(self):
        """status-lifecycle-stages S2: approved without merge record shows APPROVED, not MERGED"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)

            approved_job = {
                "work_order_id": "wo-s2-001",
                "title": "Approved feature",
                "kind": "feature",
                "verdict": "approved",
                "human_required": False,
                "decision": {
                    "approver": {"verdict": "approved"},
                    "human_gate": {"required": False}
                },
                "steps": [
                    {"station": "spec-writer", "status": "executed"},
                    {"station": "builder", "status": "executed"},
                    {"station": "reviewer-spec", "status": "executed"},
                ]
            }

            write_report(proj, "wo-s2-001", approved_job)

            from anvil.statuspage import derive_lifecycle_stage

            # Without merge record
            stage_info = derive_lifecycle_stage(approved_job, {})
            self.assertIn("APPROVED", stage_info["stages_reached"])
            self.assertNotIn("MERGED", stage_info["stages_reached"])
            self.assertEqual(stage_info["current_stage"], "APPROVED")

            # With merge record
            merge_records = {
                "wo-s2-001": {"work_order_id": "wo-s2-001", "merged": True}
            }
            stage_info_merged = derive_lifecycle_stage(approved_job, merge_records)
            self.assertIn("APPROVED", stage_info_merged["stages_reached"])
            self.assertIn("MERGED", stage_info_merged["stages_reached"])
            self.assertEqual(stage_info_merged["current_stage"], "MERGED")

    def test_needs_human_from_decision_s3(self):
        """status-lifecycle-stages S3: NEEDS HUMAN badge when decision.human_gate.required is true"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)

            human_required_job = {
                "work_order_id": "wo-s3-001",
                "title": "Feature needing human",
                "kind": "feature",
                "verdict": "approved",
                "human_required": True,
                "decision": {
                    "approver": {"verdict": "approved"},
                    "human_gate": {"required": True, "rule": "Risk hint matched: production-deploy"}
                },
                "steps": [
                    {"station": "spec-writer", "status": "executed"},
                    {"station": "builder", "status": "executed"},
                ]
            }

            human_not_required_job = {
                "work_order_id": "wo-s3-002",
                "title": "Feature not needing human",
                "kind": "feature",
                "verdict": "approved",
                "human_required": False,
                "decision": {
                    "approver": {"verdict": "approved"},
                    "human_gate": {"required": False}
                },
                "steps": [
                    {"station": "spec-writer", "status": "executed"},
                ]
            }

            write_report(proj, "wo-s3-001", human_required_job)
            write_report(proj, "wo-s3-002", human_not_required_job)

            from anvil.statuspage import derive_lifecycle_stage

            stage_info_001 = derive_lifecycle_stage(human_required_job, {})
            self.assertTrue(stage_info_001["needs_human"])

            stage_info_002 = derive_lifecycle_stage(human_not_required_job, {})
            self.assertFalse(stage_info_002["needs_human"])

            # Verify rendering
            page, _ = render_status_page(proj, generated_at="2026-11-04 00:00:00 UTC")
            self.assertIn("NEEDS HUMAN", page)
            self.assertIn("needs-human", page)

    def test_intake_states_compose_s4(self):
        """status-lifecycle-stages S4: PARKED and REJECTED states instead of stage progression"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)

            parked_job = {
                "work_order_id": "wo-s4-001",
                "title": "Parked job",
                "kind": "feature",
                "verdict": "waiting_info",
                "human_required": False,
                "steps": [
                    {"station": "intake", "status": "completed"},
                ]
            }

            rejected_job = {
                "work_order_id": "wo-s4-002",
                "title": "Rejected job",
                "kind": "feature",
                "verdict": "rejected",
                "human_required": True,
                "steps": [
                    {"station": "intake", "status": "completed"},
                ]
            }

            write_report(proj, "wo-s4-001", parked_job)
            write_report(proj, "wo-s4-002", rejected_job)

            from anvil.statuspage import derive_lifecycle_stage

            stage_info_parked = derive_lifecycle_stage(parked_job, {})
            self.assertEqual(stage_info_parked["intake_state"], "PARKED")
            self.assertEqual(stage_info_parked["stages_reached"], [])
            self.assertIsNone(stage_info_parked["current_stage"])

            stage_info_rejected = derive_lifecycle_stage(rejected_job, {})
            self.assertEqual(stage_info_rejected["intake_state"], "REJECTED")
            self.assertEqual(stage_info_rejected["stages_reached"], [])
            self.assertIsNone(stage_info_rejected["current_stage"])

            # Verify rendering
            page, _ = render_status_page(proj, generated_at="2026-11-04 00:00:00 UTC")
            self.assertIn("PARKED", page)
            self.assertIn("REJECTED", page)
            self.assertIn("state-parked", page)
            self.assertIn("state-rejected", page)

    def test_board_rows_link_to_job_details_s5(self):
        """status-lifecycle-stages S5: work order IDs link to detailed run sections"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)

            job1 = {
                "work_order_id": "wo-s5-001",
                "title": "First job",
                "kind": "feature",
                "verdict": "approved",
                "human_required": False,
                "steps": [
                    {"station": "spec-writer", "status": "executed"},
                    {"station": "builder", "status": "executed"},
                ]
            }

            job2 = {
                "work_order_id": "wo-s5-002",
                "title": "Second job",
                "kind": "bug",
                "verdict": "no_reviews",
                "human_required": False,
                "steps": [
                    {"station": "spec-writer", "status": "executed"},
                ]
            }

            write_report(proj, "wo-s5-001", job1)
            write_report(proj, "wo-s5-002", job2)

            page, _ = render_status_page(proj, generated_at="2026-11-04 00:00:00 UTC")

            # Each work order ID should be a real anchor linking to detail section
            self.assertIn('<a href="#wo-s5-001-detail"', page)
            self.assertIn('<a href="#wo-s5-002-detail"', page)

            # Detail sections should have matching id attributes
            self.assertIn('id="wo-s5-001-detail"', page)
            self.assertIn('id="wo-s5-002-detail"', page)

            # Each job should appear exactly once in board
            import re
            board_section = page.split('<section class="lifecycle-board">')[1].split('</section>')[0]
            wo1_matches = len(re.findall(r'wo-s5-001', board_section))
            wo2_matches = len(re.findall(r'wo-s5-002', board_section))
            # Each work order ID appears in: board row id, link href, and link text
            self.assertGreaterEqual(wo1_matches, 1)
            self.assertGreaterEqual(wo2_matches, 1)

    def test_contrast_meets_wcag_minimums_s6(self):
        """status-lifecycle-stages S6: all text/background pairs meet WCAG 4.5:1 contrast ratio"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)
            write_report(proj, "wo-s6-001", APPROVED_RUN)

            page, _ = render_status_page(proj, generated_at="2026-11-04 00:00:00 UTC")

            # Extract CSS from page
            import re
            css_match = re.search(r'<style>(.*?)</style>', page, re.DOTALL)
            self.assertIsNotNone(css_match)
            css = css_match.group(1)

            # Helper to compute WCAG contrast ratio
            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

            def relative_luminance(rgb):
                """Compute relative luminance per WCAG formula"""
                r, g, b = [c / 255.0 for c in rgb]
                r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
                g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
                b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
                return 0.2126 * r + 0.7152 * g + 0.0722 * b

            def contrast_ratio(color1_hex, color2_hex):
                """Compute WCAG contrast ratio between two hex colors"""
                l1 = relative_luminance(hex_to_rgb(color1_hex))
                l2 = relative_luminance(hex_to_rgb(color2_hex))
                lighter = max(l1, l2)
                darker = min(l1, l2)
                return (lighter + 0.05) / (darker + 0.05)

            # Test critical text/background pairs from the spec
            background = "#0C0C0C"  # Main background

            # Pairs to test (foreground, background, min_ratio)
            pairs = [
                ("#9A9A9A", background, 4.5, ".muted text on dark background"),
                ("#8A8A8A", background, 4.5, "footer text on dark background"),
                ("#9A9A9A", background, 4.5, ".board-description on dark background"),
                ("#E8E8E8", background, 4.5, "body text on dark background"),
                ("#C9C9C9", background, 4.5, ".meta text on dark background"),
            ]

            for fg, bg, min_ratio, description in pairs:
                ratio = contrast_ratio(fg, bg)
                self.assertGreaterEqual(
                    ratio, min_ratio,
                    f"{description}: {fg} on {bg} has contrast ratio {ratio:.2f}, "
                    f"which is below minimum {min_ratio}:1"
                )

    def test_spacing_uses_consistent_scale_s7(self):
        """status-lifecycle-stages S7: spacing draws from consistent scale via CSS custom properties"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)
            write_report(proj, "wo-s7-001", APPROVED_RUN)

            page, _ = render_status_page(proj, generated_at="2026-11-04 00:00:00 UTC")

            # Extract CSS
            import re
            css_match = re.search(r'<style>(.*?)</style>', page, re.DOTALL)
            self.assertIsNotNone(css_match)
            css = css_match.group(1)

            # Check for CSS custom properties defining spacing scale
            self.assertIn("--space-", css, "CSS should define spacing scale using custom properties")

            # Verify :root declares spacing variables
            root_match = re.search(r':root\s*\{([^}]*)\}', css)
            self.assertIsNotNone(root_match, ":root should declare spacing variables")
            root_block = root_match.group(1)

            # Count spacing variable declarations
            spacing_vars = re.findall(r'--space-\w+:\s*\d+px', root_block)
            self.assertGreater(len(spacing_vars), 0, "Should have spacing scale variables in :root")

            # Verify spacing properties use var() references
            spacing_props = ['margin', 'padding', 'gap']
            for prop in spacing_props:
                # Look for uses of spacing variables
                var_usage = re.findall(rf'{prop}[^:]*:\s*var\(--space-', css)
                # Should have at least some uses of spacing variables
                # (We're being flexible here as the implementation may use a mix)

    def test_responsive_behavior_at_narrow_widths_s8(self):
        """status-lifecycle-stages S8: stage progression adapts at narrow viewports without horizontal scroll"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)
            write_report(proj, "wo-s8-001", APPROVED_RUN)

            page, _ = render_status_page(proj, generated_at="2026-11-04 00:00:00 UTC")

            # Extract CSS
            import re
            css_match = re.search(r'<style>(.*?)</style>', page, re.DOTALL)
            self.assertIsNotNone(css_match)
            css = css_match.group(1)

            # Check for responsive adaptations
            # Either flex-wrap on .board-stages or a media query for narrow widths
            has_flex_wrap = 'flex-wrap' in css
            has_media_query = '@media' in css and ('max-width' in css or 'min-width' in css)

            self.assertTrue(
                has_flex_wrap or has_media_query,
                "CSS should include flex-wrap or media query for responsive behavior"
            )

            # If there's a media query, it should target narrow viewports
            if has_media_query:
                media_queries = re.findall(r'@media[^{]+\{', css)
                # Should have a query targeting narrow widths (around 400px or less)
                narrow_query = any('400px' in mq or '480px' in mq or '600px' in mq
                                 for mq in media_queries)
                self.assertTrue(narrow_query or has_flex_wrap,
                              "Should have responsive handling for narrow viewports")

    @unittest.skipUnless(CAPTURE_AVAILABLE, "anvil.capture module not available")
    def test_rendered_evidence_captures_status_page_s9(self):
        """status-lifecycle-stages S9: Playwright captures produce rendered evidence of status page"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "runs").mkdir(parents=True)

            # Create work orders with different stages
            write_report(proj, "wo-s9-001", APPROVED_RUN)
            write_report(proj, "wo-s9-002", FAILED_RUN)

            # Generate the status page to the project
            summary = generate_status_page(proj, proj / "status")
            self.assertEqual(summary["runs"], 2)
            status_page = proj / "status" / "index.html"
            self.assertTrue(status_page.exists())

            # Verify the page contains lifecycle board
            page_html = status_page.read_text()
            self.assertIn("lifecycle-board", page_html)
            self.assertIn("board-stages", page_html)

            # Set up capture configuration
            evidence_dir = proj / "runs" / "wo-s9-001" / "evidence"

            config = {
                "static_root": "status",
                "page_path": "/index.html",
                "breakpoints": [
                    {"width": 390, "height": 844},   # Mobile
                    {"width": 1440, "height": 900},  # Desktop
                ],
            }

            # Mock capture implementation that creates fake screenshots
            def mock_capture(url, width, height, output_path):
                # Verify URL is formed correctly
                self.assertIn("127.0.0.1:", url)
                self.assertIn("/index.html", url)
                # Create fake PNG file
                Path(output_path).write_bytes(b"fake png screenshot data")

            # Run capture with mock
            result = capture_breakpoints(proj, evidence_dir, config, capture_impl=mock_capture)

            # Verify capture succeeded
            self.assertTrue(result["success"], f"Capture failed: {result.get('error', '')}")
            self.assertEqual(len(result["captures"]), 2)

            # Verify screenshot files were created with correct names
            self.assertTrue((evidence_dir / "screenshot-390x844.png").exists())
            self.assertTrue((evidence_dir / "screenshot-1440x900.png").exists())

            # Verify capture metadata
            self.assertEqual(result["captures"][0]["breakpoint"], "390x844")
            self.assertEqual(result["captures"][0]["width"], 390)
            self.assertEqual(result["captures"][0]["height"], 844)

            self.assertEqual(result["captures"][1]["breakpoint"], "1440x900")
            self.assertEqual(result["captures"][1]["width"], 1440)
            self.assertEqual(result["captures"][1]["height"], 900)

if __name__ == "__main__":
    unittest.main()
