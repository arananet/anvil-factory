## Summary

Created comprehensive test coverage for wo-gh-15 round 5 final loopback defects.

**Test files created:**
- `tests/test_quality_final_loopback.py` - 5 tests proving both defects exist
- `tests/test_quality_final_loopback_coverage.md` - Test documentation
- `runs/wo-gh-15/test-writer.output.md` - Station output

**Current test results:**
- 398 total tests (393 existing + 5 new)
- 5 failures from new tests (expected - proves defects exist)
- All existing tests green (hard constraint satisfied)

**Defects proven:**

1. **F1 - Prompt Documentation**: `test_reviewer_design_prompt_documents_same_subject_test_duty` fails because stations/reviewer-design/PROMPT.md line 73 has only a generic instruction, not the explicit S7 same-subject test duty required by the spec.

2. **F2 - Sanitization Regression**: 4 tests fail because anvil/quality.py lines 140, 146-147 interpolate work_order.identity_reference and work_order.identity_traits into packet markdown without control character sanitization, violating round 1 finding F3.

The tests will pass once the builder implements both fixes, verifying the implementation is complete.
