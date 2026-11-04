Perfect! All tests pass. Let me create a summary of the implementation.

## Summary

I've successfully implemented the per-job cost measurement feature per the spec in `.openspec/specs/cost-measurement/spec.md`. All 18 scenario tests pass, and the full test suite (285 tests) remains green.

### Implementation Details

**Created Files:**
1. **`anvil/cost.py`** - Core cost measurement module with:
   - `load_price_table()` - Loads and validates price table from anvil.yaml
   - `validate_price_table()` - Validates required fields (source, date_recorded)
   - `calculate_cost()` - Calculates cost from usage and model prices, supports both transcript format (input_tokens/output_tokens) and gateway format (prompt_tokens/completion_tokens)
   - `build_cost_section()` - Builds cost summary with measured/unmeasured counts

2. **`docs/COST-MEASUREMENT.md`** - Feature documentation with examples and configuration guide

**Modified Files:**
1. **`anvil/runner.py`**:
   - Loads price table at pipeline start
   - Calculates cost for each step with usage data
   - Adds cost section to RunReport.to_dict() with total, measured_steps, and unmeasured_steps
   - Updates swimlane to display cost with coverage (e.g., "$3.5000 (2 of 8 steps measured)")

2. **`anvil/config.py`**:
   - Added "intake" to DEFAULT_MODELS with "reasoning-strong"

3. **`stations/intake/station.json`**:
   - Changed model from "default" to "reasoning-strong"

4. **`CHANGELOG.md`**:
   - Added feature description to Unreleased section

### Scenario Coverage

✅ **S1**: Transcript usage summed and priced per step  
✅ **S2**: Gateway usage consumed from HTTP responses  
✅ **S3**: Unmeasured steps recorded with measured=false and reason  
✅ **S4**: Cost section with total (sum of measured only) and coverage counts  
✅ **S5**: Price table with required source and date_recorded labels  

### Key Features

- **No estimation**: Only measured usage contributes to costs; unmeasured stays null
- **Honest reporting**: Cost section shows coverage (e.g., "2 of 8 steps measured")
- **No verdict impact**: Cost never affects pass/fail decisions
- **Dual format support**: Handles both transcript and gateway usage formats
- **Validation**: Rejects price entries missing source or date_recorded

All requirements from work order wo-gh-10 have been met.
