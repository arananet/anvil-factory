import json, tempfile, unittest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT = Path(__file__).resolve().parent.parent

class TestChecksGatePureFunction(unittest.TestCase):
    """Test the pure checks_gate function from anvil/gates.py"""

    def test_checks_gate_function_signature(self):
        """checks-gate: checks_gate function exists with correct signature"""
        try:
            from anvil.gates import checks_gate
        except ImportError:
            self.fail("anvil.gates module must exist with checks_gate function")

        # Verify function signature matches loopback requirement:
        # checks_gate(phase, base_ref_config, changed_files, project_dir, work_order_id, timeout)
        import inspect
        sig = inspect.signature(checks_gate)
        params = list(sig.parameters.keys())

        expected_params = ["phase", "base_ref_config", "changed_files", "project_dir", "work_order_id", "timeout"]
        self.assertEqual(params, expected_params,
                        f"checks_gate signature should be {expected_params}, got {params}")

    def test_checks_gate_passes_with_all_checks_passing(self):
        """checks-gate: pure function returns pass verdict when all checks pass"""
        from anvil.gates import checks_gate

        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)

            base_ref_config = {
                "checks": ["echo 'test'", "exit 0"],
                "protected_paths": ["tests/"]
            }

            changed_files = ["src/main.py"]  # Not a protected path

            result = checks_gate(
                phase="pre-review",
                base_ref_config=base_ref_config,
                changed_files=changed_files,
                project_dir=project_dir,
                work_order_id="wo-test-001",
                timeout=60
            )

            self.assertIsInstance(result, dict)
            self.assertEqual(result["gate_verdict"], "pass")
            self.assertEqual(result["status"], "passed")
            self.assertIn("commands", result)
            self.assertIn("exit_codes", result)
            self.assertEqual(result["protected_path_verdict"], "pass")

    def test_checks_gate_fails_with_failing_check(self):
        """checks-gate: pure function returns fail verdict when a check fails"""
        from anvil.gates import checks_gate

        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)

            base_ref_config = {
                "checks": ["exit 1"],  # Failing check
                "protected_paths": ["tests/"]
            }

            changed_files = ["src/main.py"]

            result = checks_gate(
                phase="pre-review",
                base_ref_config=base_ref_config,
                changed_files=changed_files,
                project_dir=project_dir,
                work_order_id="wo-test-002",
                timeout=60
            )

            self.assertIsInstance(result, dict)
            self.assertEqual(result["gate_verdict"], "fail")
            self.assertEqual(result["status"], "failed")
            self.assertIn("exit_codes", result)
            self.assertTrue(any(code != 0 for code in result["exit_codes"]))

    def test_checks_gate_fails_with_protected_path_touched(self):
        """checks-gate: pure function returns fail verdict when protected path is touched"""
        from anvil.gates import checks_gate

        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)

            base_ref_config = {
                "checks": ["exit 0"],  # Passing check
                "protected_paths": ["tests/", "anvil.json"]
            }

            changed_files = ["tests/test_new.py"]  # Protected path

            result = checks_gate(
                phase="pre-review",
                base_ref_config=base_ref_config,
                changed_files=changed_files,
                project_dir=project_dir,
                work_order_id="wo-test-003",
                timeout=60
            )

            self.assertIsInstance(result, dict)
            self.assertEqual(result["gate_verdict"], "fail")
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["protected_path_verdict"], "fail")
            self.assertIn("protected_path_findings", result)

    def test_checks_gate_not_configured_with_no_checks(self):
        """checks-gate: pure function returns not_configured status when no checks defined"""
        from anvil.gates import checks_gate

        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)

            base_ref_config = {}  # No checks configured

            changed_files = ["src/main.py"]

            result = checks_gate(
                phase="pre-review",
                base_ref_config=base_ref_config,
                changed_files=changed_files,
                project_dir=project_dir,
                work_order_id="wo-test-004",
                timeout=60
            )

            self.assertIsInstance(result, dict)
            self.assertEqual(result["status"], "not_configured")

    def test_checks_gate_records_phase(self):
        """checks-gate: pure function records the phase (pre-review or pre-deploy)"""
        from anvil.gates import checks_gate

        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)

            base_ref_config = {
                "checks": ["exit 0"],
                "protected_paths": ["tests/"]
            }

            changed_files = ["src/main.py"]

            for phase in ["pre-review", "pre-deploy"]:
                result = checks_gate(
                    phase=phase,
                    base_ref_config=base_ref_config,
                    changed_files=changed_files,
                    project_dir=project_dir,
                    work_order_id="wo-test-005",
                    timeout=60
                )

                self.assertEqual(result["phase"], phase)

    def test_checks_gate_protected_path_prefix_matching(self):
        """checks-gate: protected paths are matched as prefixes"""
        from anvil.gates import checks_gate

        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)

            base_ref_config = {
                "checks": ["exit 0"],
                "protected_paths": ["tests/"]
            }

            # These should match
            for changed_file in ["tests/test_a.py", "tests/subdir/test_b.py"]:
                result = checks_gate(
                    phase="pre-review",
                    base_ref_config=base_ref_config,
                    changed_files=[changed_file],
                    project_dir=project_dir,
                    work_order_id="wo-test-006",
                    timeout=60
                )
                self.assertEqual(result["protected_path_verdict"], "fail",
                               f"{changed_file} should match protected prefix tests/")

            # This should not match
            result = checks_gate(
                phase="pre-review",
                base_ref_config=base_ref_config,
                changed_files=["src/tests_util.py"],  # Not under tests/
                project_dir=project_dir,
                work_order_id="wo-test-007",
                timeout=60
            )
            self.assertEqual(result["protected_path_verdict"], "pass",
                           "src/tests_util.py should not match protected prefix tests/")

    def test_checks_gate_is_pure_function(self):
        """checks-gate: checks_gate is a pure function with no side effects on runner state"""
        from anvil.gates import checks_gate

        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)

            base_ref_config = {
                "checks": ["exit 0"],
                "protected_paths": ["tests/"]
            }

            changed_files = ["src/main.py"]

            # Call function multiple times with same inputs
            results = []
            for _ in range(3):
                result = checks_gate(
                    phase="pre-review",
                    base_ref_config=base_ref_config,
                    changed_files=changed_files,
                    project_dir=project_dir,
                    work_order_id="wo-test-008",
                    timeout=60
                )
                results.append(result)

            # Results should be consistent (pure function property)
            for result in results:
                self.assertEqual(result["gate_verdict"], results[0]["gate_verdict"])
                self.assertEqual(result["status"], results[0]["status"])

if __name__ == "__main__":
    unittest.main()
