"""Per-station token budgets and the completeness gate before review
(spec: station-budgets-completeness, work order wo-gh-42).

Every runner test drives a real sdlc-default run (anvil.runner.run_pipeline)
with a fake runtime: no network, no model. The fake runtime behaves like the
command executor: it writes the token-efficiency per-attempt usage artifact
(<output>.usage.json, schema anvil/usage@1, through the real
anvil.telemetry.UsageRecorder) and returns usage and telemetry from it. S1
runs the real station wrapper (tools/claude_station.py) under the real
CommandExecutor against a stand-in claude CLI on PATH.

Interface these tests pin where the spec leaves names to the builder:
  anvil.yaml efficiency.station_budgets {station: int} and
      efficiency.default_station_budget int (R1). An absent default adds 0 to
      the worst case (the spec's S3 example: 900000 + 200000 against 1000000
      is an excess of exactly 100000).
  anvil.config.validate_station_budgets(config, pipelines, registry=None)
      -> {pipeline.name: worst_case_tokens}; raises ValueError naming the
      pipeline and the excess. pipelines are anvil.pipeline.Pipeline objects;
      a model station is one whose registry kind is agent (or intake).
      A worst case equal to max_run_tokens loads; one token more does not.
  run_pipeline on a project whose partitions exceed the cap raises ValueError
      before any model call.
  report["budgets"] = {"stations": {sid: {"partition": int, "consumed": int|None, ...}},
                       "outcomes": [{"station", "outcome", "partition", "consumed", ...}]}
      outcome "refused" (with "refused_at"), "budget_exceeded" (in-flight
      ceiling) or "proceeded_unmeasured" (R2, R3). consumed None means unmeasured.
  report["completeness"] = [{"attempt": int, "passed": bool, "gaps": [str, ...]}, ...]
      one entry per evaluated builder attempt, its own field set (R4).
  report["cost"]["stations"][sid] = {"partition", "consumed", "amount", "priced", "source"}
      amount and source come from the recorded price table; an unpriced model
      has amount None and priced False (R5).
  The in-flight ceiling (R3) is observed end to end: the wrapper reads the
      runtime's usage while the session runs (the stand-in claude CLI emits
      stream-json events when --output-format stream-json is requested, as the
      real CLI does, and a single result envelope otherwise), kills the session
      past the partition, and records the attempt in the usage artifact with
      status budget_exceeded, station, reason naming the partition, the
      dispatched model and the partial usage.

Scenario map:
  S1 (R3, R6a)   test_s1_in_flight_ceiling_stops_builder_at_its_partition
  S2 (R2, R6b)   test_s2_exhausted_builder_is_refused_loopback_with_zero_calls,
                 test_s2_station_inside_its_partition_is_dispatched_again
  S3 (R1, R6c)   test_s3_over_cap_example_names_pipeline_and_excess,
                 test_s3_default_applies_to_unnamed_model_stations,
                 test_s3_worst_case_equal_to_cap_loads_one_more_fails,
                 test_s3_bad_partition_value_is_rejected,
                 test_s3_factory_partitions_sum_to_exactly_15000000,
                 test_s3_factory_config_validates_for_every_pipeline,
                 test_s3_factory_other_keys_and_packet_budgets_unchanged,
                 test_s3_over_cap_project_does_not_run
  S4 (R4, R6d)   test_s4_missing_builder_report_dispatches_zero_reviewers,
                 test_s4_missing_report_alone_blocks_review_when_checks_pass,
                 test_s4_completeness_gaps_names_a_missing_or_empty_report,
                 test_s4_failing_checks_verdict_dispatches_zero_reviewers
  S4, S5, S8 scope (owner ruling 2026-11-22: completeness only where partitions are configured)
                 test_s4_s8_scope_no_partitions_keeps_present_behavior,
                 test_s4_s8_scope_default_station_budget_alone_gates_review,
                 test_s5_scope_station_budgets_alone_gates_and_passes_complete_work
  S5 (R4, R6d)   test_s5_complete_attempt_dispatches_the_reviewer_stage
  S6 (R5)        test_s6_cost_section_prices_partitions_where_the_table_covers
  S7 (R2)        test_s7_unmeasured_with_require_usage_is_refused,
                 test_s7_unmeasured_without_require_usage_proceeds_and_says_so
  S8 (R4)        test_s8_failed_test_writer_without_artifact_blocks_review,
                 test_s8_empty_delta_blocks_review_at_max_loopbacks
  S9 (R4)        test_s9_completeness_never_reruns_the_suite_or_literal_check
  S10 (R7, R8)   test_s10_execution_doc_names_both_budget_keys,
                 test_s10_changelog_and_one_decision_record,
                 test_s10_builder_report_evidence
  S11            test_s11_diff_stays_inside_the_allowed_write_set,
                 test_s11_existing_test_files_untouched,
                 test_s11_no_dashes_in_changed_files
"""
import json
import os
import re
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

from anvil import config as anvil_config  # noqa: E402
from anvil import gates as anvil_gates  # noqa: E402
from anvil import runner as anvil_runner  # noqa: E402
from anvil.config import load_anvil_config  # noqa: E402
from anvil.executor import CommandExecutor, ExecutorError  # noqa: E402
from anvil.model import WorkOrder  # noqa: E402
from anvil.pipeline import load_pipeline  # noqa: E402
from anvil.scaffold import init_project  # noqa: E402
from anvil.stations import load_registry  # noqa: E402
from anvil.telemetry import UsageRecorder, normalize_usage, summarize_steps  # noqa: E402

BASE_REF = "72a84126a600fafb99446946694b5de809e01e66"
RUN_CAP = 15000000
FACTORY_PARTITIONS = {
    "intake": 200000, "spec-writer": 600000, "test-writer": 3200000, "builder": 6400000,
    "reviewer-spec": 600000, "reviewer-security": 600000, "reviewer-tests": 600000,
    "reviewer-architecture": 600000, "reviewer-design": 600000, "reviewer-ux": 600000,
    "approver": 200000, "triage-human": 100000, "deployer": 300000, "observer": 400000,
}
REVIEWERS = ("reviewer-spec", "reviewer-security", "reviewer-tests",
             "reviewer-architecture", "reviewer-design", "reviewer-ux")
MODEL = "claude-opus-5-5"
SMALL = {"input_tokens": 100, "output_tokens": 10}
WO = "wo-sbc"
WRAPPER = ROOT / "tools" / "claude_station.py"
DASHES = "[\u2013\u2014]"


# ---------------------------------------------------------------- helpers

def registry():
    return load_registry(ROOT / "stations")


def sdlc_pipeline(reg=None):
    reg = reg or registry()
    return load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))


def partitions(**overrides):
    """Every sdlc-default model station named, generous unless overridden."""
    table = {sid: 100000 for sid in FACTORY_PARTITIONS}
    table.update({k.replace("_", "-"): v for k, v in overrides.items()})
    return table


def make_project(tmp, station_budgets=None, default_station_budget=None, checks=None,
                 require_usage=None, max_run_tokens=RUN_CAP, prices=None):
    project = init_project(Path(tmp) / "project", "Budget demo")
    config = json.loads((project / "anvil.yaml").read_text(encoding="utf-8"))
    eff = config.setdefault("efficiency", {})
    eff["max_run_tokens"] = max_run_tokens
    eff["max_packet_tokens"] = 48000
    if station_budgets is not None:
        eff["station_budgets"] = station_budgets
    if default_station_budget is not None:
        eff["default_station_budget"] = default_station_budget
    if require_usage is not None:
        eff["require_usage"] = require_usage
    if prices is not None:
        config["prices"] = prices
    (project / "anvil.yaml").write_text(json.dumps(config, indent=2), encoding="utf-8")
    if checks is not None:
        anvil_json = json.loads((project / "anvil.json").read_text(encoding="utf-8"))
        anvil_json["checks"] = checks
        (project / "anvil.json").write_text(json.dumps(anvil_json, indent=2), encoding="utf-8")
    return project


def envelope(usage, result="done"):
    """A claude CLI result envelope; usage None means the runtime reported none."""
    data = {"type": "result", "subtype": "success", "is_error": False, "num_turns": 2, "result": result}
    if usage is not None:
        data["usage"] = dict(usage)
    return json.dumps(data)


class Scripted:
    """Fake runtime that keeps the command executor's evidence contract.

    script maps a station id to a list of per call behaviours (the last one
    repeats). A behaviour is a dict: usage (dict, or None for unmeasured),
    write ({relative path: text} written into the project), fail (bool,
    an ordinary station failure), model, output.
    """
    name = "fake"

    def __init__(self, script=None):
        self.script = script or {}
        self.calls = []
        self.packets = []

    def execute(self, text, station_id, output_path=None, cwd=None, **kwargs):
        index = sum(1 for c in self.calls if c == station_id)
        self.calls.append(station_id)
        self.packets.append((station_id, text))
        plan = self.script.get(station_id) or [{}]
        behaviour = plan[min(index, len(plan) - 1)]
        usage = behaviour.get("usage", SMALL)
        model = behaviour.get("model", MODEL)
        output = behaviour.get("output")
        if output is None:
            output = json.dumps({"intake_outcome": {"outcome": "accepted"}}) if station_id == "intake" else "done"
        for rel, content in (behaviour.get("write") or {}).items():
            target = Path(cwd) / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        usage_path = Path(str(output_path) + ".usage.json") if output_path is not None else None
        if usage_path is not None:
            usage_path.unlink(missing_ok=True)
        recorder = UsageRecorder(usage_path)
        recorder.record(envelope(usage, output), "claude",
                        "failed" if behaviour.get("fail") else "succeeded", 10.0, model)
        telemetry = recorder.summary()
        if behaviour.get("fail"):
            raise ExecutorError(
                f"command executor exited 2: claude_station: claude exited 1 for station {station_id}: "
                "is_error=True; subtype=error_during_execution; result=tool failed | {}",
                {"usage": normalize_usage(telemetry["usage"]), "telemetry": telemetry})
        return {"output": output, "usage": normalize_usage(telemetry["usage"]),
                "telemetry": telemetry, "model": model}

    def count(self, station_id):
        return self.calls.count(station_id)

    def reviewer_calls(self):
        return [c for c in self.calls if c.startswith("reviewer")]

    def packets_for(self, station_id):
        return [text for sid, text in self.packets if sid == station_id]


def run(project, runtime, max_loopbacks=0):
    """Run the line; a run that raises still leaves its record on disk."""
    reg = registry()
    try:
        anvil_runner.run_pipeline(project, sdlc_pipeline(reg), WorkOrder(id=WO, kind="feature", title="Budgets"),
                                  registry=reg, executor=runtime, max_loopbacks=max_loopbacks)
    except Exception:
        pass
    path = project / "runs" / WO / "report.json"
    if not path.is_file():
        raise AssertionError("the run left no report.json")
    return json.loads(path.read_text(encoding="utf-8"))


def outcomes(report, station=None, outcome=None):
    found = (report.get("budgets") or {}).get("outcomes")
    if not isinstance(found, list):
        raise AssertionError("report.json carries no budgets.outcomes list")
    return [o for o in found if (station is None or o.get("station") == station)
            and (outcome is None or o.get("outcome") == outcome)]


def completeness(report):
    found = report.get("completeness")
    if not isinstance(found, list) or not found:
        raise AssertionError("report.json carries no completeness evaluations")
    return found


TEST_FILE = {"tests/test_feature.py": "import unittest\n\nclass T(unittest.TestCase):\n    def test_x(self):\n        pass\n"}
SRC_FILE = {"src/feature.py": "VALUE = 1\n"}
REPORT_REL = f"runs/{WO}/builder.output.md"
COMPLETE = {"test-writer": [{"write": TEST_FILE}], "builder": [{"write": SRC_FILE}]}


# ---------------------------------------------------------------- R1: configuration

class PartitionConfiguration(unittest.TestCase):
    def test_s3_over_cap_example_names_pipeline_and_excess(self):
        """S3: builder 900000 + reviewer-spec 200000 against max_run_tokens 1000000 fails naming sdlc-default and 100000"""
        config = {"efficiency": {"max_run_tokens": 1000000,
                                 "station_budgets": {"builder": 900000, "reviewer-spec": 200000}}}
        reg = registry()
        with self.assertRaises(ValueError) as caught:
            anvil_config.validate_station_budgets(config, [sdlc_pipeline(reg)], reg)
        message = str(caught.exception)
        self.assertIn("sdlc-default", message)
        self.assertRegex(message, r"(?<!\d)100000(?!\d)", "the error does not name the excess of 100000")

    def test_s3_default_applies_to_unnamed_model_stations(self):
        """S3: the default is charged once per unnamed model station: 500000 + 3 x 300000 exceeds 1000000 by 400000"""
        reg = registry()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tiny.json"
            path.write_text(json.dumps({"name": "tiny", "stages": [
                {"station": "builder"}, {"station": "checks-gate"},
                {"parallel": ["reviewer-spec", "reviewer-tests"]}, {"station": "observer"}]}), encoding="utf-8")
            tiny = load_pipeline(path, known_stations=set(reg.ids()))
        unnamed = [s for s in tiny.topological_order() if reg.get(s).kind == "agent" and s != "builder"]
        self.assertEqual(len(unnamed), 3)
        config = {"efficiency": {"max_run_tokens": 1000000, "station_budgets": {"builder": 500000},
                                 "default_station_budget": 300000}}
        with self.assertRaises(ValueError) as caught:
            anvil_config.validate_station_budgets(config, [tiny], reg)
        message = str(caught.exception)
        self.assertIn("tiny", message)
        excess = 500000 + 300000 * len(unnamed) - 1000000
        self.assertRegex(message, rf"(?<!\d){excess}(?!\d)")
        # the deterministic checks gate takes no partition: without the default, it fits
        config["efficiency"]["default_station_budget"] = 100000
        self.assertEqual(anvil_config.validate_station_budgets(config, [tiny], reg),
                         {"tiny": 500000 + 100000 * len(unnamed)})

    def test_s3_worst_case_equal_to_cap_loads_one_more_fails(self):
        """S3: a worst case equal to max_run_tokens loads; one token over fails naming an excess of 1"""
        reg = registry()
        config = {"efficiency": {"max_run_tokens": 1000000,
                                 "station_budgets": {"builder": 800000, "reviewer-spec": 200000}}}
        self.assertEqual(anvil_config.validate_station_budgets(config, [sdlc_pipeline(reg)], reg),
                         {"sdlc-default": 1000000})
        config["efficiency"]["station_budgets"]["builder"] = 800001
        with self.assertRaises(ValueError) as caught:
            anvil_config.validate_station_budgets(config, [sdlc_pipeline(reg)], reg)
        self.assertRegex(str(caught.exception), r"(?<!\d)1(?!\d)")
        self.assertIn("sdlc-default", str(caught.exception))

    def test_s3_bad_partition_value_is_rejected(self):
        """S3: a partition that is not a positive integer fails to load, naming the station"""
        reg = registry()
        for bad in (-5, "lots", True, 1.5):
            config = {"efficiency": {"max_run_tokens": 1000000, "station_budgets": {"builder": bad}}}
            with self.assertRaises(ValueError, msg=repr(bad)) as caught:
                anvil_config.validate_station_budgets(config, [sdlc_pipeline(reg)], reg)
            self.assertIn("builder", str(caught.exception))

    def factory_config(self):
        return load_anvil_config(ROOT / "anvil.yaml")

    def test_s3_factory_partitions_sum_to_exactly_15000000(self):
        """S3: the factory anvil.yaml ships the corrected sdlc-default table, summing to exactly 15000000"""
        eff = self.factory_config()["efficiency"]
        self.assertEqual(eff.get("station_budgets"), FACTORY_PARTITIONS)
        self.assertEqual(sum(eff["station_budgets"].values()), RUN_CAP)
        self.assertEqual(eff["max_run_tokens"], RUN_CAP)

    def test_s3_factory_config_validates_for_every_pipeline(self):
        """S3: the factory config loads against every pipeline it can run; sdlc-default's worst case is 15000000"""
        reg = registry()
        pipes = [load_pipeline(p, known_stations=set(reg.ids())) for p in sorted((ROOT / "pipelines").glob("*.json"))]
        self.assertGreater(len(pipes), 1)
        worst = anvil_config.validate_station_budgets(self.factory_config(), pipes, reg)
        self.assertEqual(worst["sdlc-default"], RUN_CAP)
        self.assertEqual(set(worst), {p.name for p in pipes})
        for name, total in worst.items():
            self.assertLessEqual(total, RUN_CAP, name)

    def test_s3_factory_other_keys_and_packet_budgets_unchanged(self):
        """S3 and guardrails: only the two efficiency keys are new; the packet budget lookup is unaffected"""
        current = self.factory_config()
        try:
            base_text = subprocess.run(["git", "show", f"{BASE_REF}:anvil.yaml"], cwd=str(ROOT),
                                       capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            self.skipTest("git is not available")
        if base_text.returncode != 0:
            self.skipTest("the base ref is not in this checkout")
        base = json.loads(base_text.stdout)
        stripped = json.loads(json.dumps(current))
        stripped["efficiency"].pop("station_budgets", None)
        stripped["efficiency"].pop("default_station_budget", None)
        self.assertEqual(stripped, base)
        for sid in FACTORY_PARTITIONS:
            self.assertEqual(anvil_config.get_station_budget(current, sid),
                             anvil_config.get_station_budget(base, sid), sid)

    def test_s3_over_cap_project_does_not_run(self):
        """S3: a project whose partitions exceed its run cap fails at load with zero model calls"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, station_budgets={"builder": 900000, "reviewer-spec": 200000},
                                   max_run_tokens=1000000)
            runtime = Scripted()
            reg = registry()
            with self.assertRaises(ValueError) as caught:
                anvil_runner.run_pipeline(project, sdlc_pipeline(reg), WorkOrder(id=WO, kind="feature", title="x"),
                                          registry=reg, executor=runtime, max_loopbacks=0)
            self.assertRegex(str(caught.exception), r"(?<!\d)100000(?!\d)")
            self.assertEqual(runtime.calls, [])


# ---------------------------------------------------------------- R2: pre-call check

class PreCallCheck(unittest.TestCase):
    def test_s2_exhausted_builder_is_refused_loopback_with_zero_calls(self):
        """S2: a builder that used its 5000 partition on attempt 1 is refused the loopback, zero calls, run ends budget_exceeded"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, station_budgets=partitions(builder=5000), checks=["exit 1"])
            runtime = Scripted({"test-writer": [{"write": TEST_FILE}],
                                "builder": [{"write": SRC_FILE, "usage": {"input_tokens": 4500, "output_tokens": 500}}]})
            report = run(project, runtime, max_loopbacks=2)
            self.assertEqual(runtime.count("builder"), 1, "the refused builder was dispatched again")
            self.assertEqual(runtime.calls[-1], "builder", "a station was called after the refusal")
            self.assertEqual(runtime.reviewer_calls(), [])
            self.assertTrue(any(s.get("status") == "loopback" for s in report["steps"]),
                            "the gate never asked for the loopback the refusal must stop")
            refused = outcomes(report, "builder", "refused")
            self.assertEqual(len(refused), 1, report.get("budgets"))
            self.assertEqual(refused[0]["partition"], 5000)
            self.assertEqual(refused[0]["consumed"], 5000)
            self.assertIn("refused_at", refused[0])
            # the refusal itself cost no model call: every recorded call is a runtime call
            self.assertEqual(summarize_steps(report["steps"])["calls"], len(runtime.calls))
            self.assertEqual(report.get("exit_status"), "budget_exceeded")
            reason = report.get("termination_reason") or ""
            self.assertIn("builder", reason)
            self.assertIn("5000", reason)
            statuses = {s["station"]: s["status"] for s in report["steps"] if s.get("station") in REVIEWERS}
            self.assertEqual(set(statuses.values()) - {"skipped", "not_run"}, set())
            stations = report["budgets"]["stations"]
            self.assertEqual(stations["builder"]["partition"], 5000)
            self.assertEqual(stations["builder"]["consumed"], 5000)

    def test_s2_station_inside_its_partition_is_dispatched_again(self):
        """S2 (counter case): a builder with partition left gets its loopback; no refusal is recorded"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, station_budgets=partitions(builder=50000), checks=["exit 1"])
            runtime = Scripted({"test-writer": [{"write": TEST_FILE}],
                                "builder": [{"write": SRC_FILE, "usage": {"input_tokens": 4500, "output_tokens": 500}}]})
            report = run(project, runtime, max_loopbacks=1)
            self.assertEqual(runtime.count("builder"), 2)
            self.assertEqual(outcomes(report, outcome="refused"), [])
            self.assertEqual(report["budgets"]["stations"]["builder"]["consumed"], 10000)
            self.assertNotEqual(report.get("exit_status"), "budget_exceeded")

    def test_s7_unmeasured_with_require_usage_is_refused(self):
        """S7: require_usage true, the builder's attempt 1 was unmeasured: its re-dispatch is refused as exhausted"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, station_budgets=partitions(), checks=["exit 1"], require_usage=True)
            runtime = Scripted({"test-writer": [{"write": TEST_FILE}],
                                "builder": [{"write": SRC_FILE, "usage": None}]})
            report = run(project, runtime, max_loopbacks=2)
            self.assertEqual(runtime.count("builder"), 1)
            refused = outcomes(report, "builder", "refused")
            self.assertEqual(len(refused), 1, report.get("budgets"))
            self.assertIsNone(refused[0]["consumed"], "unmeasured usage was counted as a number")
            self.assertEqual(refused[0]["partition"], 100000)
            self.assertIsNone(report["budgets"]["stations"]["builder"]["consumed"])

    def test_s7_unmeasured_without_require_usage_proceeds_and_says_so(self):
        """S7: require_usage false (the factory default): the re-dispatch proceeds and the record says unmeasured"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, station_budgets=partitions(), checks=["exit 1"], require_usage=False)
            runtime = Scripted({"test-writer": [{"write": TEST_FILE}],
                                "builder": [{"write": SRC_FILE, "usage": None}]})
            report = run(project, runtime, max_loopbacks=1)
            self.assertEqual(runtime.count("builder"), 2)
            self.assertEqual(outcomes(report, "builder", "refused"), [])
            proceeded = outcomes(report, "builder", "proceeded_unmeasured")
            self.assertEqual(len(proceeded), 1, report.get("budgets"))


# ---------------------------------------------------------------- R3: in-flight ceiling

# Stand-in claude CLI. With --output-format stream-json it streams one
# assistant event per model call, each carrying that call's usage, the way
# the real CLI does; otherwise it prints one result envelope at the end.
# The heavy station streams FAKE_HEAVY_EVENTS calls of 1100 tokens, then
# keeps working for FAKE_HEAVY_SLEEP seconds before it would finish.
FAKE_CLAUDE = r'''#!/usr/bin/env python3
import json, os, sys, time
args = sys.argv[1:]
prompt = args[args.index("-p") + 1] if "-p" in args else ""
station = ""
for line in prompt.splitlines():
    if line.startswith("# Task packet:"):
        station = line.split(":", 1)[1].strip()
        break
log = os.environ.get("FAKE_LOG")
if log:
    with open(log, "a") as handle:
        handle.write(station + "\n")
heavy = station == os.environ.get("FAKE_HEAVY_STATION")
stream = "stream-json" in args
result = json.dumps({"intake_outcome": {"outcome": "accepted"}}) if station == "intake" else "done"
calls = int(os.environ.get("FAKE_HEAVY_EVENTS", "5")) if heavy else 1
per = {"input_tokens": 1000, "output_tokens": 100} if heavy else {"input_tokens": 10, "output_tokens": 5}
if stream:
    print(json.dumps({"type": "system", "subtype": "init", "session_id": "fake", "model": os.environ.get("FAKE_MODEL", "")}), flush=True)
    for i in range(calls):
        print(json.dumps({"type": "assistant", "session_id": "fake", "message": {
            "id": "msg_%d" % i, "type": "message", "role": "assistant",
            "content": [{"type": "text", "text": "working"}], "usage": per}}), flush=True)
        time.sleep(0.05)
if heavy:
    time.sleep(float(os.environ.get("FAKE_HEAVY_SLEEP", "20")))
total = {k: v * calls for k, v in per.items()}
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "num_turns": calls,
                  "result": result, "usage": total}), flush=True)
'''


def clean_env(**extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("ANVIL_", "FAKE_"))}
    env.update(extra)
    return env


class InFlightCeiling(unittest.TestCase):
    def test_s1_in_flight_ceiling_stops_builder_at_its_partition(self):
        """S1: builder partition 3000 under 5 x 1100 scripted tokens: killed at the partition, budget_exceeded, reviewers untouched"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            project = make_project(tmp, station_budgets=partitions(builder=3000))
            bin_dir = tmp / "bin"
            bin_dir.mkdir()
            fake = bin_dir / "claude"
            fake.write_text(FAKE_CLAUDE, encoding="utf-8")
            fake.chmod(0o755)
            log = tmp / "calls.log"
            executor = CommandExecutor({"command": f"{sys.executable} {WRAPPER} {{packet}} {{output}}"})
            reg = registry()
            env = clean_env(PATH=f"{bin_dir}:{os.environ['PATH']}", FAKE_LOG=str(log),
                            FAKE_HEAVY_STATION="builder", FAKE_HEAVY_EVENTS="5", FAKE_HEAVY_SLEEP="20",
                            ANVIL_STATION_TIMEOUT_SECONDS="12")
            started = time.monotonic()
            with mock.patch.dict(os.environ, env, clear=True):
                try:
                    anvil_runner.run_pipeline(project, sdlc_pipeline(reg),
                                              WorkOrder(id=WO, kind="feature", title="Ceiling"),
                                              registry=reg, executor=executor, max_loopbacks=1)
                except Exception:
                    pass
            elapsed = time.monotonic() - started
            report = json.loads((project / "runs" / WO / "report.json").read_text(encoding="utf-8"))
            called = log.read_text(encoding="utf-8").split() if log.is_file() else []
            self.assertEqual(called, ["intake", "spec-writer", "test-writer", "builder"])

            builder = [s for s in report["steps"] if s.get("station") == "builder"]
            self.assertEqual(len(builder), 1)
            builder = builder[0]
            self.assertEqual(builder["status"], "budget_exceeded", builder.get("detail"))
            self.assertLess(builder["duration_ms"], 12000, "the builder ran to its timeout, not its partition")
            self.assertLess(elapsed, 30)
            partial = normalize_usage(builder.get("usage"))
            self.assertIsNotNone(partial, "the partial usage the runtime exposed was not recorded")
            self.assertGreaterEqual(partial["total_tokens"], 3000)
            self.assertLess(partial["total_tokens"], 5 * 1100, "the session was not stopped before it finished")
            self.assertIsNotNone(builder.get("executed_model"))

            artifact = json.loads((project / "runs" / WO / "builder.output.md.usage.json").read_text(encoding="utf-8"))
            last = artifact["attempts"][-1]
            self.assertEqual(last["status"], "budget_exceeded")
            self.assertEqual(last.get("station"), "builder")
            self.assertIn("3000", str(last.get("reason")))
            self.assertEqual(last["configured_model"], builder["executed_model"])
            self.assertTrue(last["usage_complete"])
            self.assertGreaterEqual(last["usage"]["total_tokens"], 3000)

            exceeded = outcomes(report, "builder", "budget_exceeded")
            self.assertEqual(len(exceeded), 1, report.get("budgets"))
            self.assertEqual(exceeded[0]["partition"], 3000)
            stations = report["budgets"]["stations"]
            for sid in REVIEWERS:
                self.assertEqual(stations[sid]["consumed"], 0, sid)
                self.assertEqual(stations[sid]["partition"], 100000, sid)

            self.assertEqual(report.get("exit_status"), "budget_exceeded")
            reason = report.get("termination_reason") or ""
            self.assertIn("builder", reason)
            self.assertIn("3000", reason)
            order = sdlc_pipeline(reg).topological_order()
            statuses = {s["station"]: s["status"] for s in report["steps"] if s.get("station") in order}
            for sid in order[order.index("builder") + 1:]:
                self.assertEqual(statuses.get(sid), "not_run", sid)


# ---------------------------------------------------------------- R4: completeness

class CompletenessGate(unittest.TestCase):
    def test_s4_missing_builder_report_dispatches_zero_reviewers(self):
        """S4: a builder attempt with no report artifact: completeness fails naming it, loops back once, zero reviewers"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, station_budgets=partitions(), checks=["true"])
            runtime = Scripted({"test-writer": [{"write": TEST_FILE}], "builder": [{"fail": True}]})
            report = run(project, runtime, max_loopbacks=1)
            self.assertEqual(runtime.reviewer_calls(), [])
            self.assertEqual(runtime.count("builder"), 2, "the gaps did not return to the builder")
            self.assertEqual(report["loopbacks"], 1)
            evaluations = completeness(report)
            self.assertEqual(len(evaluations), 2)
            for evaluation in evaluations:
                self.assertFalse(evaluation["passed"])
                self.assertTrue(any(REPORT_REL in gap for gap in evaluation["gaps"]), evaluation)
            self.assertEqual([e["attempt"] for e in evaluations], [1, 2])

    def test_s4_missing_report_alone_blocks_review_when_checks_pass(self):
        """S4: builder changed a file, checks pass, report missing or empty: the report gap alone blocks review"""
        passed = {"passed": True, "findings": [], "log": "", "report": "", "required_literals": [],
                  "missing_literals": [], "observed": "present"}
        for output in ("", "   \n"):
            with self.subTest(output=repr(output)), tempfile.TemporaryDirectory() as tmp:
                project = make_project(tmp, station_budgets=partitions(), checks=["true"])
                runtime = Scripted({"test-writer": [{"write": TEST_FILE}],
                                    "builder": [{"write": SRC_FILE, "output": output}]})
                # Stand in for a gate whose literal validation passed, so the
                # completeness report check is the only thing left to fail.
                with mock.patch.object(anvil_runner, "validate_builder_report", lambda *a, **k: dict(passed)):
                    report = run(project, runtime, max_loopbacks=0)
                self.assertEqual(runtime.reviewer_calls(), [])
                gate = [s for s in report["steps"] if s.get("station") == "checks-gate"]
                self.assertEqual(gate[0].get("gate_verdict"), "pass")
                evaluation = completeness(report)[0]
                self.assertFalse(evaluation["passed"])
                self.assertEqual(evaluation["gate_verdict"], "pass")
                self.assertEqual(len(evaluation["gaps"]), 1, evaluation)
                self.assertIn(REPORT_REL, evaluation["gaps"][0])

    def test_s4_completeness_gaps_names_a_missing_or_empty_report(self):
        """S4: completeness_gaps on an otherwise complete attempt with a passing verdict names only the report"""
        order = ["intake", "spec-writer", "test-writer", "builder", "checks-gate"]
        steps = [{"station": "test-writer", "status": "executed"}, {"station": "builder", "status": "executed"}]
        for content in (None, "", "  \n", "report"):
            with self.subTest(content=repr(content)), tempfile.TemporaryDirectory() as tmp:
                project = Path(tmp)
                run_dir = project / "runs" / WO
                run_dir.mkdir(parents=True)
                for rel, text in {**TEST_FILE, **SRC_FILE}.items():
                    (project / rel).parent.mkdir(parents=True, exist_ok=True)
                    (project / rel).write_text(text, encoding="utf-8")
                if content is not None:
                    (run_dir / "builder.output.md").write_text(content, encoding="utf-8")
                gaps = anvil_runner.completeness_gaps(project, run_dir, order, 4, steps, 1, "pass",
                                                      list(SRC_FILE), list(TEST_FILE))
                if content == "report":
                    self.assertEqual(gaps, [])
                else:
                    self.assertEqual(len(gaps), 1, gaps)
                    self.assertIn(REPORT_REL, gaps[0])

    def test_s4_failing_checks_verdict_dispatches_zero_reviewers(self):
        """S4: a failing checks verdict: completeness fails naming the checks gate, one loopback, zero reviewers"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, station_budgets=partitions(), checks=["exit 1"])
            runtime = Scripted(COMPLETE)
            report = run(project, runtime, max_loopbacks=1)
            self.assertEqual(runtime.reviewer_calls(), [])
            self.assertEqual(runtime.count("builder"), 2)
            self.assertEqual(report["loopbacks"], 1, "a failed attempt consumed more than one loopback")
            evaluations = completeness(report)
            self.assertEqual(len(evaluations), 2)
            for evaluation in evaluations:
                self.assertFalse(evaluation["passed"])
                self.assertTrue(any("check" in gap.lower() for gap in evaluation["gaps"]), evaluation)

    def test_s5_complete_attempt_dispatches_the_reviewer_stage(self):
        """S5: every artifact present and checks passing: completeness passes in its own field set, reviewers run"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, station_budgets=partitions(), checks=["true"])
            runtime = Scripted(COMPLETE)
            report = run(project, runtime, max_loopbacks=0)
            self.assertEqual(len(completeness(report)), 1)
            evaluation = completeness(report)[0]
            self.assertTrue(evaluation["passed"])
            self.assertEqual(evaluation["gaps"], [])
            self.assertEqual(evaluation["attempt"], 1)
            self.assertGreater(len(runtime.reviewer_calls()), 0, "a complete attempt dispatched no reviewer")
            first_reviewer = min(runtime.calls.index(r) for r in runtime.reviewer_calls())
            self.assertEqual(runtime.calls[first_reviewer - 1], "builder")
            gate = [s for s in report["steps"] if s.get("station") == "checks-gate"]
            self.assertEqual(gate[0].get("gate_verdict"), "pass")
            self.assertNotIn("completeness", gate[0], "completeness is mixed into the checks result")

    def test_s8_failed_test_writer_without_artifact_blocks_review(self):
        """S8: test-writer recorded failed with no test files: gap names it, returns to the builder, zero reviewers"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, station_budgets=partitions(), checks=["true"])
            runtime = Scripted({"test-writer": [{"fail": True}], "builder": [{"write": SRC_FILE}]})
            report = run(project, runtime, max_loopbacks=1)
            self.assertEqual(runtime.reviewer_calls(), [])
            self.assertEqual(runtime.count("test-writer"), 1)
            self.assertEqual(runtime.count("builder"), 2, "the gaps did not return to the builder")
            self.assertEqual(report["loopbacks"], 1)
            evaluation = completeness(report)[0]
            self.assertFalse(evaluation["passed"])
            self.assertTrue(any("test-writer" in gap for gap in evaluation["gaps"]), evaluation)
            second_packet = runtime.packets_for("builder")[1]
            self.assertIn("test-writer", second_packet, "the builder's loopback packet does not name the gap")
            self.assertNotEqual(report.get("verdict"), "approved")

    def test_s8_empty_delta_blocks_review_at_max_loopbacks(self):
        """S8: an attempt that changed no file fails completeness naming the delta; at max loopbacks no further builder call"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, station_budgets=partitions(), checks=["true"])
            runtime = Scripted()
            report = run(project, runtime, max_loopbacks=0)
            self.assertEqual(runtime.reviewer_calls(), [])
            self.assertEqual(runtime.count("builder"), 1)
            self.assertEqual(report["loopbacks"], 0)
            evaluation = completeness(report)[0]
            self.assertFalse(evaluation["passed"])
            self.assertTrue(any("delta" in gap.lower() for gap in evaluation["gaps"]), evaluation)
            self.assertNotEqual(report.get("verdict"), "approved")
            self.assertNotEqual(report.get("exit_status"), "completed")

    def test_s4_s8_scope_no_partitions_keeps_present_behavior(self):
        """S4, S5, S8 scope (owner ruling 2026-11-22): no efficiency partitions, an empty delta still reaches review, no completeness record"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, checks=["true"])
            eff = json.loads((project / "anvil.yaml").read_text(encoding="utf-8")).get("efficiency", {})
            self.assertNotIn("station_budgets", eff)
            self.assertNotIn("default_station_budget", eff)
            runtime = Scripted()
            report = run(project, runtime, max_loopbacks=0)
            self.assertGreater(len(runtime.reviewer_calls()), 0,
                               "a project without partitions lost its present review flow")
            self.assertEqual(runtime.count("builder"), 1)
            self.assertFalse(report.get("completeness"), "completeness evaluated where no partition is configured")

    def test_s4_s8_scope_default_station_budget_alone_gates_review(self):
        """S4, S8 scope (owner ruling 2026-11-22): default_station_budget alone activates completeness; an empty delta dispatches zero reviewers"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, default_station_budget=100000, checks=["true"])
            runtime = Scripted()
            report = run(project, runtime, max_loopbacks=0)
            self.assertEqual(runtime.reviewer_calls(), [])
            evaluation = completeness(report)[0]
            self.assertFalse(evaluation["passed"])
            self.assertTrue(any("delta" in gap.lower() for gap in evaluation["gaps"]), evaluation)

    def test_s5_scope_station_budgets_alone_gates_and_passes_complete_work(self):
        """S5 scope (owner ruling 2026-11-22): station_budgets without a default activates completeness, which passes a complete attempt"""
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, station_budgets=partitions(), checks=["true"])
            eff = json.loads((project / "anvil.yaml").read_text(encoding="utf-8"))["efficiency"]
            self.assertNotIn("default_station_budget", eff)
            runtime = Scripted(COMPLETE)
            report = run(project, runtime, max_loopbacks=0)
            self.assertTrue(completeness(report)[0]["passed"])
            self.assertGreater(len(runtime.reviewer_calls()), 0)

    def test_s9_completeness_never_reruns_the_suite_or_literal_check(self):
        """S9: suite runs equal the red check plus gate runs, and builder report validation runs once per attempt"""
        for script, loops in ((COMPLETE, 0), ({"test-writer": [{"fail": True}], "builder": [{"write": SRC_FILE}]}, 1)):
            with tempfile.TemporaryDirectory() as tmp:
                counter = Path(tmp) / "suite-runs.txt"
                command = f"{sys.executable} -c \"open(r'{counter}', 'a').write('run\\n')\""
                project = make_project(tmp, station_budgets=partitions(), checks=[command])
                runtime = Scripted(script)
                real = anvil_gates.validate_builder_report
                seen = []

                def spy(*args, **kwargs):
                    seen.append(args)
                    return real(*args, **kwargs)

                with mock.patch.object(anvil_gates, "validate_builder_report", spy), \
                        mock.patch.object(anvil_runner, "validate_builder_report", spy):
                    report = run(project, runtime, max_loopbacks=loops)
                completeness(report)
                runs = counter.read_text(encoding="utf-8").split() if counter.is_file() else []
                gate_runs = sum(len(s.get("commands") or []) for s in report["steps"]
                                if s.get("station") == "checks-gate")
                red_runs = sum(len((s.get("red_check") or {}).get("commands") or []) for s in report["steps"])
                self.assertGreater(gate_runs, 0)
                self.assertEqual(len(runs), gate_runs + red_runs, "the suite ran outside the gate and red check")
                self.assertEqual(len(seen), runtime.count("builder"),
                                 "the builder report literal validation ran more than once per attempt")


# ---------------------------------------------------------------- R5: money framing

class MoneyFraming(unittest.TestCase):
    def test_s6_cost_section_prices_partitions_where_the_table_covers(self):
        """S6: a priced station shows partition, tokens and amount from the table; an unpriced one shows tokens only"""
        prices = {MODEL: {"input_per_million": 3.0, "output_per_million": 15.0,
                          "source": "test-pricing-2026-11", "date_recorded": "2026-11-21"}}
        with tempfile.TemporaryDirectory() as tmp:
            project = make_project(tmp, station_budgets=partitions(intake=250000), checks=["true"], prices=prices)
            script = dict(COMPLETE)
            script["spec-writer"] = [{"model": "unpriced-model-x", "usage": {"input_tokens": 700, "output_tokens": 70}}]
            runtime = Scripted(script)
            report = run(project, runtime, max_loopbacks=0)
            stations = (report.get("cost") or {}).get("stations")
            self.assertIsInstance(stations, dict, "the cost section carries no per-station budget view")
            intake = stations["intake"]
            self.assertEqual(intake["partition"], 250000)
            self.assertEqual(intake["consumed"], 110)
            self.assertTrue(intake["priced"])
            self.assertAlmostEqual(intake["amount"], 100 * 3.0 / 1e6 + 10 * 15.0 / 1e6, places=9)
            self.assertIn("test-pricing-2026-11", str(intake["source"]))
            spec = stations["spec-writer"]
            self.assertEqual(spec["partition"], 100000)
            self.assertEqual(spec["consumed"], 770)
            self.assertFalse(spec["priced"])
            self.assertIsNone(spec["amount"])
            # cost-measurement semantics unchanged: the total is the sum of measured steps
            measured = [s for s in report["steps"] if s.get("cost") is not None]
            self.assertEqual(report["cost"]["total"], sum(s["cost"] for s in measured))


# ---------------------------------------------------------------- R7, R8, guardrails: the tree

def git(*args):
    return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True, timeout=30)


def changed_paths(test):
    """Paths changed from the base ref to the working tree, untracked files included."""
    try:
        if git("cat-file", "-e", BASE_REF + "^{commit}").returncode != 0:
            test.skipTest("the base ref is not in this checkout")
        diff = git("diff", "--name-status", BASE_REF)
        untracked = git("ls-files", "--others", "--exclude-standard")
    except (OSError, subprocess.TimeoutExpired):
        test.skipTest("git is not available")
    test.assertEqual(diff.returncode, 0, diff.stderr)
    entries = []
    for line in diff.stdout.splitlines():
        parts = line.split("\t")
        entries.append((parts[0][0], parts[-1]))
    entries += [("A", p) for p in untracked.stdout.splitlines() if p.strip()]
    return entries


ALLOWED_FILES = {"anvil/config.py", "anvil.yaml", "anvil/executor.py", "anvil/runner.py", "anvil/gates.py",
                 "anvil/telemetry.py", "tools/claude_station.py", "tools/dispatch_station.py", "CHANGELOG.md"}
# The line's own bookkeeping for this order: its run directory, its work order
# records and the spec the spec-writer station revised. status/ is the status
# page the line regenerates after every run (see the merge of wo-gh-41).
LINE_BOOKKEEPING = ("runs/wo-gh-42/", "work_orders/wo-gh-42.json", "work-orders/issue-42.json",
                    ".openspec/specs/station-budgets-completeness/", "status/")


class TreeEvidence(unittest.TestCase):
    def test_s10_execution_doc_names_both_budget_keys(self):
        """S10: docs/EXECUTION.md names both efficiency keys and the top level packet key, and states the difference"""
        text = (ROOT / "docs" / "EXECUTION.md").read_text(encoding="utf-8")
        for needle in ("efficiency.station_budgets", "efficiency.default_station_budget", "max_run_tokens",
                       "completeness"):
            self.assertIn(needle, text)
        paragraphs = re.split(r"\n\s*\n", text)
        both = [p for p in paragraphs if "efficiency.station_budgets" in p
                and re.search(r"(?<![.\w])station_budgets", p) and "packet" in p.lower()]
        self.assertTrue(both, "no paragraph sets the top level station_budgets packet cap against the efficiency keys")

    def test_s10_changelog_and_one_decision_record(self):
        """S10: CHANGELOG.md has a wo-gh-42 entry and exactly one new decision record exists"""
        self.assertIn("wo-gh-42", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
        added = [p for status, p in changed_paths(self) if status == "A" and p.startswith("brain/decisions/")]
        self.assertEqual(len(added), 1, added)
        record = (ROOT / added[0]).read_text(encoding="utf-8")
        self.assertIn("partition", record.lower())

    def test_s10_builder_report_evidence(self):
        """S10 (R8): the builder report carries the literals, the base ref, the table with its sum, the count, the test files"""
        path = ROOT / "runs" / "wo-gh-42" / "builder.output.md"
        self.assertTrue(path.is_file(), "runs/wo-gh-42/builder.output.md does not exist")
        text = path.read_text(encoding="utf-8")
        for literal in (BASE_REF, "station-budgets-completeness", "15000000", "completeness"):
            self.assertIn(literal, text)
        for sid, value in FACTORY_PARTITIONS.items():
            self.assertIn(sid, text)
            self.assertIn(str(value), text)
        self.assertRegex(text, r"(?i)\b\d{3,}\s+tests\b", "the report states no full factory test count")
        new_tests = [p for status, p in changed_paths(self)
                     if status == "A" and p.startswith("tests/") and p.endswith(".py")]
        self.assertTrue(new_tests)
        for rel in new_tests:
            self.assertIn(Path(rel).name, text)

    def test_s11_diff_stays_inside_the_allowed_write_set(self):
        """S11: every changed path is in the allowed write set; pipelines/ and anvil.json are untouched"""
        outside = []
        for status, rel in changed_paths(self):
            if rel in ALLOWED_FILES or rel.startswith(LINE_BOOKKEEPING):
                continue
            if rel.startswith("docs/") and rel.endswith(".md"):
                continue
            if rel.startswith("brain/decisions/") and status == "A":
                continue
            if rel.startswith("tests/") and status == "A":
                continue
            outside.append(f"{status} {rel}")
        self.assertEqual(outside, [])
        names = [rel for _, rel in changed_paths(self)]
        self.assertNotIn("anvil.json", names)
        self.assertEqual([n for n in names if n.startswith("pipelines/")], [])

    def test_s11_existing_test_files_untouched(self):
        """S11: no test file that exists at the base ref is modified or deleted"""
        touched = [f"{status} {rel}" for status, rel in changed_paths(self)
                   if rel.startswith("tests/") and status != "A"]
        self.assertEqual(touched, [])

    def test_s11_no_dashes_in_changed_files(self):
        """S11: no em dash or en dash in any changed or new file"""
        found = []
        for status, rel in changed_paths(self):
            path = ROOT / rel
            if status == "D" or not path.is_file():
                continue
            # A station packet is the line's rendering of a frozen station
            # prompt (stations/<id>/PROMPT.md); the order neither writes nor
            # may edit that text, so packets are outside this check.
            if rel.startswith("runs/") and rel.endswith(".packet.md"):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if re.search(DASHES, text):
                found.append(rel)
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
