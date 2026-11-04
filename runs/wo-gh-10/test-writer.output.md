Tests complete for cost measurement feature (wo-gh-10). Created comprehensive test suite in `tests/test_cost_measurement.py` covering all spec scenarios S1-S5:

**Coverage:**
- S1: Transcript usage summed and priced (2 tests)
- S2: Gateway usage from HTTP responses (2 tests)
- S3: Unmeasured steps handled honestly (3 tests)
- S4: Cost total with coverage reporting (3 tests)
- S5: Price table validation (3 tests)
- Integration scenarios (5 tests)

**Status:** All 18 tests passing ✓

Tests verify the implementation should:
- Calculate cost as (input_tokens × input_price + output_tokens × output_price) / 1M
- Support both transcript format (input_tokens/output_tokens) and gateway format (prompt_tokens/completion_tokens)
- Leave unmeasured steps with null cost when no usage or price table entry exists
- Build cost section with total, measured_steps, and unmeasured_steps counts
- Require price table entries to have source and date_recorded fields
- Never allow cost to affect verdicts

Output documented in `runs/wo-gh-10/test-writer.output.md`.
