"""Stop futile loops (spec: stop-futile-loops, work order wo-gh-49).

Every run test drives a scripted sdlc-default run through the real runner
(anvil.runner.run_pipeline) with an in process fake runtime, in the manner of
tests/test_continuous_run_accounting.py: no network, no model. The fake
builder writes the files its attempt is scripted to write into the project
tree; the fake reviewers write runs/<wo>/<station>.review.json; the checks
gate runs a real shell command that prints the project file gate.txt and
fails when it is non-empty, so the gate output of each attempt is whatever
that attempt's builder left in gate.txt.

Interface these tests pin where the spec leaves names to the builder:
  anvil.model.Review carries the kept question as the attribute owner_ruling
      (None or absent when no question was kept), and Review.to_dict() carries
      it as "owner_ruling", so the reviewer envelope keeps it (R1.1, R1.3);
  the reviewer step record in report["steps"] carries owner_ruling_ignored, a
      string with the reason, when a value was dropped (R1.3);
  report["owner_rulings"] = [{"station": ..., "question": ...}] and
      report["next_human_action"] a non-empty string (R2.2, R5.3);
  a malformed efficiency.gate_failure_patterns makes run_pipeline raise
      ValueError naming efficiency.gate_failure_patterns (R4.1);
  sinks are observed by wrapping anvil.sinks.SinkSet.deliver, never by mocking
      the runner (R5.4).

Scenario map:
  S1  (R6.1a)  test_s1_owner_ruling_ends_the_run_after_one_builder_call,
               test_s1_comment_prints_the_question_under_its_heading,
               test_s1_reviewer_packet_and_prompts_carry_the_instruction,
               test_s1_exit_statuses_are_registered
  S2  (R6.1b)  test_s2_ordinary_finding_still_loops_back
  S3  (R6.1c)  test_s3_unchanged_second_attempt_ends_with_no_progress,
               test_s3_second_attempt_writing_only_under_runs_is_no_progress,
               test_s3_unanswered_checks_gate_loopback_is_no_progress,
               test_s3_first_attempt_is_never_compared
  S4  (R6.1d)  test_s4_same_fail_line_twice_ends_with_checks_stuck,
               test_s4_long_repeated_signature_is_truncated
  S5  (R6.1d)  test_s5_different_failure_loops_on
  S6  (R6.1e)  test_s6_unrecognized_failure_never_stops_early
  S7  (R6.1f)  test_s7_owner_ruling_stop_off_loops_back,
               test_s7_no_progress_stop_off_dispatches_gate_and_reviewers,
               test_s7_repeated_gate_failure_stop_off_makes_third_attempt,
               test_s7_custom_failure_patterns,
               test_s7_malformed_failure_patterns_fail_loading
  S8  (R6.1g)  test_s8_validate_review_file_accepts_owner_ruling,
               test_s8_parse_review_keeps_owner_ruling,
               test_s8_parse_review_drops_bad_values,
               test_s8_dropped_value_is_recorded_on_the_step,
               test_s8_review_suffix_unchanged
  S9           test_s9_stops_reach_the_sink_and_add_no_event_kind
  S10          test_s10_no_dashes_in_this_file,
               test_s10_protected_paths_untouched (skips unless wo-gh-49),
               test_s10_no_dashes_in_lines_this_order_adds (skips unless wo-gh-49)
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
for entry in (str(ROOT), str(ROOT / "tools")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from anvil import runner as anvil_runner  # noqa: E402
from anvil import sinks as anvil_sinks  # noqa: E402
from anvil.model import WorkOrder  # noqa: E402
from anvil.pipeline import load_pipeline  # noqa: E402
from anvil.scaffold import init_project  # noqa: E402
from anvil.stations import load_registry  # noqa: E402
import claude_station  # noqa: E402
import line_comment  # noqa: E402

BASE_REF = "d74c83aefff95fba777ca04505116cfb63c6c8f3"
WO = "wo-sfl"
MODEL = "claude-opus-5-5"
SMALL = {"input_tokens": 100, "output_tokens": 10}
QUESTION = ("R2 contradicts protected test tests/test_example.py::test_x; "
            "options: amend the test or drop R2")
FAIL_X = "FAIL: test_x (tests.test_example.T.test_x)"
FAIL_Y = "FAIL: test_y (tests.test_example.T.test_y)"
FAIL_Z = "FAIL: test_z (tests.test_example.T.test_z)"
STOPS = ("owner_ruling_needed", "no_progress", "checks_stuck")
BASE_EVENT_KINDS = {"run.started", "run.resumed", "station.finished", "loopback", "run.finished", "run.crashed"}
AFTER_APPROVER = ("triage-human", "deployer", "observer")
CHECK_SCRIPT = (
    "import pathlib, sys\n"
    "p = pathlib.Path('gate.txt')\n"
    "text = p.read_text(encoding='utf-8') if p.is_file() else ''\n"
    "if text.strip():\n"
    "    print(text)\n"
    "    sys.exit(1)\n"
)


def changes_requested(station, attempt):
    return {"station": station, "verdict": "changes_requested" if station == "reviewer-spec" else "pass",
            "findings": ["the empty input case is not handled"]}


def with_ruling(question=QUESTION):
    def review(station, attempt):
        data = changes_requested(station, attempt)
        if station == "reviewer-spec":
            data["owner_ruling"] = question
        return data
    return review


def all_pass(station, attempt):
    return {"station": station, "verdict": "pass", "findings": ["all good"]}


def gate_lines(*per_attempt):
    """Builder script: attempt n writes app.py (a real change) and gate.txt with per_attempt[n-1]."""
    return [{"app.py": f"value = {n}\n", "gate.txt": text} for n, text in enumerate(per_attempt, start=1)]


class Line:
    """A scaffolded project, a fake runtime and one run of sdlc-default."""
    name = "fake"

    def __init__(self, tmp, builds=None, review=all_pass, checks=False, efficiency=None):
        self.tmp = Path(tmp)
        self.project = init_project(self.tmp / "project", "Futile loops demo")
        self.run_dir = self.project / "runs" / WO
        self.builds = builds if builds is not None else [{"app.py": f"value = {n}\n"} for n in range(1, 6)]
        self.review = review
        self.calls = []
        self.packets = []
        config_path = self.project / "anvil.yaml"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config.setdefault("efficiency", {}).update(efficiency or {})
        config_path.write_text(json.dumps(config), encoding="utf-8")
        if checks:
            script = self.tmp / "check_gate.py"
            script.write_text(CHECK_SCRIPT, encoding="utf-8")
            anvil_json = json.loads((self.project / "anvil.json").read_text(encoding="utf-8"))
            anvil_json["checks"] = [f'"{sys.executable}" "{script}"']
            (self.project / "anvil.json").write_text(json.dumps(anvil_json), encoding="utf-8")

    # the fake runtime
    def execute(self, text, station_id, **kwargs):
        self.calls.append(station_id)
        self.packets.append((station_id, text))
        output = "done"
        if station_id == "intake":
            output = json.dumps({"intake_outcome": {"outcome": "accepted"}})
        elif station_id == "builder":
            attempt = self.calls.count("builder")
            files = self.builds[attempt - 1] if attempt <= len(self.builds) else {}
            for rel, content in files.items():
                path = self.project / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            output = f"Builder report, attempt {attempt}"
        elif station_id.startswith("reviewer"):
            attempt = self.calls.count("builder")
            data = self.review(station_id, attempt)
            if data is not None:
                self.run_dir.mkdir(parents=True, exist_ok=True)
                (self.run_dir / f"{station_id}.review.json").write_text(json.dumps(data), encoding="utf-8")
        return {"output": output, "usage": dict(SMALL), "model": MODEL}

    def run(self, max_loopbacks=2, raise_errors=False):
        reg = load_registry(ROOT / "stations")
        pipe = load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))
        try:
            anvil_runner.run_pipeline(self.project, pipe, WorkOrder(id=WO, kind="feature", title="Futile loops"),
                                      registry=reg, executor=self, max_loopbacks=max_loopbacks)
        except Exception:
            if raise_errors:
                raise
        return self.report()

    def report(self):
        path = self.run_dir / "report.json"
        if not path.is_file():
            raise AssertionError("the run left no report.json")
        return json.loads(path.read_text(encoding="utf-8"))

    def reviewer_calls_after(self, nth_builder):
        """Reviewer calls the runtime received after the nth builder call."""
        seen = 0
        after = []
        for station in self.calls:
            if station == "builder":
                seen += 1
            elif seen >= nth_builder and station.startswith("reviewer"):
                after.append(station)
        return after

    def events(self):
        path = self.run_dir / "events.jsonl"
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def statuses(report, stations):
    return {s["station"]: s["status"] for s in report["steps"] if s.get("station") in stations}


def gate_runs(report):
    return [s for s in report["steps"] if s.get("station") == "checks-gate" and s.get("status") != "not_run"]


class StopAssertions(unittest.TestCase):
    def assert_stop(self, report, exit_status):
        self.assertEqual(report.get("exit_status"), exit_status, report.get("termination_reason"))
        self.assertIn(exit_status, anvil_runner.EXIT_STATUSES)
        reason = report.get("termination_reason")
        self.assertIsInstance(reason, str)
        self.assertTrue(reason.strip())
        action = report.get("next_human_action")
        self.assertIsInstance(action, str, "R5.3: a stop names the next human action")
        self.assertTrue(action.strip())
        self.assertEqual(statuses(report, AFTER_APPROVER), {sid: "not_run" for sid in AFTER_APPROVER})
        return reason


# -- S1, S2: an owner ruling ---------------------------------------------------

class OwnerRuling(StopAssertions):
    def test_s1_exit_statuses_are_registered(self):
        """S1, R5.1: the three stops join the runner's closed set of exit statuses"""
        for status in STOPS:
            self.assertIn(status, anvil_runner.EXIT_STATUSES)
        for status in ("completed", "checks_stopped", "runtime_refused", "error", "signal"):
            self.assertIn(status, anvil_runner.EXIT_STATUSES, "existing exit statuses are kept")

    def test_s1_owner_ruling_ends_the_run_after_one_builder_call(self):
        """S1 (R2.1, R2.2, R2.3, R2.5, R5.3): reviewer-spec asks for the owner, the run ends owner_ruling_needed"""
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, review=with_ruling())
            report = line.run()
            self.assertEqual(line.calls.count("builder"), 1, "no loopback after an owner ruling")
            reason = self.assert_stop(report, "owner_ruling_needed")
            self.assertIn("reviewer-spec", reason)
            self.assertIn(QUESTION, reason)
            self.assertEqual(report.get("owner_rulings"), [{"station": "reviewer-spec", "question": QUESTION}])
            self.assertEqual(report.get("verdict"), "changes_requested", "the verdict vocabulary does not grow")
            gate = (report.get("decision") or {}).get("human_gate") or {}
            self.assertIn("owner ruling needed", str(gate.get("rule")).lower())
            self.assertTrue(report.get("human_required"))
            self.assertFalse([s for s in report["steps"] if s.get("status") == "loopback"])

    def test_s1_comment_prints_the_question_under_its_heading(self):
        """S1 (R2.4): tools/line_comment.py prints the question under the heading Owner ruling needed"""
        with tempfile.TemporaryDirectory() as tmp:
            report = Line(tmp, review=with_ruling()).run()
        for code in (1, 3):
            lines = line_comment.render(report, code).splitlines()
            heads = [i for i, text in enumerate(lines) if "Owner ruling needed" in text]
            self.assertTrue(heads, "no Owner ruling needed heading in the comment")
            below = lines[heads[0] + 1:]
            self.assertTrue([text for text in below if QUESTION in text and "reviewer-spec" in text],
                            "the question and its station are not listed under the heading")

    def test_s1_comment_without_rulings_has_no_heading(self):
        """S1 (R2.4): a report that did not end with an owner ruling prints no Owner ruling needed heading"""
        with tempfile.TemporaryDirectory() as tmp:
            report = Line(tmp, review=all_pass).run()
        self.assertNotIn("Owner ruling needed", line_comment.render(report, 0))

    def test_s1_reviewer_packet_and_prompts_carry_the_instruction(self):
        """S1 (R1.2): the reviewer packet and every reviewer prompt tell the reviewer when to set owner_ruling"""
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, review=all_pass)
            line.run()
        reviewer_packets = [text for sid, text in line.packets if sid.startswith("reviewer")]
        self.assertTrue(reviewer_packets)
        for text in reviewer_packets:
            self.assertIn("owner_ruling", text)
        prompts = sorted((ROOT / "stations").glob("reviewer-*/PROMPT.md"))
        self.assertTrue(prompts)
        for prompt in prompts:
            self.assertIn("owner_ruling", prompt.read_text(encoding="utf-8"), str(prompt))
        self.assertNotIn("owner_ruling", claude_station.review_suffix(WO, "reviewer-spec"))

    def test_s2_ordinary_finding_still_loops_back(self):
        """S2 (R2.1): the same review without owner_ruling sends the work back to the builder"""
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, review=changes_requested)
            report = line.run()
            self.assertGreaterEqual(line.calls.count("builder"), 2)
            self.assertNotEqual(report.get("exit_status"), "owner_ruling_needed")
            self.assertFalse(report.get("owner_rulings"))


# -- S3: an attempt that changes nothing ----------------------------------------

class NoProgress(StopAssertions):
    def test_s3_unchanged_second_attempt_ends_with_no_progress(self):
        """S3 (R3.1, R3.2): a second builder attempt writing no file ends no_progress, no gate or reviewer for it"""
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, builds=[{"app.py": "value = 1\n"}, {}], review=changes_requested, checks=True)
            report = line.run()
            self.assertEqual(line.calls.count("builder"), 2)
            self.assertEqual(line.calls[-1], "builder", "a station ran after the unchanged attempt")
            self.assertEqual(line.reviewer_calls_after(2), [])
            self.assertEqual(len(gate_runs(report)), 1, "the checks gate ran for the unchanged attempt")
            reason = self.assert_stop(report, "no_progress")
            self.assertRegex(reason.lower(), r"attempt\D{0,20}2\b")
            self.assertIn("approver", reason)

    def test_s3_second_attempt_writing_only_under_runs_is_no_progress(self):
        """S3 (R3.1): a second attempt that writes only under runs/ also ends no_progress"""
        with tempfile.TemporaryDirectory() as tmp:
            builds = [{"app.py": "value = 1\n"}, {f"runs/{WO}/scratch.md": "notes only\n"}]
            line = Line(tmp, builds=builds, review=changes_requested)
            report = line.run()
            self.assertEqual(line.reviewer_calls_after(2), [])
            self.assert_stop(report, "no_progress")

    def test_s3_unanswered_checks_gate_loopback_is_no_progress(self):
        """S3 (R3.2): an unchanged attempt after a checks gate loopback ends no_progress naming the gate"""
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, builds=[{"app.py": "value = 1\n", "gate.txt": "Segmentation fault\n"}, {}],
                        checks=True)
            report = line.run()
            self.assertEqual(line.calls.count("builder"), 2)
            self.assertEqual(len(gate_runs(report)), 1)
            reason = self.assert_stop(report, "no_progress")
            self.assertIn("checks", reason.lower())

    def test_s3_first_attempt_is_never_compared(self):
        """S3 (R3.1): a first builder attempt that writes nothing goes on to the gate and the reviewers"""
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, builds=[{}], review=all_pass)
            report = line.run()
            self.assertNotEqual(report.get("exit_status"), "no_progress")
            self.assertTrue(line.reviewer_calls_after(1))


# -- S4 to S6: the same gate failure twice --------------------------------------

class ChecksStuck(StopAssertions):
    def test_s4_same_fail_line_twice_ends_with_checks_stuck(self):
        """S4 (R4.1, R4.2): the same unittest FAIL line on attempts 1 and 2 ends checks_stuck, no third builder"""
        with tempfile.TemporaryDirectory() as tmp:
            noise = "Ran 12 tests in 0.1s\n"
            line = Line(tmp, builds=gate_lines(f"{FAIL_X}\n{noise}", f"{noise}{FAIL_X}\nother text\n",
                                               f"{FAIL_X}\n"), checks=True)
            report = line.run(max_loopbacks=2)
            self.assertEqual(line.calls.count("builder"), 2)
            self.assertEqual(line.reviewer_calls_after(1), [])
            reason = self.assert_stop(report, "checks_stuck")
            self.assertIn(FAIL_X, reason)
            self.assertEqual(len(gate_runs(report)), 2)

    def test_s4_each_default_pattern_is_recognized(self):
        """S4 (R4.1): unittest ERROR:, pytest FAILED and node --test not ok lines are failure lines by default"""
        for text in ("ERROR: test_x (tests.test_example.T.test_x)",
                     "FAILED tests/test_example.py::test_x - AssertionError",
                     "not ok 3 - renders the header"):
            with self.subTest(line=text), tempfile.TemporaryDirectory() as tmp:
                line = Line(tmp, builds=gate_lines(text + "\n", text + "\n", text + "\n"), checks=True)
                report = line.run(max_loopbacks=2)
                self.assertEqual(line.calls.count("builder"), 2)
                self.assertIn(text, self.assert_stop(report, "checks_stuck"))

    def test_s4_long_repeated_signature_is_truncated(self):
        """S4 (R4.2): a repeated signature of more than 2000 characters gives a reason of at most 2000"""
        many = "".join(f"FAIL: test_{n:03d} (tests.test_example.LongSuiteName.test_{n:03d}_{'x' * 30})\n"
                       for n in range(60))
        self.assertGreater(len(many), 2000)
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, builds=gate_lines(many, many, many), checks=True)
            report = line.run(max_loopbacks=2)
            reason = self.assert_stop(report, "checks_stuck")
            self.assertLessEqual(len(reason), 2000)
            self.assertIn("FAIL: test_", reason)

    def test_s5_different_failure_loops_on(self):
        """S5 (R4.2, R4.3): test_x then test_y is progress, the line loops back for attempt 3 as today"""
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, builds=gate_lines(FAIL_X + "\n", FAIL_Y + "\n", FAIL_Z + "\n"), checks=True)
            report = line.run(max_loopbacks=2)
            self.assertEqual(line.calls.count("builder"), 3)
            self.assertEqual(report.get("exit_status"), "checks_stopped")
            self.assertEqual(report.get("loopbacks"), 2)

    def test_s6_unrecognized_failure_never_stops_early(self):
        """S6 (R4.3): the same Segmentation fault output twice is not checks_stuck; attempts run out as today"""
        with tempfile.TemporaryDirectory() as tmp:
            seg = "Segmentation fault\n"
            line = Line(tmp, builds=gate_lines(seg, seg, seg), checks=True)
            report = line.run(max_loopbacks=2)
            self.assertNotEqual(report.get("exit_status"), "checks_stuck")
            self.assertEqual(report.get("exit_status"), "checks_stopped")
            self.assertEqual(line.calls.count("builder"), 3)
            self.assertEqual(report.get("loopbacks"), 2)
            self.assertEqual(len(gate_runs(report)), 3)


# -- S7: each stop can be turned off --------------------------------------------

class Switches(unittest.TestCase):
    def test_s7_owner_ruling_stop_off_loops_back(self):
        """S7 (R5.2): stop_on_owner_ruling false, the S1 run loops back and the review still keeps the question"""
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, review=with_ruling(), efficiency={"stop_on_owner_ruling": False})
            report = line.run()
            self.assertGreaterEqual(line.calls.count("builder"), 2)
            self.assertNotEqual(report.get("exit_status"), "owner_ruling_needed")
            envelope = json.loads((line.run_dir / "envelopes" / "reviewer-spec.envelope.json")
                                  .read_text(encoding="utf-8"))
            self.assertEqual((envelope.get("review") or {}).get("owner_ruling"), QUESTION)

    def test_s7_no_progress_stop_off_dispatches_gate_and_reviewers(self):
        """S7 (R5.2): stop_on_no_progress false, the S3 run dispatches the gate and reviewers for attempt 2"""
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, builds=[{"app.py": "value = 1\n"}, {}], review=changes_requested, checks=True,
                        efficiency={"stop_on_no_progress": False})
            report = line.run()
            self.assertNotEqual(report.get("exit_status"), "no_progress")
            self.assertTrue(line.reviewer_calls_after(2))
            self.assertGreaterEqual(len(gate_runs(report)), 2)

    def test_s7_repeated_gate_failure_stop_off_makes_third_attempt(self):
        """S7 (R5.2): stop_on_repeated_gate_failure false, the S4 run makes a third builder attempt"""
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, builds=gate_lines(FAIL_X + "\n", FAIL_X + "\n", FAIL_X + "\n"), checks=True,
                        efficiency={"stop_on_repeated_gate_failure": False})
            report = line.run(max_loopbacks=2)
            self.assertEqual(line.calls.count("builder"), 3)
            self.assertEqual(report.get("exit_status"), "checks_stopped")

    def test_s7_custom_failure_patterns(self):
        """S7 (R4.1): gate_failure_patterns ["^BROKEN "] stops on BROKEN widget and no longer on FAIL: test_x"""
        efficiency = {"gate_failure_patterns": ["^BROKEN "]}
        with tempfile.TemporaryDirectory() as tmp:
            text = "BROKEN widget\n"
            line = Line(tmp, builds=gate_lines(text, text, text), checks=True, efficiency=efficiency)
            report = line.run(max_loopbacks=2)
            self.assertEqual(report.get("exit_status"), "checks_stuck")
            self.assertEqual(line.calls.count("builder"), 2)
            self.assertIn("BROKEN widget", report.get("termination_reason", ""))
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, builds=gate_lines(FAIL_X + "\n", FAIL_X + "\n", FAIL_X + "\n"), checks=True,
                        efficiency=efficiency)
            report = line.run(max_loopbacks=2)
            self.assertEqual(report.get("exit_status"), "checks_stopped")
            self.assertEqual(line.calls.count("builder"), 3)

    def test_s7_malformed_failure_patterns_fail_loading(self):
        """S7 (R4.1): a pattern that does not compile or a value that is not a list of strings is an error naming the key"""
        for bad in ("(", ["("], [7], {"a": "b"}):
            with self.subTest(value=bad), tempfile.TemporaryDirectory() as tmp:
                line = Line(tmp, efficiency={"gate_failure_patterns": bad})
                with self.assertRaises(ValueError) as caught:
                    line.run(raise_errors=True)
                self.assertIn("efficiency.gate_failure_patterns", str(caught.exception))
                self.assertNotIn("builder", line.calls)


# -- S8: the review contract ----------------------------------------------------

class ReviewContract(unittest.TestCase):
    def review_text(self, **extra):
        return json.dumps({"station": "reviewer-spec", "verdict": "changes_requested", "findings": ["f1"], **extra})

    def test_s8_validate_review_file_accepts_owner_ruling(self):
        """S8 (R1.3): validate_review_file accepts a review with owner_ruling, and with a value it will drop"""
        for value in ("Q?", 7, "   "):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "reviewer-spec.review.json"
                path.write_text(self.review_text(owner_ruling=value), encoding="utf-8")
                self.assertEqual(claude_station.validate_review_file(path, "reviewer-spec"), (True, ""))

    def test_s8_parse_review_keeps_owner_ruling(self):
        """S8 (R1.1, R1.3): parse_review keeps owner_ruling Q? with verdict and findings unchanged"""
        review = anvil_runner.parse_review(self.review_text(owner_ruling="Q?"), "reviewer-spec")
        self.assertIsNotNone(review)
        self.assertEqual((review.verdict, review.findings), ("changes_requested", ["f1"]))
        self.assertEqual(getattr(review, "owner_ruling", None), "Q?")
        self.assertEqual(review.to_dict().get("owner_ruling"), "Q?")

    def test_s8_parse_review_drops_bad_values(self):
        """S8 (R1.3): owner_ruling 7 or blank is dropped and the review still counts unchanged"""
        for value in (7, "   ", None, ["Q?"]):
            with self.subTest(value=value):
                review = anvil_runner.parse_review(self.review_text(owner_ruling=value), "reviewer-spec")
                self.assertIsNotNone(review)
                self.assertEqual((review.station, review.verdict, review.findings),
                                 ("reviewer-spec", "changes_requested", ["f1"]))
                self.assertFalse(getattr(review, "owner_ruling", None))
        plain = anvil_runner.parse_review(self.review_text(), "reviewer-spec")
        self.assertFalse(getattr(plain, "owner_ruling", None), "a review without the field means what it means today")

    def test_s8_dropped_value_is_recorded_on_the_step(self):
        """S8 (R1.3): a dropped owner_ruling is recorded as owner_ruling_ignored with its reason, no stop"""
        for value, words in ((7, ("not a string", "int")), ("   ", ("empty",))):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                def review(station, attempt, value=value):
                    data = changes_requested(station, attempt)
                    if station == "reviewer-spec":
                        data["owner_ruling"] = value
                    return data
                line = Line(tmp, review=review)
                report = line.run(max_loopbacks=0)
                self.assertNotEqual(report.get("exit_status"), "owner_ruling_needed")
                self.assertEqual(report.get("verdict"), "changes_requested")
                counted = ((report.get("decision") or {}).get("approver") or {}).get("reviews_counted") or []
                self.assertIn({"station": "reviewer-spec", "verdict": "changes_requested"}, counted)
                spec_steps = [s for s in report["steps"] if s.get("station") == "reviewer-spec"]
                ignored = [str(s.get("owner_ruling_ignored")) for s in spec_steps if s.get("owner_ruling_ignored")]
                self.assertTrue(ignored, "owner_ruling_ignored is not on the reviewer-spec step")
                for word in words:
                    self.assertIn(word, ignored[0])

    def test_s8_review_suffix_unchanged(self):
        """S8 (R1.2): review_suffix returns the same text as at the base ref"""
        expected = ("\n\n## Runtime reminder\n\n"
                    f"Your complete answer is exactly one review JSON object written to "
                    f"runs/{WO}/reviewer-spec.review.json. The free output transcript "
                    "stays as provenance and is never parsed for a review.\n")
        self.assertEqual(claude_station.review_suffix(WO, "reviewer-spec"), expected)


# -- S9: the stops reach the live progress comment ------------------------------

class SinkRecorder:
    """A recording fake sink: wraps SinkSet.deliver and keeps every record handed to the sinks."""

    def __init__(self):
        self.records = []

    def __enter__(self):
        recorder = self

        def deliver(sink_set, record, export_errors):
            recorder.records.append(json.loads(json.dumps(record)))
            return []

        self._patch = mock.patch.object(anvil_sinks.SinkSet, "deliver", deliver)
        self._patch.start()
        return self

    def __exit__(self, *exc):
        self._patch.stop()
        return False


class Progress(unittest.TestCase):
    def scripted(self, tmp, status):
        if status == "owner_ruling_needed":
            return Line(tmp, review=with_ruling())
        if status == "no_progress":
            return Line(tmp, builds=[{"app.py": "value = 1\n"}, {}], review=changes_requested)
        return Line(tmp, builds=gate_lines(FAIL_X + "\n", FAIL_X + "\n", FAIL_X + "\n"), checks=True)

    def test_s9_stops_reach_the_sink_and_add_no_event_kind(self):
        """S9 (R5.4): the last record handed to the sink carries the stop's exit_status; no new event kind"""
        for status in STOPS:
            with self.subTest(exit_status=status), tempfile.TemporaryDirectory() as tmp, SinkRecorder() as sink:
                line = self.scripted(tmp, status)
                report = line.run()
                self.assertEqual(report.get("exit_status"), status)
                self.assertTrue(sink.records, "no record reached the sinks")
                self.assertEqual(sink.records[-1].get("exit_status"), status)
                self.assertEqual(sink.records[-1].get("state"), "finished")
                kinds = {event.get("event") for event in line.events()}
                self.assertLessEqual(kinds, BASE_EVENT_KINDS)
                self.assertIn("run.finished", kinds)


# -- S10: guardrails --------------------------------------------------------------

class Guardrails(unittest.TestCase):
    def test_s10_no_dashes_in_this_file(self):
        """S10: this test file carries no em or en dash"""
        text = Path(__file__).read_text(encoding="utf-8")
        self.assertNotIn("\u2014", text)
        self.assertNotIn("\u2013", text)

    @staticmethod
    def git(*args):
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout

    @unittest.skipUnless(os.environ.get("ANVIL_WORK_ORDER_ID") == "wo-gh-49", "facts about the wo-gh-49 run only")
    def test_s10_protected_paths_untouched(self):
        """S10 (R6.3): no existing test, workflow, pipeline, anvil.json or sinks module modified or deleted"""
        changed = self.git("diff", "--name-only", "--diff-filter=MD", BASE_REF, "--",
                           "tests", ".github/workflows", "pipelines", "anvil.json",
                           "anvil/sinks.py", "anvil/telemetry.py").split()
        self.assertEqual(changed, [])

    @unittest.skipUnless(os.environ.get("ANVIL_WORK_ORDER_ID") == "wo-gh-49", "facts about the wo-gh-49 run only")
    def test_s10_no_dashes_in_lines_this_order_adds(self):
        """S10: no line this order adds outside runs/ carries an em or en dash"""
        diff = self.git("diff", BASE_REF, "--", ".", ":(exclude)runs")
        added = [line for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")]
        self.assertEqual([line for line in added if "\u2014" in line or "\u2013" in line], [])


if __name__ == "__main__":
    unittest.main()
