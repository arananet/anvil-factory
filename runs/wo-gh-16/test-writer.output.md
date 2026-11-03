Test-writer station complete. I've updated the review parsing integrity test suite for loopback round 2:

**Test file:** `/home/runner/work/anvil-factory/anvil-factory/tests/test_review_parsing_integrity.py`

**Changes made:**

1. **Enhanced L2 defect detection** - The `test_wrapper_restatement_matches_or_defers_to_canonical_packet_loopback_l2` test now precisely identifies the hybrid defect from the loopback round 1 finding, where `REVIEW_SUFFIX` both defers to the packet AND restates contract terms with different wording

2. **New compliance tests** - Added `TestLoopbackRound2Compliance` class with tests measuring the success criterion: whether reviewer stations emit parseable review JSON that counts

3. **All existing tests preserved** - Round 1, loopback round 1, and regression tests remain unchanged

**Current state:** 21 tests total, 20 pass, 1 expected failure (the L2 test detecting the hybrid defect). The suite is ready for builder implementation.
