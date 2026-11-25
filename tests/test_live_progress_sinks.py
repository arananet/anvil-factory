"""Live progress sinks: the github-issue sink and the sinks configuration (spec: live-progress-sinks, wo-gh-47).

Every run test drives a scripted sdlc-default run through the real runner
(anvil.runner.run_pipeline) with an in process fake runtime and a local HTTP
collector on 127.0.0.1. GITHUB_API_URL always points at the collector, so no
test reaches a real GitHub host.

Interface these tests pin where the spec leaves names to the builder:
  a state write is one call of anvil.observe.RunRecorder.state (spec Terms) or
      one call of anvil.observe.mark_crashed; the tests count writes by wrapping
      RunRecorder.state, never by mocking the sink;
  loading the configuration is anvil.config.load_anvil_config(path), which
      raises ValueError for a malformed observability.sinks (R1.1, R5.3);
  the comment table rows read "| <station> | <status> | <attempt> | <tokens> |".

Scenario map:
  S1  (test a)  test_s1_one_comment_created_then_only_edited
  S2  (test b)  test_s2_edit_before_builder_shows_builder_running
  S3  (test c)  test_s3_http_500_changes_nothing_but_one_export_error,
                test_s3_unreachable_api_gives_one_export_error,
                test_s3_silent_api_is_bounded_by_the_timeout
  S4  (test d)  test_s4_non_wo_gh_id_makes_no_call_and_records_reason,
                test_s4_missing_token_makes_no_call_and_records_reason,
                test_s4_missing_repository_records_reason
  S7  (test f)  test_s7_no_sink_configured_makes_no_call
  S8  (test g)  test_s8_malformed_sinks_fail_loading_naming_the_entry,
                test_s8_valid_sinks_load, test_s8_token_env_reaching_a_station_fails_loading
  S9  (test h)  test_s9_token_appears_only_in_the_authorization_header
  S10           test_s10_runtime_refused_is_shown_as_final_state,
                test_s10_unknown_exit_status_is_shown_verbatim
  S11           test_s11_crash_edits_the_same_comment
  S12           test_s12_factory_and_scaffold_enable_github_issue_only,
                test_s12_operations_documents_the_project_sink
  S13           test_s13_runner_holds_no_network_code,
                test_s13_frozen_paths_and_existing_tests_untouched (skips unless wo-gh-47)
  S14           test_s14_docs_decision_changelog_and_no_dashes
  S15           test_s15_headers_workflow_link_and_scalar_facts_only
Project sink scenarios S5, S6, S16 live in tests/test_live_progress_project_sink.py.
"""
import contextlib
import http.server
import io
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from anvil import observe  # noqa: E402
from anvil import runner as anvil_runner  # noqa: E402
from anvil.config import load_anvil_config  # noqa: E402
from anvil.executor import ExecutorError  # noqa: E402
from anvil.model import WorkOrder  # noqa: E402
from anvil.pipeline import load_pipeline  # noqa: E402
from anvil.scaffold import init_project  # noqa: E402
from anvil.stations import load_registry  # noqa: E402
from anvil.telemetry import summarize_steps  # noqa: E402

BASE_REF = "ae0bbfb2af95b41d96d8e2af7c9f8b787f54d83b"
REPO = "acme/demo"
MODEL = "claude-opus-5-5"
SMALL = {"input_tokens": 100, "output_tokens": 10}
OUTPUT_MARKER = "STATION_OUTPUT_MARKER_47_do_not_publish"
MARKER_RE = re.compile(r"^<!-- anvil-progress run_id=(\S+) -->")
TIMING_KEY_RE = re.compile(r"duration|elapsed|_ms$|_seconds$|_at$|timestamp")
SCRUBBED_ENV = ("GH_TOKEN", "GITHUB_TOKEN", "GITHUB_REPOSITORY", "GITHUB_API_URL", "GITHUB_GRAPHQL_URL",
                "GITHUB_RUN_ID", "GITHUB_SERVER_URL", "ANVIL_PROJECTS_TOKEN")
ISSUE_SINK = [{"type": "github-issue"}]


def sdlc_order():
    """The flat pipeline order of sdlc-default, read from the real pipeline file."""
    data = json.loads((ROOT / "pipelines" / "sdlc-default.json").read_text(encoding="utf-8"))
    order = []
    for stage in data["stages"]:
        order.extend(stage["parallel"] if "parallel" in stage else [stage["station"]])
    return order


# -- local GitHub stand in ---------------------------------------------------

class Collector:
    """A local stand in for the GitHub REST and GraphQL APIs that records every request.

    mode "ok" serves issue comments (list, create, edit) and, through `project`,
    a GraphQL Projects v2 board; mode "500" answers HTTP 500 to everything.
    """

    def __init__(self, mode="ok", project=None):
        self.mode = mode
        self.project = project
        self.requests = []  # (method, path, headers, body text)
        self.comments = {}  # id -> body
        self.next_id = 7001
        self.lock = threading.Lock()

    def __enter__(self):
        collector = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def _handle(self, method):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length).decode("utf-8") if length else ""
                with collector.lock:
                    collector.requests.append((method, self.path, dict(self.headers), body))
                    status, payload = collector.answer(method, self.path, body)
                data = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                self._handle("GET")

            def do_POST(self):
                self._handle("POST")

            def do_PATCH(self):
                self._handle("PATCH")

            def log_message(self, *args):
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()

    def answer(self, method, path, body):
        if self.mode == "500":
            return 500, {"message": "server error"}
        route = path.split("?", 1)[0]
        if route.endswith("/graphql") and self.project is not None:
            return 200, self.project.answer(json.loads(body or "{}"))
        if method == "GET" and re.fullmatch(r"/repos/[^/]+/[^/]+/issues/\d+/comments", route):
            return 200, [{"id": cid, "body": text} for cid, text in sorted(self.comments.items())]
        if method == "POST" and re.fullmatch(r"/repos/[^/]+/[^/]+/issues/\d+/comments", route):
            cid = self.next_id
            self.next_id += 1
            self.comments[cid] = json.loads(body)["body"]
            return 201, {"id": cid, "body": self.comments[cid]}
        match = re.fullmatch(r"/repos/[^/]+/[^/]+/issues/comments/(\d+)", route)
        if method == "PATCH" and match and int(match.group(1)) in self.comments:
            self.comments[int(match.group(1))] = json.loads(body)["body"]
            return 200, {"id": int(match.group(1)), "body": self.comments[int(match.group(1))]}
        return 404, {"message": "Not Found"}

    # views
    def writes(self):
        """POST and PATCH requests to the issue comments API, in order."""
        return [(m, p, h, b) for m, p, h, b in self.requests
                if m in ("POST", "PATCH") and "/issues/" in p]

    def bodies(self):
        return [json.loads(b)["body"] for _, _, _, b in self.writes()]


class Silent:
    """A TCP listener that accepts connections and never answers."""

    def __enter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(64)
        self.url = f"http://127.0.0.1:{self.sock.getsockname()[1]}"
        return self

    def __exit__(self, *exc):
        self.sock.close()


@contextlib.contextmanager
def github_env(**values):
    """os.environ without any GitHub variable from the host, plus the given values."""
    with mock.patch.dict(os.environ):
        for name in SCRUBBED_ENV:
            os.environ.pop(name, None)
        for name, value in values.items():
            if value is not None:
                os.environ[name] = value
        yield


# -- scripted run -----------------------------------------------------------

class Scripted:
    """Fake runtime in the line process: scripted per station, records every call."""
    name = "fake"

    def __init__(self, run_dir, script=None, verdicts=None, on_call=None):
        self.run_dir = Path(run_dir)
        self.script = script or {}
        self.verdicts = verdicts or {}
        self.on_call = on_call
        self.calls = []

    def execute(self, text, station_id, **kwargs):
        self.calls.append(station_id)
        if self.on_call:
            self.on_call(station_id)
        behaviour = self.script.get(station_id)
        if callable(behaviour):
            return behaviour()
        if station_id.startswith("reviewer"):
            verdict = self.verdicts.get(station_id, "pass")
            (self.run_dir / f"{station_id}.review.json").write_text(json.dumps(
                {"station": station_id, "verdict": verdict, "findings": ["all good"]}), encoding="utf-8")
        output = f"{OUTPUT_MARKER} from {station_id}"
        if station_id == "intake":
            output = json.dumps({"intake_outcome": {"outcome": "accepted"}, "note": OUTPUT_MARKER})
        return {"output": output, "usage": dict(SMALL), "model": MODEL}


def make_project(tmp, sinks=ISSUE_SINK, timeout_seconds=None, env_deny=None, name="proj"):
    """A scaffolded project; sinks=None removes observability.sinks entirely."""
    project = init_project(Path(tmp) / name, "Sinks demo")
    path = project / "anvil.yaml"
    config = json.loads(path.read_text(encoding="utf-8"))
    obs = dict(config.get("observability") or {})
    if sinks is None:
        obs.pop("sinks", None)
    else:
        obs["sinks"] = sinks
    if timeout_seconds is not None:
        obs["timeout_seconds"] = timeout_seconds
    config["observability"] = obs
    if env_deny:
        config.setdefault("runtime", {})
        config["runtime"] = dict(config["runtime"] or {}, env_deny=list(env_deny))
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return project


class Run:
    """The outcome of one scripted run: report, state writes, error."""

    def __init__(self, project, wo_id):
        self.project = Path(project)
        self.wo_id = wo_id
        self.run_dir = self.project / "runs" / wo_id
        self.report = None
        self.error = None
        self.writes = []  # (state record, seconds the state write took)
        self.counts = []  # counter() after each state write, when a counter is given
        self.runtime = None

    def state(self):
        return json.loads((self.run_dir / "state.json").read_text(encoding="utf-8"))

    def events(self):
        return [json.loads(line) for line in (self.run_dir / "events.jsonl").read_text().splitlines()]

    def saved_report(self):
        return json.loads((self.run_dir / "report.json").read_text(encoding="utf-8"))


def run_line(project, wo_id, script=None, verdicts=None, on_call=None, max_loopbacks=2, pipeline=None,
             expect_error=False, finish_hook=None, counter=None):
    """Drive the real runner; count state writes by wrapping RunRecorder.state."""
    result = Run(project, wo_id)
    reg = load_registry(ROOT / "stations")
    pipe = load_pipeline(pipeline or (ROOT / "pipelines" / "sdlc-default.json"), known_stations=set(reg.ids()))
    runtime = result.runtime = Scripted(result.run_dir, script, verdicts, on_call)
    original_state = observe.RunRecorder.state
    original_finish = observe.RunRecorder.finish

    def counting_state(self, *args, **kwargs):
        started = time.monotonic()
        record = original_state(self, *args, **kwargs)
        result.writes.append((record, time.monotonic() - started))
        if counter is not None:
            result.counts.append(counter())
        return record

    def hooked_finish(self, steps, report):
        return original_finish(self, steps, finish_hook(dict(report)) if finish_hook else report)

    out = io.StringIO()
    with mock.patch.object(observe.RunRecorder, "state", counting_state), \
            mock.patch.object(observe.RunRecorder, "finish", hooked_finish), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            report = anvil_runner.run_pipeline(project, pipe, WorkOrder(id=wo_id, kind="feature", title="Sinks"),
                                               registry=reg, executor=runtime, max_loopbacks=max_loopbacks)
            result.report = report.to_dict()
        except Exception as exc:  # noqa: BLE001 - the crash scenario expects it
            if not expect_error:
                raise
            result.error = exc
    return result


def table_rows(body):
    """{station: (status, attempt, tokens)} from the comment's station table."""
    rows = {}
    for line in body.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.strip().startswith("|") and len(cells) == 4 and cells[0] not in ("Station", "") \
                and not set(cells[0]) <= set("-: "):
            rows[cells[0]] = tuple(cells[1:])
    return rows


def flatten(value, prefix=""):
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            out.update(flatten(item, f"{prefix}/{key}"))
        return out
    if isinstance(value, list):
        out = {f"{prefix}#len": len(value)}
        for index, item in enumerate(value):
            out.update(flatten(item, f"{prefix}[{index}]"))
        return out
    return {prefix: value}


# -- S1, S2: one comment, edited at every state write -------------------------

class IssueCommentLifecycle(unittest.TestCase):
    def run_s1(self, tmp, sink, extra_env=None, on_call=None):
        project = make_project(tmp)
        env = {"GITHUB_REPOSITORY": REPO, "GH_TOKEN": "ghs_test_token_s1", "GITHUB_API_URL": sink.url}
        env.update(extra_env or {})
        with github_env(**env):
            return run_line(project, "wo-gh-901", on_call=on_call)

    def test_s1_one_comment_created_then_only_edited(self):
        """S1 (test a): exactly one POST, then a PATCH of that comment for every later state write"""
        with tempfile.TemporaryDirectory() as tmp, Collector() as sink:
            run = self.run_s1(tmp, sink)
            self.assertEqual(run.report["verdict"], "approved")
            writes = sink.writes()
            posts = [w for w in writes if w[0] == "POST"]
            self.assertEqual(len(posts), 1, [w[:2] for w in writes])
            self.assertEqual(posts[0][1].split("?")[0], "/repos/acme/demo/issues/901/comments")
            self.assertEqual(writes[0][0], "POST", "the first write creates the comment")
            self.assertEqual(len(sink.comments), 1)
            comment_id = list(sink.comments)[0]
            for method, path, _, _ in writes[1:]:
                self.assertEqual((method, path.split("?")[0]),
                                 ("PATCH", f"/repos/acme/demo/issues/comments/{comment_id}"))
            self.assertEqual(len(writes), len(run.writes), "one request per state write")
            last = sink.bodies()[-1]
            self.assertTrue(last.startswith(f"<!-- anvil-progress run_id={run.report['run_id']} -->"), last[:80])
            self.assertIn("ANVIL progress: wo-gh-901", last)
            self.assertIn("Pipeline: sdlc-default", last)
            self.assertIn("Verdict: approved", last)
            self.assertIn("State: finished", last)
            self.assertIn("Exit status: completed", last)
            rows = table_rows(last)
            self.assertEqual(list(rows), sdlc_order(), "one row per station in pipeline order")
            executed = [s["station"] for s in run.report["steps"] if s["status"] == "executed"]
            self.assertTrue(executed)
            for station in executed:
                self.assertEqual(rows[station][0], "done", station)
            self.assertEqual(sink.comments[comment_id], last)
            final = run.state()
            self.assertEqual(final["sinks"], [{"type": "github-issue", "active": True, "reason": None}])
            self.assertEqual(final["export_errors"], [])
            self.assertEqual(final["exit_status"], "completed")

    def test_s2_edit_before_builder_shows_builder_running(self):
        """S2 (test b): the edit sent before the builder shows it running and later stations pending"""
        seen = {}
        with tempfile.TemporaryDirectory() as tmp, Collector() as sink:
            def snapshot(station):
                if station == "builder" and "body" not in seen:
                    seen["body"] = sink.bodies()[-1]
                    seen["state"] = json.loads((Path(tmp) / "proj/runs/wo-gh-901/state.json").read_text())
            run = self.run_s1(tmp, sink, on_call=snapshot)
        body = seen["body"]
        rows = table_rows(body)
        self.assertRegex(body, r"(?m)^\| builder \| running \|")
        self.assertIn("State: running", body)
        for station in ("intake", "spec-writer", "test-writer"):
            self.assertEqual(rows[station][0], "done", station)
            self.assertEqual(rows[station][1], "1", station)
        order = sdlc_order()
        later = order[order.index("checks-gate"):order.index("approver") + 1]
        for station in later:
            self.assertEqual(rows[station], ("pending", "-", "-"), station)
        self.assertNotIn("Verdict:", body)
        state = seen["state"]
        self.assertEqual(state["stations"], order)
        self.assertEqual(state["current_station"], "builder")
        self.assertTrue(state["steps"])
        for step in state["steps"]:
            self.assertIn("total_tokens", step)
        expected = [summarize_steps([s])["total_tokens"] for s in run.report["steps"][:3]]
        self.assertEqual([s["station"] for s in run.report["steps"][:3]], ["intake", "spec-writer", "test-writer"])
        self.assertEqual([s["total_tokens"] for s in state["steps"]], expected)
        self.assertEqual(rows["intake"][2], str(expected[0]))


# -- S3: failures never decide a run ------------------------------------------

class SinkFailures(unittest.TestCase):
    def baseline(self, tmp, name):
        project = make_project(tmp, sinks=[], name=name)
        with github_env():
            return run_line(project, "wo-gh-901")

    def test_s3_http_500_changes_nothing_but_one_export_error(self):
        """S3 (test c): an API answering 500 leaves verdict, report and events as without the sink"""
        with tempfile.TemporaryDirectory() as tmp, Collector(mode="500") as sink:
            first, second = self.baseline(tmp, "base1"), self.baseline(tmp, "base2")
            base_a, base_b = flatten(first.saved_report()), flatten(second.saved_report())
            volatile = {k for k in set(base_a) | set(base_b) if base_a.get(k) != base_b.get(k)}
            # Wall clock figures are volatile even when two baselines happen to agree on them.
            volatile |= {k for k in set(base_a) | set(base_b) if TIMING_KEY_RE.search(k.rsplit("/", 1)[-1])}
            project = make_project(tmp, name="sinkrun")
            with github_env(GITHUB_REPOSITORY=REPO, GH_TOKEN="ghs_test_token_s3", GITHUB_API_URL=sink.url):
                run = run_line(project, "wo-gh-901")
            self.assertTrue(sink.requests, "the sink did call the failing API")
            self.assertEqual(run.report["verdict"], first.report["verdict"])
            with_sink = flatten(run.saved_report())
            self.assertEqual(set(with_sink) - volatile, set(base_a) - volatile)
            for key in set(base_a) - volatile:
                self.assertEqual(with_sink[key], base_a[key], key)
            self.assertEqual([e["event"] for e in run.events()], [e["event"] for e in first.events()])
            self.assertEqual(run.state()["export_errors"], ["github-issue: HTTP 500"])

    def test_s3_unreachable_api_gives_one_export_error(self):
        """S3 (test c): nothing listening on the API port: approved run, one github-issue export error"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, timeout_seconds=1)
            with github_env(GITHUB_REPOSITORY=REPO, GH_TOKEN="ghs_test_token_s3b",
                            GITHUB_API_URL="http://127.0.0.1:9"):
                run = run_line(project, "wo-gh-901")
            self.assertEqual(run.report["verdict"], "approved")
            errors = run.state()["export_errors"]
            self.assertEqual(len(errors), 1, errors)
            self.assertTrue(errors[0].startswith("github-issue: "), errors)
            self.assertNotIn("127.0.0.1", errors[0])

    def test_s3_silent_api_is_bounded_by_the_timeout(self):
        """S3 (test c, R1.7): a server that never answers costs at most about timeout_seconds per write"""
        with tempfile.TemporaryDirectory() as tmp, Silent() as silent:
            pipeline = Path(tmp) / "short.json"
            pipeline.write_text(json.dumps({"name": "short", "stages": [
                {"station": "intake"}, {"station": "builder"}, {"station": "approver"}]}))
            project = make_project(tmp, timeout_seconds=1)
            with github_env(GITHUB_REPOSITORY=REPO, GH_TOKEN="ghs_test_token_s3c", GITHUB_API_URL=silent.url):
                run = run_line(project, "wo-gh-901", pipeline=pipeline)
            self.assertTrue(run.writes)
            self.assertLess(max(seconds for _, seconds in run.writes), 2.5,
                            [round(s, 2) for _, s in run.writes])
            errors = run.state()["export_errors"]
            self.assertEqual(len(errors), 1, errors)
            self.assertTrue(errors[0].startswith("github-issue: "), errors)


# -- S4, S7: inactive sinks and no sinks make no call -------------------------

class InactiveAndAbsent(unittest.TestCase):
    def assert_inactive(self, wo_id, reason, **env):
        with tempfile.TemporaryDirectory() as tmp, Collector() as sink:
            project = make_project(tmp)
            with github_env(GITHUB_API_URL=sink.url, **env):
                run = run_line(project, wo_id)
            self.assertEqual(sink.requests, [])
            final = run.state()
            self.assertEqual(final["sinks"], [{"type": "github-issue", "active": False, "reason": reason}])
            self.assertEqual(final["export_errors"], [])
            for record, _ in run.writes:
                if "sinks" in record:
                    self.assertLessEqual(len(record["sinks"]), 1)

    def test_s4_non_wo_gh_id_makes_no_call_and_records_reason(self):
        """S4 (test d): work order wo-s4 is not wo-gh-<number>: zero requests, one reason"""
        self.assert_inactive("wo-s4", "work order id is not wo-gh-<number>",
                             GITHUB_REPOSITORY=REPO, GH_TOKEN="ghs_test_token_s4")

    def test_s4_missing_token_makes_no_call_and_records_reason(self):
        """S4 (test d): wo-gh-902 with GH_TOKEN unset: zero requests, reason names the variable"""
        self.assert_inactive("wo-gh-902", "GH_TOKEN is not set", GITHUB_REPOSITORY=REPO)

    def test_s4_missing_repository_records_reason(self):
        """S4 (R2.2): GITHUB_REPOSITORY unset: zero requests and its reason"""
        self.assert_inactive("wo-gh-902", "GITHUB_REPOSITORY is not set", GH_TOKEN="ghs_test_token_s4b")

    def test_s7_no_sink_configured_makes_no_call(self):
        """S7 (test f): observability.sinks removed: zero requests although every variable is set"""
        for sinks in (None, []):
            with self.subTest(sinks=sinks), tempfile.TemporaryDirectory() as tmp, Collector() as sink:
                project = make_project(tmp, sinks=sinks)
                with github_env(GITHUB_REPOSITORY=REPO, GH_TOKEN="ghs_test_token_s7",
                                GITHUB_API_URL=sink.url, GITHUB_GRAPHQL_URL=sink.url + "/graphql"):
                    run = run_line(project, "wo-gh-903")
                self.assertEqual(run.report["verdict"], "approved")
                self.assertEqual(sink.requests, [])
                self.assertEqual(run.state()["sinks"], [])


# -- S8: validation of observability.sinks ------------------------------------

class SinksValidation(unittest.TestCase):
    def load(self, sinks, runtime=None):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "anvil.yaml"
            config = {"version": 1, "observability": {"sinks": sinks}}
            if runtime is not None:
                config["runtime"] = runtime
            path.write_text(json.dumps(config), encoding="utf-8")
            return load_anvil_config(path)

    def assert_rejected(self, sinks, *words, runtime=None):
        with self.assertRaises(ValueError) as caught:
            self.load(sinks, runtime)
        for word in words:
            self.assertIn(word, str(caught.exception))
        return str(caught.exception)

    def test_s8_malformed_sinks_fail_loading_naming_the_entry(self):
        """S8 (test g): a malformed sinks list fails loading and names the entry and the key or type"""
        self.assert_rejected([{"type": "github-issue"}, {"type": "github-project", "owner": "acme"}],
                             "observability.sinks[1]", "number")
        self.assert_rejected([{"type": "slack"}], "observability.sinks[0]", "slack")
        message = self.assert_rejected({"type": "github-issue"}, "observability.sinks")
        self.assertNotIn("observability.sinks[", message)
        self.assert_rejected(["github-issue"], "observability.sinks[0]")
        self.assert_rejected([{"token_env": "GH_TOKEN"}], "observability.sinks[0]", "type")
        self.assert_rejected([{"type": "github-issue", "channel": "x"}], "observability.sinks[0]", "channel")
        self.assert_rejected([{"type": "github-issue", "token_env": ""}], "observability.sinks[0]", "token_env")
        project = {"type": "github-project", "owner": "acme", "number": 3}
        self.assert_rejected([dict(project, number=True)], "observability.sinks[0]", "number")
        self.assert_rejected([dict(project, number=0)], "observability.sinks[0]", "number")
        self.assert_rejected([dict(project, owner="")], "observability.sinks[0]", "owner")
        self.assert_rejected([dict(project, owner_type="team")], "observability.sinks[0]", "owner_type")
        self.assert_rejected([dict(project, columns={"deploy": "Shipping"})], "observability.sinks[0]", "deploy")
        self.assert_rejected([{"type": "github-issue"}, dict(project, status_field="")],
                             "observability.sinks[1]", "status_field")

    def test_s8_valid_sinks_load(self):
        """S8 (R1.1): absent, empty and well formed sinks lists load"""
        self.assertEqual(self.load([])["observability"]["sinks"], [])
        self.assertEqual(self.load([{"type": "github-issue"}])["observability"]["sinks"], [{"type": "github-issue"}])
        full = {"type": "github-project", "owner": "acme", "number": 3, "owner_type": "organization",
                "status_field": "Stage", "token_env": "ANVIL_PROJECTS_TOKEN",
                "columns": {"human": "Waiting on owner", "done": "Shipped"}}
        loaded = self.load([{"type": "github-issue"}, full], runtime={"env_deny": ["ANVIL_PROJECTS_TOKEN"]})
        self.assertEqual(loaded["observability"]["sinks"][1], full)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "anvil.yaml"
            path.write_text(json.dumps({"version": 1, "observability": {"timeout_seconds": 2}}))
            self.assertEqual(load_anvil_config(path)["observability"], {"timeout_seconds": 2})

    def test_s8_token_env_reaching_a_station_fails_loading(self):
        """S8 (R5.3): a token_env a station could see fails loading; env_deny makes it pass"""
        entry = [{"type": "github-issue", "token_env": "MY_PROJECT_TOKEN"}]
        self.assert_rejected(entry, "observability.sinks[0]", "token_env")
        self.assertEqual(self.load(entry, runtime={"env_deny": ["MY_PROJECT_TOKEN"]})["observability"]["sinks"],
                         entry)
        self.assert_rejected([{"type": "github-issue"}], "observability.sinks[0]", "token_env",
                             runtime={"env_keep": ["GH_TOKEN"]})


# -- S9, S15: tokens and scalar facts ------------------------------------------

class TokensAndContent(unittest.TestCase):
    SENTINEL = "ghs_SENTINEL_47_0123456789"

    def test_s9_token_appears_only_in_the_authorization_header(self):
        """S9 (test h): the token is in the Authorization header only, never in a body or a run file"""
        with tempfile.TemporaryDirectory() as tmp, Collector() as sink:
            project = make_project(tmp)
            with github_env(GITHUB_REPOSITORY=REPO, GH_TOKEN=self.SENTINEL, GITHUB_API_URL=sink.url):
                run = run_line(project, "wo-gh-901")
            self.assertTrue(sink.requests)
            for method, path, headers, body in sink.requests:
                lowered = {k.lower(): v for k, v in headers.items()}
                self.assertEqual(lowered.get("authorization"), f"Bearer {self.SENTINEL}", (method, path))
                self.assertNotIn(self.SENTINEL, body)
                self.assertNotIn(self.SENTINEL, path)
            files = [p for p in run.run_dir.rglob("*") if p.is_file()]
            self.assertTrue({"state.json", "events.jsonl", "report.json"} <= {p.name for p in files})
            for path in files:
                self.assertNotIn(self.SENTINEL.encode(), path.read_bytes(), str(path))

    def test_s15_headers_workflow_link_and_scalar_facts_only(self):
        """S15 (R2.3, R2.6): API headers, the workflow run link, and no path, detail or station output"""
        with tempfile.TemporaryDirectory() as tmp, Collector() as sink:
            project = make_project(tmp)
            with github_env(GITHUB_REPOSITORY=REPO, GH_TOKEN="ghs_test_token_s15", GITHUB_API_URL=sink.url,
                            GITHUB_RUN_ID="4242", GITHUB_SERVER_URL="https://github.example"):
                run = run_line(project, "wo-gh-901")
            self.assertTrue(sink.requests)
            for method, path, headers, _ in sink.requests:
                lowered = {k.lower(): v for k, v in headers.items()}
                self.assertTrue(path.startswith("/repos/acme/demo/issues/"), path)
                self.assertEqual(lowered.get("accept"), "application/vnd.github+json")
                self.assertEqual(lowered.get("user-agent"), "anvil-progress")
            bodies = sink.bodies()
            self.assertIn("Workflow run: https://github.example/acme/demo/actions/runs/4242", bodies[-1])
            self.assertIn("Loopbacks: 0", bodies[-1])
            self.assertRegex(bodies[-1], r"(?m)^Updated: \S+")
            self.assertRegex(bodies[-1], r"(?m)^Tokens: \d+")
            self.assertRegex(bodies[-1], r"(?m)^Cost: (\$\d+\.\d{4}|not priced)")
            details = {str(s.get("detail")) for s in run.report["steps"] if len(str(s.get("detail") or "")) >= 20}
            for body in bodies:
                self.assertNotIn(str(project), body)
                self.assertNotIn(str(Path(tmp)), body)
                self.assertNotIn(OUTPUT_MARKER, body)
                for detail in details:
                    self.assertNotIn(detail, body)

    def test_s15_no_workflow_link_without_run_id(self):
        """S15 (R2.5): without GITHUB_RUN_ID the body carries no workflow run line"""
        with tempfile.TemporaryDirectory() as tmp, Collector() as sink:
            project = make_project(tmp)
            with github_env(GITHUB_REPOSITORY=REPO, GH_TOKEN="ghs_test_token_s15b", GITHUB_API_URL=sink.url):
                run_line(project, "wo-gh-901")
            self.assertTrue(sink.bodies())
            self.assertNotIn("Workflow run:", sink.bodies()[-1])


# -- S10, S11: every final state ----------------------------------------------

REFUSED_402 = ("command executor exited 2: claude_station: claude exited 1 for station builder: "
               "is_error=True; subtype=success; api_error_status=402; stop_reason=stop_sequence; "
               "num_turns=2; result=API Error: 402 Insufficient unified billing balance for this request. | {}")


def refuse():
    raise ExecutorError(REFUSED_402, {"usage": dict(SMALL)})


class FinalStates(unittest.TestCase):
    def test_s10_runtime_refused_is_shown_as_final_state(self):
        """S10: a runtime_refused stop shows State finished, the exit status, and later stations not run"""
        with tempfile.TemporaryDirectory() as tmp, Collector() as sink:
            project = make_project(tmp)
            with github_env(GITHUB_REPOSITORY=REPO, GH_TOKEN="ghs_test_token_s10", GITHUB_API_URL=sink.url):
                run = run_line(project, "wo-gh-901", script={"builder": refuse})
            self.assertEqual(run.report.get("exit_status"), "runtime_refused")
            last = sink.bodies()[-1]
            self.assertIn("State: finished", last)
            self.assertIn("Exit status: runtime_refused", last)
            self.assertIn(f"Verdict: {run.report['verdict']}", last)
            rows = table_rows(last)
            self.assertEqual(rows["builder"][0], "failed")
            self.assertEqual(rows["intake"][0], "done")
            order = sdlc_order()
            for station in order[order.index("checks-gate"):]:
                self.assertEqual(rows[station][0], "not run", station)
            self.assertNotIn("402 Insufficient", last)
            self.assertEqual(run.state()["exit_status"], "runtime_refused")

    def test_s10_unknown_exit_status_is_shown_verbatim(self):
        """S10 (R2.5): an exit status the sink has never heard of is shown as is"""
        with tempfile.TemporaryDirectory() as tmp, Collector() as sink:
            project = make_project(tmp)
            with github_env(GITHUB_REPOSITORY=REPO, GH_TOKEN="ghs_test_token_s10b", GITHUB_API_URL=sink.url):
                run_line(project, "wo-gh-901",
                         finish_hook=lambda report: dict(report, exit_status="some_future_status"))
            self.assertIn("Exit status: some_future_status", sink.bodies()[-1])
            self.assertIn("State: finished", sink.bodies()[-1])

    def test_s11_crash_edits_the_same_comment(self):
        """S11: the crashed write from mark_crashed edits the run's comment, without the error text"""
        secret = "the runner lost its disk CRASH_TEXT_47"

        def explode():
            raise RuntimeError(secret)

        with tempfile.TemporaryDirectory() as tmp, Collector() as sink:
            project = make_project(tmp)
            with github_env(GITHUB_REPOSITORY=REPO, GH_TOKEN="ghs_test_token_s11", GITHUB_API_URL=sink.url):
                run = run_line(project, "wo-gh-901", script={"builder": explode}, expect_error=True)
            self.assertIsInstance(run.error, RuntimeError)
            self.assertEqual(run.state()["state"], "crashed")
            writes = sink.writes()
            self.assertEqual([w[0] for w in writes].count("POST"), 1)
            self.assertEqual(len(sink.comments), 1)
            comment_id = list(sink.comments)[0]
            method, path, _, body = writes[-1]
            self.assertEqual((method, path.split("?")[0]), ("PATCH", f"/repos/acme/demo/issues/comments/{comment_id}"))
            last = json.loads(body)["body"]
            self.assertIn("State: crashed", last)
            self.assertNotIn("CRASH_TEXT_47", last)
            self.assertNotIn("RuntimeError", last)
            self.assertEqual(MARKER_RE.match(last).group(1), run.state()["run_id"])
            self.assertNotIn("CRASH_TEXT_47", json.dumps(run.state()["export_errors"]))


# -- S12 to S14: what ships, guardrails, docs --------------------------------

class Shipping(unittest.TestCase):
    def test_s12_factory_and_scaffold_enable_github_issue_only(self):
        """S12 (R4.1, R4.2): factory anvil.yaml and anvil init both enable github-issue and not github-project"""
        factory = json.loads((ROOT / "anvil.yaml").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            scaffolded = json.loads((init_project(Path(tmp) / "fresh", "Fresh") / "anvil.yaml").read_text())
        for name, config in (("factory", factory), ("scaffold", scaffolded)):
            sinks = (config.get("observability") or {}).get("sinks")
            self.assertIsInstance(sinks, list, name)
            self.assertIn({"type": "github-issue"}, sinks, name)
            self.assertFalse([s for s in sinks if s.get("type") == "github-project"], name)
        self.assertGreater(factory["efficiency"]["max_run_tokens"], 0, "other keys kept")
        load_anvil_config(ROOT / "anvil.yaml")  # the factory's own config passes its validation

    def test_s12_operations_documents_the_project_sink(self):
        """S12 (R4.3): docs/OPERATIONS.md documents the github-project sink"""
        text = (ROOT / "docs" / "OPERATIONS.md").read_text(encoding="utf-8")
        for word in ("github-project", "github-issue", "status_field", "Needs human", "token_env", "env_deny"):
            self.assertIn(word, text)
        self.assertIn("sink", (ROOT / "docs" / "EXECUTION.md").read_text(encoding="utf-8").lower())

    def test_s13_runner_holds_no_network_code(self):
        """S13 (R1.10): anvil/runner.py imports no network module and never says retry; sinks live in anvil/sinks.py

        Note: runner.py at the base ref already imports urllib.parse (URL parsing, no network),
        so this test pins the network modules rather than the bare word urllib.
        """
        text = (ROOT / "anvil" / "runner.py").read_text(encoding="utf-8")
        for word in ("urllib.request", "urlopen", "http.client", "import socket", "retry"):
            self.assertNotIn(word, text)
        sinks = ROOT / "anvil" / "sinks.py"
        self.assertTrue(sinks.is_file(), "the sink module beside the recorder")
        self.assertIn("sinks", (ROOT / "anvil" / "observe.py").read_text(encoding="utf-8"))
        import inspect
        self.assertEqual(list(inspect.signature(observe.mark_crashed).parameters), ["run_dir", "error"])

    @unittest.skipUnless(os.environ.get("ANVIL_WORK_ORDER_ID") == "wo-gh-47", "facts about the wo-gh-47 run only")
    def test_s13_frozen_paths_and_existing_tests_untouched(self):
        """S13 (R4.4, R6.2, R6.3): frozen paths and every existing test file match the base ref"""
        def git(*args):
            return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        frozen = git("diff", BASE_REF, "--", "tools/line_comment.py", ".github/workflows", "pipelines",
                     "anvil.json", "anvil/executor.py")
        self.assertEqual(frozen, "")
        changed = git("diff", "--name-status", BASE_REF, "--", "tests").splitlines()
        touched = [line for line in changed if not line.startswith("A")]
        self.assertEqual(touched, [], "existing test files modified or deleted")

    def test_s14_docs_decision_changelog_and_no_dashes(self):
        """S14 (R4.5): README section of at most 15 lines, the decision record, the changelog, no dashes"""
        readme = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
        starts = [i for i, line in enumerate(readme) if re.match(r"^#+\s+Watching a run\s*$", line)]
        self.assertEqual(len(starts), 1, "one Watching a run section")
        level = len(readme[starts[0]]) - len(readme[starts[0]].lstrip("#"))
        section = []
        for line in readme[starts[0] + 1:]:
            match = re.match(r"^(#+)\s", line)
            if match and len(match.group(1)) <= level:
                break
            section.append(line)
        while section and not section[-1].strip():
            section.pop()
        self.assertLessEqual(len(section), 15)
        self.assertIn("docs/OPERATIONS.md", "\n".join(section))
        self.assertIn("comment", "\n".join(section).lower())
        decision = ROOT / "brain" / "decisions" / "0015-live-progress-sinks.md"
        self.assertTrue(decision.is_file())
        self.assertIn("live-progress-sinks", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
        produced = [ROOT / "anvil" / "sinks.py", decision, Path(__file__),
                    ROOT / "tests" / "test_live_progress_project_sink.py"]
        for path in produced:
            self.assertTrue(path.is_file(), str(path))
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("\u2014", text, str(path))
            self.assertNotIn("\u2013", text, str(path))

    @unittest.skipUnless(os.environ.get("ANVIL_WORK_ORDER_ID") == "wo-gh-47", "facts about the wo-gh-47 run only")
    def test_s14_no_dashes_in_lines_this_order_adds(self):
        """S14: no line this order adds to any file carries an em or en dash"""
        diff = subprocess.run(["git", "diff", BASE_REF, "--", ".", ":(exclude)runs"], cwd=ROOT,
                              capture_output=True, text=True, check=True).stdout
        added = [line for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")]
        self.assertEqual([line for line in added if "\u2014" in line or "\u2013" in line], [])


if __name__ == "__main__":
    unittest.main()
