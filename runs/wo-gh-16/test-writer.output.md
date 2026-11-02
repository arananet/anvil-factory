Perfect! All existing tests pass, and only the 6 new tests that document implementation gaps are failing. Let me create a summary of what was delivered:

## Test Suite Complete

I've written comprehensive tests for the review parsing integrity spec (`.openspec/specs/review-parsing-integrity/spec.md`). The test suite is in `/home/runner/work/anvil-factory/anvil-factory/tests/test_review_parsing_integrity.py`.

### Test Coverage

**17 tests mapping to all 6 spec scenarios:**

**S1 - One Authoritative Channel:**
- ✅ `test_free_output_not_parsed_for_review_s1` - Verifies free output stays as provenance
- ❌ `test_review_written_to_authoritative_channel_s1` - Needs .review.json implementation

**S2 - Whole Document Parse:**
- ✅ `test_json_with_markdown_fence_parses_s2` - Handles markdown fences
- ❌ `test_exact_json_object_parses_s2` - Needs .review.json implementation
- ❌ `test_no_scanning_for_first_match_s2` - Needs removal of scanning behavior

**S3 - Fail Closed:**
- ✅ `test_empty_review_file_fails_closed_s3` - Empty file handling
- ✅ `test_malformed_json_fails_closed_s3` - Malformed JSON handling
- ✅ `test_missing_review_file_fails_closed_s3` - Missing file handling
- ❌ `test_prose_only_output_fails_closed_and_reports_shrinkage_s3` - Needs decision rule update

**S4 - Platform25 Evidence:**
- ✅ `test_platform25_actual_shape_with_single_review_s4` - Clean single review passes
- ❌ `test_example_object_before_real_review_counts_real_verdict_s4` - Needs whole-document parsing

**S5 - Packet and Prompt Contract:**
- ✅ `test_reviewer_design_has_three_json_examples_before_fix_s5` - Documents current state
- ✅ `test_reviewer_design_verdict_vocabulary_s5` - Documents vocabulary
- ❌ `test_reviewer_prompts_have_no_json_examples_s5` - Needs prompt cleanup (reviewer-design)

**S6 - Regression Tests:**
- ✅ `test_all_eight_pipelines_valid_s6` - All 8 pipelines load correctly
- ✅ `test_no_stations_added_removed_or_renamed_s6` - Station stability
- ✅ `test_model_routing_unchanged_s6` - Model routing preserved

### Test Results

- **111 total tests** in the full suite (94 existing + 17 new)
- **105 passing** (all existing tests + 11 new regression guards)
- **6 failing** (documenting expected implementation gaps)

All existing tests pass - no regressions introduced. The 6 failing tests precisely document what needs to be implemented.
