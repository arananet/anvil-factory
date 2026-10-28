import json, tempfile, threading, unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
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

FAKE_EXECUTOR = '''
import json, sys
packet_path = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "pass"
station = ""
for line in open(packet_path, encoding="utf-8"):
    if line.startswith("# Task packet:"):
        station = line.split(":", 1)[1].strip()
        break
if mode == "boom":
    print("executor exploded", file=sys.stderr)
    sys.exit(3)
if station.startswith("reviewer"):
    verdict = "pass" if mode == "pass" else "fail"
    print(json.dumps({"station": station, "verdict": verdict,
                      "findings": ["Fake executor review for " + station]}))
elif mode == "garbage" and station.startswith("reviewer"):
    print("no json here at all")
else:
    print("Executed " + station)
'''

def make_project(tmp):
    proj = Path(tmp) / "proj"
    init_project(proj, "Demo")
    scaffold_spec(proj, "demo-feature", "Demo Feature")
    return proj

def command_executor(tmp, mode="pass"):
    script = Path(tmp) / "fake_executor.py"
    script.write_text(FAKE_EXECUTOR)
    return create_executor({"kind": "command",
                            "command": f"{sys.executable} {script} {{packet}} {mode}",
                            "timeout_seconds": 60})

def hotfix_pipe(reg):
    return load_pipeline(ROOT / "pipelines" / "hotfix.json", known_stations=set(reg.ids()))

def sdlc_pipe(reg):
    return load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))

class TestRunScopedApprover(unittest.TestCase):
    def test_packets_only_run_is_no_reviews_despite_passing_project_reviews_s10(self):
        """factory-pipeline-engine S10: approver aggregates only reviews produced during the run"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            base = proj / "reviews" / "demo-feature"; base.mkdir(parents=True)
            for s in ["reviewer-spec", "reviewer-security", "reviewer-tests", "reviewer-architecture"]:
                (base / f"{s}.json").write_text(json.dumps({"station": s, "verdict": "pass", "findings": ["standing record"]}))
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-scope-001", kind="feature", title="Scoped")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg)
            self.assertEqual(report.verdict, "no_reviews")
            statuses = {s["station"]: s["status"] for s in report.steps}
            self.assertEqual(statuses["reviewer-spec"], "packet_ready")

    def test_executor_pass_review_approves(self):
        """Part A: a run whose reviewer executor returns pass reviews is approved"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-scope-002", kind="bug", title="Fix it")
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))
            self.assertEqual(report.verdict, "approved")
            self.assertFalse(report.human_required)

class TestCommandExecution(unittest.TestCase):
    def test_executed_step_and_output_artifact_s1(self):
        """agent-execution S1: executed packet, output artifact, envelope names the executor"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-exec-001", kind="bug", title="Run it")
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))
            run_dir = proj / "runs" / "wo-exec-001"
            statuses = {s["station"]: s["status"] for s in report.steps}
            self.assertEqual(statuses["builder"], "executed")
            self.assertEqual(statuses["reviewer-spec"], "executed")
            out = run_dir / "builder.output.md"
            self.assertTrue(out.exists())
            self.assertIn("Executed builder", out.read_text())
            env = json.loads((run_dir / "envelopes" / "builder.envelope.json").read_text())
            self.assertEqual(env["status"], "executed")
            self.assertEqual(env["executor"], "command")
            self.assertIsNone(report.steps[0].get("cost"))

    def test_garbage_review_output_records_parse_failure_s3(self):
        """agent-execution S3: unparseable reviewer output records review_parse_failed and no review counts"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            script = Path(tmp) / "garbage.py"
            script.write_text('import sys\nprint("plain text, no review json")\n')
            executor = create_executor({"kind": "command",
                                        "command": f"{sys.executable} {script} {{packet}}",
                                        "timeout_seconds": 60})
            wo = WorkOrder(id="wo-exec-002", kind="bug", title="Garbage")
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg, executor=executor)
            self.assertEqual(report.verdict, "no_reviews")
            env = json.loads((proj / "runs" / "wo-exec-002" / "envelopes" / "reviewer-spec.envelope.json").read_text())
            self.assertTrue(env.get("review_parse_failed"))

    def test_failing_executor_marks_step_failed_s2(self):
        """agent-execution S2: a failing executor fails the step with the error recorded"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-exec-003", kind="bug", title="Boom")
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "boom"))
            statuses = {s["station"]: s["status"] for s in report.steps}
            self.assertEqual(statuses["builder"], "failed")
            builder = [s for s in report.steps if s["station"] == "builder"][0]
            self.assertIn("executor exploded", builder["detail"])
            env = json.loads((proj / "runs" / "wo-exec-003" / "envelopes" / "builder.envelope.json").read_text())
            self.assertEqual(env["status"], "failed")
            self.assertIn("error", env)

    def test_unknown_executor_kind_marks_step_failed_s2(self):
        """agent-execution S2: an unknown executor kind fails openly, never packet_ready"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            executor = create_executor({"kind": "telepathy"})
            wo = WorkOrder(id="wo-exec-004", kind="bug", title="Unknown")
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg, executor=executor)
            statuses = {s["station"]: s["status"] for s in report.steps}
            self.assertEqual(statuses["builder"], "failed")
            self.assertNotEqual(statuses["builder"], "packet_ready")

class TestHttpExecution(unittest.TestCase):
    def test_http_executor_records_usage_and_cost_stays_null_s4(self):
        """agent-execution S4: OpenAI style response, usage tokens recorded, cost null"""
        captured = {}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                captured["body"] = self.rfile.read(length).decode()
                captured["auth"] = self.headers.get("Authorization")
                payload = {"choices": [{"message": {"content": json.dumps(
                    {"station": "reviewer-spec", "verdict": "pass", "findings": ["stub review"]})}}],
                    "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18}}
                raw = json.dumps(payload).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            import os
            os.environ["ANVIL_TEST_STUB_KEY"] = "stub-key-value"
            with tempfile.TemporaryDirectory() as tmp:
                proj = make_project(tmp)
                reg = load_registry(ROOT / "stations")
                executor = create_executor({"kind": "http",
                                            "endpoint": f"http://127.0.0.1:{server.server_port}/v1/chat/completions",
                                            "model": "stub-model", "api_key_env": "ANVIL_TEST_STUB_KEY",
                                            "timeout_seconds": 30})
                wo = WorkOrder(id="wo-exec-005", kind="bug", title="HTTP run")
                report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg, executor=executor)
                self.assertEqual(captured.get("auth"), "Bearer stub-key-value")
                reviewer = [s for s in report.steps if s["station"] == "reviewer-spec"][0]
                self.assertEqual(reviewer["status"], "executed")
                self.assertEqual(reviewer["usage"]["total_tokens"], 18)
                self.assertIsNone(reviewer["cost"])
                env = json.loads((proj / "runs" / "wo-exec-005" / "envelopes" / "reviewer-spec.envelope.json").read_text())
                self.assertEqual(env["tokens"]["total_tokens"], 18)
                self.assertEqual(env["executor"], "http:stub-model")
        finally:
            server.shutdown()
            import os
            os.environ.pop("ANVIL_TEST_STUB_KEY", None)

DEPLOY_SCRIPT = '''
import os, sys
from pathlib import Path
target = Path("deployed-target")
target.mkdir(exist_ok=True)
(target / "marker.txt").write_text(os.environ.get("ANVIL_WORK_ORDER_ID", ""))
print("deployed " + os.environ.get("ANVIL_WORK_ORDER_ID", ""))
'''

def deploy_cfg(tmp, verify):
    script = Path(tmp) / "deploy.py"
    script.write_text(DEPLOY_SCRIPT)
    return {"command": f"{sys.executable} {script}", "verify": verify, "timeout_seconds": 60}

class TestDeployVerify(unittest.TestCase):
    def test_deployed_verified_s5_s6(self):
        """agent-execution S5 and S6: approved run deploys, verification passes, deployed_verified"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-deploy-001", kind="bug", title="Ship it")
            verify = [f"{sys.executable} -c \"from pathlib import Path; assert Path('deployed-target/marker.txt').read_text() == 'wo-deploy-001'\""]
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"),
                                  deploy_cfg=deploy_cfg(tmp, verify))
            self.assertEqual(report.deployment_status, "deployed_verified")
            statuses = [(s["station"], s["status"]) for s in report.steps]
            self.assertIn(("deployer", "executed"), statuses)
            self.assertIn(("verifier", "executed"), statuses)
            out = proj / "runs" / "wo-deploy-001" / "deployer.output.md"
            self.assertIn("deployed wo-deploy-001", out.read_text())
            self.assertEqual(report.verify_results[0]["status"], "pass")
            swim = (proj / "runs" / "wo-deploy-001" / "swimlane.md").read_text()
            self.assertIn("deployed_verified", swim)

    def test_verify_failure_is_deployed_unverified_s6(self):
        """agent-execution S6: failing verification means deployed_unverified, never success"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-deploy-002", kind="bug", title="Ship it")
            verify = [f"{sys.executable} -c \"raise SystemExit('post deploy check failed')\""]
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"),
                                  deploy_cfg=deploy_cfg(tmp, verify))
            self.assertEqual(report.deployment_status, "deployed_unverified")
            statuses = [(s["station"], s["status"]) for s in report.steps]
            self.assertIn(("verifier", "failed"), statuses)
            self.assertTrue((proj / "runs" / "wo-deploy-002" / "verify-findings.md").exists())
            self.assertEqual(report.verify_results[0]["status"], "fail")

    def test_deploy_command_failure_is_deploy_failed_s6(self):
        """agent-execution S6: a failing deploy command sets deploy_failed and skips verification"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-deploy-003", kind="bug", title="Ship it")
            cfg = {"command": f"{sys.executable} -c \"raise SystemExit(2)\"",
                   "verify": [f"{sys.executable} -c \"pass\""], "timeout_seconds": 60}
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"), deploy_cfg=cfg)
            self.assertEqual(report.deployment_status, "deploy_failed")
            self.assertEqual(report.verify_results, [])

    def test_no_deploy_when_not_approved_s7(self):
        """agent-execution S7: failing reviews mean no deploy command runs"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-deploy-004", kind="bug", title="Ship it")
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "fail"),
                                  deploy_cfg=deploy_cfg(tmp, []))
            self.assertIsNone(report.deployment_status)
            self.assertFalse((proj / "deployed-target").exists())
            statuses = {s["station"]: s["status"] for s in report.steps}
            self.assertEqual(statuses["deployer"], "packet_ready")

    def test_no_deploy_when_human_gate_blocks_s7(self):
        """agent-execution S7: a risk hint blocks the deploy even when reviews pass"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-deploy-005", kind="bug", title="Payments fix", risk_hints=["payments"])
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"),
                                  deploy_cfg=deploy_cfg(tmp, []))
            self.assertEqual(report.verdict, "approved")
            self.assertTrue(report.human_required)
            self.assertIsNone(report.deployment_status)
            self.assertFalse((proj / "deployed-target").exists())

    def test_no_deploy_without_execute_mode_s7(self):
        """agent-execution S7: a deploy config alone never deploys; deployer stays a packet"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-deploy-006", kind="bug", title="Ship it")
            report = run_pipeline(proj, hotfix_pipe(reg), wo, registry=reg,
                                  deploy_cfg=deploy_cfg(tmp, []))
            self.assertIsNone(report.deployment_status)
            statuses = {s["station"]: s["status"] for s in report.steps}
            self.assertEqual(statuses["deployer"], "packet_ready")
            self.assertFalse((proj / "deployed-target").exists())

if __name__ == "__main__":
    unittest.main()
