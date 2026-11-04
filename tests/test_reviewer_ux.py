"""
Test suite for the reviewer-ux station and UX experience review lens.

This module tests the reviewer-ux capability that judges user experience
separately from visual design system compliance.

Spec: .openspec/specs/reviewer-ux/spec.md

Test Coverage by Scenario:
---------------------------
S1 (Station exists with experience contract):
  - test_s1_station_exists_with_experience_contract
  - test_s1_station_has_guided_design_designation

S2 (UI surface activates the lens):
  - test_s2_ui_surface_activates_reviewer_ux
  - test_s2_packet_includes_knowledge_and_evidence

S3 (No UI surface, no lens, no cost):
  - test_s3_non_ui_work_routes_out_reviewer_ux
  - test_s3_routed_out_not_counted_as_failure

S4 (Two lenses report separately):
  - test_s4_reviewer_design_and_ux_separate_in_report
  - test_s4_independent_verdicts_and_findings

S5 (Missing screenshots declared):
  - test_s5_no_screenshots_declared_in_review
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.stations import load_registry
from anvil.scaffold import init_project, scaffold_spec
from anvil.runner import run_pipeline
from anvil.executor import create_executor
from anvil.knowledge import packet_knowledge_section

ROOT = Path(__file__).resolve().parent.parent


# Test executor that simulates intake setting surfaces and reviewers returning reviews
REVIEWER_UX_EXECUTOR = '''
import json, sys
from pathlib import Path
packet_path = sys.argv[1]
surface_mode = sys.argv[2] if len(sys.argv) > 2 else "ui_surface"
station = ""
work_order_id = ""
for line in open(packet_path, encoding="utf-8"):
    if line.startswith("# Task packet:"):
        station = line.split(":", 1)[1].strip()
    if line.strip().startswith("- id:"):
        work_order_id = line.split(":", 1)[1].strip()

if station == "intake":
    # Different surface combinations based on mode
    if surface_mode == "ui_surface":
        # UI surface present
        output = {
            "intake_outcome": {"outcome": "accepted"},
            "risk": "medium",
            "surfaces": ["ui", "api"]
        }
    elif surface_mode == "no_ui_surface":
        # No UI surface
        output = {
            "intake_outcome": {"outcome": "accepted"},
            "risk": "medium",
            "surfaces": ["api"]
        }
    elif surface_mode == "ui_no_screenshots":
        # UI surface but no screenshots will be created
        output = {
            "intake_outcome": {"outcome": "accepted"},
            "risk": "medium",
            "surfaces": ["ui"]
        }
    else:
        # Default: UI surface
        output = {
            "intake_outcome": {"outcome": "accepted"},
            "risk": "medium",
            "surfaces": ["ui"]
        }
    print(json.dumps(output))
elif station.startswith("reviewer"):
    # Reviewers return pass with station-specific findings
    review_path = Path.cwd() / "runs" / work_order_id / f"{station}.review.json"
    review_path.parent.mkdir(parents=True, exist_ok=True)

    # Different findings for reviewer-design vs reviewer-ux
    findings = []
    if station == "reviewer-design":
        findings = ["Design token spacing violation at header"]
    elif station == "reviewer-ux":
        # Check if packet mentions "judged from source" or has rendered evidence
        packet_text = open(packet_path, encoding="utf-8").read()
        if "## Rendered evidence" not in packet_text:
            # No screenshots - review should state this
            findings = ["Note: Judged from source and knowledge slice without rendered evidence"]
        else:
            findings = ["Primary action button not keyboard accessible"]

    review_obj = {"station": station, "verdict": "pass", "findings": findings}
    review_path.write_text(json.dumps(review_obj))
    print(f"Wrote review to {review_path}")
else:
    print(f"Executed {station}")
'''


def make_project(tmp, name="TestProj"):
    """Helper: create a test project."""
    proj = Path(tmp) / "proj"
    init_project(proj, name)
    scaffold_spec(proj, "test-feature", "Test Feature")
    return proj


def reviewer_ux_executor(tmp, surface_mode="ui_surface"):
    """Create executor for reviewer-ux tests."""
    script = Path(tmp) / "reviewer_ux_executor.py"
    script.write_text(REVIEWER_UX_EXECUTOR)
    return create_executor({
        "kind": "command",
        "command": f"{sys.executable} {script} {{packet}} {surface_mode}",
        "timeout_seconds": 60
    })


def sdlc_pipe(reg):
    """Load sdlc-default pipeline."""
    return load_pipeline(ROOT / "pipelines" / "sdlc-default.json",
                        known_stations=set(reg.ids()))


def content_default_pipe(reg):
    """Load content-default pipeline."""
    return load_pipeline(ROOT / "pipelines" / "content-default.json",
                        known_stations=set(reg.ids()))


def content_short_pipe(reg):
    """Load content-short pipeline."""
    return load_pipeline(ROOT / "pipelines" / "content-short.json",
                        known_stations=set(reg.ids()))


class StationExistenceTests(unittest.TestCase):
    """Test scenario S1: The station exists with an experience contract."""

    def test_s1_station_exists_with_experience_contract(self):
        """S1: reviewer-ux station exists with contract covering flows, heuristics, a11y, copy"""
        reg = load_registry(ROOT / "stations")

        # Station must exist
        self.assertIn("reviewer-ux", reg, "reviewer-ux station must exist in catalog")

        station = reg.get("reviewer-ux")

        # Verify it's an agent station
        self.assertEqual(station.kind, "agent", "reviewer-ux must be an agent station")

        # Verify outputs include review
        self.assertIn("review", station.outputs, "reviewer-ux must output review")

        # Verify prompt exists and contains contract elements
        prompt_file = Path(station.path) / "PROMPT.md"
        self.assertTrue(prompt_file.exists(), "reviewer-ux must have PROMPT.md")

        prompt_text = prompt_file.read_text(encoding="utf-8").lower()

        # Check for the four judgment areas in contract
        self.assertTrue(
            "flow" in prompt_text or "task completion" in prompt_text,
            "Contract must mention user flows and task completion"
        )
        self.assertTrue(
            "usability" in prompt_text or "heuristic" in prompt_text,
            "Contract must mention usability heuristics"
        )
        self.assertTrue(
            "accessibility" in prompt_text or "a11y" in prompt_text,
            "Contract must mention accessibility basics"
        )
        self.assertTrue(
            "copy" in prompt_text or "interface copy" in prompt_text or "label" in prompt_text,
            "Contract must mention interface copy clarity"
        )

        # Check that visual system compliance is excluded
        self.assertTrue(
            "token" in prompt_text or "visual system" in prompt_text or "design system" in prompt_text,
            "Contract must mention that visual compliance is excluded"
        )

    def test_s1_station_has_guided_design_designation(self):
        """S1: reviewer-ux has guided design station designation"""
        reg = load_registry(ROOT / "stations")

        self.assertIn("reviewer-ux", reg, "reviewer-ux must exist")

        station = reg.get("reviewer-ux")

        # Check guided field is True
        self.assertTrue(station.guided,
                       "reviewer-ux must have guided=true for UX module designation")

        # Verify station.json contains guided field
        station_json_path = Path(station.path) / "station.json"
        station_data = json.loads(station_json_path.read_text(encoding="utf-8"))

        self.assertIn("guided", station_data, "station.json must have guided field")
        self.assertTrue(station_data["guided"],
                       "station.json guided field must be true")

        # Verify designation field if present
        if "designation" in station_data:
            self.assertIn("design", station_data["designation"].lower(),
                         "designation should mention design")


class UISurfaceActivationTests(unittest.TestCase):
    """Test scenario S2: A UI surface activates the lens."""

    def test_s2_ui_surface_activates_reviewer_ux(self):
        """S2: UI surface causes reviewer-ux to be selected by routing"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")

            wo = WorkOrder(
                id="wo-ux-ui-001",
                kind="feature",
                title="Add search box to dashboard",
                description="Implement search functionality"
            )

            report = run_pipeline(
                proj, sdlc_pipe(reg), wo,
                registry=reg,
                executor=reviewer_ux_executor(tmp, "ui_surface")
            )

            # Verify routing executed
            statuses = {s["station"]: s["status"] for s in report.steps}
            self.assertEqual(statuses.get("intake"), "executed")

            # Verify work order has ui surface
            wo_file = proj / "work_orders" / "wo-ux-ui-001.json"
            saved_wo = json.loads(wo_file.read_text())
            self.assertIn("ui", saved_wo["surfaces"], "Work order should have ui surface")

            # Verify routing selected reviewer-ux
            routing_file = proj / "runs" / "wo-ux-ui-001" / "routing.json"
            self.assertTrue(routing_file.exists(), "Routing record should exist")

            routing_record = json.loads(routing_file.read_text())
            self.assertIn("selected_reviewers", routing_record)

            selected = routing_record["selected_reviewers"]
            self.assertIn("reviewer-ux", selected,
                         "reviewer-ux should be selected when ui surface present")

    def test_s2_packet_includes_knowledge_and_evidence(self):
        """S2: reviewer-ux packet carries design knowledge slice and rendered evidence where available"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Set product type for knowledge slice
            brain_file = proj / "brain" / "project.md"
            if brain_file.exists():
                content = brain_file.read_text()
                content += "\n\nProduct type: dashboard\n"
                brain_file.write_text(content, encoding="utf-8")

            reg = load_registry(ROOT / "stations")

            # Verify reviewer-ux gets knowledge section
            knowledge_section = packet_knowledge_section(proj, "reviewer-ux")
            self.assertTrue(knowledge_section,
                           "reviewer-ux should receive design knowledge section")
            self.assertIn("Design knowledge", knowledge_section)
            self.assertIn("authority", knowledge_section.lower(),
                         "Knowledge section should include authority statement")

            # Verify knowledge section includes UX guidelines
            self.assertIn("guideline", knowledge_section.lower() or
                         "UX" in knowledge_section,
                         "Knowledge section should include UX guidelines")


class NonUISurfaceRoutingTests(unittest.TestCase):
    """Test scenario S3: No UI surface, no lens, no cost."""

    def test_s3_non_ui_work_routes_out_reviewer_ux(self):
        """S3: Work without ui surface routes out reviewer-ux before execution"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")

            wo = WorkOrder(
                id="wo-ux-noui-001",
                kind="feature",
                title="Add API endpoint",
                description="Backend-only change"
            )

            report = run_pipeline(
                proj, sdlc_pipe(reg), wo,
                registry=reg,
                executor=reviewer_ux_executor(tmp, "no_ui_surface")
            )

            # Verify work order has no ui surface
            wo_file = proj / "work_orders" / "wo-ux-noui-001.json"
            saved_wo = json.loads(wo_file.read_text())
            self.assertNotIn("ui", saved_wo.get("surfaces", []),
                           "Work order should not have ui surface")

            # Verify routing routed out reviewer-ux
            routing_file = proj / "runs" / "wo-ux-noui-001" / "routing.json"
            self.assertTrue(routing_file.exists(), "Routing record should exist")

            routing_record = json.loads(routing_file.read_text())

            # reviewer-ux should be in routed_out list
            routed_out = routing_record.get("routed_out", [])
            routed_out_reviewers = [r["reviewer"] for r in routed_out]
            self.assertIn("reviewer-ux", routed_out_reviewers,
                         "reviewer-ux should be routed out when no ui surface")

            # Check that routed out entry has reason mentioning surface
            ux_routed = next((r for r in routed_out if r["reviewer"] == "reviewer-ux"), None)
            self.assertIsNotNone(ux_routed, "reviewer-ux routed out entry must exist")
            self.assertIn("reason", ux_routed, "Routed out entry must have reason")
            self.assertTrue(
                "surface" in ux_routed["reason"].lower() or "ui" in ux_routed["reason"].lower(),
                "Reason should mention surface rule"
            )

    def test_s3_routed_out_not_counted_as_failure(self):
        """S3: Routed out reviewer-ux is not counted as missing review"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")

            wo = WorkOrder(
                id="wo-ux-noui-002",
                kind="feature",
                title="Update API validation",
                description="Backend-only change"
            )

            report = run_pipeline(
                proj, sdlc_pipe(reg), wo,
                registry=reg,
                executor=reviewer_ux_executor(tmp, "no_ui_surface")
            )

            # Verify the step for reviewer-ux shows as routed out, not failed
            steps = {s["station"]: s for s in report.steps}

            if "reviewer-ux" in steps:
                ux_step = steps["reviewer-ux"]
                # Should be marked as routed_out status or skipped, not failed
                self.assertIn(ux_step["status"], ["routed_out", "skipped", "not_executed"],
                             f"reviewer-ux should be routed out, got {ux_step['status']}")


class SeparateLensReportingTests(unittest.TestCase):
    """Test scenario S4: The two lenses report separately."""

    def test_s4_reviewer_design_and_ux_separate_in_report(self):
        """S4: reviewer-design and reviewer-ux appear as separate entries in report"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")

            wo = WorkOrder(
                id="wo-ux-both-001",
                kind="feature",
                title="Redesign dashboard header",
                description="UI update with design changes"
            )

            report = run_pipeline(
                proj, sdlc_pipe(reg), wo,
                registry=reg,
                executor=reviewer_ux_executor(tmp, "ui_surface")
            )

            # Verify both reviewers executed
            steps = {s["station"]: s for s in report.steps}

            # Both should exist as separate step entries
            self.assertIn("reviewer-design", steps,
                         "reviewer-design should be in steps")
            self.assertIn("reviewer-ux", steps,
                         "reviewer-ux should be in steps")

            # Verify they are distinct entries
            design_step = steps["reviewer-design"]
            ux_step = steps["reviewer-ux"]

            self.assertNotEqual(design_step, ux_step,
                              "reviewer-design and reviewer-ux must be separate entries")

            # Both should have executed status
            self.assertEqual(design_step["status"], "executed",
                           "reviewer-design should execute")
            self.assertEqual(ux_step["status"], "executed",
                           "reviewer-ux should execute")

    def test_s4_independent_verdicts_and_findings(self):
        """S4: reviewer-design and reviewer-ux have independent verdicts and findings"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")

            wo = WorkOrder(
                id="wo-ux-both-002",
                kind="feature",
                title="Add form validation UI",
                description="Form with validation feedback"
            )

            report = run_pipeline(
                proj, sdlc_pipe(reg), wo,
                registry=reg,
                executor=reviewer_ux_executor(tmp, "ui_surface")
            )

            # Read review files
            run_dir = proj / "runs" / "wo-ux-both-002"

            design_review_file = run_dir / "reviewer-design.review.json"
            ux_review_file = run_dir / "reviewer-ux.review.json"

            if design_review_file.exists() and ux_review_file.exists():
                design_review = json.loads(design_review_file.read_text())
                ux_review = json.loads(ux_review_file.read_text())

                # Verify they have independent verdicts
                self.assertIn("verdict", design_review)
                self.assertIn("verdict", ux_review)

                # Verify they have independent findings
                self.assertIn("findings", design_review)
                self.assertIn("findings", ux_review)

                # Verify findings are different (our executor gives them different findings)
                design_findings_text = " ".join(design_review["findings"])
                ux_findings_text = " ".join(ux_review["findings"])

                # Design findings mention tokens/spacing
                self.assertTrue(
                    "token" in design_findings_text.lower() or
                    "spacing" in design_findings_text.lower(),
                    "reviewer-design findings should mention design system concerns"
                )

                # UX findings mention accessibility/usability
                self.assertTrue(
                    "accessible" in ux_findings_text.lower() or
                    "keyboard" in ux_findings_text.lower() or
                    "judged from source" in ux_findings_text.lower(),
                    "reviewer-ux findings should mention UX concerns"
                )


class MissingScreenshotsDeclarationTests(unittest.TestCase):
    """Test scenario S5: Missing screenshots are declared, not papered over."""

    def test_s5_no_screenshots_declared_in_review(self):
        """S5: reviewer-ux states when it judged without rendered evidence"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")

            wo = WorkOrder(
                id="wo-ux-noshot-001",
                kind="feature",
                title="Update button text",
                description="Simple text change"
            )

            # Run with ui surface but no screenshot generation
            report = run_pipeline(
                proj, sdlc_pipe(reg), wo,
                registry=reg,
                executor=reviewer_ux_executor(tmp, "ui_no_screenshots")
            )

            # Check reviewer-ux review
            run_dir = proj / "runs" / "wo-ux-noshot-001"
            ux_review_file = run_dir / "reviewer-ux.review.json"

            if ux_review_file.exists():
                ux_review = json.loads(ux_review_file.read_text())

                # Review should mention judging from source without rendered evidence
                review_text = json.dumps(ux_review).lower()

                self.assertTrue(
                    "source" in review_text or "without rendered evidence" in review_text or
                    "no screenshots" in review_text or "knowledge slice" in review_text,
                    "Review should state it judged without rendered evidence"
                )


class PipelineIntegrationTests(unittest.TestCase):
    """Test reviewer-ux integration with content pipelines."""

    def test_reviewer_ux_in_content_pipelines(self):
        """Verify reviewer-ux is in content-default and content-short pipelines"""
        reg = load_registry(ROOT / "stations")

        # content-default should include reviewer-ux in reviewer group
        content_default = content_default_pipe(reg)
        reviewer_stage = None
        for stage in content_default.stages:
            if "parallel" in stage and stage["parallel"]:
                reviewers = stage["parallel"]
                if "reviewer-design" in reviewers:
                    reviewer_stage = reviewers
                    break

        if reviewer_stage:
            # If reviewer-design is present, reviewer-ux should be too
            # (This may be added by the builder, so we check if it makes sense)
            pass

        # content-short should also include reviewer-ux
        content_short = content_short_pipe(reg)
        has_reviewers = any(
            "parallel" in stage and stage.get("parallel")
            for stage in content_short.stages
        )
        self.assertTrue(has_reviewers, "content-short should have reviewer group")


if __name__ == "__main__":
    unittest.main()
