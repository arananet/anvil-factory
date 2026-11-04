## Review Complete

All tests are **real, mapped, and passing**.

### Verification Summary

**Gate Loopback 2 Requirements:**

1. **Three tests now call real implementation** (no longer skipping):
   - `test_s1_malformed_entry_fails_validation` → calls `validate_knowledge_entry()` with malformed data (line 88)
   - `test_s10_guide_designation_names_design_model` → calls `get_design_model_from_routing()` (line 558)
   - `test_s1_builtin_dataset_exists_and_validates` → calls `load_builtin_knowledge()` (line 64)

2. **All 27 tests pass** ✓

3. **Tests are mapped to spec scenarios**:
   - S1-S10 coverage across all test classes
   - Gate loopback wiring tests included

4. **Implementation is properly wired**:
   - `Station.guided` field exists in dataclass (stations.py:22)
   - `load_registry` preserves it (stations.py:70)
   - Runner applies design model from routing policy to guided stations (runner.py:490-494)
   - `get_design_model_from_routing()` reads from `MODEL_POLICY["designer"]` (knowledge.py:499-506)

**Verdict:** pass
