Review complete. I've identified three tests that need fixes:

1. **test_s1_malformed_entry_fails_validation** (line 58) - Skipped due to incorrect import `load_knowledge` instead of `load_builtin_knowledge`

2. **test_s10_guide_designation_names_design_model** (line 548) - Skipped due to incorrect import `load_routing_policy` which doesn't exist; should use `get_design_model_from_routing()` or access `MODEL_POLICY` directly

3. **test_s1_builtin_dataset_exists_and_validates** (line 33) - Only checks files exist, doesn't call `load_builtin_knowledge()` to test the actual loader behavior

The gate loopback wiring tests (run-level packet injection, pack loading, sensitive path rejection) are all real and passing. The implementation is correctly wired. However, these three test issues need to be fixed to ensure complete coverage per the standing note that tests must call implementations and assert behavior, not just check for existence of data structures.

**Review written to:** `runs/wo-gh-11/reviewer-tests.review.json`
