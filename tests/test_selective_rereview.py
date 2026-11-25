"""Selective re-review: a review that passed is counted again, not asked again (operator change, decision 0019).

After the approver returns the work to the builder, every reviewer ran
again, the ones that had passed included. With
efficiency.carry_passed_reviews set, only the reviewers that did not pass
are dispatched on the next attempt. The fake runtime and project of
tests/test_stop_futile_loops.py are reused.
"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for entry in (str(ROOT), str(ROOT / "tests")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from anvil import telemetry  # noqa: E402
from test_stop_futile_loops import Line  # noqa: E402

ON = {"carry_passed_reviews": True}


def spec_fails_first(station, attempt):
    """reviewer-spec asks for changes on attempt 1 and passes afterwards; every other reviewer passes."""
    failing = station == "reviewer-spec" and attempt == 1
    return {"station": station, "verdict": "changes_requested" if failing else "pass",
            "findings": ["the empty input case is not handled"] if failing else []}


def spec_never_passes(station, attempt):
    failing = station == "reviewer-spec"
    return {"station": station, "verdict": "changes_requested" if failing else "pass",
            "findings": ["still not handled"] if failing else []}


def reviewer_steps(report):
    return [s for s in report["steps"] if str(s.get("station", "")).startswith("reviewer")]


class SelectiveRereview(unittest.TestCase):
    def test_default_asks_every_reviewer_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, review=spec_fails_first)
            report = line.run()
            first = [c for c in line.calls[:line.calls.index("builder", line.calls.index("builder") + 1)]
                     if c.startswith("reviewer")]
            self.assertGreater(len(first), 1, "the scenario needs more than one reviewer")
            self.assertEqual(sorted(line.reviewer_calls_after(2)), sorted(first))
            self.assertEqual(report["verdict"], "approved")
            self.assertNotIn("carried", {s["status"] for s in reviewer_steps(report)})
            self.assertNotIn("reviews_carried", report["decision"]["approver"])

    def test_switch_on_dispatches_only_the_reviewer_that_did_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, review=spec_fails_first, efficiency=ON)
            report = line.run()
            self.assertEqual(line.calls.count("builder"), 2)
            self.assertEqual(line.reviewer_calls_after(2), ["reviewer-spec"])
            self.assertEqual(report["verdict"], "approved")
            approver = report["decision"]["approver"]
            counted = {c["station"]: c["verdict"] for c in approver["reviews_counted"]}
            self.assertEqual(set(counted), set(approver["reviews_expected"]), "carried reviews are counted")
            self.assertEqual(set(counted.values()), {"pass"})
            carried = approver["reviews_carried"]
            self.assertEqual({c["station"] for c in carried}, set(approver["reviews_expected"]) - {"reviewer-spec"})
            self.assertEqual({c["from_attempt"] for c in carried}, {1})

    def test_carried_step_is_recorded_and_makes_no_model_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, review=spec_fails_first, efficiency=ON)
            report = line.run()
            carried = [s for s in reviewer_steps(report) if s["status"] == "carried"]
            self.assertTrue(carried)
            for step in carried:
                self.assertIn("carried from attempt 1", step["detail"])
                self.assertIsNone(step.get("executor"))
                self.assertFalse(step.get("usage"))
            self.assertEqual(report["token_usage"]["calls"], len(line.calls), "one counted call per runtime call")

    def test_reviewer_that_keeps_failing_is_asked_on_every_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            line = Line(tmp, review=spec_never_passes, efficiency=ON)
            report = line.run(max_loopbacks=2)
            self.assertEqual(line.calls.count("builder"), 3)
            self.assertEqual(line.reviewer_calls_after(2), ["reviewer-spec", "reviewer-spec"])
            self.assertNotEqual(report["verdict"], "approved")

    def test_first_attempt_is_reviewed_in_full_with_the_switch_on(self):
        with tempfile.TemporaryDirectory() as tmp:
            off = Line(Path(tmp) / "off", review=spec_fails_first)
            off.run(max_loopbacks=0)
            on = Line(Path(tmp) / "on", review=spec_fails_first, efficiency=ON)
            on.run(max_loopbacks=0)
            self.assertEqual([c for c in on.calls if c.startswith("reviewer")],
                             [c for c in off.calls if c.startswith("reviewer")])

    def test_switch_must_be_boolean(self):
        with self.assertRaises(ValueError) as caught:
            telemetry.efficiency_config({"efficiency": {"carry_passed_reviews": "yes"}})
        self.assertIn("efficiency.carry_passed_reviews", str(caught.exception))

    def test_no_dashes_in_this_file(self):
        self.assertNotRegex(Path(__file__).read_text(encoding="utf-8"), "[\\u2013\\u2014]")


if __name__ == "__main__":
    unittest.main()
