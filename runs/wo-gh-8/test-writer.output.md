## Completed

I've fixed all three placeholder tests in `tests/test_risk_routing.py` and added comprehensive coverage for all gate loopback findings:

**Fixed Finding D - Three Placeholder Tests:**
- `test_config_above_policy_fails_load_s4`: Now validates that `validate_model_assignment` catches policy violations
- `test_default_routing_table_exists`: Verifies factory ships complete default routing configuration
- `test_project_can_override_routing_config`: Tests project config overrides work correctly

**Added Finding B - Configuration Validation (2 tests):**
- Tests for invalid reviewer IDs and invalid model references (skip until builder implements validation)

**Added Finding C - Policy Ceiling Overrides (2 tests):**
- Tests for project policy_ceilings configuration and factory defaults

**Added Finding E - Routing Trust (3 tests):**
- Tests verifying routing trusts intake outcomes as stamped

**Test Results:** 21 passing, 2 skipped (waiting for validation implementation), 0 failures in 4.1s

All spec scenarios S1-S7 fully covered. Output written to `runs/wo-gh-8/test-writer.output.md`.
