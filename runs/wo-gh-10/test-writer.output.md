Perfect! All cost measurement tests pass. Let me create a summary of the work completed:

## Summary

Successfully authored cost measurement tests for wo-gh-10 in `tests/test_cost_measurement.py`.

**Test Coverage (15 tests mapping to spec scenarios S1-S5):**

- **S1 (Transcript usage)**: 3 tests verify usage summing, pricing, and zero-cost handling
- **S2 (Gateway usage)**: 3 tests verify both gateway format normalization and unmeasured handling  
- **S3 (Unmeasured steps)**: 2 tests verify no-usage and no-price scenarios with proper reason recording
- **S4 (Cost section)**: 4 tests verify report aggregation, measured/unmeasured counts, and total calculation
- **S5 (Price table validation)**: 3 tests verify source/date requirement enforcement

**Implementation tested:**
- `anvil.cost.validate_price_table()` - validation with source/date requirements
- `anvil.cost.load_price_table()` - config loading with error handling
- `anvil.cost.calculate_cost()` - usage → cost with measured/unmeasured logic
- `anvil.cost.build_cost_section()` - report aggregation
- `anvil.runner.run_pipeline()` - integration tests with custom executors

All tests are real: they call the actual implementation and assert behavior. The full suite (282 tests) remains green.
