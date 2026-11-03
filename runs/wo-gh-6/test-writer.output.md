Tests complete. I've written comprehensive tests for the loopback round:

**Critical S4 Regression Tests** (2 tests in `tests/test_checks_gate.py`):
- Uncommitted mutation: proves gate uses base ref commands when config mutated in working tree
- Committed mutation: proves gate uses base ref commands when config mutated in committed work branch

**Station Kind Test** (1 test in `tests/test_checks_gate.py`):
- Verifies checks-gate has kind='deterministic' or is documented in ARCHITECTURE.md

**Pure Function Tests** (8 tests in new `tests/test_gates.py`):
- Function signature verification
- Pass/fail verdicts
- Protected path detection
- Not configured status
- Phase recording
- Prefix matching
- Function purity

All tests map to spec scenarios S1-S6 with focus on the S4 security finding. Output written to `runs/wo-gh-6/test-writer.output.md`.
