## Completion

Fixed three tests in `tests/test_design_knowledge.py` per the GATE LOOPBACK 2 requirements:

**Changes:**
1. Added correct imports: `load_builtin_knowledge`, `validate_knowledge_entry`, `get_design_model_from_routing`
2. **test_s1_builtin_dataset_exists_and_validates** - Now calls the loader and asserts success
3. **test_s1_malformed_entry_fails_validation** - Removed skip pattern, tests malformed entry validation  
4. **test_s10_guide_designation_names_design_model** - Uses real accessor to verify guided stations resolve to policy's design model

All three tests now pass. Full suite: 309 tests OK (1 skipped).

Output written to `runs/wo-gh-11/test-writer.output.md`.
