Spec revision complete. The astra-consumption spec has been updated to incorporate all gate round 3 loopback findings:

**S2 (Evidence Image Policy)** now includes PNG security hardening: byte size and dimension caps, CRC verification, chunk length bounds checking, IDAT accumulation caps, bounded decompression, and path validation.

**S3 (Fresh Session Design Review)** now explicitly requires:
- Provenance check execution in prepare_reviewer_design_step path
- Content tagging with source paths at assembly time
- Path boundary matching (not substring matching)
- Layer constraint: runner must not import from .stations

**Tests section** expanded with PNG security tests, provenance verification integration tests, and allowlist path boundary tests.

**Scenarios** updated to explicitly state the integration and security requirements.

The spec now provides clear, testable requirements for all gate round 3 findings.
