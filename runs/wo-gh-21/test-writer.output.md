Tests have been written and saved to `/home/runner/work/anvil-factory/anvil-factory/tests/test_astra_consumption.py`.

The test file contains comprehensive test coverage for all scenarios in the spec:

**S1 - Packet Budget (TestTokenEstimator, TestPacketBudget)**
- Estimator determinism, zero for empty, monotonic growth
- Over budget packet trimming in declared order
- Fail policy preventing execution
- Under budget byte identity
- Report fields recording

**S2 - Evidence Image Policy (TestContactSheet)**
- Contact sheet dimensions within max width
- Scaling down proportionally, never up
- Original captures unchanged
- Non-PNG failure handling

**S3 - Scoped Design Review (TestScopedReview)**
- reviewer-design packet contents (design, spec, diff, contact sheet)
- Allowlist check rejecting out-of-scope content
- Allowlist check passing for scoped content

**S4 - Stable Prefix Layout (TestPacketLayout)**
- Stable prefix sharing across runs
- Design and learnings before work order block

**S5 - Per Station Cost Visibility**
- Covered in budget tests (report fields)

All tests use Python standard library only (no external dependencies), following the project's constraint. The tests are written for functionality that will be implemented, following TDD approach.
