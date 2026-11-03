## Test Review Complete

I've reviewed the test suite for work order wo-gh-8 (risk routing feature). The review is written to `runs/wo-gh-8/reviewer-tests.review.json`.

**Verdict: Changes Requested**

All 16 tests pass and provide good coverage for scenarios S1-S6, but there are critical issues:

1. **S4 test is a placeholder** (line 404): `test_config_above_policy_fails_load_s4` uses `self.assertTrue(True, ...)` without actually validating that config loading fails when a model exceeds the policy ceiling.

2. **Two additional placeholder tests** (lines 590, 607): `test_default_routing_table_exists` and `test_project_can_override_routing_config` also pass without real assertions.

3. **S4 requirement not implemented**: `validate_model_assignment()` exists in routing.py:71 but is never called during config loading, so the policy ceiling enforcement isn't working.

4. **Tests use mock executor**: The test suite simulates routing behavior rather than exercising the actual `anvil/routing.py` implementation, so implementation bugs wouldn't be caught.

The other scenarios (S1, S2, S3, S5, S6) have proper tests that validate the expected behavior.
