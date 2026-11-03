## Review Complete

I've reviewed the tests in `tests/test_astra_consumption.py` against the spec and the round 4 loopback requirements.

**Verdict: PASS**

All tests are real, mapped to spec scenarios, and passing (36/36 tests passed).

### Round 4 Items Verified

**Item 1** (Provenance check integration): The test `test_provenance_check_integration_fails_on_violation` now correctly uses `unittest.mock.patch` to make `build_reviewer_design_packet` return a packet with out-of-allowlist provenance tags, then calls `prepare_reviewer_design_step` (not the verifier directly) and verifies `AllowlistViolation` is raised. This satisfies spec S3 line 85-86 requirement that "prepare_reviewer_design_step itself is tested."

**Item 2** (IDAT hard cap): The test `test_png_idat_decompression_hard_cap_during_inflation` creates a compression bomb (1 MB of zeros compressing to tiny size, expecting only 80 bytes) and verifies it's rejected. The implementation uses `decompressor.decompress(idat_data, expected_raw_size)` where the max_length parameter enforces a hard cap during decompression - the decompressor never materializes more than expected_raw_size bytes before detecting the violation.

### Test Coverage

- **S1** (packet budget): Estimator determinism, budget trim order, fail policy, under budget byte identity, report fields ✓
- **S2** (evidence policy): Contact sheet assembly, PNG security hardening (size caps, CRC verification, bounds checks, IDAT caps, path validation) ✓
- **S3** (scoped review): Packet contents, provenance verification by tags, integration through prepare_reviewer_design_step, path boundary matching ✓
- **S4** (stable prefix): Stable prefix across runs, layout order ✓
- **S5** (cost visibility): Report measurements ✓

Review written to `runs/wo-gh-21/reviewer-tests.review.json`.
