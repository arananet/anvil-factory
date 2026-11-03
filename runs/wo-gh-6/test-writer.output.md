Perfect! The tests are complete. I've added 6 regression tests to `tests/test_checks_gate.py` for loopback round 2:

## Tests Written

**Test Class: `TestChecksGateBuilderDeltaSemantics`**

1. **test_test_writer_adds_tests_builder_changes_source_gate_passes** - Verifies that when test-writer adds/modifies test files but builder changes only source files, the gate passes and reviewers spawn (requirement 1)

2. **test_builder_modifies_existing_base_ref_test_file_gate_fails** - Proves builder modification of an existing base ref test file triggers gate failure with protected path finding (requirement 2)

3. **test_builder_deletes_test_file_gate_fails** - Confirms builder deletion of a test file fails the gate (requirement 3)

4. **test_builder_modifies_checks_config_gate_fails_commands_from_base_ref** - Validates that builder modification of checks config fails the gate while commands still resolve from base ref (requirement 4)

5. **test_loopback_attempt_judged_on_own_delta** - Demonstrates that each attempt is judged on its own builder delta, not cumulative changes (requirement 5)

6. **test_builder_additions_to_protected_paths_recorded_not_violations** - Verifies that builder additions to protected paths are recorded as observations, not violations (clarified semantics)

All tests follow the factory suite style with git repo setup, direct calls to the `checks_gate` pure function from `anvil/gates.py`, and clear assertions verifying the loopback round 2 clarified semantics: the gate judges only the builder station's delta, not test-writer output.
