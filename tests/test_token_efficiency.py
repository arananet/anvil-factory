"""Token-efficiency scenarios: runtime evidence, spending controls and pages."""
import json
import os
import shlex
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from anvil.executor import CommandExecutor, ExecutorError
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.runner import RunReport, run_pipeline
from anvil.scaffold import init_project
from anvil.stations import load_registry
from anvil.statuspage import generate_status_page, render_status_page
from anvil.telemetry import normalize_usage, parse_runtime_output, UsageRecorder, summarize_steps, public_report

ROOT = Path(__file__).resolve().parent.parent


class RuntimeEvidenceTests(unittest.TestCase):
    def test_public_export_omits_prompts_paths_and_environment_s3(self):
        raw = {"work_order_id": "wo-safe", "description": "private prompt", "steps": [{
            "station": "builder", "status": "executed", "artifacts": ["/private/path"],
            "executor": {"kind": "command", "detail": "private command"},
            "environment": {"TOKEN": "private credential"},
            "usage": {"input_tokens": 10, "output_tokens": 2},
            "attempts": [{"status": "succeeded", "prompt": "private prompt",
                          "usage": {"input_tokens": 10, "output_tokens": 2}}]}]}
        safe = json.dumps(public_report(raw))
        for text in ("private prompt", "/private/path", "private command", "private credential"):
            self.assertNotIn(text, safe)
        self.assertEqual(public_report(raw)["token_usage"]["total_tokens"], 12)

    def test_partial_codex_usage_keeps_partial_coverage_s1(self):
        with tempfile.TemporaryDirectory() as tmp:
            recorder = UsageRecorder(Path(tmp) / "usage.json")
            events = [{"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 2}},
                      {"type": "turn.failed"}]
            recorder.record("\n".join(json.dumps(e) for e in events), "codex", "failed", 1, "test")
            data = recorder.summary()
            self.assertFalse(data["complete"])
            self.assertEqual(data["usage"]["total_tokens"], 12)
            self.assertFalse(summarize_steps([{"station": "builder", "attempts": data["attempts"]}])["complete"])

    def test_claude_cache_tokens_count_once_s1(self):
        result = parse_runtime_output(json.dumps({
            "type": "result", "result": "done", "num_turns": 3,
            "usage": {"input_tokens": 100, "output_tokens": 20,
                      "cache_read_input_tokens": 400, "cache_creation_input_tokens": 50},
            "total_cost_usd": 0.03,
        }), "claude")
        self.assertEqual(result["output"], "done")
        self.assertEqual(result["usage"]["input_tokens"], 550)
        self.assertEqual(result["usage"]["total_tokens"], 570)
        self.assertEqual(result["usage"]["cached_input_tokens"], 400)
        self.assertEqual(result["usage"]["cache_creation_input_tokens"], 50)

    def test_codex_events_use_turn_usage_not_message_usage_s1(self):
        events = [
            {"type": "item.completed", "item": {"type": "agent_message", "text": "done"}},
            {"type": "turn.completed", "usage": {
                "input_tokens": 1000, "cached_input_tokens": 800,
                "output_tokens": 100, "reasoning_output_tokens": 70}},
        ]
        result = parse_runtime_output("\n".join(json.dumps(e) for e in events), "codex")
        self.assertEqual(result["output"], "done")
        self.assertEqual(result["usage"]["total_tokens"], 1100)
        self.assertEqual(result["usage"]["reasoning_tokens"], 70)

    def test_invalid_or_missing_usage_is_unknown_s1(self):
        for usage in (None, {}, {"input_tokens": -1, "output_tokens": 2},
                      {"cost": 2}, {"input_tokens": 2},
                      {"input_tokens": True, "output_tokens": 1}):
            with self.subTest(usage=usage):
                self.assertIsNone(normalize_usage(usage))
        self.assertEqual(normalize_usage({"input_tokens": 0, "output_tokens": 0})["total_tokens"], 0)

    def test_attempts_include_correction_failure_and_unknown_s2(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "usage.json"
            recorder = UsageRecorder(target)
            for status, usage in [("failed", {"input_tokens": 12, "output_tokens": 3}),
                                  ("succeeded", {"input_tokens": 20, "output_tokens": 5}),
                                  ("timed_out", None)]:
                recorder.record(json.dumps({"type": "result", "result": "x", "usage": usage}),
                                "claude", status, 10, "test-model")
            data = json.loads(target.read_text())
            self.assertEqual(data["usage"]["total_tokens"], 40)
            self.assertEqual(len(data["attempts"]), 3)
            self.assertEqual(data["unmeasured_attempts"], 1)
            self.assertFalse(data["complete"])
            self.assertNotIn("result", data["attempts"][0])

    def test_executor_reads_fresh_evidence_and_preserves_failure_s3(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet = root / "p.md"
            packet.write_text("packet")
            out = root / "builder.output.md"
            script = root / "runtime.py"
            script.write_text("import json,os\nfrom pathlib import Path\n"
                              "Path(os.environ['ANVIL_USAGE_PATH']).write_text(json.dumps("
                              "{'schema':'anvil/usage@1','usage':{'input_tokens':10,'output_tokens':2},"
                              "'attempts':[{'status':'failed','usage':{'input_tokens':10,'output_tokens':2}}]}))\n"
                              "raise SystemExit(3)\n")
            import shlex
            executor = CommandExecutor({"command": shlex.quote(sys.executable) + " " + shlex.quote(str(script))})
            with self.assertRaises(ExecutorError) as caught:
                executor.execute("p", "builder", packet_path=packet, output_path=out)
            self.assertEqual(caught.exception.result["usage"]["total_tokens"], 12)
            # An unrelated subsequent invocation must not inherit those 12 tokens.
            executor = CommandExecutor({"command": shlex.quote(sys.executable) + " -c 'print(1)'"})
            result = executor.execute("p", "builder", packet_path=packet, output_path=out)
            self.assertIsNone(result["usage"])

    def test_partial_summary_counts_failed_attempts_s2_s3(self):
        steps = [
            {"station": "builder", "status": "executed", "executor": "command",
             "usage": {"input_tokens": 10, "output_tokens": 2}},
            {"station": "reviewer-tests", "status": "failed", "executor": "command"},
            {"station": "checks-gate", "status": "completed"},
        ]
        totals = summarize_steps(steps)
        self.assertEqual(totals["total_tokens"], 12)
        self.assertEqual(totals["measured_calls"], 1)
        self.assertEqual(totals["unmeasured_calls"], 1)
        self.assertFalse(totals["complete"])
        self.assertIsNone(summarize_steps(steps[1:])["total_tokens"])


class BudgetAndPageTests(unittest.TestCase):
    def test_call_count_and_required_usage_prevent_next_call_s4(self):
        for limits in ({"max_agent_calls": 1}, {"require_usage": True}):
            with self.subTest(limits=limits), tempfile.TemporaryDirectory() as tmp:
                project = init_project(Path(tmp) / "project", "Usage policy")
                config = json.loads((project / "anvil.yaml").read_text())
                config["efficiency"] = limits
                (project / "anvil.yaml").write_text(json.dumps(config))
                path = Path(tmp) / "pipeline.json"
                path.write_text(json.dumps({"name": "policy", "stages": [
                    {"station": "builder"}, {"station": "reviewer-tests"}]}))
                class Runtime:
                    name = "fake"
                    def __init__(self): self.calls = []
                    def execute(self, text, station_id, **kwargs):
                        self.calls.append(station_id)
                        return {"output": "done", "usage": None}
                runtime = Runtime()
                result = run_pipeline(project, load_pipeline(path), WorkOrder(id="wo-policy", kind="feature", title="Policy"), executor=runtime)
                self.assertEqual(runtime.calls, ["builder"])
                self.assertEqual(result.verdict, "budget_exceeded")
                self.assertIsNone(result.to_dict()["token_usage"]["total_tokens"])

    def test_rerun_preserves_consumption_in_history_s3(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = init_project(Path(tmp) / "project", "History demo")
            path = Path(tmp) / "pipeline.json"
            path.write_text(json.dumps({"name": "history", "stages": [{"station": "builder"}]}))
            class Runtime:
                name = "fake"
                def execute(self, text, station_id, **kwargs):
                    return {"output": "done", "usage": {"input_tokens": 10, "output_tokens": 2}}
            for _ in range(2):
                run_pipeline(project, load_pipeline(path), WorkOrder(id="wo-same", kind="feature", title="History"), executor=Runtime())
            _, summary = render_status_page(project)
            self.assertEqual(summary["token_usage"]["total_tokens"], 24)
            self.assertEqual(summary["token_usage"]["calls"], 2)
            self.assertEqual(summary["runs"], 2)

    def test_packet_limit_blocks_call_without_dropping_spec_s5(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = init_project(Path(tmp) / "project", "Packet limit")
            config = json.loads((project / "anvil.yaml").read_text())
            config["efficiency"]["max_packet_tokens"] = 10
            (project / "anvil.yaml").write_text(json.dumps(config))
            path = Path(tmp) / "pipeline.json"
            path.write_text(json.dumps({"name": "packet", "stages": [{"station": "spec-writer"}]}))
            class Runtime:
                name = "unused"
                def execute(self, *args, **kwargs):
                    raise AssertionError("Oversized packet must not reach the model")
            result = run_pipeline(project, load_pipeline(path), WorkOrder(id="wo-large", kind="feature", title="Large"), executor=Runtime())
            self.assertEqual(result.verdict, "budget_exceeded")
            self.assertEqual(result.to_dict()["token_usage"]["calls"], 0)

    def test_backend_packet_omits_interface_context_s5(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = init_project(Path(tmp) / "project", "Backend")
            (project / "design" / "DESIGN.md").write_text("# Design\nINTERFACE_CONTEXT_SENTINEL\n")
            path = Path(tmp) / "pipeline.json"
            path.write_text(json.dumps({"name": "backend", "stages": [{"station": "builder"}]}))
            packets = []
            class Runtime:
                name = "fake"
                def execute(self, text, station_id, **kwargs):
                    packets.append(text)
                    return {"output": "done", "usage": {"input_tokens": 10, "output_tokens": 2}}
            run_pipeline(project, load_pipeline(path), WorkOrder(id="wo-backend", kind="feature", title="Backend"), executor=Runtime())
            self.assertNotIn("## Design system", packets[0])
            self.assertNotIn("INTERFACE_CONTEXT_SENTINEL", packets[0])
            self.assertIn("## Consumption discipline", packets[0])

    def test_run_budget_prevents_next_model_call_and_refreshes_page_s4(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = init_project(Path(tmp) / "project", "Budget demo")
            config = json.loads((project / "anvil.yaml").read_text())
            config["efficiency"] = {"max_run_tokens": 10}
            (project / "anvil.yaml").write_text(json.dumps(config))
            pipe = Path(tmp) / "pipeline.json"
            pipe.write_text(json.dumps({"name": "budget", "stages": [
                {"station": "builder"}, {"station": "reviewer-tests"}, {"station": "approver"}]}))
            class Runtime:
                name = "fake"
                writes_artifacts = True
                def __init__(self): self.calls = []
                def execute(self, text, station_id, **kwargs):
                    self.calls.append(station_id)
                    return {"output": "done", "usage": {"input_tokens": 10, "output_tokens": 2}}
            runtime = Runtime()
            report = run_pipeline(project, load_pipeline(pipe), WorkOrder(id="wo-budget", kind="feature", title="Budget"),
                                  registry=load_registry(ROOT / "stations"), executor=runtime)
            self.assertEqual(runtime.calls, ["builder"])
            self.assertEqual(report.verdict, "budget_exceeded")
            self.assertEqual(report.to_dict()["token_usage"]["total_tokens"], 12)
            self.assertIn("budget_exceeded", (project / "status" / "index.html").read_text())

    def test_project_summary_and_attempt_details_escape_names_s6_s8(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = init_project(Path(tmp) / "project", "<script>bad()</script>")
            report = RunReport(work_order_id="wo-measured", pipeline="test", steps=[{
                "station": "builder", "status": "executed", "executor": "command",
                "executed_model": "<img onerror=bad>",
                "usage": {"input_tokens": 100, "output_tokens": 20, "cached_input_tokens": 80},
                "attempts": [{"attempt": 1, "status": "succeeded",
                              "usage": {"input_tokens": 100, "output_tokens": 20}}],
            }])
            folder = project / "runs" / report.work_order_id
            folder.mkdir(parents=True)
            (folder / "report.json").write_text(json.dumps(report.to_dict()))
            page, summary = render_status_page(project)
            self.assertIn("120", page)
            self.assertIn("Input tokens", page)
            self.assertIn("Cached input", page)
            self.assertIn("Attempt 1", page)
            self.assertNotIn("<script>bad()", page)
            self.assertNotIn("<img onerror", page)
            self.assertEqual(summary["token_usage"]["total_tokens"], 120)

    def test_historical_unknown_does_not_render_as_zero_s6(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = init_project(Path(tmp) / "project", "Old project")
            folder = project / "runs" / "wo-old"
            folder.mkdir(parents=True)
            (folder / "report.json").write_text(json.dumps({"work_order_id": "wo-old", "steps": [
                {"station": "builder", "status": "executed"}]}))
            page, summary = render_status_page(project)
            self.assertIn("Unknown", page)
            self.assertEqual(summary["token_usage"]["unmeasured_calls"], 1)
            self.assertIsNone(summary["token_usage"]["total_tokens"])

    def test_scaffold_and_portfolio_pages_s7(self):
        with tempfile.TemporaryDirectory() as tmp:
            factory = init_project(Path(tmp) / "factory", "Factory")
            a = init_project(Path(tmp) / "one", "Same name")
            b = init_project(Path(tmp) / "two", "Same name")
            self.assertTrue((a / "status" / "index.html").is_file())
            result = generate_status_page(factory, projects=[a, b])
            self.assertEqual(len(result["projects"]), 2)
            paths = [entry["page"] for entry in result["projects"]]
            self.assertEqual(len(set(paths)), 2)
            self.assertEqual(paths, ["projects/one/index.html", "projects/two/index.html"])
            for path in paths:
                self.assertTrue((factory / "status" / path).is_file())
            page = (factory / "status" / "index.html").read_text()
            self.assertIn("Same name", page)
            self.assertNotIn(str(Path(tmp)), page)


class WrapperEvidenceTests(unittest.TestCase):
    """Real wrapper processes with fake provider CLIs: no paid model calls."""
    def invoke(self, provider, mode="correct", cap=None, separate_project=False):
        tmp = tempfile.mkdtemp(prefix="anvil-usage-test-")
        self.addCleanup(shutil.rmtree, tmp, True)
        root = Path(tmp)
        work_id = "wo-usage-" + root.name
        target = init_project(root / "project", "Runtime target") if separate_project else ROOT
        run_dir = target / "runs" / work_id
        self.addCleanup(shutil.rmtree, run_dir, True)
        binary = root / provider
        binary.write_text(f"#!{sys.executable}\n" + '''import json, os, sys
from pathlib import Path
assert Path.cwd().resolve() == Path(os.environ['FAKE_EXPECTED_CWD']).resolve(), 'Runtime used the factory tree instead of the target project'
record = Path(os.environ['FAKE_CALLS'])
n = int(record.read_text()) if record.exists() else 0
record.write_text(str(n+1))
assert ('--json' in sys.argv) if os.environ['FAKE_PROVIDER']=='codex' else ('json' in sys.argv and '--max-turns' in sys.argv)
review = Path(os.environ['FAKE_REVIEW'])
review.parent.mkdir(parents=True, exist_ok=True)
review.write_text('invalid' if n == 0 else json.dumps({'station':'reviewer-tests','verdict':'pass','findings':[]}))
usage = {'input_tokens':10,'output_tokens':2}
if os.environ['FAKE_PROVIDER']=='codex':
    print(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':'done'}}))
    print(json.dumps({'type':'turn.failed' if os.environ['FAKE_MODE']=='fail' else 'turn.completed','usage':usage}))
else:
    print(json.dumps({'type':'result','result':'done','usage':usage,'num_turns':2}))
sys.exit(3 if os.environ['FAKE_MODE']=='fail' else 0)
''')
        binary.chmod(0o755)
        packet = root / "packet.md"
        packet.write_text(f"# Task packet: reviewer-tests\n\n- id: {work_id}\n")
        env = {**os.environ, "PATH": str(root) + os.pathsep + os.environ.get("PATH", ""),
               "FAKE_CALLS": str(root / "calls"), "FAKE_REVIEW": str(run_dir / "reviewer-tests.review.json"),
               "FAKE_PROVIDER": provider, "FAKE_MODE": mode,
               "FAKE_EXPECTED_CWD": str(target),
               "CF_AIG_TOKEN": "fake-token-for-test", "ANTHROPIC_BASE_URL": "https://example.test/anthropic"}
        if cap:
            env["ANVIL_MAX_STATION_TOKENS"] = str(cap)
        executor = CommandExecutor({"command": shlex.quote(sys.executable) + " " +
                                   shlex.quote(str(ROOT / "tools" / (provider + "_station.py"))) + " {packet} {output}"})
        executor.limits = {"ANVIL_MAX_RUNTIME_TURNS": 4}
        with patch.dict(os.environ, env, clear=True):
            try:
                result = executor.execute("", "reviewer-tests", packet_path=packet, output_path=root / "output.md",
                                          cwd=target,
                                          configured_model="openai/gpt-6.1-sol" if provider == "codex" else "claude-sonnet-5-5")
            except ExecutorError as exc:
                result = exc.result
                result["failed"] = True
        return result

    def test_claude_correction_includes_both_attempts_s2(self):
        result = self.invoke("claude")
        self.assertEqual(result["usage"]["total_tokens"], 24)
        self.assertEqual(len(result["telemetry"]["attempts"]), 2)
        self.assertNotIn("fake-token-for-test", json.dumps(result))

    def test_codex_failure_preserves_usage_s2(self):
        result = self.invoke("codex", mode="fail")
        self.assertTrue(result["failed"])
        self.assertEqual(result["usage"]["total_tokens"], 12)
        self.assertEqual(result["telemetry"]["attempts"][0]["status"], "failed")

    def test_no_correction_after_station_threshold_s4(self):
        result = self.invoke("claude", cap=1)
        self.assertTrue(result["failed"])
        self.assertEqual(len(result["telemetry"]["attempts"]), 1)

    def test_project_handoff_executes_in_target_tree_s2(self):
        result = self.invoke("claude", separate_project=True)
        self.assertFalse(result.get("failed"))
        self.assertEqual(result["usage"]["total_tokens"], 24)


if __name__ == "__main__":
    unittest.main()
