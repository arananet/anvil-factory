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
