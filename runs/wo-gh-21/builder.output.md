## Summary

Gate round 4 implementation complete. Both items fixed:

**Item 1 - Provenance Integration Test:** The test `test_provenance_check_integration_fails_on_violation` now uses `unittest.mock.patch` to mock `build_reviewer_design_packet` and calls `prepare_reviewer_design_step` to verify it raises `AllowlistViolation`, satisfying the spec S3 requirement.

**Item 2 - IDAT Hard Cap:** Fixed decompression in `anvil/runner.py` to use `expected_raw_size` as the max_length parameter (not the fixed 8192). The decompressor now:
- Decompresses at most `expected_raw_size` bytes using `decompressor.decompress(idat_data, expected_raw_size)`
- Checks for excess data by attempting to decompress one more byte
- Fails during decompression if the stream yields more than expected
- Never materializes more than `expected_raw_size` bytes before failing

**Test results:**
- Both round 4 specific tests pass
- All 36 astra-consumption tests pass  
- All 187 factory tests pass

**Scope compliance:** Only `anvil/runner.py` and `tests/test_astra_consumption.py` changed. No modifications to tools, prompts, or wo-gh-24 mechanisms. Standard library only. No em/en dash characters.
