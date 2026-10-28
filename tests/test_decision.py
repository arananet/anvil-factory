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
from anvil.approver import RISK_SCAN_ORDER
from anvil.gates import RISK_HINTS

ROOT = Path(__file__).resolve().parent.parent

FAKE_EXECUTOR = '''
import json, sys
packet_path = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "pass"
station = ""
for line in open(packet_path, encoding="utf-8"):
    if line.startswith("# Task packet:"):
        station = line.split(":", 1)[1].strip()
        break
if station.startswith("reviewer"):
    if mode == "fail":
        verdict = "fail"
    elif mode == "changes" and station == "reviewer-spec":
        verdict = "changes_requested"
    else:
        verdict = "pass"
    print(json.dumps({"station": station, "verdict": verdict,
                      "findings": ["Fake executor review for " + station]}))
else:
    print("Executed " + station)
'''

NO_HUMAN_RULE = ("Verdict approved and no risk hints matched (scanned: auth, payments, "
                 "data-deletion, production-deploy, secrets, publishing), so no human is required.")
NO_REVIEWS_RULE = ("No reviews were produced in this run, so the verdict is no_reviews; "
                   "standing project reviews are never counted.")

def make_project(tmp):
    proj = Path(tmp) / "proj"
    init_project(proj, "Demo")
    scaffold_spec(proj, "demo-feature", "Demo Feature")
    return proj

def hotfix_pipe(reg):
    return load_pipeline(ROOT / "pipelines" / "hotfix.json", known_stations=set(reg.ids()))

def command_executor(tmp, mode="pass"):
    script = Path(tmp) / "fake_executor.py"
    script.write_text(FAKE_EXECUTOR)
    return create_executor({"kind": "command",
                            "command": f"{sys.executable} {script} {{packet}} {mode}",
                            "timeout_seconds": 60})

def read_report(proj, wo_id):
    return json.loads((Path(proj) / "runs" / wo_id / "report.json").read_text())

class TestScanOrderSync(unittest.TestCase):
    def test_scan_order_covers_exactly_the_gate_risk_hints(self):
        """The explanation scan order and the gate's RISK_HINTS set must never drift apart"""
        self.assertEqual(set(RISK_SCAN_ORDER), RISK_HINTS)
        self.assertEqual(len(RISK_SCAN_ORDER), len(RISK_HINTS))

class TestDecisionRecorded(unittest.TestCase):
    def test_approved_run_decision_sentences_s11(self):
        """factory-pipeline-engine S11: pass reviews, no hints, decision explains approval and no human"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-dec-001", kind="bug", title="Decide well")
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))
            self.assertEqual(report.verdict, "approved")
            self.assertFalse(report.human_required)
            decision = report.decision
            self.assertEqual(decision["approver"]["reviews_counted"],
                             [{"station": "reviewer-spec", "verdict": "pass"},
                              {"station": "reviewer-security", "verdict": "pass"}])
            self.assertEqual(decision["approver"]["reviews_expected"],
                             ["reviewer-spec", "reviewer-security"])
            self.assertEqual(decision["approver"]["rule"], "All counted reviews passed.")
            self.assertEqual(decision["human_gate"],
                             {"required": False, "rule": NO_HUMAN_RULE, "hints_matched": []})
            saved = read_report(proj, "wo-dec-001")
            self.assertEqual(saved["risk_hints"], [])
            self.assertEqual(saved["decision"], decision)
            swim = (proj / "runs" / "wo-dec-001" / "swimlane.md").read_text()
            self.assertIn("## Decision", swim)
            self.assertIn("All counted reviews passed.", swim)
            self.assertIn(NO_HUMAN_RULE, swim)

    def test_packet_only_run_decision_sentences_s11(self):
        """factory-pipeline-engine S11: no reviews in the run, verdict no_reviews, human required by verdict"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-dec-002", kind="bug", title="Packets only")
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg)
            self.assertEqual(report.verdict, "no_reviews")
            self.assertTrue(report.human_required)
            decision = report.decision
            self.assertEqual(decision["approver"]["reviews_counted"], [])
            self.assertEqual(decision["approver"]["reviews_expected"],
                             ["reviewer-spec", "reviewer-security"])
            self.assertEqual(decision["approver"]["rule"], NO_REVIEWS_RULE)
            self.assertEqual(decision["human_gate"]["rule"],
                             "Verdict is no_reviews, not approved, so a human is required.")
            self.assertTrue(decision["human_gate"]["required"])
            self.assertEqual(decision["human_gate"]["hints_matched"], [])
            swim = (proj / "runs" / "wo-dec-002" / "swimlane.md").read_text()
            self.assertIn(NO_REVIEWS_RULE, swim)
            self.assertIn("Verdict is no_reviews, not approved, so a human is required.", swim)

    def test_approved_with_payments_hint_decision_s11(self):
        """factory-pipeline-engine S11: approved verdict with a payments hint, human required by the risk path"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-dec-003", kind="bug", title="Payments fix", risk_hints=["payments"])
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))
            self.assertEqual(report.verdict, "approved")
            self.assertTrue(report.human_required)
            decision = report.decision
            self.assertEqual(decision["approver"]["rule"], "All counted reviews passed.")
            self.assertEqual(decision["human_gate"]["rule"],
                             "Verdict approved, but the work order carries the risk hint 'payments', so a human is required.")
            self.assertEqual(decision["human_gate"]["hints_matched"], ["payments"])
            saved = read_report(proj, "wo-dec-003")
            self.assertEqual(saved["risk_hints"], ["payments"])
            self.assertEqual(saved["decision"]["human_gate"]["hints_matched"], ["payments"])

    def test_rejected_run_names_failing_reviewer_s11(self):
        """factory-pipeline-engine S11: a fail review rejects the run and the rule names the reviewer"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-dec-004", kind="bug", title="Broken fix")
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "fail"))
            self.assertEqual(report.verdict, "rejected")
            self.assertTrue(report.human_required)
            rule = report.decision["approver"]["rule"]
            self.assertEqual(rule, "Reviewers reviewer-spec, reviewer-security returned fail.")
            self.assertIn("reviewer-spec", rule)
            self.assertEqual(report.decision["human_gate"]["rule"],
                             "Verdict is rejected, not approved, so a human is required.")

    def test_changes_requested_names_reviewer_s11(self):
        """factory-pipeline-engine S11: a changes_requested review is named in the approver rule"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-dec-005", kind="bug", title="Needs changes")
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "changes"))
            self.assertEqual(report.verdict, "changes_requested")
            self.assertEqual(report.decision["approver"]["rule"],
                             "Reviewer reviewer-spec requested changes.")
            self.assertEqual(report.decision["approver"]["reviews_counted"],
                             [{"station": "reviewer-spec", "verdict": "changes_requested"},
                              {"station": "reviewer-security", "verdict": "pass"}])

if __name__ == "__main__":
    unittest.main()
