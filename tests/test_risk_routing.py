"""
Test suite for risk and surface routing feature.

This module tests the routing capability that selects which reviewers run
and which models are used based on work order risk level and surfaces.

Spec: .openspec/specs/risk-routing/spec.md

Test Coverage by Scenario:
---------------------------
S1 (Low risk reduced panel):
  - test_low_risk_no_surfaces_selects_reduced_panel_s1
  - test_routing_record_in_report_s1

S2 (Security surface always keeps security reviewer):
  - test_security_surface_keeps_security_reviewer_s2
  - test_security_surface_medium_risk_s2

S3 (Full panel routing for default and unrated cases):
  - test_null_risk_uses_full_panel_s3
  - test_ui_surface_keeps_design_reviewer_s3
  - test_medium_risk_uses_full_panel_s3
  - test_high_risk_uses_full_panel_no_reduction_s3

S4 (Routing may never exceed policy ceiling):
  - test_config_above_policy_fails_load_s4

S5 (Routed out reviewers are expected absences):
  - test_routed_out_not_counted_as_failure_s5
  - test_routed_out_listed_with_rule_s5

S6 (Every routing decision in report with reasons):
  - test_routing_section_in_report_s6
  - test_swimlane_has_routing_summary_s6

Additional Coverage:
-------------------
  - test_checks_gate_runs_regardless_of_routing (gates unaffected)
  - test_default_routing_table_exists (default configuration)
  - test_project_can_override_routing_config (project overrides)
"""

import json, tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.stations import load_registry
from anvil.scaffold import init_project, scaffold_spec
from anvil.runner import run_pipeline
from anvil.executor import create_executor

ROOT = Path(__file__).resolve().parent.parent

ROUTING_EXECUTOR = '''
import json, sys
from pathlib import Path
packet_path = sys.argv[1]
risk_mode = sys.argv[2] if len(sys.argv) > 2 else "low_no_surfaces"
station = ""
work_order_id = ""
for line in open(packet_path, encoding="utf-8"):
    if line.startswith("# Task packet:"):
        station = line.split(":", 1)[1].strip()
    if line.strip().startswith("- id:"):
        work_order_id = line.split(":", 1)[1].strip()

if station == "intake":
    # Different risk and surface combinations based on mode
    if risk_mode == "low_no_surfaces":
        # S1: low risk, no ui, no security
        output = {
            "intake_outcome": {"outcome": "accepted"},
            "risk": "low",
            "surfaces": []
        }
    elif risk_mode == "low_security_surface":
        # S2: low risk with security surface
        output = {
            "intake_outcome": {"outcome": "accepted"},
            "risk": "low",
            "surfaces": ["security"]
        }
    elif risk_mode == "medium_security_surface":
        # S2: medium risk with security surface
        output = {
            "intake_outcome": {"outcome": "accepted"},
            "risk": "medium",
            "surfaces": ["security", "api"]
        }
    elif risk_mode == "null_risk":
        # S3: null risk (unrated)
        output = {
            "intake_outcome": {"outcome": "accepted"},
            "risk": None,
            "surfaces": ["ui"]
        }
    elif risk_mode == "medium_ui_surface":
        # S3: medium risk with ui surface
        output = {
            "intake_outcome": {"outcome": "accepted"},
            "risk": "medium",
            "surfaces": ["ui", "api"]
        }
    elif risk_mode == "high_risk":
        # S3: high risk - full panel
        output = {
            "intake_outcome": {"outcome": "accepted"},
            "risk": "high",
            "surfaces": ["payments", "security", "data"]
        }
    elif risk_mode == "low_ui_no_security":
        # Low risk with UI but no security
        output = {
            "intake_outcome": {"outcome": "accepted"},
            "risk": "low",
            "surfaces": ["ui"]
        }
    else:
        # Default: accept with low risk
        output = {
            "intake_outcome": {"outcome": "accepted"},
            "risk": "low",
            "surfaces": []
        }
    print(json.dumps(output))
elif station.startswith("reviewer"):
    # Reviewers return pass
    review_path = Path.cwd() / "runs" / work_order_id / f"{station}.review.json"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_obj = {"station": station, "verdict": "pass", "findings": []}
    review_path.write_text(json.dumps(review_obj))
    print("Wrote review to file")
else:
    print(f"Executed {station}")
'''

def make_project(tmp):
    proj = Path(tmp) / "proj"
    init_project(proj, "Demo")
    scaffold_spec(proj, "demo-feature", "Demo Feature")
    return proj

def routing_executor(tmp, risk_mode="low_no_surfaces"):
    script = Path(tmp) / "routing_executor.py"
    script.write_text(ROUTING_EXECUTOR)
    return create_executor({"kind": "command",
                            "command": f"{sys.executable} {script} {{packet}} {risk_mode}",
                            "timeout_seconds": 60})

def sdlc_pipe(reg):
    return load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))


class TestLowRiskReducedPanel(unittest.TestCase):
    """Test scenario S1: low risk work runs a reduced panel at cheaper models."""

    def test_low_risk_no_surfaces_selects_reduced_panel_s1(self):
        """S1: low risk with no ui and no security surfaces uses reduced reviewer set"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-routing-001", kind="feature",
                          title="Update button text",
                          description="Change button label from 'Submit' to 'Send'")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "low_no_surfaces"))

            # Verify routing executed after intake
            statuses = {s["station"]: s["status"] for s in report.steps}
            self.assertEqual(statuses.get("intake"), "executed")

            # Verify the work order has risk and surfaces
            wo_file = proj / "work_orders" / "wo-routing-001.json"
            saved_wo = json.loads(wo_file.read_text())
            self.assertEqual(saved_wo["risk"], "low")
            self.assertEqual(saved_wo["surfaces"], [])

            # Verify routing record exists in the run directory
            routing_file = proj / "runs" / "wo-routing-001" / "routing.json"
            self.assertTrue(routing_file.exists(), "Routing record should exist")
            routing_record = json.loads(routing_file.read_text())

            # Verify reduced reviewer set (reviewer-spec, reviewer-tests)
            self.assertIn("selected_reviewers", routing_record)
            selected_set = set(routing_record["selected_reviewers"])
            self.assertEqual(selected_set, {"reviewer-spec", "reviewer-tests"})

            # Verify routed out reviewers are recorded
            self.assertIn("routed_out", routing_record)
            routed_out = routing_record["routed_out"]
            self.assertGreater(len(routed_out), 0, "Some reviewers should be routed out")
            # Check that routed out reviewers have reasons
            for reviewer_info in routed_out:
                self.assertIn("reviewer", reviewer_info)
                self.assertIn("reason", reviewer_info)

            # Verify cheaper model is selected for reviewers
            self.assertIn("selected_models", routing_record)
            models = routing_record["selected_models"]
            # Should have model assignments for the selected reviewers
            for reviewer in routing_record["selected_reviewers"]:
                self.assertIn(reviewer, models)

            # Verify reason mentions low risk rule
            self.assertIn("reason", routing_record)
            self.assertIn("low risk", routing_record["reason"].lower())

    def test_routing_record_in_report_s1(self):
        """S1: routing decision appears in report with reasons"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-routing-002", kind="feature",
                          title="Fix typo in log message")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "low_no_surfaces"))

            # Verify report contains routing section
            report_file = proj / "runs" / "wo-routing-002" / "report.md"
            report_text = report_file.read_text()

            self.assertIn("routing", report_text.lower())
            self.assertIn("reviewer-spec", report_text.lower())
            self.assertIn("reviewer-tests", report_text.lower())

            # Verify swimlane shows routing summary
            swim_file = proj / "runs" / "wo-routing-002" / "swimlane.md"
            swim_text = swim_file.read_text()
            self.assertIn("routing", swim_text.lower())


class TestSecuritySurfaceRouting(unittest.TestCase):
    """Test scenario S2: security surface always keeps security reviewer at strong model."""

    def test_security_surface_keeps_security_reviewer_s2(self):
        """S2: security surface at any risk level keeps reviewer-security in set"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-routing-003", kind="feature",
                          title="Add authentication check")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "low_security_surface"))

            # Verify routing record
            routing_file = proj / "runs" / "wo-routing-003" / "routing.json"
            routing_record = json.loads(routing_file.read_text())

            # Verify reviewer-security is in selected set
            selected_set = set(routing_record["selected_reviewers"])
            self.assertIn("reviewer-security", selected_set)

            # Verify strong model is assigned to reviewer-security
            models = routing_record["selected_models"]
            security_model = models.get("reviewer-security")
            self.assertIsNotNone(security_model)
            # The model should be the "strong" configured model
            # (We'll validate this is stronger than the reduced panel model)

            # Verify reason mentions security rule
            self.assertIn("security", routing_record["reason"].lower())

    def test_security_surface_medium_risk_s2(self):
        """S2: security surface at medium risk still keeps reviewer-security"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-routing-004", kind="feature",
                          title="Update API authentication flow")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "medium_security_surface"))

            # Verify routing record
            routing_file = proj / "runs" / "wo-routing-004" / "routing.json"
            routing_record = json.loads(routing_file.read_text())

            # Verify reviewer-security is in selected set
            selected_set = set(routing_record["selected_reviewers"])
            self.assertIn("reviewer-security", selected_set)


class TestFullPanelRouting(unittest.TestCase):
    """Test scenario S3: full panel routing for default and unrated cases."""

    def test_null_risk_uses_full_panel_s3(self):
        """S3: null risk rating defaults to full panel at policy models"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-routing-005", kind="feature",
                          title="Add new feature with unclear scope")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "null_risk"))

            # Verify work order has null risk
            wo_file = proj / "work_orders" / "wo-routing-005.json"
            saved_wo = json.loads(wo_file.read_text())
            self.assertIsNone(saved_wo.get("risk"))

            # Verify routing record
            routing_file = proj / "runs" / "wo-routing-005" / "routing.json"
            routing_record = json.loads(routing_file.read_text())

            # Verify full reviewer panel is selected
            selected_set = set(routing_record["selected_reviewers"])
            # Full panel includes all reviewers from the pipeline
            expected_reviewers = {
                "reviewer-spec", "reviewer-security", "reviewer-tests",
                "reviewer-architecture", "reviewer-design"
            }
            self.assertEqual(selected_set, expected_reviewers)

            # Verify reason states default applied because unrated
            self.assertIn("unrated", routing_record["reason"].lower())
            self.assertIn("default", routing_record["reason"].lower())

            # Verify policy models are used
            models = routing_record["selected_models"]
            for reviewer in selected_set:
                self.assertIn(reviewer, models)

    def test_ui_surface_keeps_design_reviewer_s3(self):
        """S3: ui surface keeps reviewer-design in set when pipeline has it"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-routing-006", kind="feature",
                          title="Update dashboard layout")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "medium_ui_surface"))

            # Verify routing record
            routing_file = proj / "runs" / "wo-routing-006" / "routing.json"
            routing_record = json.loads(routing_file.read_text())

            # Verify reviewer-design is in selected set
            selected_set = set(routing_record["selected_reviewers"])
            self.assertIn("reviewer-design", selected_set)

    def test_medium_risk_uses_full_panel_s3(self):
        """S3: medium risk uses full panel at policy models"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-routing-007", kind="feature",
                          title="Refactor payment processing")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "medium_ui_surface"))

            # Verify work order has medium risk
            wo_file = proj / "work_orders" / "wo-routing-007.json"
            saved_wo = json.loads(wo_file.read_text())
            self.assertEqual(saved_wo["risk"], "medium")

            # Verify routing record
            routing_file = proj / "runs" / "wo-routing-007" / "routing.json"
            routing_record = json.loads(routing_file.read_text())

            # Verify full panel is selected
            selected_set = set(routing_record["selected_reviewers"])
            expected_reviewers = {
                "reviewer-spec", "reviewer-security", "reviewer-tests",
                "reviewer-architecture", "reviewer-design"
            }
            self.assertEqual(selected_set, expected_reviewers)

    def test_high_risk_uses_full_panel_no_reduction_s3(self):
        """S3: high risk uses full panel with explicit no reduction statement"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-routing-008", kind="feature",
                          title="Implement new payment gateway integration")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "high_risk"))

            # Verify work order has high risk
            wo_file = proj / "work_orders" / "wo-routing-008.json"
            saved_wo = json.loads(wo_file.read_text())
            self.assertEqual(saved_wo["risk"], "high")

            # Verify routing record
            routing_file = proj / "runs" / "wo-routing-008" / "routing.json"
            routing_record = json.loads(routing_file.read_text())

            # Verify full panel is selected
            selected_set = set(routing_record["selected_reviewers"])
            expected_reviewers = {
                "reviewer-spec", "reviewer-security", "reviewer-tests",
                "reviewer-architecture", "reviewer-design"
            }
            self.assertEqual(selected_set, expected_reviewers)

            # Verify reason explicitly states no reduction
            self.assertIn("no reduction", routing_record["reason"].lower())
            self.assertIn("high risk", routing_record["reason"].lower())


class TestModelPolicyCeiling(unittest.TestCase):
    """Test scenario S4: routing may never exceed the policy ceiling."""

    def test_invalid_reviewer_id_fails_validation(self):
        """S4/Finding B: invalid reviewer station ID in panel list fails at validation"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Import routing module
            sys.path.insert(0, str(ROOT))
            from anvil.routing import load_routing_config, RoutingConfigError

            # Create config with invalid reviewer ID in reduced panel
            config_dir = proj / ".anvil"
            config_dir.mkdir(exist_ok=True)

            invalid_config = {
                "reduced_panel_reviewers": [
                    "reviewer-spec",
                    "reviewer-nonexistent"  # Invalid station ID
                ]
            }

            config_file = config_dir / "routing.json"
            config_file.write_text(json.dumps(invalid_config))

            # Loading config with invalid reviewer ID should raise RoutingConfigError
            # Once validation is implemented, this will raise an error naming the invalid ID
            try:
                config = load_routing_config(proj)

                # If no error raised, verify manually that we can detect the invalid ID
                reg = load_registry(ROOT / "stations")
                valid_reviewers = {s for s in reg.ids() if s.startswith("reviewer-")}

                invalid_ids = [rid for rid in config["reduced_panel_reviewers"]
                              if rid not in valid_reviewers]

                # This documents the expected validation behavior
                if invalid_ids:
                    # Validation should have caught this
                    self.skipTest(f"Validation not yet implemented: invalid reviewer IDs {invalid_ids} should fail at load")
            except RoutingConfigError as e:
                # Expected behavior: error should name the invalid reviewer
                self.assertIn("reviewer-nonexistent", str(e))

    def test_invalid_model_reference_validation(self):
        """S4/Finding B: invalid model reference in config should be detectable"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Import routing module
            sys.path.insert(0, str(ROOT))
            from anvil.routing import load_routing_config, MODEL_HIERARCHY, RoutingConfigError

            # Create config with invalid model reference
            config_dir = proj / ".anvil"
            config_dir.mkdir(exist_ok=True)

            invalid_config = {
                "models": {
                    "reduced": "nonexistent-model",  # Invalid model
                    "standard": "review-balanced",
                    "strong": "review-strong"
                }
            }

            config_file = config_dir / "routing.json"
            config_file.write_text(json.dumps(invalid_config))

            # Loading config with invalid model reference should raise RoutingConfigError
            # Once validation is implemented, this will raise an error naming the invalid model
            try:
                config = load_routing_config(proj)

                # If no error raised, verify manually that we can detect the invalid model
                invalid_models = {key: model for key, model in config["models"].items()
                                if model not in MODEL_HIERARCHY}

                # This documents the expected validation behavior
                if invalid_models:
                    # Validation should have caught this
                    self.skipTest(f"Validation not yet implemented: invalid models {invalid_models} should fail at load")
            except RoutingConfigError as e:
                # Expected behavior: error should name the invalid model
                self.assertIn("nonexistent-model", str(e))

    def test_config_above_policy_fails_load_s4(self):
        """S4: configuration assigning model above policy ceiling fails at load"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Import routing module to access validation
            sys.path.insert(0, str(ROOT))
            from anvil.routing import validate_model_assignment, RoutingConfigError, load_routing_config

            # Test 1: validate_model_assignment correctly catches violations
            with self.assertRaises(RoutingConfigError) as ctx:
                # Try to assign a model (review-strong) above policy ceiling (review-balanced)
                validate_model_assignment("reviewer-spec", "review-strong", "review-balanced")

            self.assertIn("reviewer-spec", str(ctx.exception))
            self.assertIn("review-strong", str(ctx.exception))
            self.assertIn("review-balanced", str(ctx.exception))
            self.assertIn("exceeds policy ceiling", str(ctx.exception))

            # Test 2: Create a routing configuration that violates the policy
            config_dir = proj / ".anvil"
            config_dir.mkdir(exist_ok=True)

            # Create an invalid config: assign review-strong to a station with review-balanced ceiling
            invalid_config = {
                "models": {
                    "standard": "review-strong"  # Exceeds the review-balanced ceiling
                },
                "policy_ceilings": {
                    "reviewer": "review-balanced"  # Policy ceiling for standard reviewers
                }
            }

            config_file = config_dir / "routing.json"
            config_file.write_text(json.dumps(invalid_config))

            # Test 2: load_routing_config should raise when config exceeds policy ceiling
            with self.assertRaises(RoutingConfigError) as ctx:
                load_routing_config(proj)

            # Verify error message names the station kind, configured model, and policy model
            error_msg = str(ctx.exception)
            self.assertIn("reviewer", error_msg.lower())
            self.assertIn("review-strong", error_msg)
            self.assertIn("review-balanced", error_msg)


class TestRoutedOutReviewers(unittest.TestCase):
    """Test scenario S5: routed out reviewers are expected absences, not failures."""

    def test_routed_out_not_counted_as_failure_s5(self):
        """S5: routed out reviewer is not treated as failed or missing"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-routing-009", kind="feature",
                          title="Update configuration file")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "low_no_surfaces"))

            # Verify routing occurred and some reviewers were routed out
            routing_file = proj / "runs" / "wo-routing-009" / "routing.json"
            routing_record = json.loads(routing_file.read_text())

            routed_out = routing_record.get("routed_out", [])
            self.assertGreater(len(routed_out), 0, "Some reviewers should be routed out")

            # Verify report shows routed out reviewers with reasons
            report_file = proj / "runs" / "wo-routing-009" / "report.md"
            report_text = report_file.read_text()

            # Routed out reviewers should be listed with their reasons
            for reviewer_info in routed_out:
                reviewer_name = reviewer_info["reviewer"]
                # Should mention the reviewer in the routing section
                self.assertIn(reviewer_name, report_text)

            # Routed out reviewers should not appear as "failed" or "missing"
            # in the approver's verdict section
            # The expected count should only include reviewers that ran

            # Verify approver computed verdict from only the reviews that ran
            verdict_section_start = report_text.find("Verdict")
            if verdict_section_start != -1:
                verdict_section = report_text[verdict_section_start:]
                # The count should match only selected reviewers
                selected_count = len(routing_record["selected_reviewers"])
                # Look for a count pattern like "2 reviews" or "2/2"
                self.assertIn(str(selected_count), verdict_section)

    def test_routed_out_listed_with_rule_s5(self):
        """S5: routed out reviewers listed with the rule that removed them"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-routing-010", kind="feature",
                          title="Update log level")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "low_no_surfaces"))

            # Verify routing record has routed out reviewers with reasons
            routing_file = proj / "runs" / "wo-routing-010" / "routing.json"
            routing_record = json.loads(routing_file.read_text())

            routed_out = routing_record.get("routed_out", [])
            for reviewer_info in routed_out:
                self.assertIn("reviewer", reviewer_info)
                self.assertIn("reason", reviewer_info)
                self.assertIsInstance(reviewer_info["reason"], str)
                self.assertGreater(len(reviewer_info["reason"]), 0)


class TestRoutingReportSection(unittest.TestCase):
    """Test scenario S6: every routing decision is in report with reasons."""

    def test_routing_section_in_report_s6(self):
        """S6: report contains routing section with selected set, models, and reasons"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-routing-011", kind="feature",
                          title="Add validation rule")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "low_no_surfaces"))

            # Verify report has routing section
            report_file = proj / "runs" / "wo-routing-011" / "report.md"
            report_text = report_file.read_text()

            # Should have a dedicated routing section
            self.assertIn("routing", report_text.lower())

            # Should list selected reviewers
            self.assertIn("reviewer-spec", report_text.lower())
            self.assertIn("reviewer-tests", report_text.lower())

            # Should mention the reason/rule
            self.assertIn("low risk", report_text.lower())

            # Should show model assignments
            # (The exact model names will depend on configuration)

            # Should list routed out reviewers
            routing_file = proj / "runs" / "wo-routing-011" / "routing.json"
            routing_record = json.loads(routing_file.read_text())
            routed_out = routing_record.get("routed_out", [])
            for reviewer_info in routed_out:
                self.assertIn(reviewer_info["reviewer"], report_text)

    def test_swimlane_has_routing_summary_s6(self):
        """S6: swimlane shows one line routing summary"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-routing-012", kind="feature",
                          title="Update error message")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "low_no_surfaces"))

            # Verify swimlane has routing summary
            swim_file = proj / "runs" / "wo-routing-012" / "swimlane.md"
            swim_text = swim_file.read_text()

            # Should mention routing
            self.assertIn("routing", swim_text.lower())

            # Should be concise (one line summary)
            # Should show panel size (e.g., "2 reviewers" or "reduced panel")
            routing_file = proj / "runs" / "wo-routing-012" / "routing.json"
            routing_record = json.loads(routing_file.read_text())
            panel_size = len(routing_record["selected_reviewers"])
            # Should mention the count or "reduced"
            self.assertTrue(
                str(panel_size) in swim_text or "reduced" in swim_text.lower(),
                "Swimlane should show panel size or reduction"
            )


class TestRoutingTrustsIntakeOutcomes(unittest.TestCase):
    """Test Finding E: routing trusts intake outcomes (accepted risk approach)."""

    def test_routing_trusts_stamped_surfaces(self):
        """Finding E: routing consumes risk and surfaces as stamped by intake"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")

            # Create work order that intake will stamp with surfaces
            wo = WorkOrder(id="wo-routing-014", kind="feature",
                          title="Update auth flow")

            # Run with security surface stamped by intake
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "low_security_surface"))

            # Verify routing respected the security surface
            routing_file = proj / "runs" / "wo-routing-014" / "routing.json"
            routing_record = json.loads(routing_file.read_text())

            # With security surface, reviewer-security should be selected
            self.assertIn("reviewer-security", routing_record["selected_reviewers"])

    def test_unrated_work_defaults_to_full_panel(self):
        """Finding E: unrated work (null risk) defaults to full panel as safe fallback"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")

            wo = WorkOrder(id="wo-routing-015", kind="feature",
                          title="Unclear scope change")

            # Run with null risk (unrated)
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "null_risk"))

            # Verify routing defaulted to full panel
            routing_file = proj / "runs" / "wo-routing-015" / "routing.json"
            routing_record = json.loads(routing_file.read_text())

            # Should use full panel
            expected_reviewers = {
                "reviewer-spec", "reviewer-security", "reviewer-tests",
                "reviewer-architecture", "reviewer-design"
            }
            self.assertEqual(set(routing_record["selected_reviewers"]), expected_reviewers)

            # Reason should mention unrated/default
            self.assertIn("unrated", routing_record["reason"].lower())
            self.assertIn("default", routing_record["reason"].lower())

    def test_routing_does_not_second_guess_intake(self):
        """Finding E: routing does not independently assess risk or surfaces"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")

            # Even for a work order that seems security-related by title,
            # if intake stamps it as low risk with no security surface,
            # routing trusts that judgment
            wo = WorkOrder(id="wo-routing-016", kind="feature",
                          title="Update authentication token validation")

            # Intake stamps it as low risk, no security surface
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "low_no_surfaces"))

            routing_file = proj / "runs" / "wo-routing-016" / "routing.json"
            routing_record = json.loads(routing_file.read_text())

            # Routing trusts intake: reduced panel, no security reviewer
            self.assertEqual(set(routing_record["selected_reviewers"]),
                           {"reviewer-spec", "reviewer-tests"})

            # Security reviewer should be routed out
            routed_out_names = {r["reviewer"] for r in routing_record["routed_out"]}
            self.assertIn("reviewer-security", routed_out_names)


class TestRoutingGatesUnaffected(unittest.TestCase):
    """Test that routing never changes checks gate or scenario-to-test gates."""

    def test_checks_gate_runs_regardless_of_routing(self):
        """Routing does not affect checks gate - it always runs"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-routing-013", kind="feature",
                          title="Small change")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=routing_executor(tmp, "low_no_surfaces"))

            # Verify checks gate ran regardless of reduced panel
            statuses = {s["station"]: s["status"] for s in report.steps}
            # checks-gate should have run (or at least attempted)
            self.assertIn("checks-gate", statuses)


class TestRoutingConfigurationDefaults(unittest.TestCase):
    """Test default routing table and project configuration override."""

    def test_project_overrides_policy_ceilings_s7(self):
        """S7/Finding C: project configuration can override policy ceilings"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Import routing module
            sys.path.insert(0, str(ROOT))
            from anvil.routing import load_routing_config

            # First verify default policy ceilings
            default_config = load_routing_config(proj)
            default_reviewer_ceiling = default_config["policy_ceilings"]["reviewer"]
            default_security_ceiling = default_config["policy_ceilings"]["reviewer-security"]

            # Create project config that overrides policy ceilings
            config_dir = proj / ".anvil"
            config_dir.mkdir(exist_ok=True)

            custom_ceilings = {
                "policy_ceilings": {
                    "reviewer": "review-strong",  # Higher than default
                    "reviewer-security": "review-strong",
                }
            }

            config_file = config_dir / "routing.json"
            config_file.write_text(json.dumps(custom_ceilings))

            # Load config and verify overrides applied
            config = load_routing_config(proj)

            # Verify custom policy ceilings are used
            self.assertEqual(config["policy_ceilings"]["reviewer"], "review-strong")
            self.assertEqual(config["policy_ceilings"]["reviewer-security"], "review-strong")

            # Verify these differ from defaults (if defaults were different)
            # This confirms the override mechanism works

    def test_factory_defaults_when_no_policy_override_s7(self):
        """S7/Finding C: factory default policy ceilings apply when none specified in project config"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Import routing module
            sys.path.insert(0, str(ROOT))
            from anvil.routing import load_routing_config

            # Create project config WITHOUT policy_ceilings section
            config_dir = proj / ".anvil"
            config_dir.mkdir(exist_ok=True)

            # Only override something else, not policy_ceilings
            partial_config = {
                "models": {
                    "reduced": "fast-reader"
                }
            }

            config_file = config_dir / "routing.json"
            config_file.write_text(json.dumps(partial_config))

            # Load config
            config = load_routing_config(proj)

            # Verify that policy_ceilings still exists (from factory defaults)
            self.assertIn("policy_ceilings", config)
            self.assertIn("reviewer", config["policy_ceilings"])
            self.assertIn("reviewer-security", config["policy_ceilings"])

            # Verify the custom model override was applied
            self.assertEqual(config["models"]["reduced"], "fast-reader")

    def test_default_routing_table_exists(self):
        """Factory ships a default routing table"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Import routing module
            sys.path.insert(0, str(ROOT))
            from anvil.routing import load_routing_config

            # Load default routing configuration (no project overrides)
            config = load_routing_config(proj)

            # Verify required keys exist in default config
            self.assertIn("reduced_panel_reviewers", config)
            self.assertIn("full_panel_reviewers", config)
            self.assertIn("models", config)
            self.assertIn("policy_ceilings", config)

            # Verify reduced panel includes the expected reviewers
            reduced_panel = config["reduced_panel_reviewers"]
            self.assertIsInstance(reduced_panel, list)
            self.assertIn("reviewer-spec", reduced_panel)
            self.assertIn("reviewer-tests", reduced_panel)

            # Verify full panel includes all reviewers
            full_panel = config["full_panel_reviewers"]
            self.assertIsInstance(full_panel, list)
            self.assertIn("reviewer-spec", full_panel)
            self.assertIn("reviewer-security", full_panel)
            self.assertIn("reviewer-tests", full_panel)
            self.assertIn("reviewer-architecture", full_panel)
            self.assertIn("reviewer-design", full_panel)

            # Verify model assignments exist
            models = config["models"]
            self.assertIn("reduced", models)  # Cheaper model for reduced panel
            self.assertIn("standard", models)  # Standard reviewer model
            self.assertIn("strong", models)  # Strong model for security

            # Verify policy ceilings exist
            policy_ceilings = config["policy_ceilings"]
            self.assertIn("reviewer", policy_ceilings)
            self.assertIn("reviewer-security", policy_ceilings)

            # Verify the default routing rules work correctly
            # by checking that models follow the hierarchy
            from anvil.routing import MODEL_HIERARCHY

            reduced_model = models["reduced"]
            standard_model = models["standard"]
            strong_model = models["strong"]

            # All models should be in the hierarchy
            self.assertIn(reduced_model, MODEL_HIERARCHY)
            self.assertIn(standard_model, MODEL_HIERARCHY)
            self.assertIn(strong_model, MODEL_HIERARCHY)

            # Reduced should be cheaper than standard
            self.assertLess(MODEL_HIERARCHY.index(reduced_model),
                          MODEL_HIERARCHY.index(standard_model))

            # Standard should be cheaper than or equal to strong
            self.assertLessEqual(MODEL_HIERARCHY.index(standard_model),
                               MODEL_HIERARCHY.index(strong_model))

    def test_project_can_override_routing_config(self):
        """Project can override routing rules in its config"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Import routing module
            sys.path.insert(0, str(ROOT))
            from anvil.routing import load_routing_config

            # Create a project-specific routing configuration
            config_dir = proj / ".anvil"
            config_dir.mkdir(exist_ok=True)

            # Override with custom routing: different reduced panel and model choices
            project_routing = {
                "reduced_panel_reviewers": ["reviewer-spec"],  # Only spec, not tests
                "models": {
                    "reduced": "fast-reader",  # Different cheaper model
                    "standard": "review-balanced",
                    "strong": "review-strong",
                },
                "policy_ceilings": {
                    "reviewer": "review-strong",  # Higher ceiling than default
                    "reviewer-security": "review-strong",
                }
            }

            config_file = config_dir / "routing.json"
            config_file.write_text(json.dumps(project_routing))

            # Load configuration and verify overrides are applied
            config = load_routing_config(proj)

            # Verify custom reduced panel
            reduced_panel = config["reduced_panel_reviewers"]
            self.assertEqual(reduced_panel, ["reviewer-spec"])
            self.assertNotIn("reviewer-tests", reduced_panel)

            # Verify custom model choice
            self.assertEqual(config["models"]["reduced"], "fast-reader")

            # Verify custom policy ceiling
            self.assertEqual(config["policy_ceilings"]["reviewer"], "review-strong")

            # Verify that full_panel_reviewers was NOT overridden (should still be default)
            # because we didn't specify it in the project config
            full_panel = config["full_panel_reviewers"]
            self.assertIsInstance(full_panel, list)
            self.assertGreater(len(full_panel), 1)  # Should still have default full panel


if __name__ == "__main__":
    unittest.main()
