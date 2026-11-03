Spec revised. The Astra consumption spec has been updated to revision 2 with clarifications addressing all 6 loopback findings from gate round 2:

**Key changes:**
- S2/S3 integration: Explicitly requires runner to call contact sheet assembler and scoped packet builder in the run path
- Architectural placement: Scoped packet builder must be in anvil/runner.py or helper module, not importing from anvil/stations  
- Provenance-based allowlist: Content blocks tagged with source paths; verification by tags, not pattern scanning
- PNG security hardening: Size caps, CRC validation, bounds checks, path validation
- Report visibility: Measurements must appear in actual report.json for real runs
- Integration test: Verify S2/S3 wiring with a test design order execution

Output: `runs/wo-gh-21/spec-writer.output.md`
