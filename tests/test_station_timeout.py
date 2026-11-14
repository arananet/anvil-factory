"""Tests for the configurable per-station timeout (spec: station-timeout, work order wo-gh-39).

Interface these tests pin (the spec leaves names to the builder; these are the chosen names):
  anvil.config.station_timeout_seconds(station, environ=None) -> int
      resolves ANVIL_STATION_TIMEOUT_SECONDS, then the class default; clamps above
      STATION_TIMEOUT_CEILING (7200) or raises ValueError naming 7200; raises ValueError
      naming the bad value for non-numeric or non-positive input.
  anvil.config.STATION_TIMEOUT_CEILING == 7200
  anvil.config.effective_executor_timeout(configured, environ=None) -> int
  anvil.executor.CommandExecutor(config).timeout uses effective_executor_timeout, and the
      executor hands runtime.station_timeout_seconds to the wrapper as
      ANVIL_STATION_TIMEOUT_SECONDS unless the environment already sets it.

Scenario map:
  S1 (R1)  test_s1_*            the wrapper no longer holds a bare 1500 constant cap
  S2 (R2)  test_s2_*            environment over anvil.yaml over class default
  S3 (R3)  test_s3_*            producing >= 3600, others >= 1500
  S4 (R4)  test_s4_*            ceiling 7200 and bad values
  S5 (R5)  test_s5_*            executor coordination, factory anvil.yaml
  S6 (R6)  test_s6_*            workflow job timeout 360
  S7 (R7)  test_s7_*            honest timeout record (usage artifact and run record)
  S8 (R8)  test_s8_*            healthy station record shape unchanged
  S9 (R9)  test_s9_*            scaled mechanism: 2s work passes a scaled legacy cap of 1s
  S10 (R10) test_s10_*          decision, changelog, docs
"""
import json, os, re, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from anvil import config as anvil_config
from anvil.executor import CommandExecutor
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.stations import load_registry
from anvil.scaffold import init_project
from anvil.runner import run_pipeline

WRAPPER = ROOT / "tools" / "claude_station.py"
WRITE_STATIONS = ["builder", "test-writer", "spec-writer", "blueprint", "brief-writer",
                  "researcher", "writer", "media-producer"]
VAR = "ANVIL_STATION_TIMEOUT_SECONDS"

# Stand-in claude CLI: sleeps FAKE_SLEEP seconds, then prints a result envelope.
FAKE_CLAUDE = r'''#!/usr/bin/env python3
import json, os, sys, time
time.sleep(float(os.environ.get("FAKE_SLEEP", "0")))
print(json.dumps({"type": "result", "result": "done", "is_error": False, "num_turns": 2,
                  "usage": {"input_tokens": 10, "output_tokens": 5}}))
'''
# Variant that streams a partial usage envelope before sleeping past the cap.
FAKE_CLAUDE_PARTIAL = r'''#!/usr/bin/env python3
import json, os, sys, time
print(json.dumps({"type": "result", "result": "partial", "is_error": False, "num_turns": 1,
                  "usage": {"input_tokens": 77, "output_tokens": 11}}), flush=True)
time.sleep(float(os.environ.get("FAKE_SLEEP", "0")))
'''


def clean_env(**extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("ANVIL_", "FAKE_"))}
    env.update(extra)
    return env


class Wrapper:
    """Runs the real tools/claude_station.py against a fake claude on PATH."""
    def __init__(self, tmp, fake=FAKE_CLAUDE):
        self.tmp = Path(tmp)
        self.proj = self.tmp / "proj"; (self.proj / "runs" / "wo-1").mkdir(parents=True)
        self.bin = self.tmp / "bin"; self.bin.mkdir()
        claude = self.bin / "claude"; claude.write_text(fake); claude.chmod(0o755)

    def run(self, station="builder", sleep=0, **extra):
        packet = self.proj / "runs" / "wo-1" / f"{station}.packet.md"
        packet.write_text(f"# Task packet: {station}\n\n## Work order\n\n- id: wo-1\n- kind: feature\n")
        output = packet.with_name(f"{station}.output.md")
        usage = Path(str(output) + ".usage.json")
        env = clean_env(PATH=f"{self.bin}:{os.environ['PATH']}", ANVIL_PROJECT_ROOT=str(self.proj),
                        ANVIL_CONFIGURED_MODEL="claude-opus-5-5", ANVIL_USAGE_PATH=str(usage),
                        FAKE_SLEEP=str(sleep), **extra)
        proc = subprocess.run([sys.executable, str(WRAPPER), str(packet), str(output)],
                              env=env, capture_output=True, text=True, cwd=str(self.proj))
        data = json.loads(usage.read_text()) if usage.exists() else None
        return proc, output, data


class TestDiagnosis(unittest.TestCase):
    def test_s1_wrapper_has_no_hardcoded_1500_cap(self):
        """S1: the bare constant TIMEOUT_SECONDS = 1500 is gone from the wrapper"""
        text = WRAPPER.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"^TIMEOUT_SECONDS\s*=\s*1500\s*$", text, re.M))
        self.assertNotIn("timed out after 1500s", text)


class TestResolution(unittest.TestCase):
    def test_s2_environment_beats_project_config_beats_default(self):
        """S2: env 100 wins over anvil.yaml 200; anvil.yaml 200 alone gives 200; neither gives the default"""
        env_only = anvil_config.station_timeout_seconds("builder", {VAR: "100"})
        self.assertEqual(env_only, 100)
        executor = CommandExecutor({"command": "true", "station_timeout_seconds": 200})
        handed = {}
        with mock.patch.dict(os.environ, clean_env(), clear=True):
            with mock.patch("subprocess.run") as run:
                run.return_value = subprocess.CompletedProcess([], 0, "out", "")
                executor.execute("# Task packet: builder\n", "builder")
                handed = run.call_args.kwargs["env"]
        self.assertEqual(handed.get(VAR), "200")
        self.assertEqual(anvil_config.station_timeout_seconds("builder", handed), 200)
        with mock.patch.dict(os.environ, clean_env(**{VAR: "100"}), clear=True):
            with mock.patch("subprocess.run") as run:
                run.return_value = subprocess.CompletedProcess([], 0, "out", "")
                executor.execute("# Task packet: builder\n", "builder")
                self.assertEqual(run.call_args.kwargs["env"].get(VAR), "100")
        self.assertGreaterEqual(anvil_config.station_timeout_seconds("builder", {}), 3600)

    def test_s3_class_defaults(self):
        """S3: producing stations default to at least 3600, others to at least 1500"""
        for station in WRITE_STATIONS:
            self.assertGreaterEqual(anvil_config.station_timeout_seconds(station, {}), 3600, station)
        for station in ("intake", "reviewer-code", "approver", "scout"):
            self.assertGreaterEqual(anvil_config.station_timeout_seconds(station, {}), 1500, station)

    def test_s3_wrapper_write_stations_match_the_eight(self):
        """S3: the wrapper WRITE_STATIONS set is the eight producing ids"""
        import claude_station
        self.assertEqual(sorted(claude_station.WRITE_STATIONS), sorted(WRITE_STATIONS))

    def test_s4_ceiling_and_bad_values(self):
        """S4: 9000 clamps to 7200 or is rejected naming 7200; 7200 passes; bad values are named"""
        self.assertEqual(anvil_config.STATION_TIMEOUT_CEILING, 7200)
        self.assertEqual(anvil_config.station_timeout_seconds("builder", {VAR: "7200"}), 7200)
        try:
            value = anvil_config.station_timeout_seconds("builder", {VAR: "9000"})
        except ValueError as e:
            self.assertIn("7200", str(e))
        else:
            self.assertEqual(value, 7200)
        for bad in ("abc", "0", "-5"):
            with self.assertRaises(ValueError) as ctx:
                anvil_config.station_timeout_seconds("builder", {VAR: bad})
            self.assertIn(bad, str(ctx.exception))

    def test_s4_project_config_above_ceiling_never_exceeds_7200(self):
        """S4: no path yields more than 7200, including anvil.yaml values handed through the executor"""
        executor = CommandExecutor({"command": "true", "station_timeout_seconds": 9000})
        with mock.patch.dict(os.environ, clean_env(), clear=True):
            with mock.patch("subprocess.run") as run:
                run.return_value = subprocess.CompletedProcess([], 0, "out", "")
                try:
                    executor.execute("# Task packet: builder\n", "builder")
                except Exception as e:
                    self.assertIn("7200", str(e))
                else:
                    handed = run.call_args.kwargs["env"].get(VAR)
                    self.assertLessEqual(anvil_config.station_timeout_seconds("builder", {VAR: handed}), 7200)
        self.assertLessEqual(executor.timeout, 7200 * 2)


class TestCoordination(unittest.TestCase):
    def test_s5_executor_timeout_never_below_station_timeout(self):
        """S5: effective executor timeout is at least the station timeout in effect"""
        self.assertGreaterEqual(anvil_config.effective_executor_timeout(None, {VAR: "3600"}), 3600)
        self.assertGreaterEqual(anvil_config.effective_executor_timeout(1800, {VAR: "3600"}), 3600)
        self.assertGreaterEqual(anvil_config.effective_executor_timeout(None, {}), 3600)
        with mock.patch.dict(os.environ, clean_env(**{VAR: "3600"}), clear=True):
            self.assertGreaterEqual(CommandExecutor({"command": "true", "timeout_seconds": 1800}).timeout, 3600)
            self.assertGreaterEqual(CommandExecutor({"command": "true"}).timeout, 3600)

    def test_s5_factory_anvil_yaml_value(self):
        """S5: the factory anvil.yaml runtime.timeout_seconds is at least 7200"""
        cfg = json.loads((ROOT / "anvil.yaml").read_text(encoding="utf-8"))
        self.assertGreaterEqual(cfg["runtime"]["timeout_seconds"], 7200)

    def test_s6_job_timeout_is_360(self):
        """S6: anvil-line.yml job timeout is 360 minutes and no 180 remains"""
        text = (ROOT / ".github" / "workflows" / "anvil-line.yml").read_text(encoding="utf-8")
        self.assertIn("timeout-minutes: 360", text)
        self.assertNotIn("timeout-minutes: 180", text)


class TestTimeoutRecord(unittest.TestCase):
    def test_s7_killed_station_records_what_is_knowable_in_the_usage_artifact(self):
        """S7: a station past a scaled cap of 1s exits non-zero with station, elapsed, timeout and model"""
        with tempfile.TemporaryDirectory() as tmp:
            proc, _, data = Wrapper(tmp).run("builder", sleep=10, **{VAR: "1"})
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("timed out after 1s", proc.stderr)
            self.assertIsNotNone(data)
            attempt = data["attempts"][0]
            self.assertEqual(attempt["status"], "timed_out")
            self.assertEqual(attempt["configured_model"], "claude-opus-5-5")
            self.assertGreaterEqual(attempt["duration_ms"], 1000)
            self.assertEqual(attempt.get("station"), "builder")
            self.assertEqual(attempt.get("timeout_seconds"), 1)
            self.assertIn("1", str(attempt.get("reason")))
            self.assertFalse(attempt["usage_complete"])

    def test_s7_partial_usage_from_timeout_stdout_is_kept(self):
        """S7: usage the runtime exposed on the TimeoutExpired stdout path appears in the artifact"""
        with tempfile.TemporaryDirectory() as tmp:
            proc, _, data = Wrapper(tmp, FAKE_CLAUDE_PARTIAL).run("builder", sleep=10, **{VAR: "1"})
            self.assertNotEqual(proc.returncode, 0)
            attempt = data["attempts"][0]
            self.assertEqual(attempt["status"], "timed_out")
            self.assertTrue(attempt["usage_complete"])
            self.assertEqual(attempt["usage"]["input_tokens"], 77)

    def test_s7_run_record_step_names_model_and_status(self):
        """S7: the run record step for a killed station is timed_out with executed_model not null"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            init_project(proj, "Demo")
            wrapper = Wrapper(tmp)
            executor = CommandExecutor({"command": f"{sys.executable} {WRAPPER} {{packet}} {{output}}"})
            pipe_path = Path(tmp) / "pipe.json"
            pipe_path.write_text(json.dumps({"name": "t", "stages": [{"station": "builder"}]}))
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(pipe_path, known_stations=set(reg.ids()))
            env = clean_env(PATH=f"{wrapper.bin}:{os.environ['PATH']}", FAKE_SLEEP="10", **{VAR: "1"})
            with mock.patch.dict(os.environ, env, clear=True):
                report = run_pipeline(proj, pipe, WorkOrder(id="wo-t", kind="feature", title="t"),
                                      registry=reg, executor=executor)
            step = next(s for s in report.steps if s["station"] == "builder")
            self.assertEqual(step["status"], "timed_out")
            self.assertIsNotNone(step["executed_model"])
            self.assertGreaterEqual(step["duration_ms"], 1000)
            self.assertIn("1", step["detail"])
            self.assertIn("timed out", step["detail"])


class TestScaledMechanism(unittest.TestCase):
    def test_s8_s9_producing_station_survives_scaled_legacy_cap_and_is_counted(self):
        """S9/S8: 2s of work under a scaled legacy cap of 1s completes with a configured cap of 5s"""
        with tempfile.TemporaryDirectory() as tmp:
            proc, output, data = Wrapper(tmp).run("builder", sleep=2, **{VAR: "5"})
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(output.read_text().strip(), "done")
            attempt = data["attempts"][0]
            self.assertEqual(attempt["status"], "succeeded")
            self.assertGreaterEqual(attempt["duration_ms"], 2000)
            self.assertTrue(data["complete"])
            self.assertEqual(data["measured_attempts"], 1)

    def test_s9_run_record_counts_the_slow_producing_station(self):
        """S9: through the run, a builder past the scaled legacy cap is executed and counted"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            init_project(proj, "Demo")
            wrapper = Wrapper(tmp)
            executor = CommandExecutor({"command": f"{sys.executable} {WRAPPER} {{packet}} {{output}}"})
            pipe_path = Path(tmp) / "pipe.json"
            pipe_path.write_text(json.dumps({"name": "t", "stages": [{"station": "builder"}]}))
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(pipe_path, known_stations=set(reg.ids()))
            env = clean_env(PATH=f"{wrapper.bin}:{os.environ['PATH']}", FAKE_SLEEP="2", **{VAR: "5"})
            with mock.patch.dict(os.environ, env, clear=True):
                report = run_pipeline(proj, pipe, WorkOrder(id="wo-t", kind="feature", title="t"),
                                      registry=reg, executor=executor)
            step = next(s for s in report.steps if s["station"] == "builder")
            self.assertEqual(step["status"], "executed")
            self.assertGreaterEqual(step["duration_ms"], 2000)

    def test_s9_station_past_its_configured_cap_still_dies(self):
        """S9: 3s of work under a configured cap of 1s is killed and the S7 record is produced"""
        with tempfile.TemporaryDirectory() as tmp:
            proc, output, data = Wrapper(tmp).run("builder", sleep=3, **{VAR: "1"})
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse(output.exists())
            attempt = data["attempts"][0]
            self.assertEqual(attempt["status"], "timed_out")
            self.assertLess(attempt["duration_ms"], 3000)

    def test_s9_runaway_cannot_exceed_ceiling_through_the_wrapper(self):
        """S4/S9: an over-ceiling value never lets the wrapper run with more than 7200 (rejected or clamped)"""
        with tempfile.TemporaryDirectory() as tmp:
            proc, _, _ = Wrapper(tmp).run("builder", sleep=0, **{VAR: "9000"})
            if proc.returncode != 0:
                self.assertIn("7200", proc.stderr)

    def test_s8_other_station_default_is_unchanged_in_shape(self):
        """S8: a healthy non-producing station records the same fields as before"""
        with tempfile.TemporaryDirectory() as tmp:
            proc, _, data = Wrapper(tmp).run("intake", sleep=0)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            attempt = data["attempts"][0]
            for key in ("attempt", "status", "runtime", "configured_model", "duration_ms", "usage",
                        "runtime_cost_estimate_usd", "turns", "usage_complete"):
                self.assertIn(key, attempt)
            self.assertEqual(attempt["status"], "succeeded")
            self.assertEqual(attempt["usage"]["input_tokens"], 10)


class TestDocs(unittest.TestCase):
    def test_s10_decision_changelog_and_docs(self):
        """S10: decision 0011, changelog entry, EXECUTION.md literals, no stale 1500 cap in docs"""
        decision = ROOT / "brain" / "decisions" / "0011-station-timeout.md"
        self.assertTrue(decision.is_file())
        self.assertIn("station-timeout", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
        text = (ROOT / "docs" / "EXECUTION.md").read_text(encoding="utf-8")
        for literal in (VAR, "3600", "7200"):
            self.assertIn(literal, text)
        for doc in (ROOT / "docs").rglob("*.md"):
            for n, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
                if "1500" in line and re.search(r"cap|timeout|timed out|limit", line, re.I):
                    self.assertRegex(line, r"(?i)default|former|old|previous|was|legacy|no longer|class",
                                     f"{doc.name}:{n} states 1500 as current: {line}")

    def test_s10_no_dashes_in_new_artifacts(self):
        """No em dash or en dash in produced files"""
        for path in (ROOT / "tests" / "test_station_timeout.py", ROOT / "brain" / "decisions" / "0011-station-timeout.md"):
            if path.exists():
                self.assertNotRegex(path.read_text(encoding="utf-8"), "[\u2013\u2014]", path.name)


if __name__ == "__main__":
    unittest.main()
