## Test Writer Complete

I've verified and documented the round 4 tests for wo-gh-21. The tests are correctly written and all pass.

**Two tests written for round 4 items:**

1. **Item 1 - Integration test rewrite** (test_provenance_check_integration_fails_on_violation):
   - Uses `unittest.mock.patch` to mock `build_reviewer_design_packet` 
   - Returns packet with bad provenance tags (`secrets/api_keys.py` not in allowlist)
   - Calls `prepare_reviewer_design_step` directly and verifies it raises `AllowlistViolation`
   - Satisfies spec S3 line 85-86 requirement

2. **Item 2 - IDAT hard cap regression test** (test_png_idat_decompression_hard_cap_during_inflation):
   - Creates crafted PNG with 5x5 dimensions (80 bytes expected raw size)
   - Embeds IDAT that inflates to 1 MB (compression bomb)
   - Verifies `assemble_contact_sheet` fails during decompression with hard cap error
   - Proves memory exhaustion prevention

**Test Results:**
- All 36 astra consumption tests pass ✓
- No em dash or en dash characters used ✓
- Tests map exactly to round 4 loopback items ✓

Output documented in `/runs/wo-gh-21/test-writer.output.md`. Tests are ready for implementation.
