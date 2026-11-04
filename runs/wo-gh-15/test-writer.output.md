I've completed the test-writer task for wo-gh-15 gate loopback round 4.

## Tests Created

Created `tests/test_quality_same_subject.py` with 5 integration tests proving the S7 same-subject test duty requirement:

1. **test_same_subject_duty_injected_when_identity_reference_declared** - Verifies duty appears in packet when both identity_reference and deliverable_set are declared
2. **test_same_subject_duty_absent_when_fields_not_declared** - Verifies duty is absent when fields are not declared
3. **test_same_subject_duty_with_only_identity_reference** - Verifies identity_reference alone doesn't trigger duty (both fields required)
4. **test_same_subject_duty_with_only_deliverable_set** - Verifies deliverable_set alone doesn't trigger duty (both fields required)
5. **test_same_subject_duty_references_identity_traits** - Verifies identity_traits are referenced in the duty when declared

These tests exercise the requirement end-to-end: work order → runner → packet content validation, matching the factory suite style from `test_quality_wiring.py`.

## Hard Constraints Met

- NEW test file (avoids protected path violations)
- No modifications to existing test files
- Tests only the S7 same-subject duty scope
- Syntactically valid (verified with py_compile)

Output documented in `runs/wo-gh-15/test-writer.output.md`.
