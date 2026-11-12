"""Tests for governed delivery (spec: governed-delivery).

Scenario map:
  S1  test_state_is_live_and_ends_finished_s1, test_crash_and_stall_are_visible_s1
  S2  test_events_are_structured_and_carry_no_free_text_s2
  S3  test_events_and_trace_are_exported_s3, test_export_failure_never_decides_a_run_s3
  S4  test_fleet_summary_s4
  S5  test_identity_and_policy_s5, test_policy_comes_from_the_operator_checkout_s5
  S6  test_stations_and_checks_hold_no_deploy_credentials_s6, test_docker_sandbox_wraps_the_station_s6
  S7  test_preview_per_attempt_s7, test_failed_preview_only_warns_s7
  S8  test_blueprint_deploy_targets_s8
  S9  test_github_pages_tool_s9
  S10 test_workflow_keeps_tokens_from_stations_s10
"""
import contextlib, http.server, io, json, os, re, subprocess, sys, tempfile, threading, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_autonomous_line import Line, FAKE, SHORT, DEPLOY
from anvil import line, observe
from anvil.cli import main
from anvil.executor import create_executor, sandbox_command, station_env
from anvil.pipeline import load_pipeline
from anvil.runner import run_pipeline
from anvil.stations import load_registry

ROOT = Path(__file__).resolve().parent.parent

# The fake runtime, plus a snapshot of what a station can see while it runs.
SPY = FAKE + r'''
import os, shutil
if (run_dir / "state.json").exists():
    shutil.copy(run_dir / "state.json", home / f"state.{station}.json")
(home / f"env.{station}.json").write_text(json.dumps(
    {k: os.environ.get(k) for k in ("GH_TOKEN", "CLOUDFLARE_API_TOKEN", "ANTHROPIC_API_KEY", "ANVIL_PROJECT_ROOT")}))
'''


def spy_line(tmp, stages=SHORT, **kwargs):
    h = Line(tmp, stages, **kwargs)
    (h.home / "fake.py").write_text(SPY)
    return h


def events(h, wo_id):
    return [json.loads(l) for l in (h.proj / "runs" / wo_id / "events.jsonl").read_text().splitlines()]


def state(h, wo_id):
    return json.loads((h.proj / "runs" / wo_id / "state.json").read_text())


class Collector:
    """A local HTTP endpoint that records what the line exports."""

    def __enter__(self):
        received = self.received = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                received.append((self.path, dict(self.headers), body))
                self.send_response(200); self.end_headers(); self.wfile.write(b"{}")

            def log_message(self, *args):
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown(); self.server.server_close()


class TestLiveState(unittest.TestCase):
    def test_state_is_live_and_ends_finished_s1(self):
        """S1: the state names the running station, then ends finished"""
        with tempfile.TemporaryDirectory() as tmp:
            h = spy_line(tmp)
            h.run("wo-s1")
            during = json.loads((h.home / "state.builder.json").read_text())
            self.assertEqual((during["state"], during["current_station"]), ("running", "builder"))
            self.assertEqual([s["station"] for s in during["steps"]], ["intake", "test-writer"])
            self.assertEqual(during["token_usage"]["calls"], 2)
            final = state(h, "wo-s1")
            self.assertEqual((final["state"], final["verdict"], final["schema"]),
                             ("finished", "approved", "anvil/run-state@1"))
            self.assertEqual(final["run_id"], h.report("wo-s1")["run_id"])
            self.assertFalse((h.proj / "runs/wo-s1/state.json.tmp").exists())

    def test_crash_and_stall_are_visible_s1(self):
        """S1: a run that raises is crashed, not running; an abandoned one is stalled"""
        class Exploding:
            kind = "command"; name = "boom"; writes_artifacts = True
            def execute(self, packet_text, station_id, **kwargs):
                if station_id == "builder":
                    raise RuntimeError("the runner lost its disk")
                return {"output": "ok", "usage": None}
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, SHORT)
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(h.pipeline, known_stations=set(reg.ids()))
            with self.assertRaises(RuntimeError):
                run_pipeline(h.proj, pipe, {"id": "wo-crash", "kind": "feature", "title": "T"},
                             registry=reg, executor=Exploding())
            crashed = state(h, "wo-crash")
            self.assertEqual((crashed["state"], crashed["current_station"]), ("crashed", "builder"))
            self.assertIn("RuntimeError", crashed["error"])
            self.assertFalse((h.proj / "runs/wo-crash/report.json").exists())
            last = events(h, "wo-crash")[-1]
            self.assertEqual((last["event"], last["station"], last["error"]), ("run.crashed", "builder", "RuntimeError"))
            # a state left running and untouched is reported as stalled
            path = h.proj / "runs/wo-crash/state.json"
            old = dict(crashed, state="running", updated_at=(datetime.now(timezone.utc) - timedelta(hours=4)).isoformat())
            path.write_text(json.dumps(old))
            self.assertEqual(observe.run_states(h.proj)[0]["state"], "stalled")
            path.write_text(json.dumps(dict(old, updated_at=datetime.now(timezone.utc).isoformat())))
            self.assertEqual(observe.run_states(h.proj)[0]["state"], "running")


class TestEvents(unittest.TestCase):
    def test_events_are_structured_and_carry_no_free_text_s2(self):
        """S2: boundaries, one event per step, the loopback, and scalar facts only"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, SHORT, behavior={"fail_until_attempt": 2})
            rep = h.run("wo-s2")
            evs = events(h, "wo-s2")
            kinds = [e["event"] for e in evs]
            self.assertEqual((kinds[0], kinds[-1]), ("run.started", "run.finished"))
            self.assertEqual(kinds.count("station.finished") + kinds.count("loopback"), len(rep["steps"]))
            self.assertEqual(kinds.count("loopback"), 1)
            for e in evs:
                self.assertEqual((e["schema"], e["run_id"], e["work_order_id"], e["pipeline"], e["project"]),
                                 ("anvil/event@1", rep["run_id"], "wo-s2", "line", "Demo"))
                for forbidden in ("detail", "reason", "findings", "feedback", "artifacts", "output"):
                    self.assertNotIn(forbidden, e)
                self.assertNotIn("misses the empty input edge case", json.dumps(e))
                self.assertNotIn(str(h.proj), json.dumps(e))
            builders = [e for e in evs if e.get("station") == "builder"]
            self.assertEqual([b.get("attempt", 1) for b in builders], [1, 2])
            self.assertEqual(builders[0]["configured_model"], "claude-opus-5-5")
            done = evs[-1]
            self.assertEqual((done["verdict"], done["loopbacks"], done["calls"]), ("approved", 1, 6))

    def test_events_and_trace_are_exported_s3(self):
        """S3: events go to the webhook with the token, the run goes out as one OTLP trace"""
        with tempfile.TemporaryDirectory() as tmp, Collector() as sink:
            h = Line(tmp, SHORT)
            cfg = json.loads((h.proj / "anvil.yaml").read_text())
            cfg["observability"] = {"events_url": sink.url + "/events", "events_token_env": "TEST_EVENTS_TOKEN",
                                    "otlp_endpoint": sink.url + "/v1/traces", "otlp_headers_env": "TEST_OTLP_HEADERS"}
            (h.proj / "anvil.yaml").write_text(json.dumps(cfg))
            with mock.patch.dict(os.environ, {"TEST_EVENTS_TOKEN": "tok", "TEST_OTLP_HEADERS": "x-team=core,x-key=k1"}):
                rep = h.run("wo-s3")
            posted = [body for path, _, body in sink.received if path == "/events"]
            self.assertEqual([e["event"] for e in posted], [e["event"] for e in events(h, "wo-s3")])
            self.assertTrue(all(hd.get("Authorization") == "Bearer tok"
                                for path, hd, _ in sink.received if path == "/events"))
            traces = [(hd, body) for path, hd, body in sink.received if path == "/v1/traces"]
            self.assertEqual(len(traces), 1)
            headers, trace = traces[0]
            lowered = {k.lower(): v for k, v in headers.items()}
            self.assertEqual((lowered.get("x-team"), lowered.get("x-key")), ("core", "k1"))
            spans = trace["resourceSpans"][0]["scopeSpans"][0]["spans"]
            self.assertEqual(len(spans), len(rep["steps"]) + 1)
            root = spans[0]
            self.assertRegex(root["traceId"], r"^[0-9a-f]{32}$")
            self.assertTrue(all(s["traceId"] == root["traceId"] and s["parentSpanId"] == root["spanId"] for s in spans[1:]))
            self.assertEqual(len({s["spanId"] for s in spans}), len(spans))
            self.assertTrue(all(int(s["endTimeUnixNano"]) >= int(s["startTimeUnixNano"]) for s in spans))
            attrs = {a["key"]: a["value"] for a in root["attributes"]}
            self.assertEqual(attrs["anvil.verdict"], {"stringValue": "approved"})
            self.assertEqual(attrs["anvil.work_order_id"], {"stringValue": "wo-s3"})
            self.assertEqual(state(h, "wo-s3")["export_errors"], [])

    def test_export_failure_never_decides_a_run_s3(self):
        """S3: an unreachable endpoint is recorded and changes nothing"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, SHORT)
            cfg = json.loads((h.proj / "anvil.yaml").read_text())
            cfg["observability"] = {"events_url": "http://127.0.0.1:9/events", "otlp_endpoint": "ftp://nope/v1/traces",
                                    "timeout_seconds": 1}
            (h.proj / "anvil.yaml").write_text(json.dumps(cfg))
            rep = h.run("wo-s3b")
            self.assertEqual(rep["verdict"], "approved")
            errors = state(h, "wo-s3b")["export_errors"]
            self.assertEqual(len(errors), 2)
            self.assertTrue(errors[0].startswith("events:") and errors[1].startswith("otlp:"))
            self.assertEqual(events(h, "wo-s3b")[-1]["event"], "run.finished")

    def test_fleet_summary_s4(self):
        """S4: one command answers what is running, what broke and how often the line approves"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, SHORT)
            h.run("wo-a")
            (h.home / "behavior.json").write_text(json.dumps({"fail_until_attempt": 99}))
            h.run("wo-b")
            crashed = dict(state(h, "wo-a"), work_order_id="wo-c", state="crashed", current_station="builder")
            (h.proj / "runs" / "wo-c").mkdir()
            (h.proj / "runs" / "wo-c" / "state.json").write_text(json.dumps(crashed))
            code, out, _ = h.cli("runs", h.proj, "--json")
            self.assertEqual(code, 0)
            data = json.loads(out)
            summary = data["summary"]
            self.assertEqual(summary["by_pipeline"]["line"],
                             {"runs": 2, "approved": 1, "loopbacks": 2, "approval_rate": 0.5})
            self.assertEqual(summary["reviews_not_passed_by_station"], {"reviewer-tests": 1})
            self.assertEqual(summary["interrupted"], [{"work_order_id": "wo-c", "state": "crashed", "station": "builder"}])
            self.assertEqual(summary["token_usage"]["calls"], 4 + 8)
            self.assertEqual({r["work_order_id"]: r["state"] for r in data["runs"]},
                             {"wo-a": "finished", "wo-b": "finished", "wo-c": "crashed"})
            code, text, _ = h.cli("runs", h.proj)
            self.assertIn("wo-c: crashed at builder", text)
            self.assertIn("approval rate 0.5", text)


ACTIONS = {"GITHUB_ACTIONS": "true", "GITHUB_ACTOR": "ana", "GITHUB_RUN_ID": "777"}


class TestApprovalPolicy(unittest.TestCase):
    def gated(self, tmp, policy=None):
        h = Line(tmp, DEPLOY, deploy={"command": "echo shipped > deployed.txt"})
        if policy is not None:
            cfg = json.loads((h.proj / "anvil.yaml").read_text())
            cfg["approvals"] = policy
            (h.proj / "anvil.yaml").write_text(json.dumps(cfg))
        wo = h.work_order("wo-p", risk_hints=["production-deploy"])
        self.assertEqual(h.cli("run", h.proj, "--pipeline", h.pipeline, "--work-order", wo, "--execute")[0], 3)
        return h

    def test_identity_and_policy_s5(self):
        """S5: verified identity inside Actions, and the policy decides who may approve what"""
        approval = lambda h: json.loads((h.proj / "runs/wo-p/human-approval.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            h = self.gated(tmp)
            with mock.patch.dict(os.environ, ACTIONS):
                code, _, err = h.cli("approve", h.proj, "wo-p", "--by", "someone-else")
                self.assertEqual(code, 1)
                self.assertIn("does not match the authenticated GitHub actor", err)
                self.assertFalse((h.proj / "runs/wo-p/human-approval.json").exists())
                self.assertEqual(h.cli("approve", h.proj, "wo-p", "--by", "Ana")[0], 0)
            self.assertEqual(approval(h)["identity"],
                             {"login": "ana", "source": "github-actions", "verified": True, "workflow_run": "777"})
            self.assertEqual(h.cli("resume", h.proj, "wo-p", "--pipeline", h.pipeline, "--execute")[0], 0)
            self.assertTrue(h.report("wo-p")["decision"]["human_gate"]["approval"]["identity"]["verified"])
        with tempfile.TemporaryDirectory() as tmp:
            h = self.gated(tmp, {"require_verified_identity": True, "approvers": ["ana", "bo"],
                                 "by_risk_hint": {"production-deploy": ["bo"]}})
            code, _, err = h.cli("approve", h.proj, "wo-p", "--by", "bo")
            self.assertEqual(code, 1)
            self.assertIn("verified identity", err)
            with mock.patch.dict(os.environ, dict(ACTIONS, GITHUB_ACTOR="mallory")):
                code, _, err = h.cli("approve", h.proj, "wo-p", "--by", "mallory")
                self.assertIn("not in the approvers list", err)
            with mock.patch.dict(os.environ, ACTIONS):
                code, _, err = h.cli("approve", h.proj, "wo-p", "--by", "ana")
                self.assertEqual(code, 1)
                self.assertIn("risk hint production-deploy", err)
            self.assertFalse((h.proj / "runs/wo-p/human-approval.json").exists())
            with mock.patch.dict(os.environ, dict(ACTIONS, GITHUB_ACTOR="Bo")):
                self.assertEqual(h.cli("approve", h.proj, "wo-p", "--by", "Bo")[0], 0)
            self.assertEqual(approval(h)["policy_checked"],
                             ["require_verified_identity", "approvers", "by_risk_hint:production-deploy"])
        identity = {"login": "ana", "verified": True}
        with self.assertRaises(ValueError):
            line.check_approval_policy({"override": ["bo"]}, identity, [], override=True)
        self.assertEqual(line.check_approval_policy({"override": ["ana"]}, identity, [], override=True), ["override"])
        self.assertEqual(line.check_approval_policy({"override": ["bo"]}, identity, [], override=False), [])
        self.assertEqual(line.check_approval_policy(None, identity, ["auth"], override=True), [])

    def test_policy_comes_from_the_operator_checkout_s5(self):
        """S5: a policy edited inside the run's worktree does not apply"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, DEPLOY)
            cfg = json.loads((h.proj / "anvil.yaml").read_text())
            cfg["approvals"] = {"approvers": ["bo"]}
            (h.proj / "anvil.yaml").write_text(json.dumps(cfg))
            h.git("add", "-A"); h.git("-c", "user.name=t", "-c", "user.email=t@example.test", "commit", "-q", "-m", "policy")
            wo = h.work_order("wo-iso", risk_hints=["production-deploy"])
            self.assertEqual(h.cli("run", h.proj, "--pipeline", h.pipeline, "--work-order", wo, "--execute", "--isolate")[0], 3)
            worktree = h.tmp / ".anvil-worktrees" / "proj" / "wo-iso"
            edited = json.loads((worktree / "anvil.yaml").read_text())
            edited["approvals"] = {"approvers": ["mallory"]}
            (worktree / "anvil.yaml").write_text(json.dumps(edited))
            code, _, err = h.cli("approve", h.proj, "wo-iso", "--by", "mallory", "--isolate")
            self.assertEqual(code, 1)
            self.assertIn("not in the approvers list", err)
            self.assertFalse((worktree / "runs/wo-iso/human-approval.json").exists())


class TestContainment(unittest.TestCase):
    SECRETS = {"GH_TOKEN": "ghp_secret", "CLOUDFLARE_API_TOKEN": "cf_secret", "ANTHROPIC_API_KEY": "model_key"}

    def test_stations_and_checks_hold_no_deploy_credentials_s6(self):
        """S6: stations and checks lose the tokens; the deploy command keeps them"""
        with tempfile.TemporaryDirectory() as tmp:
            h = spy_line(tmp, DEPLOY, checks=['test -z "$GH_TOKEN$CLOUDFLARE_API_TOKEN" && test -f app.txt'],
                         deploy={"command": 'test "$CLOUDFLARE_API_TOKEN" = cf_secret && echo ok > deployed.txt'})
            with mock.patch.dict(os.environ, self.SECRETS):
                rep = h.run("wo-s6")
            for station in ("intake", "test-writer", "builder", "reviewer-tests"):
                seen = json.loads((h.home / f"env.{station}.json").read_text())
                self.assertIsNone(seen["GH_TOKEN"], station)
                self.assertIsNone(seen["CLOUDFLARE_API_TOKEN"], station)
                self.assertEqual(seen["ANTHROPIC_API_KEY"], "model_key", "the model credential still reaches the station")
            self.assertEqual(rep["verdict"], "approved")
            self.assertTrue((h.proj / "deployed.txt").exists(), "the deploy command saw the deploy token")
        from anvil.gates import _run_shell
        with mock.patch.dict(os.environ, self.SECRETS):
            probe = 'test -z "$GH_TOKEN$CLOUDFLARE_API_TOKEN"'
            self.assertEqual(_run_shell(probe, ROOT, "wo-x", 30, scrub=True)[0], 0, "a project check sees no token")
            self.assertNotEqual(_run_shell(probe, ROOT, "wo-x", 30)[0], 0, "a deploy command keeps them")
        env = station_env(dict(self.SECRETS, MY_TOKEN="x", PATH="/bin"), {"env_deny": ["MY_TOKEN"], "env_keep": ["GH_TOKEN"]})
        self.assertEqual(env, {"GH_TOKEN": "ghp_secret", "ANTHROPIC_API_KEY": "model_key", "PATH": "/bin"})

    def test_docker_sandbox_wraps_the_station_s6(self):
        """S6: the container mounts only the project and gets only the allowed variables"""
        env = dict(self.SECRETS, ANVIL_PROJECT_ROOT="/work/proj", ANVIL_CONFIGURED_MODEL="claude-opus-5-5",
                   ANTHROPIC_BASE_URL="https://gw", HOME="/home/me", PATH="/usr/bin")
        argv, passed = sandbox_command("run-station p o", {"kind": "docker", "image": "anvil-station:1"}, "/work/proj", env)
        self.assertEqual(argv[:3], ["docker", "run", "--rm"])
        self.assertEqual(argv[-4:], ["anvil-station:1", "sh", "-c", "run-station p o"])
        self.assertEqual([argv[i + 1] for i, a in enumerate(argv) if a == "-v"], ["/work/proj:/work/proj"])
        self.assertIn("--cap-drop", argv); self.assertIn("no-new-privileges", argv)
        names = [argv[i + 1] for i, a in enumerate(argv) if a == "-e"]
        self.assertEqual(sorted(n for n in names if n != "HOME=/tmp"),
                         ["ANTHROPIC_API_KEY", "ANTHROPIC_BASE_URL", "ANVIL_CONFIGURED_MODEL", "ANVIL_PROJECT_ROOT"])
        self.assertNotIn("GH_TOKEN", " ".join(argv)); self.assertNotIn("ghp_secret", " ".join(argv))
        self.assertNotIn("GH_TOKEN", passed)
        # wiring: with a docker binary on PATH the executor runs the station through it
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, SHORT)
            bindir = h.tmp / "bin"; bindir.mkdir()
            fake_docker = bindir / "docker"
            fake_docker.write_text("#!/bin/sh\necho \"$@\" >> \"$DOCKER_LOG\"\nwhile [ \"$1\" != sh ]; do shift; done\nexec \"$@\"\n")
            fake_docker.chmod(0o755)
            cfg = json.loads((h.proj / "anvil.yaml").read_text())
            cfg["runtime"]["sandbox"] = {"kind": "docker", "image": "anvil-station:1", "mounts": [f"{h.home}:{h.home}"]}
            (h.proj / "anvil.yaml").write_text(json.dumps(cfg))
            with mock.patch.dict(os.environ, {"PATH": f"{bindir}:{os.environ['PATH']}", "DOCKER_LOG": str(h.tmp / "docker.log")}):
                rep = h.run("wo-box")
            self.assertEqual(rep["verdict"], "approved")
            log = (h.tmp / "docker.log").read_text().splitlines()
            self.assertEqual(len(log), 4, "every station went through the sandbox")
            self.assertIn(f"-v {h.proj.resolve()}:{h.proj.resolve()}", log[0])
        with self.assertRaises(Exception):
            sandbox_command("x", {"kind": "docker"}, "/work", {})


class TestPreview(unittest.TestCase):
    PREVIEW = {"command": 'cp app.txt "$PREVIEW_ROOT/$ANVIL_PREVIEW_NAME.txt" && echo "$ANVIL_PREVIEW_URL" >> "$PREVIEW_ROOT/urls"',
               "verify": ['test -f "$PREVIEW_ROOT/$ANVIL_PREVIEW_NAME.txt"'],
               "cleanup": 'rm "$PREVIEW_ROOT/$ANVIL_PREVIEW_NAME.txt"',
               "url": "https://{preview_name}.demo.pages.dev"}

    def test_preview_per_attempt_s7(self):
        """S7: one preview per attempt, before review, named after the order"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, SHORT, behavior={"fail_until_attempt": 2}, deploy={"preview": self.PREVIEW})
            out = h.tmp / "previews"; out.mkdir()
            with mock.patch.dict(os.environ, {"PREVIEW_ROOT": str(out)}):
                wo = h.work_order("WO_GH.12")
                code, _, _ = h.cli("run", h.proj, "--pipeline", h.pipeline, "--work-order", wo, "--execute")
                self.assertEqual(code, 0)
                rep = h.report("WO_GH.12")
                order = [s["station"] for s in rep["steps"]]
                self.assertEqual(order.count("preview"), 2)
                self.assertEqual(order[order.index("preview") + 1], "reviewer-tests")
                self.assertEqual(order[order.index("preview") - 1], "builder")
                step = [s for s in rep["steps"] if s["station"] == "preview"][-1]
                self.assertEqual((step["status"], step["url"], step["preview_name"], step["attempt"]),
                                 ("completed", "https://wo-gh-12.demo.pages.dev", "wo-gh-12", 2))
                self.assertEqual((out / "wo-gh-12.txt").read_text(), "build 2\n", "the second attempt replaced the preview")
                self.assertEqual((out / "urls").read_text().split(), ["https://wo-gh-12.demo.pages.dev"] * 2)
                self.assertIn("https://wo-gh-12.demo.pages.dev", h.packet("reviewer-tests", 1))
                self.assertNotIn("demo.pages.dev", h.packet("builder", 1))
                self.assertEqual(h.calls().count("builder"), 2, "a preview is not an agent call")
                self.assertEqual(rep["efficiency"]["limits"].get("max_agent_calls"), 32)
                comment = subprocess.run([sys.executable, str(ROOT / "tools/line_comment.py"),
                                          str(h.proj / "runs/WO_GH.12/report.json"), "0"], capture_output=True, text=True).stdout
                self.assertIn("- Preview: https://wo-gh-12.demo.pages.dev", comment)
                code, text, _ = h.cli("preview-cleanup", h.proj, "WO_GH.12")
                self.assertEqual(code, 0)
                self.assertFalse((out / "wo-gh-12.txt").exists())
        self.assertEqual(line.preview_name("wo-gh-123456789-with-a-very-long-suffix-here"), "wo-gh-123456789-with-a-very")
        self.assertLessEqual(len(line.preview_name("x" * 80)), 28)
        with self.assertRaises(ValueError):
            line.preview_name("___")

    def test_failed_preview_only_warns_s7(self):
        """S7: a preview that does not deploy is a warning, and review goes on"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, SHORT, deploy={"preview": {"command": "echo no credentials >&2; exit 7", "url": "https://{preview_name}.x"}})
            rep = h.run("wo-s7b")
            step = [s for s in rep["steps"] if s["station"] == "preview"][0]
            self.assertEqual(step["status"], "failed")
            self.assertEqual(rep["verdict"], "approved")
            self.assertTrue(any("Preview deployment failed" in w for w in rep["warnings"]))
            self.assertNotIn("Preview deployment", h.packet("reviewer-tests", 1))
            self.assertIn("no credentials", (h.proj / "runs/wo-s7b/preview.output.md").read_text())
            self.assertEqual(h.cli("preview-cleanup", h.proj, "wo-s7b")[0], 0)  # nothing configured, nothing to do


class TestDeployTargets(unittest.TestCase):
    def cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            return main([str(a) for a in argv]), out.getvalue(), err.getvalue()

    def test_blueprint_deploy_targets_s8(self):
        """S8: a new project gets its platform's deploy, preview and provision commands"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "site"
            self.assertEqual(self.cli("new-project", proj, "--name", "My Shop", "--blueprint", "static-site",
                                      "--deploy-target", "cloudflare")[0], 0)
            cfg = json.loads((proj / "anvil.yaml").read_text())
            deploy = cfg["deploy"]
            self.assertEqual(deploy["command"], "npx wrangler pages deploy public --project-name my-shop --branch main")
            self.assertIn('--branch "$ANVIL_PREVIEW_NAME"', deploy["preview"]["command"])
            self.assertEqual(deploy["preview"]["url"], "https://{preview_name}.my-shop.pages.dev")
            self.assertEqual(deploy["provision"], ["npx wrangler pages project create my-shop --production-branch main"])
            self.assertEqual(cfg["health"]["base_url"], "https://my-shop.pages.dev")
            self.assertEqual(json.loads((proj / "anvil.json").read_text())["deploy_target"], "cloudflare")
            self.assertIn("stations", cfg, "the station settings are kept")

            pages = Path(tmp) / "pages"
            self.assertEqual(self.cli("new-project", pages, "--name", "Docs", "--blueprint", "static-site",
                                      "--deploy-target", "github")[0], 0)
            gh = json.loads((pages / "anvil.yaml").read_text())["deploy"]
            self.assertIn("deploy_github_pages.py", gh["command"])
            self.assertIn("--preview", gh["preview"]["command"]); self.assertIn("--cleanup", gh["preview"]["cleanup"])

            code, _, err = self.cli("new-project", Path(tmp) / "w", "--name", "W", "--blueprint", "cloudflare-worker",
                                    "--deploy-target", "github")
            self.assertEqual(code, 2)
            self.assertIn("no deploy target github", err)
            plain = Path(tmp) / "plain"
            self.assertEqual(self.cli("new-project", plain, "--name", "Plain", "--blueprint", "static-site")[0], 0)
            self.assertNotIn("deploy", json.loads((plain / "anvil.yaml").read_text()))

            # provision runs the configured commands in order and stops at the first failure
            cfg["deploy"]["provision"] = ["echo one >> provisioned", "echo two >> provisioned"]
            (proj / "anvil.yaml").write_text(json.dumps(cfg))
            self.assertEqual(self.cli("provision", proj)[0], 0)
            self.assertEqual((proj / "provisioned").read_text().split(), ["one", "two"])
            cfg["deploy"]["provision"] = ["exit 3", "echo never >> provisioned"]
            (proj / "anvil.yaml").write_text(json.dumps(cfg))
            self.assertEqual(self.cli("provision", proj)[0], 1)
            self.assertEqual((proj / "provisioned").read_text().split(), ["one", "two"])

    def test_github_pages_tool_s9(self):
        """S9: production at the root, previews beside it, each left alone by the other"""
        tool = [sys.executable, str(ROOT / "tools" / "deploy_github_pages.py")]
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            remote = tmp / "remote.git"
            subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
            site = tmp / "site"; (site / "css").mkdir(parents=True)
            (site / "index.html").write_text("v1"); (site / "css" / "a.css").write_text("a")
            env = {k: v for k, v in os.environ.items() if k not in ("GH_TOKEN", "GITHUB_TOKEN")}
            run = lambda *a: subprocess.run(tool + list(a) + ["--remote", str(remote)], capture_output=True, text=True, env=env)
            show = lambda path: subprocess.run(["git", "--git-dir", str(remote), "show", f"gh-pages:{path}"],
                                               capture_output=True, text=True)
            self.assertEqual(run(str(site)).returncode, 0)
            self.assertEqual(show("index.html").stdout, "v1")
            self.assertEqual(show(".nojekyll").returncode, 0)
            (site / "index.html").write_text("preview")
            r = run(str(site), "--preview", "wo-gh-12")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(show("previews/wo-gh-12/index.html").stdout, "preview")
            self.assertEqual(show("index.html").stdout, "v1", "a preview does not touch production")
            (site / "index.html").write_text("v2"); (site / "css" / "a.css").unlink()
            self.assertEqual(run(str(site)).returncode, 0)
            self.assertEqual(show("index.html").stdout, "v2")
            self.assertNotEqual(show("css/a.css").returncode, 0, "production is replaced, not merged")
            self.assertEqual(show("previews/wo-gh-12/index.html").stdout, "preview", "production keeps the previews")
            self.assertIn("Nothing changed", run(str(site)).stdout)
            self.assertEqual(run("--cleanup", "wo-gh-12").returncode, 0)
            self.assertNotEqual(show("previews/wo-gh-12/index.html").returncode, 0)
            self.assertEqual(show("index.html").stdout, "v2")
            self.assertIn("nothing to remove", run("--cleanup", "wo-gh-12").stdout)
            self.assertNotEqual(run(str(site), "--preview", "../escape").returncode, 0)
        source = (ROOT / "tools" / "deploy_github_pages.py").read_text()
        self.assertIn("GIT_CONFIG_VALUE_0", source)
        self.assertNotIn("x-access-token:{token}@", source)

    def test_workflow_keeps_tokens_from_stations_s10(self):
        """S10: no persisted credentials, no job level token, and previews are cleaned up"""
        text = (ROOT / ".github" / "workflows" / "anvil-line.yml").read_text()
        self.assertEqual(text.count("persist-credentials: false"), 2)
        job_env = text[text.index("    env:\n      ANTHROPIC_BASE_URL"):text.index("    steps:")]
        self.assertNotIn("GH_TOKEN", job_env); self.assertNotIn("CLOUDFLARE_API_TOKEN", job_env)
        self.assertIn("pull_request:\n    types: [closed]", text)
        self.assertIn("preview-cleanup", text)
        self.assertIn("startsWith(github.event.pull_request.head.ref, 'anvil/')", text)
        self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", text)
        self.assertIsNone(re.search(r"run:.*\$\{\{\s*github\.event\.pull_request\.head\.ref", text))


if __name__ == "__main__":
    unittest.main()
