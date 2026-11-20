"""Operator fix: a failed station names its reason within the executor's cut.

Runs wo-gh-44 (2026-11-16) and wo-gh-41 (2026-11-20) ended no_reviews with
every model station failed, and the run record held no reason: the wrapper
printed the raw result envelope, whose reason fields follow the usage block,
and the command executor keeps the first 500 characters of a failure.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for entry in (str(ROOT), str(ROOT / "tools")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

import claude_station  # noqa: E402

EXECUTOR_CUT = 500


def envelope(**extra):
    data = {
        "duration_api_ms": 3642,
        "stop_reason": "stop_sequence",
        "session_id": "6aa9c80b-00c6-42c4-aa16-80b2d4c2c8ca",
        "total_cost_usd": 0.109058,
        "usage": {"input_tokens": 2, "cache_creation_input_tokens": 20838,
                  "cache_read_input_tokens": 0, "output_tokens": 243,
                  "padding": "x" * 600},
        "type": "result",
    }
    data.update(extra)
    return json.dumps(data)


class FailureReasonTests(unittest.TestCase):
    def test_reason_names_error_fields_and_result(self):
        reason = claude_station.failure_reason(
            envelope(is_error=True, subtype="error_during_execution", num_turns=2,
                     result="The runtime refused the request."))
        self.assertIn("is_error=True", reason)
        self.assertIn("subtype=error_during_execution", reason)
        self.assertIn("num_turns=2", reason)
        self.assertIn("result=The runtime refused the request.", reason)

    def test_reason_fits_inside_the_executor_cut(self):
        raw = envelope(is_error=True, subtype="error_during_execution",
                       result="word " * 400)
        self.assertNotIn("is_error", raw[:EXECUTOR_CUT])
        reason = claude_station.failure_reason(raw)
        line = f"claude_station: claude exited 1 for station reviewer-architecture: {reason} | {raw}"
        self.assertIn("is_error=True", line[:EXECUTOR_CUT])
        self.assertIn("result=word", line[:EXECUTOR_CUT])

    def test_result_is_one_line_and_bounded(self):
        reason = claude_station.failure_reason(envelope(is_error=True, result="a\n\nb " + "c" * 900))
        self.assertNotIn("\n", reason)
        self.assertLessEqual(len(reason), 420)

    def test_not_an_envelope_gives_no_reason(self):
        self.assertEqual(claude_station.failure_reason("plain text failure"), "")
        self.assertEqual(claude_station.failure_reason(""), "")
        self.assertEqual(claude_station.failure_reason(None), "")
        self.assertEqual(claude_station.failure_reason("[1, 2]"), "")

    def test_wrapper_puts_the_reason_before_the_raw_detail(self):
        code = (ROOT / "tools" / "claude_station.py").read_text()
        self.assertIn('detail = f"{reason} | {detail}"', code)


if __name__ == "__main__":
    unittest.main()
