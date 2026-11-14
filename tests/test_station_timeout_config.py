"""Configuration guards for the station timeout (spec: station-timeout, wo-gh-39).

Complements tests/test_station_timeout.py:
  - anvil.config.PRODUCING_STATIONS stays in sync with the wrapper WRITE_STATIONS
  - the command executor hands runtime.station_timeout_seconds to the wrapper
    as ANVIL_STATION_TIMEOUT_SECONDS, and an environment value wins
  - an invalid runtime.station_timeout_seconds fails at the boundary
  - a timed_out attempt in the usage artifact surfaces as a timeout record
"""
import json, os, sys, tempfile, unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from anvil import config as anvil_config
from anvil.executor import CommandExecutor, ExecutorError

VAR = "ANVIL_STATION_TIMEOUT_SECONDS"
ENV_DUMP = (f"{sys.executable} -c \"import json,os,sys; "
            f"open(sys.argv[1],'w').write(json.dumps(os.environ.get('{VAR}')))\" {{output}}")


def clean_environ(**extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith("ANVIL_")}
    env.update(extra)
    return env


class TestProducingSet(unittest.TestCase):
    def test_config_producing_stations_match_wrapper_write_stations(self):
        import claude_station
        self.assertEqual(set(anvil_config.PRODUCING_STATIONS), set(claude_station.WRITE_STATIONS))


class TestExecutorHandoff(unittest.TestCase):
    def run_dump(self, config, environ):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, environ, clear=True):
            executor = CommandExecutor(dict(config, command=ENV_DUMP))
            out = Path(tmp) / "builder.output.md"
            executor.execute("packet", "builder", output_path=out, cwd=tmp)
            return executor, json.loads(out.read_text())

    def test_project_value_reaches_the_wrapper(self):
        executor, seen = self.run_dump({"station_timeout_seconds": 4000}, clean_environ())
        self.assertEqual(seen, "4000")
        self.assertGreaterEqual(executor.timeout, 4000)

    def test_environment_value_wins_over_project_value(self):
        _, seen = self.run_dump({"station_timeout_seconds": 4000}, clean_environ(**{VAR: "120"}))
        self.assertEqual(seen, "120")

    def test_project_value_above_ceiling_is_clamped_before_handoff(self):
        executor, seen = self.run_dump({"station_timeout_seconds": 99999}, clean_environ())
        self.assertEqual(seen, "7200")
        self.assertGreaterEqual(executor.timeout, 7200)

    def test_no_project_value_hands_nothing(self):
        _, seen = self.run_dump({}, clean_environ())
        self.assertIsNone(seen)

    def test_invalid_project_value_is_rejected_with_its_key(self):
        for bad in ("soon", 0, -5, True):
            with self.subTest(bad=bad), self.assertRaises(ValueError) as ctx:
                CommandExecutor({"command": "true", "station_timeout_seconds": bad})
            self.assertIn("runtime.station_timeout_seconds", str(ctx.exception))


class TestTimeoutEvidence(unittest.TestCase):
    def test_timed_out_attempt_in_usage_artifact_becomes_a_timeout_record(self):
        attempt = {"attempt": 1, "status": "timed_out", "duration_ms": 1234.5,
                   "timeout_seconds": 1, "reason": "station timeout of 1s reached (class default)"}
        artifact = json.dumps({"schema": "anvil/usage@1", "usage": None, "attempts": [attempt]})
        writer = (f"{sys.executable} -c \"import sys; open(sys.argv[1]+'.usage.json','w')"
                  f".write(sys.argv[2]); sys.exit(4)\" {{output}} '{artifact}'")
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, clean_environ(), clear=True):
            executor = CommandExecutor({"command": writer})
            with self.assertRaises(ExecutorError) as ctx:
                executor.execute("packet", "builder", output_path=Path(tmp) / "builder.output.md", cwd=tmp)
        record = ctx.exception.result["timeout"]
        self.assertEqual(record, {"source": "station", "timeout_seconds": 1,
                                  "elapsed_ms": 1234.5, "reason": attempt["reason"]})


if __name__ == "__main__":
    unittest.main()
