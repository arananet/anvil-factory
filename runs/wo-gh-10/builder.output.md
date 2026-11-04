## Summary

I've completed the required changes for the wo-gh-10 CLOSING VERIFICATION RUN:

### Changes Made

Reverted exactly two out-of-scope intake configuration changes:

1. **anvil/config.py:9** - Removed `"intake": "reasoning-strong"` entry from `DEFAULT_MODELS`
2. **stations/intake/station.json:16** - Restored `model` field from `"reasoning-strong"` to `"default"`

These minimal changes restore the intake station's correct model configuration, closing finding 2 from GATE LOOPBACK 1.

### Test Status

After the reverts, 2 tests in `tests/test_cost_measurement.py` fail:
- `test_run_report_includes_cost_section`: expects 2 measured steps, gets 1  
- `test_gateway_response_with_usage`: expects intake cost, gets None

**Root cause**: The tests were written by test-writer (in this run) while the out-of-scope intake changes were still present. Tests have price entries for "reasoning-strong" but not "default", so intake correctly records as unmeasured per spec S3.

**Resolution**: The test failures will be caught by reviewer-tests. Tests need adjustment to either add "default" pricing or expect intake as unmeasured. Per standing discipline, builder cannot modify tests/ - this is test-writer work for a subsequent iteration.

The implementation itself is correct - it properly handles unmeasured steps per the cost measurement spec.
