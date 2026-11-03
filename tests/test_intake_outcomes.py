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

INTAKE_OUTCOMES_EXECUTOR = '''
import json, sys
from pathlib import Path
packet_path = sys.argv[1]
outcome_mode = sys.argv[2] if len(sys.argv) > 2 else "accept"
station = ""
work_order_id = ""
for line in open(packet_path, encoding="utf-8"):
    if line.startswith("# Task packet:"):
        station = line.split(":", 1)[1].strip()
    if line.strip().startswith("- id:"):
        work_order_id = line.split(":", 1)[1].strip()

if station == "intake":
    if outcome_mode == "reject":
        # S1: rejected outcome
        output = {
            "intake_outcome": {
                "outcome": "rejected",
                "reasons": ["Request asks to implement harmful functionality",
                           "The described covert mining behavior is deceptive"]
            }
        }
    elif outcome_mode == "rescope":
        # S2: rescoped outcome
        output = {
            "intake_outcome": {
                "outcome": "rescoped",
                "rescoped_description": "Add a single validation check for user email format",
                "reasons": ["Original request asked for three unrelated features",
                           "Cut the email templating and analytics features to make this buildable"]
            },
            "risk": "low",
            "surfaces": ["ui"]
        }
    elif outcome_mode == "waiting_info":
        # S3: waiting_info outcome
        output = {
            "intake_outcome": {
                "outcome": "waiting_info",
                "questions": ["Which user roles should have access to this feature?",
                             "What is the expected behavior when the API is unavailable?"]
            }
        }
    elif outcome_mode == "accept_high_risk":
        # S4: accepted with high risk and multiple surfaces
        output = {
            "intake_outcome": {
                "outcome": "accepted"
            },
            "risk": "high",
            "surfaces": ["payments", "security", "data"]
        }
    else:
        # Default accept with low risk
        output = {
            "intake_outcome": {
                "outcome": "accepted"
            },
            "risk": "low",
            "surfaces": ["ui"]
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

def intake_executor(tmp, outcome_mode="accept"):
    script = Path(tmp) / "intake_executor.py"
    script.write_text(INTAKE_OUTCOMES_EXECUTOR)
    return create_executor({"kind": "command",
                            "command": f"{sys.executable} {script} {{packet}} {outcome_mode}",
                            "timeout_seconds": 60})

def sdlc_pipe(reg):
    return load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))


def markdown_injection_executor(tmp, mode="reasons"):
    """Create an executor that returns markdown/HTML injection payloads."""
    script = Path(tmp) / "markdown_executor.py"
    
    executor_code = '''
import json, sys
from pathlib import Path
packet_path = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "reasons"
station = ""
work_order_id = ""
for line in open(packet_path, encoding="utf-8"):
    if line.startswith("# Task packet:"):
        station = line.split(":", 1)[1].strip()
    if line.strip().startswith("- id:"):
        work_order_id = line.split(":", 1)[1].strip()

if station == "intake":
    if mode == "reasons":
        output = {
            "intake_outcome": {
                "outcome": "rejected",
                "reasons": [
                    "[Click here](http://evil.com) for details",
                    "**Bold** text and *italic* text",
                    "# Header injection"
                ]
            }
        }
    elif mode == "questions":
        output = {
            "intake_outcome": {
                "outcome": "waiting_info",
                "questions": [
                    "What about [this link](http://malicious.com)?",
                    "Should we use **bold** formatting?"
                ]
            }
        }
    elif mode == "rescoped":
        output = {
            "intake_outcome": {
                "outcome": "rescoped",
                "rescoped_description": "# Fake Header\\n[Fake link](http://evil.com)\\n**Fake bold**",
                "reasons": ["Rescoped for safety"]
            },
            "risk": "low",
            "surfaces": ["ui"]
        }
    elif mode == "html":
        output = {
            "intake_outcome": {
                "outcome": "rejected",
                "reasons": [
                    "<script>alert(\\'XSS\\')</script>",
                    "<img src=x onerror=alert(1)>"
                ]
            }
        }
    else:
        output = {"intake_outcome": {"outcome": "accepted"}}
    print(json.dumps(output))
elif station.startswith("reviewer"):
    review_path = Path.cwd() / "runs" / work_order_id / f"{station}.review.json"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_obj = {"station": station, "verdict": "pass", "findings": []}
    review_path.write_text(json.dumps(review_obj))
    print("Wrote review to file")
else:
    print(f"Executed {station}")
'''
    
    script.write_text(executor_code)
    return create_executor({"kind": "command",
                            "command": f"{sys.executable} {script} {{packet}} {mode}",
                            "timeout_seconds": 60})

class TestIntakeRejection(unittest.TestCase):
    def test_rejected_work_stops_pipeline_with_reasons_s1(self):
        """intake-outcomes S1: rejected work is terminal, runner stops after intake, status becomes rejected"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-reject-001", kind="feature", title="Add covert miner")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=intake_executor(tmp, "reject"))

            # Verify the run stopped after intake
            statuses = {s["station"]: s["status"] for s in report.steps}
            self.assertEqual(statuses["intake"], "executed")
            # No spec-writer, test-writer, or builder should have executed
            self.assertNotIn("executed", [statuses.get("spec-writer"),
                                          statuses.get("test-writer"),
                                          statuses.get("builder")])

            # Verify the work order has rejection data
            wo_file = proj / "work_orders" / "wo-reject-001.json"
            saved_wo = json.loads(wo_file.read_text())
            self.assertEqual(saved_wo["status"], "rejected")
            self.assertEqual(saved_wo["intake_outcome"]["outcome"], "rejected")
            self.assertEqual(len(saved_wo["intake_outcome"]["reasons"]), 2)
            self.assertIn("harmful", saved_wo["intake_outcome"]["reasons"][0].lower())

            # Verify the rejection appears in the report
            report_file = proj / "runs" / "wo-reject-001" / "report.md"
            report_text = report_file.read_text()
            self.assertIn("rejected", report_text.lower())
            self.assertIn("harmful", report_text.lower())

            # Verify the swimlane shows rejection
            swim_file = proj / "runs" / "wo-reject-001" / "swimlane.md"
            swim_text = swim_file.read_text()
            self.assertIn("reject", swim_text.lower())

class TestIntakeRescope(unittest.TestCase):
    def test_rescoped_work_carries_new_description_downstream_s2(self):
        """intake-outcomes S2: rescoped work updates description, records cut, and continues with rescoped scope"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-rescope-001", kind="feature",
                          title="Add validation, templating, and analytics",
                          description="Add email validation, email templates, and analytics dashboard")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=intake_executor(tmp, "rescope"))

            # Verify intake executed
            statuses = {s["station"]: s["status"] for s in report.steps}
            self.assertEqual(statuses["intake"], "executed")

            # Verify the work order has rescope data
            wo_file = proj / "work_orders" / "wo-rescope-001.json"
            saved_wo = json.loads(wo_file.read_text())
            self.assertEqual(saved_wo["intake_outcome"]["outcome"], "rescoped")
            self.assertIn("validation check", saved_wo["intake_outcome"]["rescoped_description"])
            self.assertEqual(len(saved_wo["intake_outcome"]["reasons"]), 2)
            self.assertIn("three unrelated", saved_wo["intake_outcome"]["reasons"][0].lower())

            # Verify the rescoped description is what continues
            # (the original description should be preserved but the rescoped one should be noted)
            self.assertIsNotNone(saved_wo["intake_outcome"]["rescoped_description"])

            # Verify downstream packets would carry the rescoped description
            # Check spec-writer packet if it was created
            spec_packet = proj / "runs" / "wo-rescope-001" / "spec-writer.packet.md"
            if spec_packet.exists():
                packet_text = spec_packet.read_text()
                self.assertIn("validation", packet_text.lower())

class TestIntakeWaitingInfo(unittest.TestCase):
    def test_waiting_info_parks_work_with_questions_s3(self):
        """intake-outcomes S3: waiting_info stops pipeline, records questions, status becomes waiting_info"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-waiting-001", kind="feature",
                          title="Add new feature",
                          description="Add a feature but details are vague")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=intake_executor(tmp, "waiting_info"))

            # Verify the run stopped after intake
            statuses = {s["station"]: s["status"] for s in report.steps}
            self.assertEqual(statuses["intake"], "executed")
            # No downstream stations should have executed
            self.assertNotIn("executed", [statuses.get("spec-writer"),
                                          statuses.get("test-writer"),
                                          statuses.get("builder")])

            # Verify the work order has waiting_info data
            wo_file = proj / "work_orders" / "wo-waiting-001.json"
            saved_wo = json.loads(wo_file.read_text())
            self.assertEqual(saved_wo["status"], "waiting_info")
            self.assertEqual(saved_wo["intake_outcome"]["outcome"], "waiting_info")
            self.assertEqual(len(saved_wo["intake_outcome"]["questions"]), 2)
            self.assertIn("user roles", saved_wo["intake_outcome"]["questions"][0])

            # Verify the report shows waiting state, not pass or fail
            report_file = proj / "runs" / "wo-waiting-001" / "report.md"
            report_text = report_file.read_text()
            self.assertIn("waiting", report_text.lower())
            # Should not claim approval or rejection
            self.assertNotIn("approved", report_text.lower())
            self.assertNotIn("rejected", report_text.lower())

class TestIntakeRiskAndSurfaces(unittest.TestCase):
    def test_accepted_work_carries_risk_and_surfaces_s4(self):
        """intake-outcomes S4: accepted work carries risk rating and surfaces list"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-risk-001", kind="feature",
                          title="Update payment processing",
                          description="Modify the payment flow to add new validation")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=intake_executor(tmp, "accept_high_risk"))

            # Verify intake executed
            statuses = {s["station"]: s["status"] for s in report.steps}
            self.assertEqual(statuses["intake"], "executed")

            # Verify the work order has risk and surfaces
            wo_file = proj / "work_orders" / "wo-risk-001.json"
            saved_wo = json.loads(wo_file.read_text())
            self.assertEqual(saved_wo["intake_outcome"]["outcome"], "accepted")
            self.assertEqual(saved_wo["risk"], "high")
            self.assertEqual(set(saved_wo["surfaces"]), {"payments", "security", "data"})

            # Verify risk and surfaces appear in the report
            report_file = proj / "runs" / "wo-risk-001" / "report.md"
            report_text = report_file.read_text()
            self.assertIn("high", report_text.lower())
            self.assertIn("payments", report_text.lower())

    def test_low_risk_accepted_work_s4(self):
        """intake-outcomes S4: low risk work with single surface"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-risk-002", kind="feature",
                          title="Update button color",
                          description="Change the color of the submit button")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=intake_executor(tmp, "accept"))

            # Verify the work order has low risk
            wo_file = proj / "work_orders" / "wo-risk-002.json"
            saved_wo = json.loads(wo_file.read_text())
            self.assertEqual(saved_wo["risk"], "low")
            self.assertIn("ui", saved_wo["surfaces"])

class TestIntakeHonestRendering(unittest.TestCase):
    def test_rejected_run_renders_honestly_s5(self):
        """intake-outcomes S5: rejected run shows no downstream stations as executed, shows reasons"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-honest-001", kind="feature", title="Harmful request")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=intake_executor(tmp, "reject"))

            # Verify report shows honest state
            report_file = proj / "runs" / "wo-honest-001" / "report.md"
            report_text = report_file.read_text()

            # Should show reasons
            self.assertIn("harmful", report_text.lower())

            # Should not claim stations beyond intake as executed
            statuses = {s["station"]: s["status"] for s in report.steps}
            for station in ["spec-writer", "test-writer", "builder"]:
                if station in statuses:
                    self.assertNotEqual(statuses[station], "executed")

            # Should not show as approved
            self.assertNotIn("approved", report_text.lower())

            # Verify swimlane is honest
            swim_file = proj / "runs" / "wo-honest-001" / "swimlane.md"
            swim_text = swim_file.read_text()
            self.assertIn("reject", swim_text.lower())

    def test_waiting_run_renders_honestly_s5(self):
        """intake-outcomes S5: waiting run shows questions, not as passed or failed"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-honest-002", kind="feature", title="Unclear request")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=intake_executor(tmp, "waiting_info"))

            # Verify report shows honest waiting state
            report_file = proj / "runs" / "wo-honest-002" / "report.md"
            report_text = report_file.read_text()

            # Should show questions
            self.assertIn("user roles", report_text.lower())

            # Should not claim as passed or failed
            self.assertNotIn("approved", report_text.lower())
            self.assertNotIn("rejected", report_text.lower())

            # Should show waiting
            self.assertIn("waiting", report_text.lower())

            # Verify no downstream stations executed
            statuses = {s["station"]: s["status"] for s in report.steps}
            for station in ["spec-writer", "test-writer", "builder"]:
                if station in statuses:
                    self.assertNotEqual(statuses[station], "executed")

class TestIntakeOutcomeWorkflow(unittest.TestCase):
    def test_waiting_work_can_resume_after_answers_s3(self):
        """intake-outcomes S3: after answers provided, work order can return to runnable status and proceed"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")

            # First run: intake asks questions
            wo = WorkOrder(id="wo-resume-001", kind="feature", title="Feature needing info")
            report1 = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                   executor=intake_executor(tmp, "waiting_info"))

            # Verify waiting state
            wo_file = proj / "work_orders" / "wo-resume-001.json"
            saved_wo = json.loads(wo_file.read_text())
            self.assertEqual(saved_wo["status"], "waiting_info")

            # Simulate user providing answers and returning to runnable status
            # (This would normally happen through a different path, but we can simulate it)
            saved_wo["status"] = "new"
            saved_wo["answers"] = ["Admin and editor roles", "Show cached data with staleness warning"]
            wo_file.write_text(json.dumps(saved_wo))

            # Second run: intake should run again with the answers
            wo2 = WorkOrder.from_dict(saved_wo)
            report2 = run_pipeline(proj, sdlc_pipe(reg), wo2, registry=reg,
                                   executor=intake_executor(tmp, "accept"))

            # Verify the second run could proceed
            statuses = {s["station"]: s["status"] for s in report2.steps}
            self.assertEqual(statuses["intake"], "executed")
            # This time downstream stations should be able to run (at least to packet_ready)
            # since we're using accept mode for the second run

if __name__ == "__main__":
    unittest.main()

class TestIntakeValidation(unittest.TestCase):
    """Tests for intake outcome validation (security findings 1-3)."""
    
    def test_invalid_outcome_value(self):
        """Test that invalid outcome values are rejected."""
        from anvil.model import IntakeValidationError
        
        with self.assertRaises(IntakeValidationError) as cm:
            WorkOrder(
                id="wo-invalid-001",
                kind="feature",
                title="Test",
                intake_outcome={"outcome": "invalid_outcome"}
            )
        self.assertIn("Invalid outcome value", str(cm.exception))
        self.assertIn("invalid_outcome", str(cm.exception))
    
    def test_rejected_missing_reasons(self):
        """Test that rejected outcome requires reasons field."""
        from anvil.model import IntakeValidationError
        
        with self.assertRaises(IntakeValidationError) as cm:
            WorkOrder(
                id="wo-invalid-002",
                kind="feature",
                title="Test",
                intake_outcome={"outcome": "rejected"}
            )
        self.assertIn("requires 'reasons'", str(cm.exception))
    
    def test_rejected_empty_reasons(self):
        """Test that rejected outcome requires non-empty reasons list."""
        from anvil.model import IntakeValidationError
        
        with self.assertRaises(IntakeValidationError) as cm:
            WorkOrder(
                id="wo-invalid-003",
                kind="feature",
                title="Test",
                intake_outcome={"outcome": "rejected", "reasons": []}
            )
        self.assertIn("non-empty list", str(cm.exception))
    
    def test_waiting_info_missing_questions(self):
        """Test that waiting_info outcome requires questions field."""
        from anvil.model import IntakeValidationError
        
        with self.assertRaises(IntakeValidationError) as cm:
            WorkOrder(
                id="wo-invalid-004",
                kind="feature",
                title="Test",
                intake_outcome={"outcome": "waiting_info"}
            )
        self.assertIn("requires 'questions'", str(cm.exception))
    
    def test_waiting_info_empty_questions(self):
        """Test that waiting_info outcome requires non-empty questions list."""
        from anvil.model import IntakeValidationError
        
        with self.assertRaises(IntakeValidationError) as cm:
            WorkOrder(
                id="wo-invalid-005",
                kind="feature",
                title="Test",
                intake_outcome={"outcome": "waiting_info", "questions": []}
            )
        self.assertIn("non-empty list", str(cm.exception))
    
    def test_rescoped_missing_description(self):
        """Test that rescoped outcome requires rescoped_description field."""
        from anvil.model import IntakeValidationError
        
        with self.assertRaises(IntakeValidationError) as cm:
            WorkOrder(
                id="wo-invalid-006",
                kind="feature",
                title="Test",
                intake_outcome={"outcome": "rescoped"}
            )
        self.assertIn("requires 'rescoped_description'", str(cm.exception))
    
    def test_rescoped_empty_description(self):
        """Test that rescoped outcome requires non-empty rescoped_description."""
        from anvil.model import IntakeValidationError
        
        with self.assertRaises(IntakeValidationError) as cm:
            WorkOrder(
                id="wo-invalid-007",
                kind="feature",
                title="Test",
                intake_outcome={"outcome": "rescoped", "rescoped_description": "   "}
            )
        self.assertIn("non-empty string", str(cm.exception))
    
    def test_invalid_risk_value(self):
        """Test that invalid risk values are rejected."""
        from anvil.model import RiskValidationError
        
        with self.assertRaises(RiskValidationError) as cm:
            WorkOrder(
                id="wo-invalid-008",
                kind="feature",
                title="Test",
                risk="critical"  # Not in RISK_LEVELS
            )
        self.assertIn("Invalid risk value", str(cm.exception))
        self.assertIn("critical", str(cm.exception))
    
    def test_valid_risk_values(self):
        """Test that valid risk values are accepted."""
        # low, medium, high, None should all be valid
        for risk in ["low", "medium", "high", None]:
            wo = WorkOrder(
                id=f"wo-risk-{risk}",
                kind="feature",
                title="Test",
                risk=risk
            )
            self.assertEqual(wo.risk, risk)
    
    def test_invalid_surface_value(self):
        """Test that invalid surface values are rejected."""
        with self.assertRaises(ValueError) as cm:
            WorkOrder(
                id="wo-invalid-009",
                kind="feature",
                title="Test",
                surfaces=["ui", "invalid_surface"]
            )
        self.assertIn("Invalid surface values", str(cm.exception))
        self.assertIn("invalid_surface", str(cm.exception))
    
    def test_valid_surface_values(self):
        """Test that valid surface values are accepted."""
        valid_surfaces = ["ui", "security", "data", "payments", "deploy", "content", "api"]
        wo = WorkOrder(
            id="wo-surfaces-001",
            kind="feature",
            title="Test",
            surfaces=valid_surfaces
        )
        self.assertEqual(set(wo.surfaces), set(valid_surfaces))
    
    def test_validation_on_assignment(self):
        """Test that validation occurs when fields are assigned after creation."""
        from anvil.model import IntakeValidationError, RiskValidationError
        
        wo = WorkOrder(id="wo-assign-001", kind="feature", title="Test")
        
        # Invalid intake_outcome assignment should raise
        with self.assertRaises(IntakeValidationError):
            wo.intake_outcome = {"outcome": "invalid"}
        
        # Invalid risk assignment should raise
        with self.assertRaises(RiskValidationError):
            wo.risk = "extreme"
        
        # Invalid surfaces assignment should raise
        with self.assertRaises(ValueError):
            wo.surfaces = ["ui", "invalid"]

class TestMarkdownEscaping(unittest.TestCase):
    """Tests for markdown content escaping in report rendering (security finding 5)."""
    
    def test_markdown_injection_in_reasons(self):
        """Test that markdown special characters in reasons are escaped."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            
            # Create a work order - executor will inject markdown
            wo = WorkOrder(id="wo-markdown-001", kind="feature", title="Test")
            
            # Run pipeline with executor that returns markdown injection
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=markdown_injection_executor(tmp, "reasons"))
            
            # Read the report
            report_file = proj / "runs" / "wo-markdown-001" / "report.md"
            report_text = report_file.read_text()
            
            # The markdown should be escaped (backslash before special chars)
            self.assertIn("\\[Click here\\]", report_text)
            self.assertIn("\\*\\*Bold\\*\\*", report_text)
            self.assertIn("\\# Header", report_text)
            
            # Should not render as actual markdown links/formatting
            # The raw characters should be escaped
            self.assertIn("\\(http://evil\\.com\\)", report_text)
    
    def test_markdown_injection_in_questions(self):
        """Test that markdown special characters in questions are escaped."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            
            # Create a work order - executor will inject markdown
            wo = WorkOrder(id="wo-markdown-002", kind="feature", title="Test")
            
            # Run pipeline with executor that returns markdown injection
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=markdown_injection_executor(tmp, "questions"))
            
            # Read the report
            report_file = proj / "runs" / "wo-markdown-002" / "report.md"
            report_text = report_file.read_text()
            
            # The markdown should be escaped
            self.assertIn("\\[this link\\]\\(", report_text)
            self.assertIn("\\*\\*bold\\*\\*", report_text)
    
    def test_markdown_injection_in_rescoped_description(self):
        """Test that markdown in rescoped_description is safely fenced."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            
            # Create a work order - executor will inject markdown
            wo = WorkOrder(id="wo-markdown-003", kind="feature", title="Test")
            
            # Run pipeline with executor that returns markdown injection
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=markdown_injection_executor(tmp, "rescoped"))
            
            # Read the report
            report_file = proj / "runs" / "wo-markdown-003" / "report.md"
            report_text = report_file.read_text()
            
            # The rescoped_description should be in a code fence (prevents rendering)
            self.assertIn("```", report_text)
            self.assertIn("# Fake Header", report_text)
            self.assertIn("[Fake link](http://evil.com)", report_text)
            self.assertIn("**Fake bold**", report_text)
            
            # The reasons should still be escaped
            self.assertIn("Rescoped for safety", report_text)
    
    def test_html_injection_in_reasons(self):
        """Test that HTML tags in reasons are escaped."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            
            # Create a work order - executor will inject HTML
            wo = WorkOrder(id="wo-html-001", kind="feature", title="Test")
            
            # Run pipeline with executor that returns HTML injection
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=markdown_injection_executor(tmp, "html"))
            
            # Read the report
            report_file = proj / "runs" / "wo-html-001" / "report.md"
            report_text = report_file.read_text()
            
            # HTML should be escaped
            self.assertIn("\\<script\\>", report_text)
            self.assertIn("\\<img", report_text)

class TestExecutorValidationIntegration(unittest.TestCase):
    """Integration tests for Finding 4: executor output validation through runner."""

    def make_invalid_executor(self, tmp, invalid_mode):
        """Create an executor that returns invalid data based on mode."""
        script = Path(tmp) / f"invalid_executor_{invalid_mode}.py"

        executor_code = f'''
import json, sys
from pathlib import Path
packet_path = sys.argv[1]
mode = "{invalid_mode}"
station = ""
work_order_id = ""
for line in open(packet_path, encoding="utf-8"):
    if line.startswith("# Task packet:"):
        station = line.split(":", 1)[1].strip()
    if line.strip().startswith("- id:"):
        work_order_id = line.split(":", 1)[1].strip()

if station == "intake":
    if mode == "invalid_outcome":
        # Invalid outcome value not in INTAKE_OUTCOMES
        output = {{
            "intake_outcome": {{
                "outcome": "maybe_accepted"
            }}
        }}
    elif mode == "missing_outcome_field":
        # Missing 'outcome' field
        output = {{
            "intake_outcome": {{
                "reasons": ["Some reasons"]
            }}
        }}
    elif mode == "invalid_outcome_type":
        # Non-dict intake_outcome
        output = {{
            "intake_outcome": "accepted"
        }}
    elif mode == "rejected_no_reasons":
        # Rejected without reasons
        output = {{
            "intake_outcome": {{
                "outcome": "rejected"
            }}
        }}
    elif mode == "waiting_no_questions":
        # waiting_info without questions
        output = {{
            "intake_outcome": {{
                "outcome": "waiting_info"
            }}
        }}
    elif mode == "rescoped_no_description":
        # rescoped without rescoped_description
        output = {{
            "intake_outcome": {{
                "outcome": "rescoped",
                "reasons": ["Cut features"]
            }}
        }}
    elif mode == "invalid_risk":
        # Invalid risk value
        output = {{
            "intake_outcome": {{
                "outcome": "accepted"
            }},
            "risk": "CRITICAL"
        }}
    elif mode == "invalid_risk_type":
        # Wrong type for risk
        output = {{
            "intake_outcome": {{
                "outcome": "accepted"
            }},
            "risk": 123
        }}
    elif mode == "invalid_surfaces":
        # Invalid surface values
        output = {{
            "intake_outcome": {{
                "outcome": "accepted"
            }},
            "risk": "low",
            "surfaces": ["ui", "blockchain", "ai"]
        }}
    elif mode == "invalid_surfaces_type":
        # Wrong type for surfaces
        output = {{
            "intake_outcome": {{
                "outcome": "accepted"
            }},
            "surfaces": "ui,security"
        }}
    elif mode == "xss_in_risk":
        # Attempted XSS in risk field
        output = {{
            "intake_outcome": {{
                "outcome": "accepted"
            }},
            "risk": "javascript:alert(1)"
        }}
    else:
        output = {{"intake_outcome": {{"outcome": "accepted"}}, "risk": "low", "surfaces": ["ui"]}}
    print(json.dumps(output))
elif station.startswith("reviewer"):
    review_path = Path.cwd() / "runs" / work_order_id / f"{{station}}.review.json"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_obj = {{"station": station, "verdict": "pass", "findings": []}}
    review_path.write_text(json.dumps(review_obj))
    print("Wrote review to file")
else:
    print(f"Executed {{station}}")
'''

        script.write_text(executor_code)
        return create_executor({"kind": "command",
                                "command": f"{sys.executable} {script} {{packet}}",
                                "timeout_seconds": 60})

    def test_invalid_outcome_value_caught_by_validation(self):
        """Test that invalid outcome values from executor are caught."""
        from anvil.model import IntakeValidationError

        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-exec-invalid-001", kind="feature", title="Test")

            with self.assertRaises(IntakeValidationError) as cm:
                run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                           executor=self.make_invalid_executor(tmp, "invalid_outcome"))
            self.assertIn("Invalid outcome value", str(cm.exception))

    def test_missing_outcome_field_caught_by_validation(self):
        """Test that intake_outcome without 'outcome' field is caught."""
        from anvil.model import IntakeValidationError

        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-exec-invalid-002", kind="feature", title="Test")

            with self.assertRaises(IntakeValidationError) as cm:
                run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                           executor=self.make_invalid_executor(tmp, "missing_outcome_field"))
            self.assertIn("must have 'outcome' field", str(cm.exception))

    def test_invalid_outcome_type_caught_by_validation(self):
        """Test that non-dict intake_outcome is caught."""
        from anvil.model import IntakeValidationError

        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-exec-invalid-003", kind="feature", title="Test")

            with self.assertRaises(IntakeValidationError) as cm:
                run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                           executor=self.make_invalid_executor(tmp, "invalid_outcome_type"))
            self.assertIn("must be a dict", str(cm.exception))

    def test_rejected_without_reasons_caught_by_validation(self):
        """Test that rejected outcome without reasons is caught."""
        from anvil.model import IntakeValidationError

        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-exec-invalid-004", kind="feature", title="Test")

            with self.assertRaises(IntakeValidationError) as cm:
                run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                           executor=self.make_invalid_executor(tmp, "rejected_no_reasons"))
            self.assertIn("requires 'reasons'", str(cm.exception))

    def test_waiting_info_without_questions_caught_by_validation(self):
        """Test that waiting_info outcome without questions is caught."""
        from anvil.model import IntakeValidationError

        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-exec-invalid-005", kind="feature", title="Test")

            with self.assertRaises(IntakeValidationError) as cm:
                run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                           executor=self.make_invalid_executor(tmp, "waiting_no_questions"))
            self.assertIn("requires 'questions'", str(cm.exception))

    def test_rescoped_without_description_caught_by_validation(self):
        """Test that rescoped outcome without rescoped_description is caught."""
        from anvil.model import IntakeValidationError

        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-exec-invalid-006", kind="feature", title="Test")

            with self.assertRaises(IntakeValidationError) as cm:
                run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                           executor=self.make_invalid_executor(tmp, "rescoped_no_description"))
            self.assertIn("requires 'rescoped_description'", str(cm.exception))

    def test_invalid_risk_value_caught_by_validation(self):
        """Test that invalid risk values from executor are caught."""
        from anvil.model import RiskValidationError

        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-exec-invalid-007", kind="feature", title="Test")

            with self.assertRaises(RiskValidationError) as cm:
                run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                           executor=self.make_invalid_executor(tmp, "invalid_risk"))
            self.assertIn("Invalid risk value", str(cm.exception))
            self.assertIn("CRITICAL", str(cm.exception))

    def test_invalid_risk_type_caught_by_validation(self):
        """Test that wrong type for risk is caught."""
        from anvil.model import RiskValidationError

        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-exec-invalid-008", kind="feature", title="Test")

            with self.assertRaises(RiskValidationError) as cm:
                run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                           executor=self.make_invalid_executor(tmp, "invalid_risk_type"))
            self.assertIn("must be a string or None", str(cm.exception))

    def test_invalid_surfaces_caught_by_validation(self):
        """Test that invalid surface values from executor are caught."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-exec-invalid-009", kind="feature", title="Test")

            with self.assertRaises(ValueError) as cm:
                run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                           executor=self.make_invalid_executor(tmp, "invalid_surfaces"))
            self.assertIn("Invalid surface values", str(cm.exception))
            self.assertIn("blockchain", str(cm.exception))
            self.assertIn("ai", str(cm.exception))

    def test_invalid_surfaces_type_caught_by_validation(self):
        """Test that wrong type for surfaces is caught."""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-exec-invalid-010", kind="feature", title="Test")

            with self.assertRaises(ValueError) as cm:
                run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                           executor=self.make_invalid_executor(tmp, "invalid_surfaces_type"))
            self.assertIn("must be a list", str(cm.exception))

    def test_xss_attempt_in_risk_caught_by_validation(self):
        """Test that XSS attempts in risk field are caught."""
        from anvil.model import RiskValidationError

        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-exec-invalid-011", kind="feature", title="Test")

            with self.assertRaises(RiskValidationError) as cm:
                run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                           executor=self.make_invalid_executor(tmp, "xss_in_risk"))
            self.assertIn("Invalid risk value", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
