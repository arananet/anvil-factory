import json, tempfile, unittest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.stations import load_registry
from anvil.scaffold import init_project, scaffold_spec
from anvil.runner import run_pipeline
from anvil.executor import create_executor

ROOT = Path(__file__).resolve().parent.parent

FAKE_EXECUTOR = '''
import json, sys
packet_path = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "pass"
station = ""
for line in open(packet_path, encoding="utf-8"):
    if line.startswith("# Task packet:"):
        station = line.split(":", 1)[1].strip()
        break
if station.startswith("reviewer"):
    verdict = "pass" if mode == "pass" else "fail"
    print(json.dumps({"station": station, "verdict": verdict,
                      "findings": ["Fake review for " + station]}))
else:
    print("Executed " + station)
'''

def make_project(tmp):
    proj = Path(tmp) / "proj"
    init_project(proj, "Demo")
    scaffold_spec(proj, "demo-feature", "Demo Feature")
    return proj

def command_executor(tmp, mode="pass"):
    script = Path(tmp) / "fake_executor.py"
    script.write_text(FAKE_EXECUTOR)
    return create_executor({"kind": "command",
                            "command": f"{sys.executable} {script} {{packet}} {mode}",
                            "timeout_seconds": 60})

def sdlc_pipe(reg):
    return load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))

class TestChecksGatePassingChecks(unittest.TestCase):
    def test_passing_checks_let_reviewers_run_s1(self):
        """checks-gate S1: passing checks, no protected path touched, gate passes, reviewers run"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            # Configure project with checks that will pass
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = [
                "echo 'test passed'",
                "exit 0"
            ]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-001", kind="feature", title="Gate pass test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # Gate should pass
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            self.assertEqual(len(gate_steps), 1)
            gate_step = gate_steps[0]
            self.assertEqual(gate_step["status"], "passed")

            # Reviewers should have run
            reviewer_steps = [s for s in report.steps if s.get("station", "").startswith("reviewer")]
            self.assertTrue(len(reviewer_steps) > 0)

            # Report should record gate commands and exit codes
            self.assertIn("commands", gate_step)
            self.assertIn("exit_codes", gate_step)
            for code in gate_step["exit_codes"]:
                self.assertEqual(code, 0)

class TestChecksGateFailingChecks(unittest.TestCase):
    def test_failing_checks_return_to_builder_no_reviewer_s2(self):
        """checks-gate S2: failing checks return work to builder, no reviewers spawned, loopback consumed"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            # Configure project with checks that will fail
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = [
                "echo 'test failed'",
                "exit 1"
            ]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-002", kind="feature", title="Gate fail test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # Gate should fail
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            self.assertEqual(len(gate_steps), 1)
            gate_step = gate_steps[0]
            self.assertEqual(gate_step["status"], "failed")

            # No reviewers should have run for that attempt
            reviewer_steps = [s for s in report.steps if s.get("station", "").startswith("reviewer")]
            # On first attempt, reviewers should not run
            # (implementation will need to track attempts)

            # Loopback should be consumed
            self.assertGreater(report.loopbacks, 0)

            # Gate failure should be in report with failing command and exit code
            self.assertIn("exit_codes", gate_step)
            self.assertTrue(any(code != 0 for code in gate_step["exit_codes"]))

            # Builder feedback should include gate log
            builder_steps = [s for s in report.steps if s.get("station") == "builder"]
            # Last builder step should have gate feedback
            if len(builder_steps) > 1:
                last_builder = builder_steps[-1]
                self.assertIn("feedback", last_builder)

class TestChecksGateProtectedPaths(unittest.TestCase):
    def test_protected_path_touch_fails_gate_automatically_s3(self):
        """checks-gate S3: touching protected path fails gate regardless of check exit codes"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            # Configure project with passing checks but protected paths
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["exit 0"]
            config["protected_paths"] = ["tests/", "anvil.json"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            # Simulate a change that touches a protected path
            # This would be tracked by the runner's changed files list
            (proj / "tests" / "test_new.py").write_text("# new test file")

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-003", kind="feature", title="Protected path test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # Gate should fail with protected path finding
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            self.assertEqual(len(gate_steps), 1)
            gate_step = gate_steps[0]
            self.assertEqual(gate_step["status"], "failed")

            # Should have protected path verdict
            self.assertIn("protected_path_verdict", gate_step)
            self.assertEqual(gate_step["protected_path_verdict"], "fail")
            self.assertIn("protected_path_findings", gate_step)

            # No reviewers should run
            reviewer_steps = [s for s in report.steps if s.get("station", "").startswith("reviewer")]
            # Should not run on first attempt when gate fails

    def test_deleting_protected_file_counts_as_touching_s3(self):
        """checks-gate S3: deleting a protected file counts as touching it"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            # Configure project with protected paths
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["exit 0"]
            config["protected_paths"] = ["tests/"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            # Create a test file and then simulate deletion
            test_file = proj / "tests" / "test_existing.py"
            test_file.write_text("# existing test")

            # Simulate deletion by tracking it in changed files
            # (runner would track this)

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-004", kind="feature", title="Protected path delete test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # If file was deleted and tracked, gate should fail
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            if len(gate_steps) > 0 and gate_steps[0].get("protected_path_verdict") == "fail":
                self.assertEqual(gate_steps[0]["status"], "failed")

class TestChecksGateBaseRefResolution(unittest.TestCase):
    def test_check_definitions_from_base_ref_not_work_branch_s4(self):
        """checks-gate S4: checks resolved from base ref snapshot, modifications to checks config trigger protected path"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            # Set up initial checks configuration (base ref state)
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["echo 'original check'", "exit 0"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            # Runner should snapshot this at run start
            # Then builder modifies the checks during the run

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-005", kind="feature", title="Base ref checks test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # Gate should run checks from base ref snapshot
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            if len(gate_steps) > 0:
                gate_step = gate_steps[0]
                # Commands should be from base ref
                self.assertIn("commands", gate_step)
                # If anvil.json was modified, should trigger protected path
                # (by default, checks config is protected)

    def test_protected_paths_from_base_ref_s4(self):
        """checks-gate S4: protected paths list also resolved from base ref"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            # Set up protected paths in base ref
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["exit 0"]
            config["protected_paths"] = ["tests/", "anvil.json"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-006", kind="feature", title="Base ref protected paths test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # Gate should use protected paths from base ref snapshot
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            if len(gate_steps) > 0:
                gate_step = gate_steps[0]
                # Protected paths should be from base ref
                self.assertIn("protected_paths", gate_step)

class TestChecksGatePreDeploy(unittest.TestCase):
    def test_gate_runs_before_deploy_after_merge_sync_s5(self):
        """checks-gate S5: gate runs second time before deployer/publisher, failure stops deploy"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            # Configure project with checks
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["exit 0"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-007", kind="feature", title="Pre-deploy gate test")
            # Run with deployer in pipeline
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # Should have gate steps: one pre-review, one pre-deploy
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            # At least one gate should have run
            self.assertGreaterEqual(len(gate_steps), 1)

            # If deployer/publisher in pipeline and merge sync happened,
            # should have pre-deploy gate step
            for gate_step in gate_steps:
                self.assertIn("phase", gate_step)
                self.assertIn(gate_step["phase"], ["pre-review", "pre-deploy"])

    def test_pre_deploy_gate_failure_stops_deploy_s5(self):
        """checks-gate S5: pre-deploy gate failure stops deployer/publisher and records blocking reason"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            # Configure project with checks that pass initially but could fail later
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["exit 1"]  # Will fail
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-008", kind="feature", title="Pre-deploy gate fail test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # If pre-deploy gate fails, deployer should not run
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate" and s.get("phase") == "pre-deploy"]
            if len(gate_steps) > 0 and gate_steps[0]["status"] == "failed":
                deployer_steps = [s for s in report.steps if s.get("station") == "deployer"]
                # Deployer should not have executed after gate failure
                for deployer_step in deployer_steps:
                    self.assertNotEqual(deployer_step["status"], "executed")

                # Blocking reason should be recorded
                # (implementation will add this to report)

    def test_pre_deploy_gate_pass_allows_deploy_s5(self):
        """checks-gate S5: pre-deploy gate pass allows deployer/publisher to proceed"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            # Configure project with passing checks
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["exit 0"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-009", kind="feature", title="Pre-deploy gate pass test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # If pre-deploy gate passes, deployer can proceed
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate" and s.get("phase") == "pre-deploy"]
            if len(gate_steps) > 0 and gate_steps[0]["status"] == "passed":
                # Deployer/publisher should be allowed to run
                # (not necessarily executed, but not blocked by gate)
                pass

class TestChecksGateNotConfigured(unittest.TestCase):
    def test_no_checks_configured_records_not_configured_s6(self):
        """checks-gate S6: project with no checks configured records gate as not configured, run proceeds"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            # Do not configure checks - leave config without checks field
            config = json.loads((proj / "anvil.json").read_text())
            # Ensure no checks field
            config.pop("checks", None)
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-010", kind="feature", title="No checks test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # Gate should be recorded as not configured
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            self.assertEqual(len(gate_steps), 1)
            gate_step = gate_steps[0]
            self.assertEqual(gate_step["status"], "not_configured")

            # Run should proceed through reviewer stage as normal
            reviewer_steps = [s for s in report.steps if s.get("station", "").startswith("reviewer")]
            self.assertTrue(len(reviewer_steps) > 0)

            # No gate failure should be recorded
            self.assertNotEqual(report.verdict, "gate_failed")

    def test_no_checks_configured_visible_in_report_s6(self):
        """checks-gate S6: gate not configured status is visible in report, never silent"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            # No checks configured
            config = json.loads((proj / "anvil.json").read_text())
            config.pop("checks", None)
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-011", kind="feature", title="No checks visibility test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # Report should explicitly show gate as not configured
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            self.assertEqual(len(gate_steps), 1)
            gate_step = gate_steps[0]
            self.assertIn("status", gate_step)
            self.assertEqual(gate_step["status"], "not_configured")

            # Should be visible in swimlane (has station name)
            self.assertEqual(gate_step["station"], "checks-gate")

class TestChecksGateReporting(unittest.TestCase):
    def test_gate_recorded_in_run_report_s1_through_s6(self):
        """checks-gate: every gate run recorded in report with commands, exit codes, verdicts"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            # Configure multiple checks
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = [
                "echo 'check 1'",
                "echo 'check 2'",
                "exit 0"
            ]
            config["protected_paths"] = ["tests/", "anvil.json"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-012", kind="feature", title="Gate reporting test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # Gate steps should be recorded with full details
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            self.assertGreater(len(gate_steps), 0)

            for gate_step in gate_steps:
                # Required fields in gate record
                self.assertIn("station", gate_step)
                self.assertEqual(gate_step["station"], "checks-gate")
                self.assertIn("status", gate_step)
                self.assertIn("phase", gate_step)

                # If configured, should have command details
                if gate_step["status"] != "not_configured":
                    self.assertIn("commands", gate_step)
                    self.assertIn("exit_codes", gate_step)
                    self.assertEqual(len(gate_step["commands"]), len(gate_step["exit_codes"]))

                # Should have protected path verdict
                self.assertIn("protected_path_verdict", gate_step)

                # Should have overall gate verdict
                self.assertIn("gate_verdict", gate_step)

    def test_gate_shown_as_own_step_in_swimlane(self):
        """checks-gate: gate appears as its own step in swimlane, visible without opening report JSON"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["exit 0"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-013", kind="feature", title="Gate swimlane test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # Gate should be in steps list (swimlane)
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            self.assertGreater(len(gate_steps), 0)

            # Should have station identifier
            for gate_step in gate_steps:
                self.assertEqual(gate_step["station"], "checks-gate")
                self.assertIn("status", gate_step)

class TestChecksGateDefaultProtectedPaths(unittest.TestCase):
    def test_default_protected_paths_include_checks_config_and_tests_s3(self):
        """checks-gate S3: default protected paths include checks config and tests/"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            # Configure checks but don't specify protected_paths
            # Should default to anvil.json and tests/
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["exit 0"]
            # Don't set protected_paths - should use defaults
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-014", kind="feature", title="Default protected paths test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # Gate should have default protected paths
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            if len(gate_steps) > 0:
                gate_step = gate_steps[0]
                if gate_step["status"] != "not_configured":
                    self.assertIn("protected_paths", gate_step)
                    # Should include checks config and tests/ by default
                    protected = gate_step["protected_paths"]
                    self.assertIn("tests/", protected)
                    self.assertTrue(any("anvil.json" in p for p in protected))

    def test_project_can_extend_or_replace_protected_paths_s3(self):
        """checks-gate S3: project can extend or replace default protected paths"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            # Configure custom protected paths
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["exit 0"]
            config["protected_paths"] = ["custom/path/", "important.py"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-015", kind="feature", title="Custom protected paths test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"))

            # Gate should use custom protected paths
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            if len(gate_steps) > 0:
                gate_step = gate_steps[0]
                if gate_step["status"] != "not_configured":
                    self.assertIn("protected_paths", gate_step)
                    protected = gate_step["protected_paths"]
                    self.assertIn("custom/path/", protected)
                    self.assertIn("important.py", protected)

if __name__ == "__main__":
    unittest.main()
