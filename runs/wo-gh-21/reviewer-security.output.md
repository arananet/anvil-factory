Security review complete for wo-gh-21 round 4.

## Summary

Reviewed the two items in scope:

**Item 1 (Integration test)**: The test `test_provenance_check_integration_fails_on_violation` correctly uses `unittest.mock.patch` to mock `build_reviewer_design_packet`, returning a packet with out-of-allowlist provenance tags, then calls `prepare_reviewer_design_step` and verifies it raises `AllowlistViolation`. This satisfies the spec requirement. Runtime implementation already correct from round 3.

**Item 2 (IDAT hard cap)**: The implementation correctly prevents compression bomb memory exhaustion. Uses `decompressobj().decompress(data, max_length=expected_raw_size)` which enforces a hard limit (not a hint). At most `expected_raw_size` bytes are materialized in memory before the unconsumed_tail check detects excess and fails immediately. Regression test validates a 1 MB compression bomb is rejected after materializing only 81 bytes.

Security properties verified: hard cap enforcement, bounded memory, early detection during decompression, defense in depth with multiple checks, path boundary enforcement, and all existing hardening preserved.

**Verdict: PASS** - No security vulnerabilities identified. Both items correctly implemented with proper security properties.
