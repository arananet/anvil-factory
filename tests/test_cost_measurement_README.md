# Cost Measurement Test Suite

This test suite implements comprehensive tests for the cost measurement feature as specified in `.openspec/specs/cost-measurement/spec.md`.

## Test Coverage

### S1: Transcript Usage Is Summed and Priced Per Step

**File:** `TestCostMeasurementS1TranscriptUsage`

- `test_step_with_transcript_usage_is_measured_and_priced`: Verifies that steps with transcript usage get measured costs calculated from the price table
- `test_multiple_steps_each_get_independent_cost_measurement`: Ensures each step tracks its own cost independently

**Expected behavior:**
- Steps with usage data should have `cost` calculated as: `(input_tokens * input_price + output_tokens * output_price) / 1_000_000`
- The `cost` field should be a float, not null
- Each step's cost is independent based on its own usage and model

### S2: Gateway Usage Is Consumed When Response Reports It

**File:** `TestCostMeasurementS2GatewayUsage`

- `test_http_gateway_with_usage_object_is_measured`: HTTP gateway responses with usage objects are measured
- `test_http_gateway_without_usage_object_is_unmeasured`: HTTP responses without usage stay unmeasured

**Expected behavior:**
- HTTP executors that return `usage` with `prompt_tokens` and `completion_tokens` should be measured
- Gateway responses without usage should leave cost as null

### S3: Unmeasured Steps Stay Honestly Unmeasured

**File:** `TestCostMeasurementS3UnmeasuredSteps`

- `test_step_with_no_usage_source_records_unmeasured`: Steps with no usage have null cost
- `test_step_with_unknown_model_records_unmeasured`: Steps for models not in price table are unmeasured
- `test_unmeasured_step_contributes_nothing_to_total`: Unmeasured steps don't contribute to cost total

**Expected behavior:**
- No usage → cost is null
- No price table entry for model → cost is null
- Optional: `cost_record` with `measured: false` and `reason` explaining why

### S4: The Total Is the Sum of Measured Steps Only

**File:** `TestCostMeasurementS4ReportTotal`

- `test_cost_section_shows_total_with_coverage_counts`: Report includes cost section with total and counts
- `test_cost_total_excludes_unmeasured_steps`: Total sums only measured steps
- `test_swimlane_displays_cost_with_coverage`: Swimlane shows cost with coverage info

**Expected behavior:**
- Report dict should include a `cost` section with:
  - `total`: sum of all measured step costs
  - `measured_steps`: count of steps with non-null cost
  - `unmeasured_steps`: count of executed steps with null cost
- Swimlane markdown should display cost information with coverage (e.g., "2 of 8 steps measured")

### S5: Prices Carry Their Source and Date

**File:** `TestCostMeasurementS5PriceTableValidation`

- `test_price_table_requires_source_and_date`: Every price entry has source and date_recorded
- `test_price_table_entry_missing_source_is_invalid`: Schema rejects entries missing source
- `test_price_table_entry_missing_date_is_invalid`: Schema rejects entries missing date_recorded

**Expected behavior:**
- Price table in `anvil.yaml` under `prices` key
- Each entry must have: `input_per_million`, `output_per_million`, `source`, `date_recorded`
- Loader should validate and reject incomplete entries

### Integration Tests

**File:** `TestCostMeasurementIntegration`

- `test_full_pipeline_with_mixed_measured_and_unmeasured_steps`: End-to-end with mixed steps
- `test_deterministic_steps_have_null_cost`: Deterministic stations always have null cost
- `test_cost_calculation_with_different_models`: Different models use different prices
- `test_zero_tokens_yields_zero_cost`: Zero usage should yield 0.0 cost, not null
- `test_report_cost_never_changes_verdict`: Cost never affects pipeline verdict

## Test Helpers

### `make_price_table()`
Creates a valid price table with all required fields for testing.

### `FakeExecutorWithUsage`
Mock executor that returns configurable usage data per station.

### `FakeHTTPExecutorWithUsage`
Mock HTTP gateway executor that returns configurable usage data.

## Running the Tests

```bash
# Run all cost measurement tests
python -m unittest tests.test_cost_measurement -v

# Run specific test class
python -m unittest tests.test_cost_measurement.TestCostMeasurementS1TranscriptUsage -v

# Run specific test
python -m unittest tests.test_cost_measurement.TestCostMeasurementS1TranscriptUsage.test_step_with_transcript_usage_is_measured_and_priced -v
```

## Implementation Guidance

The tests expect the following implementation:

1. **Price Table Loading**: Load prices from `anvil.yaml` under `prices` key
2. **Cost Calculation**: For each executed step with usage, calculate cost from the configured model's price
3. **Cost Record**: Optionally add `cost_record` to steps with metadata about measurement
4. **Report Cost Section**: Add `cost` section to `RunReport.to_dict()` with total and counts
5. **Swimlane Update**: Update swimlane.md to display cost information with coverage
6. **No Estimation**: Never estimate or spread usage - unmeasured stays unmeasured

## Current Test Status

As of test writing:
- **Pass**: 10 tests (validation, unmeasured behavior, structure checks)
- **Fail**: 5 tests (require cost calculation implementation)
- **Error**: 3 tests (require report cost section implementation)

The failing/error tests define the exact behavior the builder needs to implement.
