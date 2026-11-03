Perfect! All changes have been successfully implemented and tested. Here's a summary of what was completed for work order wo-gh-21, loopback gate round 4:

## Summary

Successfully fixed the two items identified in round 4:

### ITEM 1: Integration Test Rewrite
- **Fixed**: `test_provenance_check_integration_fails_on_violation` in `tests/test_astra_consumption.py`
- **Solution**: Rewrote the test to use `unittest.mock.patch` on `build_reviewer_design_packet` to return a packet with bad provenance tags, then call `prepare_reviewer_design_step` and verify it raises `AllowlistViolation`
- **Result**: The test now drives the full preparation path as the spec requires

### ITEM 2: IDAT Decompression Hard Cap
- **Fixed**: CRITICAL security vulnerability in `anvil/runner.py` where `zlib.decompress` with `bufsize` parameter didn't enforce a hard limit
- **Solution**: Replaced with incremental decompression using `zlib.decompressobj()` that checks size after each chunk and fails immediately if data exceeds the expected raw size
- **Result**: Compression bombs are now rejected during decompression, not after full materialization
- **Added**: Regression test `test_png_idat_decompression_hard_cap_during_inflation` proving crafted over-inflating PNGs are rejected

## Test Results
✅ All 36 astra consumption tests pass
✅ Both new/rewritten tests pass
✅ All existing tests remain passing

## Files Modified
1. `anvil/runner.py` - Hard-capped IDAT decompression (lines 209-254)
2. `tests/test_astra_consumption.py` - Rewritten integration test + new regression test
3. `runs/wo-gh-21/spec-writer.output.md` - Documentation of changes

The implementation follows all round 4 scope guardrails: standard library only, no changes to tools/claude_station.py or review mechanisms, no em/en dashes, and all existing tests pass.
