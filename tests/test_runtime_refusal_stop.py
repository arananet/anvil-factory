"""Operator fix: a runtime refusal ends the run at the first refused station.

Runs of wo-gh-41 on 2026-11-20 (44674106848 and 44676367028) ran against a
gateway with no balance. Every model station was refused with HTTP 402 and the
line still called seven of them, loopbacks included, before ending no_reviews.
A refusal for credentials, balance or access is the same for every later call,
so the first one ends the run with exit_status runtime_refused.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from anvil import runner as anvil_runner  # noqa: E402
from anvil.executor import ExecutorError  # noqa: E402
from anvil.model import WorkOrder  # noqa: E402
from anvil.pipeline import load_pipeline  # noqa: E402
from anvil.scaffold import init_project  # noqa: E402
from anvil.stations import load_registry  # noqa: E402

WO = "wo-refused"
SMALL = {"input_tokens": 100, "output_tokens": 10}
REFUSED_402 = ("command executor exited 2: claude_station: claude exited 1 for station intake: "
               "is_error=True; subtype=success; api_error_status=402; stop_reason=stop_sequence; "
               "num_turns=2; result=API Error: 402 Insufficient unified billing balance for this "
               "request. | {}")


class Scripted:
    name = "fake"

    def __init__(self, script):
        self.calls = []
        self.script = script

    def execute(self, text, station_id, **kwargs):
        self.calls.append(station_id)
        behaviour = self.script.get(station_id)
        if behaviour:
            return behaviour()
        output = "done"
        if station_id == "intake":
            output = json.dumps({"intake_outcome": {"outcome": "accepted"}})
        return {"output": output, "usage": dict(SMALL), "model": "claude-opus-5-5"}


def refuse(detail):
    def kill():
        raise ExecutorError(detail, {"usage": dict(SMALL)})
    return kill


def run(tmp, script, max_loopbacks=2):
    project = init_project(Path(tmp) / "project", "Refusal demo")
    reg = load_registry(ROOT / "stations")
    pipe = load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))
    runtime = Scripted(script)
    try:
        anvil_runner.run_pipeline(project, pipe, WorkOrder(id=WO, kind="feature", title="Refused"),
                                  registry=reg, executor=runtime, max_loopbacks=max_loopbacks)
    except Exception:
        pass
    report = json.loads((project / "runs" / WO / "report.json").read_text(encoding="utf-8"))
    return report, runtime


class RefusalDetection(unittest.TestCase):
    def test_statuses_that_refuse_every_call(self):
        for code, words in (("401", "authentication"), ("402", "billing"), ("403", "forbidden")):
            reason = anvil_runner._runtime_refusal(f"is_error=True; api_error_status={code}; result=x")
            self.assertIn(words, reason)
            self.assertIn(f"HTTP {code}", reason)

    def test_transient_or_absent_statuses_do_not_end_the_run(self):
        for detail in ("is_error=True; api_error_status=429; result=rate limited",
                       "is_error=True; api_error_status=529; result=overloaded",
                       "is_error=True; subtype=error_during_execution; result=tool failed",
                       "the page said api_error_status=4021 somewhere", "", None):
            self.assertIsNone(anvil_runner._runtime_refusal(detail))

    def test_exit_status_is_registered(self):
        self.assertIn("runtime_refused", anvil_runner.EXIT_STATUSES)


class RefusalStopsTheLine(unittest.TestCase):
    def test_refused_intake_is_the_only_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            report, runtime = run(tmp, {"intake": refuse(REFUSED_402)})
            self.assertEqual(runtime.calls, ["intake"])
            self.assertEqual(report.get("exit_status"), "runtime_refused")
            self.assertIn("402", report.get("termination_reason", ""))
            self.assertIn("intake", report.get("termination_reason", ""))
            self.assertNotEqual(report.get("verdict"), "approved")
            statuses = {s["station"]: s["status"] for s in report["steps"]}
            self.assertEqual(statuses.get("intake"), "failed")
            self.assertEqual(statuses.get("builder"), "not_run")

    def test_refused_builder_gets_no_loopback_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            detail = REFUSED_402.replace("station intake", "station builder")
            report, runtime = run(tmp, {"builder": refuse(detail)})
            self.assertEqual(runtime.calls.count("builder"), 1)
            self.assertEqual(runtime.calls[-1], "builder")
            self.assertEqual(report.get("exit_status"), "runtime_refused")

    def test_an_ordinary_failure_still_runs_the_line_on(self):
        with tempfile.TemporaryDirectory() as tmp:
            ordinary = ("command executor exited 2: claude_station: claude exited 1 for station "
                        "intake: is_error=True; subtype=error_during_execution; result=tool failed | {}")
            report, runtime = run(tmp, {"intake": refuse(ordinary)})
            self.assertNotEqual(report.get("exit_status"), "runtime_refused")
            self.assertGreater(len(runtime.calls), 1)


if __name__ == "__main__":
    unittest.main()
