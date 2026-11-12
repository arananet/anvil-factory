"""Tests for the selectable station runtime (spec: runtime-selection).

Scenario map:
  S1  test_default_is_the_gateway_and_unknown_fails_s1
  S2  test_copilot_command_by_station_s2
  S3  test_copilot_runs_a_producing_station_s3, test_copilot_review_and_correction_s3
  S4  test_usage_is_read_from_the_usage_file_s4, test_unreadable_usage_stays_unknown_s4
  S5  test_project_default_and_variable_precedence_s5
  S6  test_workflow_and_smoke_follow_the_variable_s6
"""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import copilot_runtime
from anvil.executor import create_executor
from anvil.telemetry import parse_runtime_output

ROOT = Path(__file__).resolve().parent.parent
DISPATCH = ROOT / "tools" / "dispatch_station.py"

# Stand-in for the copilot CLI: records its arguments and environment, writes
# the usage statistics file, and behaves as FAKE_COPILOT says.
FAKE_COPILOT = r'''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
log = Path(os.environ["FAKE_LOG"])
calls = json.loads(log.read_text()) if log.exists() else []
calls.append({"args": args, "token": os.environ.get("COPILOT_GITHUB_TOKEN"), "cwd": os.getcwd()})
log.write_text(json.dumps(calls))
usage = next((a.split("=", 1)[1] for a in args if a.startswith("--usage-output-file=")), None)
mode = os.environ.get("FAKE_COPILOT", "ok")
if usage and mode != "no-usage":
    Path(usage).write_text(json.dumps({"aiCredits": 3, "models": {"claude-opus-5.5": {
        "inputTokens": 1200, "outputTokens": 300, "cacheReadTokens": 1000, "cacheWriteTokens": 100,
        "reasoningTokens": 50}}, "agents": {"main": {"inputTokens": 1200, "outputTokens": 300}}}))
if mode == "fail":
    print("model not available on this plan", file=sys.stderr); sys.exit(1)
prompt = args[args.index("-p") + 1]
review = os.environ.get("FAKE_REVIEW")
if review:
    target = Path(review)
    if mode == "bad-then-good" and len(calls) == 1:
        target.write_text("not json")
    else:
        target.write_text(json.dumps({"station": target.name.split(".")[0], "verdict": "pass", "findings": ["ok"]}))
if "builder" in prompt.splitlines()[0]:
    Path("built.txt").write_text("built by copilot\n")
print("station reply from copilot")
'''


class Runtime:
    def __init__(self, tmp):
        self.tmp = Path(tmp)
        self.proj = self.tmp / "proj"; (self.proj / "runs" / "wo-1").mkdir(parents=True)
        self.bin = self.tmp / "bin"; self.bin.mkdir()
        fake = self.bin / "copilot"; fake.write_text(FAKE_COPILOT); fake.chmod(0o755)
        self.log = self.tmp / "calls.json"

    def packet(self, station):
        path = self.proj / "runs" / "wo-1" / f"{station}.packet.md"
        path.write_text(f"# Task packet: {station}\n\n## Work order\n\n- id: wo-1\n- kind: feature\n")
        return path

    def env(self, **extra):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("ANVIL_", "FAKE_", "COPILOT_"))}
        env.update({"PATH": f"{self.bin}:{env['PATH']}", "FAKE_LOG": str(self.log), "ANVIL_RUNTIME": "copilot",
                    "ANVIL_PROJECT_ROOT": str(self.proj), "ANVIL_CONFIGURED_MODEL": "claude-opus-5-5",
                    "COPILOT_GITHUB_TOKEN": "ghu_copilot"})
        env.update(extra)
        return env

    def dispatch(self, station, **extra):
        packet = self.packet(station)
        output = packet.with_name(f"{station}.output.md")
        env = self.env(ANVIL_USAGE_PATH=str(output) + ".usage.json", **extra)
        proc = subprocess.run([sys.executable, str(DISPATCH), str(packet), str(output)],
                              env=env, capture_output=True, text=True, cwd=str(self.proj))
        return proc, output

    def calls(self):
        return json.loads(self.log.read_text()) if self.log.exists() else []


class TestSelection(unittest.TestCase):
    def test_default_is_the_gateway_and_unknown_fails_s1(self):
        """S1: unset means the gateway; an unknown value fails loudly before any model call"""
        self.assertEqual(copilot_runtime.selected_runtime({}), "claude-gateway")
        for value, expected in (("claude-gateway", "claude-gateway"), ("Claude", "claude-gateway"),
                                ("copilot", "copilot"), (" GitHub-Copilot ", "copilot")):
            self.assertEqual(copilot_runtime.selected_runtime({"ANVIL_RUNTIME": value}), expected)
        with self.assertRaises(ValueError):
            copilot_runtime.selected_runtime({"ANVIL_RUNTIME": "codex"})
        with tempfile.TemporaryDirectory() as tmp:
            rt = Runtime(tmp)
            proc, _ = rt.dispatch("builder", ANVIL_RUNTIME="codex")
            self.assertEqual(proc.returncode, 9)
            self.assertIn("unknown ANVIL_RUNTIME", proc.stderr)
            self.assertEqual(rt.calls(), [])

    def test_copilot_command_by_station_s2(self):
        """S2: producers get every tool; other stations read, run and write only in their run directory"""
        builder = copilot_runtime.copilot_command("P", "claude-opus-5-5", True, "/p/runs/wo-1", "/p/u.json", {})
        self.assertEqual(builder[:5], ["copilot", "-p", "P", "--model", "claude-opus-5.5"])
        self.assertIn("--allow-all-tools", builder)
        for flag in ("--silent", "--no-ask-user", "--disable-builtin-mcps", "--usage-output-file=/p/u.json"):
            self.assertIn(flag, builder)
        secrets = next(a for a in builder if a.startswith("--secret-env-vars="))
        for name in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN", "ANTHROPIC_API_KEY"):
            self.assertIn(name, secrets)
        reviewer = copilot_runtime.copilot_command("P", "claude-sonnet-5-5", False, "/p/runs/wo-1", "/p/u.json", {})
        self.assertEqual(reviewer[4], "claude-sonnet-5.5")
        self.assertNotIn("--allow-all-tools", reviewer)
        self.assertNotIn("--allow-all", reviewer); self.assertNotIn("--yolo", reviewer)
        self.assertEqual([a for a in reviewer if a.startswith("--allow-tool")],
                         ["--allow-tool=shell", "--allow-tool=read", "--allow-tool=write(/p/runs/wo-1/**)"])
        mapped = {"ANVIL_COPILOT_MODELS": json.dumps({"claude-opus-5-5": "claude-opus-latest"}),
                  "ANVIL_COPILOT_MAX_AI_CREDITS": "40"}
        custom = copilot_runtime.copilot_command("P", "claude-opus-5-5", True, "/r", "/u", mapped)
        self.assertEqual(custom[4], "claude-opus-latest")
        self.assertIn("--max-ai-credits=40", custom)
        self.assertEqual(copilot_runtime.copilot_model("claude-sonnet-5-5", mapped), "claude-sonnet-5.5")
        with self.assertRaises(ValueError):
            copilot_runtime.copilot_model("claude-opus-5-5", {"ANVIL_COPILOT_MODELS": "[1]"})


class TestCopilotStations(unittest.TestCase):
    def test_copilot_runs_a_producing_station_s3(self):
        """S3: the dispatcher runs the builder through copilot, in the project tree"""
        with tempfile.TemporaryDirectory() as tmp:
            rt = Runtime(tmp)
            proc, output = rt.dispatch("builder")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            call = rt.calls()[0]
            self.assertEqual(call["args"][0], "-p")
            self.assertEqual(call["args"][call["args"].index("--model") + 1], "claude-opus-5.5")
            self.assertIn("--allow-all-tools", call["args"])
            self.assertEqual(Path(call["cwd"]).resolve(), rt.proj.resolve())
            self.assertEqual(call["token"], "ghu_copilot")
            self.assertEqual((rt.proj / "built.txt").read_text(), "built by copilot\n")
            self.assertIn("station reply from copilot", output.read_text())
            self.assertIn('{"model": "claude-opus-5-5"}', proc.stdout, "the dispatcher self reports the model")
            self.assertNotIn("ghu_copilot", proc.stdout + proc.stderr)
            failed, _ = rt.dispatch("builder", FAKE_COPILOT="fail")
            self.assertEqual(failed.returncode, 2)
            self.assertIn("copilot exited 1", failed.stderr)
            self.assertIn("model not available", failed.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            rt = Runtime(tmp)
            (rt.bin / "copilot").unlink()
            proc, _ = rt.dispatch("builder")
            self.assertEqual(proc.returncode, 5)
            self.assertIn("copilot CLI is not on PATH", proc.stderr)

    def test_copilot_review_and_correction_s3(self):
        """S3: a reviewer keeps the review file contract and its one correction"""
        with tempfile.TemporaryDirectory() as tmp:
            rt = Runtime(tmp)
            review = rt.proj / "runs" / "wo-1" / "reviewer-tests.review.json"
            proc, _ = rt.dispatch("reviewer-tests", FAKE_REVIEW=str(review), FAKE_COPILOT="bad-then-good",
                                  ANVIL_CONFIGURED_MODEL="claude-sonnet-5-5")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            calls = rt.calls()
            self.assertEqual(len(calls), 2, "one correction attempt")
            self.assertIn("Review file correction needed", calls[1]["args"][1])
            self.assertNotIn("--allow-all-tools", calls[0]["args"])
            self.assertIn(f"--allow-tool=write({(rt.proj / 'runs' / 'wo-1').resolve()}/**)", calls[0]["args"])
            self.assertEqual(json.loads(review.read_text())["verdict"], "pass")
            self.assertTrue((rt.proj / "runs/wo-1/reviewer-tests.correction.json").exists())
            ledger = json.loads((rt.proj / "runs/wo-1/reviewer-tests.output.md.usage.json").read_text())
            self.assertEqual([a["runtime"] for a in ledger["attempts"]], ["copilot", "copilot"])

    def test_usage_is_read_from_the_usage_file_s4(self):
        """S4: tokens come from the per model breakdown, counted once"""
        with tempfile.TemporaryDirectory() as tmp:
            rt = Runtime(tmp)
            proc, output = rt.dispatch("builder")
            ledger = json.loads(Path(str(output) + ".usage.json").read_text())
            usage = ledger["attempts"][0]["usage"]
            self.assertEqual((usage["input_tokens"], usage["output_tokens"], usage["total_tokens"]), (1200, 300, 1500))
            self.assertEqual((usage["cached_input_tokens"], usage["cache_creation_input_tokens"],
                              usage["reasoning_tokens"]), (1000, 100, 50))
            self.assertTrue(ledger["complete"])
            self.assertEqual(ledger["attempts"][0]["configured_model"], "claude-opus-5-5")
            self.assertTrue(Path(str(output) + ".copilot-usage.json").exists(), "the raw statistics are kept")
        two = {"byModel": [{"model": "a", "input_tokens": 10, "output_tokens": 2},
                           {"model": "b", "input_tokens": 5, "output_tokens": 1}],
               "byAgent": [{"input_tokens": 15, "output_tokens": 3}]}
        self.assertEqual(copilot_runtime.parse_copilot_usage(two)["input_tokens"], 15)
        nested = {"total": {"tokens": 1}, "inputTokens": 7, "outputTokens": 3}
        self.assertEqual(copilot_runtime.parse_copilot_usage(nested)["output_tokens"], 3)

    def test_unreadable_usage_stays_unknown_s4(self):
        """S4: a missing or unfamiliar usage file means unknown, never a guess"""
        for data in (None, [], {}, {"credits": 4}, {"models": {"x": {"inputTokens": "many"}}},
                     {"models": {"x": {"inputTokens": -1, "outputTokens": 2}}}):
            self.assertIsNone(copilot_runtime.parse_copilot_usage(data), data)
        parsed = parse_runtime_output(json.dumps({"type": "copilot_result", "result": "hi", "usage": None}), "copilot")
        self.assertEqual((parsed["output"], parsed["usage"], parsed["usage_complete"]), ("hi", None, False))
        with tempfile.TemporaryDirectory() as tmp:
            rt = Runtime(tmp)
            proc, output = rt.dispatch("builder", FAKE_COPILOT="no-usage")
            self.assertEqual(proc.returncode, 0)
            ledger = json.loads(Path(str(output) + ".usage.json").read_text())
            self.assertIsNone(ledger["attempts"][0]["usage"])
            self.assertFalse(ledger["complete"])


class TestWiring(unittest.TestCase):
    def test_project_default_and_variable_precedence_s5(self):
        """S5: anvil.yaml names the project's runtime; the variable wins over it"""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "seen"
            executor = create_executor({"kind": "command", "provider": "copilot",
                                        "copilot_models": {"claude-opus-5-5": "claude-opus-5.5-preview"},
                                        "command": f'printf "%s|%s" "$ANVIL_RUNTIME" "$ANVIL_COPILOT_MODELS" > {out}'})
            clean = {k: v for k, v in os.environ.items() if not k.startswith("ANVIL_")}
            with mock.patch.dict(os.environ, clean, clear=True):
                executor.execute("p", "builder", cwd=tmp)
            runtime, models = out.read_text().split("|")
            self.assertEqual(runtime, "copilot")
            self.assertEqual(json.loads(models), {"claude-opus-5-5": "claude-opus-5.5-preview"})
            with mock.patch.dict(os.environ, dict(clean, ANVIL_RUNTIME="claude-gateway"), clear=True):
                executor.execute("p", "builder", cwd=tmp)
            self.assertEqual(out.read_text().split("|")[0], "claude-gateway")
            plain = create_executor({"kind": "command", "command": f'printf "%s|" "$ANVIL_RUNTIME" > {out}'})
            with mock.patch.dict(os.environ, clean, clear=True):
                plain.execute("p", "builder", cwd=tmp)
            self.assertEqual(out.read_text(), "|", "nothing is set when nothing is configured")

    def test_workflow_and_smoke_follow_the_variable_s6(self):
        """S6: the workflow installs and probes the runtime the variable names"""
        text = (ROOT / ".github" / "workflows" / "anvil-line.yml").read_text()
        self.assertIn("ANVIL_RUNTIME: ${{ vars.ANVIL_RUNTIME || 'claude-gateway' }}", text)
        self.assertIn("COPILOT_GITHUB_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN }}", text)
        self.assertIn("npm install -g @github/copilot", text)
        self.assertIn("npm install -g @anthropic-ai/claude-code", text)
        with tempfile.TemporaryDirectory() as tmp:
            rt = Runtime(tmp)
            proc = subprocess.run([sys.executable, str(ROOT / "tools" / "model_route_smoke.py")],
                                  env=rt.env(), capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("PASS Copilot CLI, claude-sonnet-5-5 (claude-sonnet-5.5): ok", proc.stdout)
            self.assertEqual([c["args"][c["args"].index("--model") + 1] for c in rt.calls()],
                             ["claude-sonnet-5.5", "claude-opus-5.5"])
            bad = subprocess.run([sys.executable, str(ROOT / "tools" / "model_route_smoke.py")],
                                 env=rt.env(ANVIL_RUNTIME="nope"), capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)
            gateway = subprocess.run([sys.executable, str(ROOT / "tools" / "model_route_smoke.py")],
                                     env={k: v for k, v in rt.env(ANVIL_RUNTIME="claude-gateway").items()
                                          if not k.startswith("ANTHROPIC_")}, capture_output=True, text=True)
            self.assertIn("Missing ANTHROPIC_BASE_URL", gateway.stdout)


if __name__ == "__main__":
    unittest.main()
