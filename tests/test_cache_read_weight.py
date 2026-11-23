"""Budget tokens: cache reads weighed by efficiency.cache_read_weight (operator change, decision 0017).

A token read from the prompt cache costs a fraction of a fresh one, yet it
counted in full against every token budget, so the limits measured how often
a station re-read its context rather than what the run cost. The weight
changes what the budgets read; reports keep the raw counts.
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from anvil import telemetry  # noqa: E402
from anvil.sinks import render_issue_comment  # noqa: E402

# 100000 fresh input, 900000 read from cache, 5000 output.
CACHED = {"input_tokens": 1000000, "output_tokens": 5000, "cached_input_tokens": 900000,
          "input_tokens_includes_cache": True}


def step(station="builder", usage=CACHED):
    return {"station": station, "status": "executed", "executor": {"kind": "command"}, "usage": usage,
            "usage_complete": True}


class WeightTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(telemetry.set_cache_read_weight, 1.0)

    def test_default_weight_counts_every_token(self):
        usage = telemetry.normalize_usage(CACHED)
        self.assertEqual(telemetry.cache_read_weight(), 1.0)
        self.assertEqual(telemetry.budget_tokens(usage), usage["total_tokens"])
        self.assertEqual(telemetry.weight_note(), "")

    def test_weight_applies_to_cache_reads_only(self):
        telemetry.set_cache_read_weight(0.1)
        usage = telemetry.normalize_usage(CACHED)
        self.assertEqual(usage["total_tokens"], 1005000, "the raw count is not changed")
        self.assertEqual(telemetry.budget_tokens(usage), 100000 + 90000 + 5000)
        self.assertIn("0.1", telemetry.weight_note())

    def test_usage_without_cache_reads_is_unchanged_at_any_weight(self):
        telemetry.set_cache_read_weight(0.0)
        usage = telemetry.normalize_usage({"input_tokens": 700, "output_tokens": 300})
        self.assertEqual(telemetry.budget_tokens(usage), 1000)
        self.assertIsNone(telemetry.budget_tokens(None))

    def test_invalid_weights_are_refused_by_name(self):
        for bad in (True, -0.1, 1.5, "0.1", None, float("nan")):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as caught:
                    telemetry.set_cache_read_weight(bad)
                self.assertIn("efficiency.cache_read_weight", str(caught.exception))
                with self.assertRaises(ValueError) as caught:
                    telemetry.efficiency_config({"efficiency": {"cache_read_weight": bad}})
                self.assertIn("efficiency.cache_read_weight", str(caught.exception))
        self.assertEqual(telemetry.efficiency_config({"efficiency": {"cache_read_weight": 0.1}})["cache_read_weight"], 0.1)

    def test_station_partition_reads_budget_tokens(self):
        steps = [step()]
        self.assertEqual(telemetry.precall_decision(steps, "builder", 500000)["decision"], "refuse")
        telemetry.set_cache_read_weight(0.1)
        found = telemetry.precall_decision(steps, "builder", 500000)
        self.assertEqual(found["decision"], "proceed")
        self.assertEqual(found["measured_tokens"], 195000)
        self.assertEqual(telemetry.precall_decision(steps, "builder", 195000)["decision"], "refuse")

    def test_run_cap_reads_budget_tokens_and_reports_stay_raw(self):
        steps = [step("test-writer"), step("builder")]
        limits = {"max_run_tokens": 1500000}
        self.assertIsNotNone(telemetry.budget_reason(steps, limits))
        telemetry.set_cache_read_weight(0.1)
        self.assertIsNone(telemetry.budget_reason(steps, limits))
        self.assertIsNotNone(telemetry.budget_reason(steps, {"max_run_tokens": 390000}))
        summary = telemetry.summarize_steps(steps)
        self.assertEqual(summary["total_tokens"], 2010000)
        self.assertEqual(summary["by_station"]["builder"]["total_tokens"], 1005000)

    def test_wrapper_process_takes_the_weight_from_the_environment(self):
        code = "from anvil import telemetry; print(telemetry.cache_read_weight())"
        for raw, expected in (("0.1", "0.1"), ("2", "1.0"), ("x", "1.0"), ("", "1.0")):
            with self.subTest(raw=raw):
                env = dict(os.environ, ANVIL_CACHE_READ_WEIGHT=raw)
                out = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), env=env,
                                     capture_output=True, text=True, timeout=60)
                self.assertEqual(out.stdout.strip(), expected, out.stderr)


class CommentTests(unittest.TestCase):
    RECORD = {"run_id": "r-1", "work_order_id": "wo-gh-900", "pipeline": "sdlc-default", "state": "running",
              "stations": ["intake"], "steps": [], "loopbacks": 0, "cost": None,
              "token_usage": {"total_tokens": 2010000}, "updated_at": "2026-11-23T00:00:00+00:00"}

    def test_comment_without_estimate_is_as_before(self):
        body = render_issue_comment(dict(self.RECORD))
        self.assertIn("Cost: not priced", body)
        self.assertNotIn("Budget tokens", body)

    def test_comment_shows_the_runtime_estimate_and_budget_tokens(self):
        record = dict(self.RECORD, runtime_cost_estimate_usd=1.4571,
                      token_usage={"total_tokens": 2010000, "budget_tokens": 390000})
        body = render_issue_comment(record)
        self.assertIn("Cost: about $1.46 (the runtime's own estimate, not an invoice)", body)
        self.assertIn("Budget tokens: 390000", body)
        self.assertIn("Tokens: 2010000", body)

    def test_a_priced_cost_wins_over_the_estimate(self):
        body = render_issue_comment(dict(self.RECORD, cost=2.5, runtime_cost_estimate_usd=1.0))
        self.assertIn("Cost: $2.5000", body)
        self.assertNotIn("estimate", body)

    def test_no_dashes_in_this_file(self):
        self.assertNotRegex(Path(__file__).read_text(encoding="utf-8"), "[\u2013\u2014]")


if __name__ == "__main__":
    unittest.main()
