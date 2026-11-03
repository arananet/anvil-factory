## Review Complete

I've verified both gate round 4 items against the spec:

**Item 1 - S3 provenance check integration test**: The test at line 1139 uses `unittest.mock.patch` to make `build_reviewer_design_packet` return a packet with out-of-allowlist provenance tags (`secrets/api_keys.py`), then calls `prepare_reviewer_design_step` and verifies it raises `AllowlistViolation`. The implementation at `anvil/runner.py:515` confirms the verifier is called in the preparation path. Test passes.

**Item 2 - IDAT decompression hard cap**: The implementation at `anvil/runner.py:219` uses `decompressor.decompress(idat_data, expected_raw_size)` where `expected_raw_size` is the `max_length` parameter (a hard limit, not the `bufsize` hint). The regression test creates a crafted PNG inflating to 1MB from 80 bytes expected and verifies rejection during decompression. Test passes.

All 36 astra consumption tests pass. The implementation satisfies both round 4 items.

Review written to: `runs/wo-gh-21/reviewer-spec.review.json`
