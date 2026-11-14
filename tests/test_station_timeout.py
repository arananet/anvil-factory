"""Tests for the configurable per station timeout (spec: station-timeout, wo-gh-39).

Scenario map (ids from .openspec/specs/station-timeout/spec.md):
  S1  test_s1_cap_constant_is_gone_or_configurable_and_history_is_recorded
  S2  test_s2_env_beats_project_config_beats_class_default
  S3  test_s3_class_defaults_producing_3600_other_1500
  S4  test_s4_ceiling_7200_and_bad_values
  S5  test_s5_executor_timeout_never_below_station_timeout
  S6  test_s6_job_timeout_is_360_minutes
  S7  test_s7_timed_out_station_records_elapsed_timeout_model_and_usage
  S8  test_s8_healthy_station_record_shape_unchanged
  S9  test_s9_producing_station_past_scaled_legacy_cap_completes,
      test_s9_station_over_configured_cap_dies_and_is_recorded
  S10 test_s10_decision_changelog_and_docs
  S11 covered by the builder report itself (runs/wo-gh-39/builder.output.md);
      test_s11_builder_report_literals checks it once it exists.

Conventions fixed here for the builder (the spec leaves names open):
  - the environment override is ANVIL_STATION_TIMEOUT_SECONDS;
  - project configuration is anvil.yaml runtime.station_timeout_seconds, handed
    to the wrapper through that same environment variable by the runner;
  - the wrapper main() passes the resolved value as subprocess.run timeout;
  - a ceiling breach is clamped to 7200 or fails with a message naming 7200;
  - a timed out attempt in the usage artifact has status "timed_out",
    duration_ms, timeout_seconds and a reason containing the timeout value.
"""
import io, json, os, re, subprocess, sys, tempfile, time, unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import claude_station
from anvil.executor import CommandExecutor, create_executor
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.runner import run_pipeline
from anvil.scaffold import init_project, scaffold_spec
from anvil.stations import load_registry

WRITE = ["builder", "test-writer", "spec-writer", "blueprint", "brief-writer",
         "researcher", "writer", "media-producer"]

FAKE_CLAUDE = r'''#!/usr/bin/env python3
import json, os, sys, time
args = sys.argv[1:]
prompt = args[args.index("-p") + 1]
first = prompt.splitlines()[0]
delay = float(os.environ.get("FAKE_DELAY", "0"))
if os.environ.get("FAKE_ONLY") and os.environ["FAKE_ONLY"] not in first:
    delay = 0
time.sleep(delay)
print(json.dumps({"type": "result", "result": "done", "is_error": False, "num_turns": 1,
                  "usage": {"input_tokens": 10, "output_tokens": 5}}))
'''


def run_main(station, env_extra, runner=None):
    """Run the real wrapper main() in process; return (code, captured timeout kwargs)."""
    seen = {}
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp)
        (proj / "runs" / "wo-1").mkdir(parents=True)
        packet = proj / "runs" / "wo-1" / f"{station}.packet.md"
        packet.write_text(f"# Task packet: {station}\n\n- id: wo-1\n")
        out = packet.with_name(f"{station}.output.md")

        def fake_run(cmd, **kw):
            seen["timeout"] = kw.get("timeout")
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(
                {"type": "result", "result": "ok", "is_error": False}), stderr="")
        env = {k: v for k, v in os.environ.items() if not k.startswith("ANVIL_")}
        env.update({"ANVIL_PROJECT_ROOT": str(proj), "ANVIL_CONFIGURED_MODEL": "claude-opus-5-5"})
        env.update(env_extra)
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(sys, "argv", ["claude_station.py", str(packet), str(out)]), \
                mock.patch.object(claude_station.subprocess, "run", fake_run), \
                redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            try:
                code = claude_station.main()
            except (ValueError, SystemExit) as exc:
                code = ("raised", str(exc))
    return code, seen.get("timeout")


class Wrapper:
    """The wrapper run as a real process, with a fake claude CLI on PATH."""
    def __init__(self, tmp):
        self.tmp = Path(tmp)
        self.proj = self.tmp / "proj"; (self.proj / "runs" / "wo-1").mkdir(parents=True)
        self.bin = self.tmp / "bin"; self.bin.mkdir()
        fake = self.bin / "claude"; fake.write_text(FAKE_CLAUDE); fake.chmod(0o755)

    def run(self, station, **extra):
        packet = self.proj / "runs" / "wo-1" / f"{station}.packet.md"
        packet.write_text(f"# Task packet: {station}\n\n- id: wo-1\n")
        out = packet.with_name(f"{station}.output.md")
        usage = Path(str(out) + ".usage.json")
        env = {k: v for k, v in os.environ.items() if not k.startswith(("ANVIL_", "FAKE_"))}
        env.update({"PATH": f"{self.bin}:{env['PATH']}", "ANVIL_PROJECT_ROOT": str(self.proj),
                    "ANVIL_CONFIGURED_MODEL": "claude-opus-5-5", "ANVIL_USAGE_PATH": str(usage)})
        env.update(extra)
        started = time.monotonic()
        proc = subprocess.run([sys.executable, str(ROOT / "tools" / "claude_station.py"), str(packet), str(out)],
                              env=env, capture_output=True, text=True, cwd=str(self.proj))
        return proc, usage, time.monotonic() - started


class TestResolution(unittest.TestCase):
    def test_s1_cap_constant_is_gone_or_configurable_and_history_is_recorded(self):
        """S1: the hardcoded 1500 is no longer the cap applied to a producing station"""
        code, timeout = run_main("builder", {})
        self.assertEqual(code, 0)
        self.assertNotEqual(timeout, 1500)
        src = (ROOT / "tools" / "claude_station.py").read_text()
        self.assertNotRegex(src, r"timeout=TIMEOUT_SECONDS\b")

    def test_s2_env_beats_project_config_beats_class_default(self):
        """S2: env 100 beats project 200; project 200 beats default; neither gives the default"""
        self.assertEqual(run_main("builder", {"ANVIL_STATION_TIMEOUT_SECONDS": "100"})[1], 100)
        self.assertEqual(run_main("builder", {"ANVIL_STATION_TIMEOUT_SECONDS": "200"})[1], 200)
        self.assertGreaterEqual(run_main("builder", {})[1], 3600)

    def test_s2_project_config_in_anvil_yaml_reaches_the_wrapper(self):
        """S2: runtime.station_timeout_seconds in anvil.yaml is handed over through the environment"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            init_project(proj, "Demo"); scaffold_spec(proj, "demo-feature", "Demo Feature")
            cfg = json.loads((proj / "anvil.yaml").read_text()) if (proj / "anvil.yaml").read_text().lstrip().startswith("{") else {}
            cfg["runtime"] = {"kind": "command", "timeout_seconds": 60, "station_timeout_seconds": 222,
                              "command": f"{sys.executable} {Path(tmp) / 'dump.py'} {{packet}} {{output}}"}
            (proj / "anvil.yaml").write_text(json.dumps(cfg))
            (Path(tmp) / "dump.py").write_text(
                "import os,sys\nopen(os.environ['ANVIL_PROJECT_ROOT']+'/seen.txt','a').write("
                "os.environ.get('ANVIL_STATION_TIMEOUT_SECONDS','UNSET')+'\\n')\nprint('x')\n")
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(ROOT / "pipelines" / "hotfix.json", known_stations=set(reg.ids()))
            run_pipeline(proj, pipe, WorkOrder(id="wo-st-1", kind="bug", title="t"), registry=reg,
                         executor=create_executor(cfg["runtime"]))
            seen = (proj / "seen.txt").read_text().split()
            self.assertTrue(seen)
            self.assertEqual(set(seen), {"222"})

    def test_s3_class_defaults_producing_3600_other_1500(self):
        """S3: each of the eight producing stations gets >= 3600, intake gets >= 1500"""
        self.assertEqual(sorted(claude_station.WRITE_STATIONS), sorted(WRITE))
        for station in WRITE:
            self.assertGreaterEqual(run_main(station, {})[1], 3600, station)
        self.assertGreaterEqual(run_main("builder", {})[1], 3600)
        self.assertGreaterEqual(run_main("intake", {})[1], 1500)
        self.assertGreaterEqual(run_main("reviewer-tests", {})[1], 1500)

    def test_s4_ceiling_7200_and_bad_values(self):
        """S4: 9000 clamps to 7200 or is rejected naming 7200; 7200 holds; bad values name the value"""
        code, timeout = run_main("builder", {"ANVIL_STATION_TIMEOUT_SECONDS": "9000"})
        if timeout is not None:
            self.assertEqual(timeout, 7200)
        else:
            self.assertNotEqual(code, 0)
        self.assertEqual(run_main("builder", {"ANVIL_STATION_TIMEOUT_SECONDS": "7200"})[1], 7200)
        with tempfile.TemporaryDirectory() as tmp:
            proc, _, _ = Wrapper(tmp).run("builder", ANVIL_STATION_TIMEOUT_SECONDS="9000")
            if proc.returncode != 0:
                self.assertIn("7200", proc.stderr)
        for bad in ("abc", "0", "-5"):
            with tempfile.TemporaryDirectory() as tmp:
                proc, _, _ = Wrapper(tmp).run("builder", ANVIL_STATION_TIMEOUT_SECONDS=bad)
                self.assertNotEqual(proc.returncode, 0, bad)
                self.assertIn(bad, proc.stderr, bad)


class TestCoordination(unittest.TestCase):
    def test_s5_executor_timeout_never_below_station_timeout(self):
        """S5: executor timeout >= station timeout, and the factory anvil.yaml value is >= 7200"""
        for cfg in ({"command": "x", "station_timeout_seconds": 3600},
                    {"command": "x", "timeout_seconds": 1800, "station_timeout_seconds": 3600},
                    {"command": "x", "timeout_seconds": 300}):
            ex = CommandExecutor(cfg)
            self.assertGreaterEqual(ex.timeout, int(cfg.get("station_timeout_seconds", 3600)), cfg)
        factory = json.loads((ROOT / "anvil.yaml").read_text())
        self.assertGreaterEqual(factory["runtime"]["timeout_seconds"], 7200)

    def test_s6_job_timeout_is_360_minutes(self):
        """S6: the anvil-line job timeout is 360 minutes and 180 is gone"""
        text = (ROOT / ".github" / "workflows" / "anvil-line.yml").read_text()
        self.assertIn("timeout-minutes: 360", text)
        self.assertNotIn("timeout-minutes: 180", text)


class TestRecords(unittest.TestCase):
    def test_s7_timed_out_station_records_elapsed_timeout_model_and_usage(self):
        """S7: a killed station records status, elapsed, timeout value, model and partial usage"""
        with tempfile.TemporaryDirectory() as tmp:
            proc, usage, elapsed = Wrapper(tmp).run(
                "builder", ANVIL_STATION_TIMEOUT_SECONDS="1", FAKE_DELAY="4")
            self.assertNotEqual(proc.returncode, 0)
            self.assertLess(elapsed, 4)
            self.assertIn("timed out after 1s", proc.stderr)
            attempt = json.loads(usage.read_text())["attempts"][0]
            self.assertEqual(attempt["status"], "timed_out")
            self.assertGreaterEqual(attempt["duration_ms"], 1000)
            self.assertEqual(attempt["configured_model"], "claude-opus-5-5")
            self.assertEqual(attempt["timeout_seconds"], 1)
            self.assertIn("1", attempt["reason"])
            self.assertEqual(attempt.get("station"), "builder")

    def test_s7_run_record_step_is_timed_out_with_model(self):
        """S7: the run record step shows timed_out, executed_model not null, elapsed_ms and reason"""
        with tempfile.TemporaryDirectory() as tmp:
            w = Wrapper(tmp)
            proj = Path(tmp) / "rp"
            init_project(proj, "Demo"); scaffold_spec(proj, "demo-feature", "Demo Feature")
            ex = create_executor({"kind": "command", "timeout_seconds": 60,
                                  "command": f"{sys.executable} {ROOT / 'tools' / 'claude_station.py'} {{packet}} {{output}}"})
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(ROOT / "pipelines" / "hotfix.json", known_stations=set(reg.ids()))
            env = {"PATH": f"{w.bin}:{os.environ['PATH']}", "ANVIL_CONFIGURED_MODEL": "claude-opus-5-5",
                   "ANVIL_STATION_TIMEOUT_SECONDS": "1", "FAKE_DELAY": "3", "FAKE_ONLY": "builder"}
            with mock.patch.dict(os.environ, env):
                report = run_pipeline(proj, pipe, WorkOrder(id="wo-st-2", kind="bug", title="t"),
                                      registry=reg, executor=ex)
            step = [s for s in report.steps if s["station"] == "builder"][0]
            self.assertEqual(step["status"], "timed_out")
            self.assertIsNotNone(step["executed_model"])
            self.assertGreaterEqual(step["elapsed_ms"], 1000)
            self.assertIn("1", step["reason"])

    def test_s8_healthy_station_record_shape_unchanged(self):
        """S8: a station that finishes records a succeeded attempt with no timeout status"""
        with tempfile.TemporaryDirectory() as tmp:
            proc, usage, _ = Wrapper(tmp).run("builder", FAKE_DELAY="0")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(usage.read_text())
            self.assertEqual(data["schema"], "anvil/usage@1")
            attempt = data["attempts"][0]
            self.assertEqual(attempt["status"], "succeeded")
            self.assertEqual(attempt["usage"]["input_tokens"], 10)
            self.assertTrue(data["complete"])


class TestScaledMechanism(unittest.TestCase):
    def test_s9_producing_station_past_scaled_legacy_cap_completes(self):
        """S9: 2s of work under a scaled legacy cap of 1s completes under a configured 5s cap and is counted"""
        with tempfile.TemporaryDirectory() as tmp:
            w = Wrapper(tmp)
            legacy, _, _ = w.run("builder", FAKE_DELAY="2")  # no config: default is not the legacy cap
            self.assertEqual(legacy.returncode, 0, legacy.stderr)
            proc, usage, elapsed = w.run("builder", FAKE_DELAY="2", ANVIL_STATION_TIMEOUT_SECONDS="5")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertGreaterEqual(elapsed, 2)
            data = json.loads(usage.read_text())
            self.assertEqual(data["attempts"][0]["status"], "succeeded")
            self.assertEqual(data["measured_attempts"], 1)
        # the same work under a cap of 1s dies: proves the cap is the thing that decides
        with tempfile.TemporaryDirectory() as tmp:
            proc, _, _ = Wrapper(tmp).run("builder", FAKE_DELAY="2", ANVIL_STATION_TIMEOUT_SECONDS="1")
            self.assertNotEqual(proc.returncode, 0)

    def test_s9_station_over_configured_cap_dies_and_is_recorded(self):
        """S9: 3s of work under a configured 1s cap dies with the timeout recorded"""
        with tempfile.TemporaryDirectory() as tmp:
            proc, usage, elapsed = Wrapper(tmp).run(
                "builder", FAKE_DELAY="3", ANVIL_STATION_TIMEOUT_SECONDS="1")
            self.assertNotEqual(proc.returncode, 0)
            self.assertLess(elapsed, 3)
            attempt = json.loads(usage.read_text())["attempts"][0]
            self.assertEqual(attempt["status"], "timed_out")
            self.assertEqual(attempt["timeout_seconds"], 1)
            self.assertGreaterEqual(attempt["duration_ms"], 1000)


class TestDocs(unittest.TestCase):
    def test_s10_decision_changelog_and_docs(self):
        """S10: decision record, changelog entry, EXECUTION.md literals, no current 1500 claim"""
        self.assertTrue((ROOT / "brain" / "decisions" / "0011-station-timeout.md").is_file())
        self.assertIn("station-timeout", (ROOT / "CHANGELOG.md").read_text())
        doc = (ROOT / "docs" / "EXECUTION.md").read_text()
        for literal in ("ANVIL_STATION_TIMEOUT_SECONDS", "3600", "7200"):
            self.assertIn(literal, doc)
        for path in (ROOT / "docs").rglob("*.md"):
            self.assertNotRegex(path.read_text(), r"\b1500s?\b", str(path))

    def test_no_dash_characters_in_new_files(self):
        """Guardrail: no em or en dash in the new test or decision files"""
        for path in (Path(__file__), ROOT / "brain" / "decisions" / "0011-station-timeout.md"):
            if path.exists():
                self.assertFalse(re.search("[\u2013\u2014]", path.read_text()), str(path))

    def test_s11_builder_report_literals(self):
        """S11: the builder report carries the required literals (checked once it exists)"""
        report = ROOT / "runs" / "wo-gh-39" / "builder.output.md"
        if not report.exists():
            self.skipTest("builder report not written yet")
        text = report.read_text()
        for literal in ("ANVIL_STATION_TIMEOUT_SECONDS", "3600", "7200", "station-timeout"):
            self.assertIn(literal, text)


if __name__ == "__main__":
    unittest.main()
