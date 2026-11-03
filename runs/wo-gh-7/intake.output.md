I've launched an agent to fix the five security findings from reviewer-security. The agent is working on:

1. Adding input validation to WorkOrder model for intake_outcome, risk, and surfaces fields
2. Fixing report markdown rendering to safely escape user-provided content  
3. Adding tests for the validation and safe rendering
4. Updating CHANGELOG if needed

The agent will ensure all validation happens in the WorkOrder model so both direct construction and runner assignment are covered, and will make sure invalid data fails with clear, named errors.

Perfect! All five security findings have been successfully fixed. Here's a summary:

## Security Fixes Completed

### Files Modified (451 lines added/changed)

1. **anvil/model.py** (+90 lines)
   - Added vocabulary constants: `INTAKE_OUTCOMES`, `RISK_LEVELS`, `SURFACES`
   - Added error classes: `IntakeValidationError`, `RiskValidationError`
   - Added validation functions: `_validate_intake_outcome()`, `_validate_risk()`, `_validate_surfaces()`
   - Added `__setattr__()` override to WorkOrder class for runtime validation
   - Validation happens both at construction and assignment time

2. **anvil/runner.py** (+23 lines)
   - Added `_escape_markdown()` function to escape special characters
   - Updated report rendering to escape user-provided content (reasons, questions)
   - Fenced rescoped_description in code blocks for safe rendering

3. **tests/test_intake_outcomes.py** (+340 lines)
   - Added `TestIntakeValidation` class with 13 tests covering:
     - Invalid outcome values
     - Missing/empty required fields (reasons, questions, rescoped_description)
     - Invalid risk values
     - Invalid surface values
     - Runtime validation on field assignment
   - Added `TestMarkdownEscaping` class with 4 tests covering:
     - Markdown injection in reasons
     - HTML injection in reasons
     - Markdown injection in questions
     - Safe fencing of rescoped_description

4. **CHANGELOG.md** (updated)
   - Updated Unreleased section to document validation and escaping

### Test Results
- ✅ **24/24** intake outcomes tests pass (including 17 new tests)
- ✅ **208/208** total project tests pass
- ✅ All 8 pipelines valid
- ✅ No regressions introduced

### Security Improvements
✅ **Finding 1 Fixed**: intake_outcome validation enforces vocabulary and required fields  
✅ **Finding 2 Fixed**: risk validation constrained to {low, medium, high, None}  
✅ **Finding 3 Fixed**: surfaces validation constrained to defined vocabulary  
✅ **Finding 4 Fixed**: Runtime validation via `__setattr__()` catches invalid executor output  
✅ **Finding 5 Fixed**: Markdown/HTML escaping prevents content injection in reports

The implementation validates in the WorkOrder model (single source of truth) so both direct construction and runner assignment are covered. Invalid data fails loudly with named errors, never silently coerced.
