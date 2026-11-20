"""Continuous run accounting (spec: continuous-run-accounting, work order wo-gh-41).

Every test drives a scripted sdlc-default run through the real runner
(anvil.runner.run_pipeline) with a fake runtime: no network, no model.

Interface these tests pin where the spec leaves names to the builder:
  report["checkpoint"] = {"last_completed_station": str, "elapsed_ms": number,
                          "usage_so_far": {"total_tokens": ...}}  (R1.1; usage_so_far
      follows anvil.telemetry.summarize_steps over the steps recorded so far)
  report["exit_status"] in EXIT_STATUSES, report["termination_reason"] non empty (R2.2)
  a station that never ran has a step {"station": id, "status": "not_run"} (R2.3)
  report["budget_death"] = {"measured_tokens": int, "max_run_tokens": int,
                            "station_in_flight": str}  (R2.4)
  anvil.runner.render_swimlane(report_dict) -> str  (R3.1, the swimlane renderer
      callable on a report.json alone)
  a turn limit death is the runtime failure the claude CLI reports as
      subtype=error_max_turns (the wrapper puts that reason in the executor error)
  checkpoint writes go through os.replace or os.rename onto report.json (R1.2);
      the tests observe them by wrapping those two functions, never by mocking the runner.

Scenario map:
  S1 (R2.1, R2.3, R2.4)  test_s1_budget_death_mid_builder_leaves_complete_report
  S2 (R2.1, R2.2, R2.3)  test_s2_station_timeout_death_is_recorded,
                         test_s2_uncaught_error_death_is_recorded,
                         test_s2_timeout_and_error_statuses_differ
  S3 (R1.1, R1.3)        test_s3_checkpoints_accumulate_during_healthy_run,
                         test_s3_final_report_is_last_checkpoint_plus_verdict
  S4 (R3.1, R3.2)        test_s4_killed_record_renders_without_a_run,
                         test_s4_later_run_preserves_killed_record_in_history
  S5 (R2.1, R2.2)        test_s5_sigterm_completes_the_record, test_s5_sigint_completes_the_record
  S6 (R1.2, R2.5)        test_s6_checkpoint_writes_are_atomic,
                         test_s6_failed_rename_keeps_previous_report
  S7 (R3.3)              test_s7_legacy_report_still_renders
  S8 (R2.1, R2.2, R2.3)  test_s8_turn_limit_stop, test_s8_checks_gate_stop, test_s8_intake_rejected_stop
  S9 (R4.2)              test_s9_existing_test_files_untouched, test_s9_no_dashes_in_this_file
"""
import contextlib
import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
for entry in (str(ROOT), str(ROOT / "tools")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from anvil import runner as anvil_runner  # noqa: E402
from anvil.executor import ExecutorError  # noqa: E402
from anvil.model import WorkOrder  # noqa: E402
from anvil.pipeline import load_pipeline  # noqa: E402
from anvil.scaffold import init_project  # noqa: E402
from anvil.stations import load_registry  # noqa: E402
from anvil.statuspage import render_status_page  # noqa: E402
from anvil.telemetry import normalize_usage, summarize_steps  # noqa: E402
import line_comment  # noqa: E402

EXIT_STATUSES = {"completed", "budget_exceeded", "station_timeout", "turn_limit",
                 "checks_stopped", "intake_stopped", "error", "signal"}
CAP = 6000000
BUILDER_TOKENS = 6359529
MODEL = "claude-opus-5-5"
SMALL = {"input_tokens": 100, "output_tokens": 10}
WO = "wo-cra"


def registry():
    return load_registry(ROOT / "stations")


def sdlc_pipeline(reg):
    return load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))


def make_project(tmp, max_run_tokens=CAP, checks=None, max_runtime_turns=None):
    project = init_project(Path(tmp) / "project", "Accounting demo")
    config = json.loads((project / "anvil.yaml").read_text(encoding="utf-8"))
    config.setdefault("efficiency", {})["max_run_tokens"] = max_run_tokens
    if max_runtime_turns is not None:
        config["efficiency"]["max_runtime_turns"] = max_runtime_turns
    (project / "anvil.yaml").write_text(json.dumps(config), encoding="utf-8")
    if checks is not None:
        anvil_json = json.loads((project / "anvil.json").read_text(encoding="utf-8"))
        anvil_json["checks"] = checks
        (project / "anvil.json").write_text(json.dumps(anvil_json), encoding="utf-8")
    return project


class Scripted:
    """Fake runtime: scripted per station, records every call it receives."""
    name = "fake"

    def __init__(self, script=None, on_call=None):
        self.calls = []
        self.script = script or {}
        self.on_call = on_call

    def execute(self, text, station_id, **kwargs):
        self.calls.append(station_id)
        if self.on_call:
            self.on_call(station_id)
        behaviour = self.script.get(station_id)
        if callable(behaviour):
            return behaviour()
        output = "done"
        if station_id == "intake":
            output = json.dumps({"intake_outcome": {"outcome": "accepted"}})
        return {"output": output, "usage": dict(SMALL), "model": MODEL}


def budget_kill():
    raise ExecutorError("command executor exited 8: claude_station: token threshold reached",
                        {"usage": {"input_tokens": 6300000, "output_tokens": 59529}})


TIMEOUT = {"source": "station", "timeout_seconds": 5, "elapsed_ms": 5000.0,
           "reason": "station timeout of 5s reached (station)"}


def timeout_kill():
    raise ExecutorError("command executor exited 4: claude_station: station builder timed out after 5s",
                        {"usage": {"input_tokens": 77, "output_tokens": 11}, "timeout": dict(TIMEOUT)})


def injected_error():
    raise RuntimeError("injected")


def turn_limit_kill():
    raise ExecutorError("command executor exited 1: claude_station: claude exited 1 for station builder: "
                        "is_error=True subtype=error_max_turns num_turns=40 | {}",
                        {"usage": {"input_tokens": 500, "output_tokens": 50}})


def run(project, runtime, max_loopbacks=0):
    """Run the line; a run that raises still leaves its record. Returns the record on disk."""
    reg = registry()
    try:
        anvil_runner.run_pipeline(project, sdlc_pipeline(reg), WorkOrder(id=WO, kind="feature", title="Accounting"),
                                  registry=reg, executor=runtime, max_loopbacks=max_loopbacks)
    except Exception:
        pass
    return read_report(project)


def read_report(project):
    path = project / "runs" / WO / "report.json"
    if not path.is_file():
        raise AssertionError("the run left no report.json")
    return json.loads(path.read_text(encoding="utf-8"))


def pipeline_order():
    return sdlc_pipeline(registry()).topological_order()


class ReportSpy:
    """Wraps os.replace and os.rename and snapshots every write onto report.json."""

    def __init__(self, fail_after=None):
        self.snapshots = []
        self.sources = []
        self.fail_after = fail_after
        self.real_replace, self.real_rename = os.replace, os.rename

    def _wrap(self, real):
        def spy(src, dst, *args, **kwargs):
            if Path(dst).name == "report.json":
                self.sources.append((Path(src), Path(dst)))
                if self.fail_after is not None and len(self.sources) > self.fail_after:
                    raise OSError("injected rename failure")
                self.snapshots.append(Path(src).read_text(encoding="utf-8"))
            return real(src, dst, *args, **kwargs)
        return spy

    def __enter__(self):
        self._patches = [mock.patch.object(os, "replace", self._wrap(self.real_replace)),
                         mock.patch.object(os, "rename", self._wrap(self.real_rename))]
        for p in self._patches:
            p.start()
        return self

    def __exit__(self, *exc):
        for p in self._patches:
            p.stop()
        return False


class Completeness(unittest.TestCase):
    """The S1 completeness assertions, shared by every death scenario."""

    def assert_complete(self, report, runtime, last_ran, exit_status):
        order = pipeline_order()
        self.assertIn(report.get("exit_status"), EXIT_STATUSES)
        self.assertEqual(report["exit_status"], exit_status)
        reason = report.get("termination_reason")
        self.assertIsInstance(reason, str)
        self.assertTrue(reason.strip(), "termination_reason is empty")
        by_station = {}
        for step in report["steps"]:
            if step.get("station") in order:
                by_station.setdefault(step["station"], []).append(step)
        for sid in order:
            self.assertEqual(len(by_station.get(sid, [])), 1, f"{sid} must appear exactly once in the steps")
        cut = order.index(last_ran)
        for sid in order[:cut + 1]:
            self.assertNotEqual(by_station[sid][0]["status"], "not_run", f"{sid} ran and must carry its outcome")
        for sid in order[cut + 1:]:
            self.assertEqual(by_station[sid][0]["status"], "not_run", f"{sid} never ran")
        for sid in order[:cut]:
            if sid in runtime.calls:
                self.assertEqual(by_station[sid][0].get("executed_model"), MODEL, sid)
        self.assertEqual(runtime.calls[-1], last_ran, "the runtime received a call after the death")
        # cost-measurement semantics, unchanged: the total is the sum of measured steps
        cost = report["cost"]
        measured = [s for s in report["steps"] if s.get("cost") is not None]
        self.assertEqual(cost["total"], sum(s["cost"] for s in measured))
        self.assertEqual(cost["measured_steps"], len(measured))
        return by_station


class DeathTests(Completeness):
    def test_s1_budget_death_mid_builder_leaves_complete_report(self):
        """S1: a run killed at the 6000000 cap mid-builder leaves a complete, parseable record"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            runtime = Scripted({"builder": budget_kill})
            report = run(project, runtime)
            by_station = self.assert_complete(report, runtime, "builder", "budget_exceeded")
            self.assertEqual(runtime.calls, ["intake", "spec-writer", "test-writer", "builder"])
            builder = by_station["builder"][0]
            self.assertEqual(normalize_usage(builder["usage"])["total_tokens"], BUILDER_TOKENS)
            death = report.get("budget_death")
            self.assertIsInstance(death, dict, "the record carries no budget_death section")
            self.assertEqual(death["max_run_tokens"], CAP)
            self.assertEqual(death["station_in_flight"], "builder")
            expected = summarize_steps(report["steps"])["total_tokens"]
            self.assertEqual(death["measured_tokens"], expected)
            self.assertEqual(expected, BUILDER_TOKENS + 3 * (SMALL["input_tokens"] + SMALL["output_tokens"]))
            self.assertGreater(death["measured_tokens"], CAP)
            self.assertIn("builder", report["termination_reason"])
            self.assertIn(str(CAP), report["termination_reason"])

    def test_s2_station_timeout_death_is_recorded(self):
        """S2: a builder past its station timeout ends the run with exit_status station_timeout"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            runtime = Scripted({"builder": timeout_kill})
            report = run(project, runtime)
            by_station = self.assert_complete(report, runtime, "builder", "station_timeout")
            builder = by_station["builder"][0]
            self.assertEqual(builder["status"], "timed_out")
            self.assertIsNotNone(builder["executed_model"])
            self.assertEqual(builder["timeout"], {"station": "builder", **TIMEOUT})
            self.assertIn("timed out", builder["detail"])
            self.assertIn("builder", report["termination_reason"])
            self.assertIn("5", report["termination_reason"])

    def test_s2_uncaught_error_death_is_recorded(self):
        """S2: RuntimeError('injected') in the builder step ends the run with exit_status error"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            runtime = Scripted({"builder": injected_error})
            report = run(project, runtime)
            self.assert_complete(report, runtime, "builder", "error")
            self.assertIn("RuntimeError", report["termination_reason"])
            self.assertIn("injected", report["termination_reason"])

    def test_s2_timeout_and_error_statuses_differ(self):
        """S2: the timeout and error exit statuses differ from each other and from budget_exceeded"""
        statuses = []
        for death in (timeout_kill, injected_error):
            with tempfile.TemporaryDirectory() as tmp:
                statuses.append(run(make_project(tmp), Scripted({"builder": death})).get("exit_status"))
        self.assertEqual(statuses, ["station_timeout", "error"])
        self.assertNotIn("budget_exceeded", statuses)

    def test_s8_turn_limit_stop(self):
        """S8: a builder stopped at max_runtime_turns ends the run with exit_status turn_limit"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, max_runtime_turns=40)
            runtime = Scripted({"builder": turn_limit_kill})
            report = run(project, runtime)
            self.assert_complete(report, runtime, "builder", "turn_limit")
            self.assertIn("builder", report["termination_reason"])

    def test_s8_checks_gate_stop(self):
        """S8: failing checks with no loopback left end the run with exit_status checks_stopped"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, checks=["exit 1"])
            runtime = Scripted()
            report = run(project, runtime, max_loopbacks=0)
            order = pipeline_order()
            self.assertEqual(report.get("exit_status"), "checks_stopped")
            self.assertTrue((report.get("termination_reason") or "").strip())
            self.assertIn("checks", report["termination_reason"])
            self.assertEqual(runtime.calls[-1], "builder", "a model station ran after the checks gate stop")
            after = order[order.index("checks-gate") + 1:]
            statuses = {s["station"]: s["status"] for s in report["steps"] if s.get("station") in after}
            self.assertEqual(statuses, {sid: "not_run" for sid in after})

    def test_s8_intake_rejected_stop(self):
        """S8: an intake outcome of rejected ends the run with exit_status intake_stopped"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            rejected = lambda: {"output": json.dumps({"intake_outcome": {  # noqa: E731
                "outcome": "rejected", "reasons": ["out of scope for this project"]}}),
                "usage": dict(SMALL), "model": MODEL}
            runtime = Scripted({"intake": rejected})
            report = run(project, runtime)
            self.assert_complete(report, runtime, "intake", "intake_stopped")
            self.assertEqual(runtime.calls, ["intake"])
            self.assertIn("rejected", report["termination_reason"])


class CheckpointTests(unittest.TestCase):
    def healthy_run(self, tmp):
        project = make_project(tmp)
        disk_reads = {}

        def on_call(station_id):
            path = project / "runs" / WO / "report.json"
            if path.is_file():
                disk_reads[station_id] = json.loads(path.read_text(encoding="utf-8"))

        runtime = Scripted(on_call=on_call)
        with ReportSpy() as spy:
            final = run(project, runtime)
        return project, runtime, spy, disk_reads, final

    def checkpoints(self, spy, final_text):
        records = [json.loads(text) for text in spy.snapshots]
        if spy.snapshots and spy.snapshots[-1] == final_text:
            records = records[:-1]
        return [r for r in records if (r.get("checkpoint") or {}).get("last_completed_station")]

    def test_s3_checkpoints_accumulate_during_healthy_run(self):
        """S3: report.json is checkpointed after each station, readable mid-run"""
        with tempfile.TemporaryDirectory() as tmp:
            project, runtime, spy, disk_reads, final = self.healthy_run(tmp)
            final_text = (project / "runs" / WO / "report.json").read_text(encoding="utf-8")
            cps = self.checkpoints(spy, final_text)
            self.assertTrue(cps, "no checkpoint of report.json was written during the run")
            order = pipeline_order()
            # a mid-run read sees the record as of the last finished station
            self.assertEqual(disk_reads["builder"]["checkpoint"]["last_completed_station"], "test-writer")
            self.assertEqual(disk_reads["observer"]["checkpoint"]["last_completed_station"], "deployer")
            self.assertEqual([s["station"] for s in disk_reads["builder"]["steps"]
                              if s.get("station") in order and s.get("status") != "not_run"],
                             ["intake", "spec-writer", "test-writer"])
            # one checkpoint per finished station, in order
            seen = []
            for cp in cps:
                sid = cp["checkpoint"]["last_completed_station"]
                if not seen or seen[-1] != sid:
                    seen.append(sid)
            ran = [s["station"] for s in final["steps"] if s.get("station") in order]
            self.assertEqual(seen, ran)
            elapsed = [cp["checkpoint"]["elapsed_ms"] for cp in cps]
            for value in elapsed:
                self.assertIsInstance(value, (int, float))
            self.assertEqual(elapsed, sorted(elapsed), "elapsed_ms decreased between checkpoints")
            for cp in cps:
                sid = cp["checkpoint"]["last_completed_station"]
                self.assertIn(sid, [s["station"] for s in cp["steps"]])
                self.assertEqual(cp["checkpoint"]["usage_so_far"]["total_tokens"],
                                 summarize_steps(cp["steps"])["total_tokens"])
            # checkpointing adds no station and no model call
            model_steps = [s for s in final["steps"] if s.get("executed_model")]
            self.assertEqual(len(runtime.calls), len(model_steps))

    def test_s3_final_report_is_last_checkpoint_plus_verdict(self):
        """S3: the final report equals the last checkpoint plus verdict, decision and exit fields"""
        with tempfile.TemporaryDirectory() as tmp:
            project, _, spy, _, final = self.healthy_run(tmp)
            final_text = (project / "runs" / WO / "report.json").read_text(encoding="utf-8")
            cps = self.checkpoints(spy, final_text)
            self.assertTrue(cps, "no checkpoint of report.json was written during the run")
            last = cps[-1]
            self.assertEqual(final.get("exit_status"), "completed")
            self.assertTrue(final.get("termination_reason"))
            self.assertEqual(final["steps"], last["steps"])
            # human_required mirrors decision.human_gate.required, part of the decision section
            allowed = {"verdict", "decision", "human_required", "exit_status", "termination_reason"}
            for key in set(final) | set(last):
                if key not in allowed:
                    self.assertEqual(final.get(key), last.get(key), f"{key} changed after the last checkpoint")

    def test_s6_checkpoint_writes_are_atomic(self):
        """S6: every checkpoint is a sibling temp file renamed over report.json, none left behind"""
        with tempfile.TemporaryDirectory() as tmp:
            project, _, spy, _, _ = self.healthy_run(tmp)
            run_dir = project / "runs" / WO
            self.assertTrue(spy.sources, "report.json was never written by rename")
            for src, dst in spy.sources:
                self.assertEqual(dst.resolve(), (run_dir / "report.json").resolve())
                self.assertEqual(src.parent.resolve(), run_dir.resolve(), "temporary file is not a sibling")
                self.assertFalse(src.exists(), f"temporary file {src.name} left behind")
            for text in spy.snapshots:
                json.loads(text)
            json.loads((run_dir / "report.json").read_text(encoding="utf-8"))

    def test_s6_failed_rename_keeps_previous_report(self):
        """S6/R2.5: a rename that raises leaves the previous report.json unchanged and says why on stderr"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            err = io.StringIO()
            with ReportSpy(fail_after=1) as spy, contextlib.redirect_stderr(err):
                try:
                    run(project, Scripted())
                except AssertionError:
                    pass
            self.assertGreaterEqual(len(spy.sources), 2, "no write after the first checkpoint went by rename")
            self.assertEqual(len(spy.snapshots), 1)
            on_disk = (project / "runs" / WO / "report.json").read_text(encoding="utf-8")
            self.assertEqual(on_disk, spy.snapshots[0])
            json.loads(on_disk)
            self.assertIn("injected rename failure", err.getvalue())


def render_swimlane(case, report):
    renderer = getattr(anvil_runner, "render_swimlane", None)
    if renderer is None:
        case.fail("anvil.runner has no render_swimlane(report) renderer")
    return renderer(report)


class KilledRecordTests(unittest.TestCase):
    def test_s4_killed_record_renders_without_a_run(self):
        """S4: line_comment and the swimlane render the S1 record alone, no station executing"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            runtime = Scripted({"builder": budget_kill})
            report = run(project, runtime)
            calls = list(runtime.calls)
            self.assertEqual(report.get("exit_status"), "budget_exceeded")
            for out in (line_comment.render(report, 1), render_swimlane(self, report)):
                self.assertRegex(out, r"(?i)exit status")
                self.assertIn("budget_exceeded", out)
                self.assertIn("builder", out)
                self.assertIn("not_run", out)
            self.assertEqual(runtime.calls, calls, "rendering called the runtime")

    def test_s4_later_run_preserves_killed_record_in_history(self):
        """S4/R3.2: a later run keeps the killed record byte identical under history/ before checkpointing"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            run(project, Scripted({"builder": budget_kill}))
            run_dir = project / "runs" / WO
            killed = (run_dir / "report.json").read_bytes()
            self.assertEqual(json.loads(killed).get("exit_status"), "budget_exceeded")
            seen_at_start = {}

            def on_call(station_id):
                if station_id == "intake":
                    history = run_dir / "history"
                    seen_at_start["preserved"] = any(
                        p.read_bytes() == killed for p in history.glob("*.json")) if history.is_dir() else False
                    seen_at_start["report"] = (run_dir / "report.json").read_bytes()

            run(project, Scripted(on_call=on_call))
            self.assertTrue(seen_at_start["preserved"], "killed record not preserved before the new run started")
            self.assertEqual(seen_at_start["report"], killed, "a checkpoint of the new run overwrote the record early")
            self.assertTrue(any(p.read_bytes() == killed for p in (run_dir / "history").glob("*.json")))
            self.assertNotEqual((run_dir / "report.json").read_bytes(), killed)

    def test_s7_legacy_report_still_renders(self):
        """S7: runs/wo-gh-20/report.json (no checkpoint or exit keys) renders in every consumer"""
        legacy_path = ROOT / "runs" / "wo-gh-20" / "report.json"
        legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
        for key in ("checkpoint", "exit_status", "termination_reason"):
            self.assertNotIn(key, legacy)
        with tempfile.TemporaryDirectory() as tmp:
            project = init_project(Path(tmp) / "project", "Legacy")
            target = project / "runs" / "wo-gh-20"
            target.mkdir(parents=True)
            (target / "report.json").write_bytes(legacy_path.read_bytes())
            self.assertIn("wo-gh-20", line_comment.render(legacy, 1))
            html, _ = render_status_page(project)
            self.assertIn("wo-gh-20", html)
            self.assertIn("intake", render_swimlane(self, legacy))


CHILD = r'''
import json, sys, time
from pathlib import Path
root, project, marker = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, str(root))
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.stations import load_registry
from anvil.runner import run_pipeline

class Runtime:
    name = "fake"
    def execute(self, text, station_id, **kwargs):
        if station_id == "builder":
            marker.write_text("in builder")
            time.sleep(60)
        out = json.dumps({"intake_outcome": {"outcome": "accepted"}}) if station_id == "intake" else "done"
        return {"output": out, "usage": {"input_tokens": 100, "output_tokens": 10}, "model": "claude-opus-5-5"}

reg = load_registry(root / "stations")
pipe = load_pipeline(root / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))
run_pipeline(project, pipe, WorkOrder(id="wo-cra", kind="feature", title="Signal"), registry=reg,
             executor=Runtime(), max_loopbacks=0)
'''


class SignalTests(unittest.TestCase):
    def kill_mid_builder(self, signum):
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp)
            script = Path(tmp) / "child.py"
            script.write_text(CHILD, encoding="utf-8")
            marker = Path(tmp) / "marker"
            proc = subprocess.Popen([sys.executable, str(script), str(ROOT), str(project), str(marker)],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                deadline = time.monotonic() + 60
                while not marker.exists() and proc.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertTrue(marker.exists(), f"child never reached the builder: {proc.stderr.read() if proc.poll() is not None else ''}")
                proc.send_signal(signum)
                proc.wait(timeout=30)
            finally:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait()
                proc.stdout.close()
                proc.stderr.close()
            return read_report(project)

    def assert_signal_record(self, report, name):
        order = pipeline_order()
        self.assertEqual(report.get("exit_status"), "signal")
        self.assertEqual(report.get("termination_reason"), name)
        statuses = {}
        for step in report["steps"]:
            if step.get("station") in order:
                statuses.setdefault(step["station"], []).append(step["status"])
        for sid in order:
            self.assertEqual(len(statuses.get(sid, [])), 1, f"{sid} must appear exactly once")
        for sid in ("intake", "spec-writer", "test-writer"):
            self.assertEqual(statuses[sid], ["executed"])
        for sid in order[order.index("builder") + 1:]:
            self.assertEqual(statuses[sid], ["not_run"], sid)

    def test_s5_sigterm_completes_the_record(self):
        """S5: SIGTERM mid-builder leaves a completed record with exit_status signal, reason SIGTERM"""
        self.assert_signal_record(self.kill_mid_builder(signal.SIGTERM), "SIGTERM")

    def test_s5_sigint_completes_the_record(self):
        """S5: SIGINT mid-builder leaves a completed record with exit_status signal, reason SIGINT"""
        self.assert_signal_record(self.kill_mid_builder(signal.SIGINT), "SIGINT")


class SuiteTests(unittest.TestCase):
    def test_s9_existing_test_files_untouched(self):
        """S9: no test file tracked at HEAD is modified or deleted in the working tree.

        The spec names base ref 4675a131eb9aa88097741dc3cdc9772c3db17550, but main has moved
        past it (several test files changed on main since), so the check runs against HEAD,
        the ref this run started from.
        """
        try:
            proc = subprocess.run(["git", "diff", "--name-status", "HEAD", "--", "tests"], cwd=str(ROOT),
                                  capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            self.skipTest("git is not available")
        if proc.returncode != 0:
            self.skipTest("not a git checkout")
        touched = [line for line in proc.stdout.splitlines() if line[:1] in {"M", "D"}]
        self.assertEqual(touched, [])

    def test_s9_no_dashes_in_this_file(self):
        """Project style: no em dash or en dash in produced files"""
        for path in (Path(__file__), ROOT / ".openspec" / "specs" / "continuous-run-accounting" / "spec.md"):
            self.assertNotRegex(path.read_text(encoding="utf-8"), "[\u2013\u2014]", path.name)


if __name__ == "__main__":
    unittest.main()
