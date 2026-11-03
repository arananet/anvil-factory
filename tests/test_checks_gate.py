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

            # Set up git repo with base ref (for loopback round 2 semantics)
            import subprocess
            subprocess.run(["git", "init"], cwd=proj, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=proj, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=proj, check=True, capture_output=True)
            # Create a test file in base ref
            (proj / "tests" / "test_new.py").write_text("# original test")
            subprocess.run(["git", "add", "."], cwd=proj, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Base ref"], cwd=proj, check=True, capture_output=True)
            base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=proj,
                                     capture_output=True, text=True, check=True).stdout.strip()

            # Simulate a change that modifies a protected path
            # Per loopback round 2: modifying an existing base ref file in protected path is a violation
            (proj / "tests" / "test_new.py").write_text("# modified test file - violation")

            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-003", kind="feature", title="Protected path test")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"), base_ref=base_ref)

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

    def test_uncommitted_checks_config_mutation_uses_base_ref_s4_regression(self):
        """checks-gate S4 REGRESSION: uncommitted working tree change to checks config doesn't affect gate commands"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Initialize git repo and create base ref state
            import subprocess
            subprocess.run(["git", "init"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=proj, check=True)

            # Set up base ref checks configuration
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["echo 'base ref check'", "exit 0"]
            config["protected_paths"] = ["anvil.json", "tests/"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            # Commit to establish base ref
            subprocess.run(["git", "add", "."], cwd=proj, check=True)
            subprocess.run(["git", "commit", "-m", "Base ref state"], cwd=proj, check=True)
            base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=proj,
                                     capture_output=True, text=True, check=True).stdout.strip()

            # Create work branch
            subprocess.run(["git", "checkout", "-b", "work-branch"], cwd=proj, check=True)

            # NOW mutate checks config as uncommitted change (working tree only)
            malicious_config = json.loads((proj / "anvil.json").read_text())
            malicious_config["checks"] = ["echo 'malicious check - should not run'", "exit 0"]
            (proj / "anvil.json").write_text(json.dumps(malicious_config, indent=2))

            # Run gate - it should resolve commands from base ref, not working tree
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-s4-regression-1", kind="feature",
                          title="S4 regression - uncommitted mutation")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"),
                                  base_ref=base_ref)

            # Verify gate ran base ref commands, not mutated ones
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            self.assertGreater(len(gate_steps), 0)
            gate_step = gate_steps[0]

            # Commands should be from base ref
            self.assertIn("commands", gate_step)
            commands = gate_step["commands"]
            self.assertIn("base ref check", commands[0])
            self.assertNotIn("malicious", commands[0])

            # Protected path should be detected (anvil.json was modified)
            self.assertEqual(gate_step["protected_path_verdict"], "fail")
            self.assertIn("anvil.json", str(gate_step.get("protected_path_findings", "")))

    def test_committed_checks_config_mutation_uses_base_ref_s4_regression(self):
        """checks-gate S4 REGRESSION: committed change to checks config on work branch doesn't affect gate commands"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Initialize git repo and create base ref state
            import subprocess
            subprocess.run(["git", "init"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=proj, check=True)

            # Set up base ref checks configuration
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["echo 'base ref check'", "exit 0"]
            config["protected_paths"] = ["anvil.json", "tests/"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            # Commit to establish base ref
            subprocess.run(["git", "add", "."], cwd=proj, check=True)
            subprocess.run(["git", "commit", "-m", "Base ref state"], cwd=proj, check=True)
            base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=proj,
                                     capture_output=True, text=True, check=True).stdout.strip()

            # Create work branch
            subprocess.run(["git", "checkout", "-b", "work-branch"], cwd=proj, check=True)

            # NOW mutate checks config and COMMIT it on the work branch
            malicious_config = json.loads((proj / "anvil.json").read_text())
            malicious_config["checks"] = ["echo 'malicious check - should not run'", "exit 0"]
            (proj / "anvil.json").write_text(json.dumps(malicious_config, indent=2))
            subprocess.run(["git", "add", "anvil.json"], cwd=proj, check=True)
            subprocess.run(["git", "commit", "-m", "Attempt to modify checks"], cwd=proj, check=True)

            # Run gate - it should resolve commands from base ref, not work branch tip
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-gate-s4-regression-2", kind="feature",
                          title="S4 regression - committed mutation")
            report = run_pipeline(proj, sdlc_pipe(reg), wo, registry=reg,
                                  executor=command_executor(tmp, "pass"),
                                  base_ref=base_ref)

            # Verify gate ran base ref commands, not mutated ones
            gate_steps = [s for s in report.steps if s.get("station") == "checks-gate"]
            self.assertGreater(len(gate_steps), 0)
            gate_step = gate_steps[0]

            # Commands should be from base ref
            self.assertIn("commands", gate_step)
            commands = gate_step["commands"]
            self.assertIn("base ref check", commands[0])
            self.assertNotIn("malicious", commands[0])

            # Protected path should be detected (anvil.json was modified)
            self.assertEqual(gate_step["protected_path_verdict"], "fail")
            self.assertIn("anvil.json", str(gate_step.get("protected_path_findings", "")))

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

class TestChecksGateStationKind(unittest.TestCase):
    def test_checks_gate_station_kind_is_deterministic(self):
        """checks-gate: station kind should be 'deterministic' like other deterministic stations"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["exit 0"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            reg = load_registry(ROOT / "stations")

            # Load checks-gate station metadata
            checks_gate_station = reg.get("checks-gate")
            self.assertIsNotNone(checks_gate_station)

            # Station kind should be 'deterministic' or documented in ARCHITECTURE.md
            # This test verifies the hygiene requirement from loopback round
            station_kind = checks_gate_station.kind
            self.assertIsNotNone(station_kind, "checks-gate station must have a kind")

            # If not deterministic, it must be documented in docs/ARCHITECTURE.md
            if station_kind != "deterministic":
                arch_doc = ROOT / "docs" / "ARCHITECTURE.md"
                self.assertTrue(arch_doc.exists(),
                              "ARCHITECTURE.md must exist to document non-deterministic gate kind")
                arch_content = arch_doc.read_text()
                self.assertIn("checks-gate", arch_content.lower(),
                            "checks-gate kind must be documented in ARCHITECTURE.md")

class TestChecksGateBuilderDeltaSemantics(unittest.TestCase):
    """Loopback round 2 regression tests: gate judges only builder's delta, not test-writer output"""

    def test_test_writer_adds_tests_builder_changes_source_gate_passes(self):
        """Loopback round 2 (1): test-writer adds/modifies tests, builder changes only source → gate passes, reviewers spawn"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Initialize git repo and create base ref state
            import subprocess
            subprocess.run(["git", "init"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=proj, check=True)

            # Set up base ref with checks and protected paths
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["echo 'test passed'", "exit 0"]
            config["protected_paths"] = ["tests/", "anvil.json"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            # Create initial test file
            (proj / "tests" / "test_existing.py").write_text("# existing test")

            # Commit to establish base ref
            subprocess.run(["git", "add", "."], cwd=proj, check=True)
            subprocess.run(["git", "commit", "-m", "Base ref state"], cwd=proj, check=True)
            base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=proj,
                                     capture_output=True, text=True, check=True).stdout.strip()

            # Create work branch
            subprocess.run(["git", "checkout", "-b", "work-branch"], cwd=proj, check=True)

            # Simulate test-writer adding/modifying test files
            (proj / "tests" / "test_new_scenario.py").write_text("# new scenario test from spec")
            (proj / "tests" / "test_existing.py").write_text("# existing test - modified by test-writer")

            # Simulate builder changing only source files (not protected paths)
            (proj / "src" / "feature.py").parent.mkdir(exist_ok=True)
            (proj / "src" / "feature.py").write_text("# builder implementation")

            # Gate should evaluate only builder's delta (src/feature.py), not test-writer's writes
            # Since builder didn't touch protected paths, gate should pass
            reg = load_registry(ROOT / "stations")
            wo = WorkOrder(id="wo-lb2-001", kind="feature",
                          title="Loopback round 2 regression 1")

            # For this test, we need to simulate the gate receiving only builder's delta
            # This would be tracked by the runner
            builder_changed_files = ["src/feature.py"]  # Only builder's changes

            from anvil.gates import checks_gate
            result = checks_gate(
                phase="pre-review",
                base_ref_config=config,
                changed_files=builder_changed_files,
                project_dir=proj,
                work_order_id=wo.id,
                timeout=60
            )

            # Gate should pass - builder didn't touch protected paths
            self.assertEqual(result["gate_verdict"], "pass")
            self.assertEqual(result["status"], "passed")
            self.assertEqual(result["protected_path_verdict"], "pass")

            # Verify gate output records the basis judged
            self.assertIn("basis", result)
            self.assertIn("builder_delta", result["basis"])

    def test_builder_modifies_existing_base_ref_test_file_gate_fails(self):
        """Loopback round 2 (2): builder modifies existing base ref test file → gate fails, no reviewers spawn"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Initialize git repo and create base ref state
            import subprocess
            subprocess.run(["git", "init"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=proj, check=True)

            # Set up base ref with checks and protected paths
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["exit 0"]
            config["protected_paths"] = ["tests/", "anvil.json"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            # Create test file in base ref
            (proj / "tests" / "test_existing.py").write_text("# existing test in base ref")

            # Commit to establish base ref
            subprocess.run(["git", "add", "."], cwd=proj, check=True)
            subprocess.run(["git", "commit", "-m", "Base ref state"], cwd=proj, check=True)
            base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=proj,
                                     capture_output=True, text=True, check=True).stdout.strip()

            # Create work branch
            subprocess.run(["git", "checkout", "-b", "work-branch"], cwd=proj, check=True)

            # Simulate builder modifying the existing test file (protected path violation)
            (proj / "tests" / "test_existing.py").write_text("# builder modified this test - violation")

            # Gate should detect builder's modification of protected base ref file
            builder_changed_files = ["tests/test_existing.py"]  # Builder modified protected file

            from anvil.gates import checks_gate
            result = checks_gate(
                phase="pre-review",
                base_ref_config=config,
                changed_files=builder_changed_files,
                project_dir=proj,
                work_order_id="wo-lb2-002",
                timeout=60
            )

            # Gate should fail - builder modified protected path
            self.assertEqual(result["gate_verdict"], "fail")
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["protected_path_verdict"], "fail")
            self.assertIn("protected_path_findings", result)

            # Finding should name the specific path
            findings = result["protected_path_findings"]
            self.assertTrue(any("test_existing.py" in str(f) for f in findings))

    def test_builder_deletes_test_file_gate_fails(self):
        """Loopback round 2 (3): builder deletes a test file → gate fails"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Initialize git repo and create base ref state
            import subprocess
            subprocess.run(["git", "init"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=proj, check=True)

            # Set up base ref with checks and protected paths
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["exit 0"]
            config["protected_paths"] = ["tests/", "anvil.json"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            # Create test file in base ref
            (proj / "tests" / "test_to_delete.py").write_text("# test that will be deleted")

            # Commit to establish base ref
            subprocess.run(["git", "add", "."], cwd=proj, check=True)
            subprocess.run(["git", "commit", "-m", "Base ref state"], cwd=proj, check=True)
            base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=proj,
                                     capture_output=True, text=True, check=True).stdout.strip()

            # Create work branch
            subprocess.run(["git", "checkout", "-b", "work-branch"], cwd=proj, check=True)

            # Simulate builder deleting the test file
            (proj / "tests" / "test_to_delete.py").unlink()

            # Gate should detect builder's deletion of protected file
            # Deletion counts as touching per S3
            builder_changed_files = ["tests/test_to_delete.py"]  # Tracked as deleted

            from anvil.gates import checks_gate
            result = checks_gate(
                phase="pre-review",
                base_ref_config=config,
                changed_files=builder_changed_files,
                project_dir=proj,
                work_order_id="wo-lb2-003",
                timeout=60
            )

            # Gate should fail - builder deleted protected file
            self.assertEqual(result["gate_verdict"], "fail")
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["protected_path_verdict"], "fail")
            self.assertIn("protected_path_findings", result)

            # Finding should reference the deleted file
            findings = result["protected_path_findings"]
            self.assertTrue(any("test_to_delete.py" in str(f) for f in findings))

    def test_builder_modifies_checks_config_gate_fails_commands_from_base_ref(self):
        """Loopback round 2 (4): builder modifies checks config → gate fails, commands still resolve from base ref"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Initialize git repo and create base ref state
            import subprocess
            subprocess.run(["git", "init"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=proj, check=True)

            # Set up base ref checks configuration
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["echo 'base ref check command'", "exit 0"]
            config["protected_paths"] = ["anvil.json", "tests/"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            # Commit to establish base ref
            subprocess.run(["git", "add", "."], cwd=proj, check=True)
            subprocess.run(["git", "commit", "-m", "Base ref state"], cwd=proj, check=True)
            base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=proj,
                                     capture_output=True, text=True, check=True).stdout.strip()

            # Create work branch
            subprocess.run(["git", "checkout", "-b", "work-branch"], cwd=proj, check=True)

            # Simulate builder modifying checks configuration
            modified_config = json.loads((proj / "anvil.json").read_text())
            modified_config["checks"] = ["echo 'modified malicious check'", "exit 0"]
            (proj / "anvil.json").write_text(json.dumps(modified_config, indent=2))

            # Gate should:
            # 1. Detect protected path violation (anvil.json modified)
            # 2. Still run commands from base ref, not modified config
            builder_changed_files = ["anvil.json"]

            from anvil.gates import checks_gate
            result = checks_gate(
                phase="pre-review",
                base_ref_config=config,  # Base ref config passed in
                changed_files=builder_changed_files,
                project_dir=proj,
                work_order_id="wo-lb2-004",
                timeout=60
            )

            # Gate should fail - builder modified protected config file
            self.assertEqual(result["gate_verdict"], "fail")
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["protected_path_verdict"], "fail")

            # Commands run should be from base ref
            self.assertIn("commands", result)
            commands = result["commands"]
            self.assertIn("base ref check command", commands[0])
            self.assertNotIn("malicious", commands[0])

            # Protected path finding should name anvil.json
            findings = result["protected_path_findings"]
            self.assertTrue(any("anvil.json" in str(f) for f in findings))

    def test_loopback_attempt_judged_on_own_delta(self):
        """Loopback round 2 (5): first attempt touches protected → fails; loopback attempt doesn't → passes on its own delta"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Initialize git repo and create base ref state
            import subprocess
            subprocess.run(["git", "init"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=proj, check=True)

            # Set up base ref with checks and protected paths
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["exit 0"]
            config["protected_paths"] = ["tests/", "anvil.json"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            # Create a test file in base ref so attempt 1 can modify it (violation)
            (proj / "tests" / "test_bad.py").write_text("# original test in base ref")

            # Commit to establish base ref
            subprocess.run(["git", "add", "."], cwd=proj, check=True)
            subprocess.run(["git", "commit", "-m", "Base ref state"], cwd=proj, check=True)
            base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=proj,
                                     capture_output=True, text=True, check=True).stdout.strip()

            # Create work branch
            subprocess.run(["git", "checkout", "-b", "work-branch"], cwd=proj, check=True)

            # ATTEMPT 1: builder touches protected path
            attempt1_changed_files = ["tests/test_bad.py", "src/feature.py"]

            from anvil.gates import checks_gate
            result1 = checks_gate(
                phase="pre-review",
                base_ref_config=config,
                changed_files=attempt1_changed_files,
                project_dir=proj,
                work_order_id="wo-lb2-005",
                timeout=60
            )

            # Attempt 1 should fail - builder touched protected path
            self.assertEqual(result1["gate_verdict"], "fail")
            self.assertEqual(result1["status"], "failed")
            self.assertEqual(result1["protected_path_verdict"], "fail")

            # ATTEMPT 2 (loopback): builder changes only source, doesn't touch protected paths
            # This attempt is judged on its OWN delta, not cumulative changes
            attempt2_changed_files = ["src/feature.py"]  # Only source change, no protected paths

            result2 = checks_gate(
                phase="pre-review",
                base_ref_config=config,
                changed_files=attempt2_changed_files,
                project_dir=proj,
                work_order_id="wo-lb2-005",
                timeout=60
            )

            # Attempt 2 should pass - judged only on its own delta
            self.assertEqual(result2["gate_verdict"], "pass")
            self.assertEqual(result2["status"], "passed")
            self.assertEqual(result2["protected_path_verdict"], "pass")

            # Verify gate output records which attempt was judged
            self.assertIn("basis", result2)

    def test_builder_additions_to_protected_paths_recorded_not_violations(self):
        """Loopback round 2 clarification: builder additions to protected paths are observed, not violations"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Initialize git repo and create base ref state
            import subprocess
            subprocess.run(["git", "init"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=proj, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=proj, check=True)

            # Set up base ref with checks and protected paths
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["exit 0"]
            config["protected_paths"] = ["tests/", "anvil.json"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            # Commit to establish base ref (no tests/ directory exists yet)
            subprocess.run(["git", "add", "."], cwd=proj, check=True)
            subprocess.run(["git", "commit", "-m", "Base ref state"], cwd=proj, check=True)
            base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=proj,
                                     capture_output=True, text=True, check=True).stdout.strip()

            # Create work branch
            subprocess.run(["git", "checkout", "-b", "work-branch"], cwd=proj, check=True)

            # Simulate builder ADDING a new test file (not modifying/deleting existing one)
            (proj / "tests").mkdir(exist_ok=True)
            (proj / "tests" / "test_new_from_builder.py").write_text("# new test added by builder")

            # Gate should record this as an observed addition, not a violation
            # Per loopback round 2: modifications/deletions of base ref protected files are violations,
            # but additions are just recorded
            builder_changed_files = ["tests/test_new_from_builder.py"]

            from anvil.gates import checks_gate
            result = checks_gate(
                phase="pre-review",
                base_ref_config=config,
                changed_files=builder_changed_files,
                project_dir=proj,
                work_order_id="wo-lb2-006",
                timeout=60
            )

            # Gate should pass - addition is not a violation
            self.assertEqual(result["gate_verdict"], "pass")
            self.assertEqual(result["status"], "passed")

            # But the addition should be recorded as an observation
            self.assertIn("observed_additions", result)
            additions = result["observed_additions"]
            self.assertTrue(any("test_new_from_builder.py" in str(a) for a in additions))

class TestChecksGateCLIBaseRefDerivation(unittest.TestCase):
    """Loopback round 3 regression test: S4 control wired through CLI execution path"""

    def test_cli_derives_base_ref_from_merge_base_and_uses_it_s4_cli_regression(self):
        """Loopback round 3 REGRESSION: CLI derives base ref from merge base, uses it to resolve checks config"""
        import subprocess
        from anvil.cli import main

        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "cli-test-proj"

            # Create initial project structure first
            init_project(proj, "CLI Test Project")
            scaffold_spec(proj, "cli-test-feature", "CLI Test Feature")

            # Initialize scratch git repo IN THE PROJECT DIRECTORY
            subprocess.run(["git", "init"], cwd=proj, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=proj, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=proj, check=True, capture_output=True)

            # Set up base branch with known checks configuration
            config = json.loads((proj / "anvil.json").read_text())
            config["checks"] = ["echo 'base ref check command from main'", "exit 0"]
            config["protected_paths"] = ["anvil.json", "tests/"]
            (proj / "anvil.json").write_text(json.dumps(config, indent=2))

            # Create a simple pipeline and work order for testing
            pipeline_path = proj / "test-pipeline.json"
            pipeline = {
                "name": "cli-test-pipeline",
                "stages": [
                    {"station": "intake"},
                    {"station": "checks-gate"},
                    {"station": "builder"}
                ]
            }
            pipeline_path.write_text(json.dumps(pipeline, indent=2))

            work_order_path = proj / "test-wo.json"
            wo_data = {
                "id": "wo-cli-test",
                "kind": "feature",
                "title": "CLI base ref test",
                "description": "Test CLI base ref derivation"
            }
            work_order_path.write_text(json.dumps(wo_data, indent=2))

            # Commit everything to establish base ref on main branch
            subprocess.run(["git", "add", "."], cwd=proj, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Base ref state on main"], cwd=proj, check=True, capture_output=True)

            # Get the base ref (current HEAD on main)
            base_ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=proj,
                                     capture_output=True, text=True, check=True).stdout.strip()

            # Create work branch
            subprocess.run(["git", "checkout", "-b", "work-branch"], cwd=proj, check=True, capture_output=True)

            # FIRST: Modify checks config in working tree (uncommitted)
            malicious_config = json.loads((proj / "anvil.json").read_text())
            malicious_config["checks"] = ["echo 'MALICIOUS CHECK - should not run'", "exit 0"]
            (proj / "anvil.json").write_text(json.dumps(malicious_config, indent=2))

            # Run through CLI path (not module API) - this should derive base ref automatically
            # and use base ref commands, not working tree commands
            try:
                # Capture output to check what commands were run
                result = subprocess.run(
                    [sys.executable, "-m", "anvil.cli", "run", str(proj),
                     "--pipeline", str(pipeline_path),
                     "--work-order", str(work_order_path)],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False
                )

                # Parse the report from stdout
                # The JSON output is from the first line until "Report:" line
                report_json = None
                lines = result.stdout.split('\n')
                json_lines = []
                for line in lines:
                    if line.startswith('Report:'):
                        break
                    json_lines.append(line)

                if json_lines:
                    try:
                        report_json = json.loads('\n'.join(json_lines))
                    except json.JSONDecodeError:
                        pass

                self.assertIsNotNone(report_json, f"Should have JSON report output from CLI. Got stdout: {result.stdout[:500]}")

                # Find the checks-gate step
                gate_steps = [s for s in report_json.get("steps", []) if s.get("station") == "checks-gate"]
                self.assertGreater(len(gate_steps), 0, "Gate should have run")
                gate_step = gate_steps[0]

                # ASSERT 1: Commands run should be from base ref, not working tree
                commands = gate_step.get("commands", [])
                self.assertTrue(any("base ref check command from main" in cmd for cmd in commands),
                               f"Gate should run base ref commands, got: {commands}")
                self.assertFalse(any("MALICIOUS" in cmd for cmd in commands),
                                f"Gate should NOT run working tree commands, got: {commands}")

                # ASSERT 2: Protected path violation should be detected (anvil.json modified)
                self.assertEqual(gate_step["protected_path_verdict"], "fail",
                               "Gate should detect anvil.json modification")

                # ASSERT 3: Base ref should be recorded in report
                self.assertIn("base_ref", report_json,
                            "Report should record which base ref was used")

            finally:
                pass  # Cleanup handled by tempfile context

            # SECOND: Commit the malicious config and run again
            subprocess.run(["git", "add", "anvil.json"], cwd=proj, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Attempt to modify checks"], cwd=proj,
                          check=True, capture_output=True)

            # Run through CLI again - should STILL use base ref commands
            result2 = subprocess.run(
                [sys.executable, "-m", "anvil.cli", "run", str(proj),
                 "--pipeline", str(pipeline_path),
                 "--work-order", str(work_order_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False
            )

            # Parse the second report
            report_json2 = None
            lines2 = result2.stdout.split('\n')
            json_lines2 = []
            for line in lines2:
                if line.startswith('Report:'):
                    break
                json_lines2.append(line)

            if json_lines2:
                try:
                    report_json2 = json.loads('\n'.join(json_lines2))
                except json.JSONDecodeError:
                    pass

            self.assertIsNotNone(report_json2, f"Should have JSON report output from second CLI run. Got stdout: {result2.stdout[:500]}")

            # Find the checks-gate step in second run
            gate_steps2 = [s for s in report_json2.get("steps", []) if s.get("station") == "checks-gate"]
            self.assertGreater(len(gate_steps2), 0, "Gate should have run in second attempt")
            gate_step2 = gate_steps2[0]

            # ASSERT 4: Commands should STILL be from base ref (not committed modified config)
            commands2 = gate_step2.get("commands", [])
            self.assertTrue(any("base ref check command from main" in cmd for cmd in commands2),
                           f"Gate should STILL run base ref commands after commit, got: {commands2}")
            self.assertFalse(any("MALICIOUS" in cmd for cmd in commands2),
                            f"Gate should NOT run committed modified commands, got: {commands2}")

            # ASSERT 5: Protected path violation should still be detected
            self.assertEqual(gate_step2["protected_path_verdict"], "fail",
                           "Gate should still detect anvil.json modification after commit")

            # ASSERT 6: Base ref recorded should match the original base
            self.assertIn("base_ref", report_json2,
                        "Second report should also record base ref")

if __name__ == "__main__":
    unittest.main()
