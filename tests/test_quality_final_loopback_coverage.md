# Test Coverage for Quality Standard Round 5 Final Loopback

This document describes the tests in `test_quality_final_loopback.py` that prove the two defects identified in round 5 of wo-gh-15.

## Defect 1: Prompt Documentation (F1)

**Finding**: stations/reviewer-design/PROMPT.md line 73 has only a generic instruction to "follow duties stated in the packet" rather than explicitly documenting the S7 same-subject test duty.

**Test**: `test_reviewer_design_prompt_documents_same_subject_test_duty`

Verifies that the reviewer-design PROMPT.md file explicitly documents:
- When the same-subject test applies (identity_reference and deliverable_set present)
- What the reviewer must do (compare across deliverable set against identity reference)
- How to handle divergence (quality failure with named asset and trait)
- Where to record findings (quality section)

The test reads the PROMPT.md file and checks for presence of these elements using pattern matching.

## Defect 2: Sanitization Regression (F2)

**Finding**: anvil/quality.py interpolates work_order.identity_reference and work_order.identity_traits into packet markdown without control character sanitization (around lines 140, 146-147), violating round 1 finding F3.

**Tests**:

### `test_identity_reference_sanitizes_control_characters`
Creates a work order with control characters (NULL \x00 and Unit Separator \x1f) in identity_reference field, generates the quality charter section, and verifies control characters are removed from the output.

### `test_identity_traits_sanitize_control_characters`
Creates a work order with control characters (Backspace \x08, Escape \x1b, Delete \x7f) in identity_traits items, generates the quality charter section, and verifies control characters are removed from each trait.

### `test_all_quality_packet_interpolations_are_sanitized`
Comprehensive test with control characters in all quality-related work order fields (identity_reference, deliverable_set, identity_traits). Verifies that dangerous control characters (excluding safe \n and \t) are sanitized from packet output.

### `test_anchor_section_sanitizes_control_characters`
Tests the anchor section output separately to ensure control characters in anchors and identity fields are sanitized in both the charter section and the anchor section.

## Test Characteristics

- **File**: tests/test_quality_final_loopback.py (NEW file, per round 4 constraint)
- **Framework**: unittest (factory suite style)
- **Isolation**: Does not modify existing test files
- **Expected Behavior**: All 5 tests should FAIL on the current tree, proving both defects exist
- **Post-Fix Behavior**: All 5 tests should PASS after implementing the two fixes

## Control Characters Tested

The sanitization tests cover common dangerous control characters:
- \x00 (NULL) - can terminate strings
- \x08 (Backspace) - can delete prior characters
- \x0e, \x0f (Shift Out/In) - character set switching
- \x1b (Escape) - can trigger terminal commands
- \x1f (Unit Separator) - field delimiter
- \x7f (Delete) - can remove characters

Safe characters \n (newline) and \t (tab) are explicitly excluded from sanitization checks as they are safe in markdown.
