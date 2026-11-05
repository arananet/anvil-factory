Excellent! The implementation is complete and verified. Let me create a summary:

## Loopback Round 2 Implementation Complete

### Part 1: L2 Finding Fixed ✓

**The defect:** tools/claude_station.py had a hybrid that both deferred to the packet AND restated contract terms in different words.

**The fix:** Chose **shape (i)** - repeat the canonical wording word-for-word from anvil/runner.py.

**Implementation:**
- Removed the `REVIEW_SUFFIX` constant (had the hybrid defect)
- Created `review_suffix(work_order_id, station_id)` function that builds canonical wording dynamically
- Added `work_order_id_of()` to extract work order ID from packet
- Updated main() to call `review_suffix()` for reviewer stations

**Rationale for shape (i):**
Evidence from loopback round 1 showed 4 of 5 reviewers wrote prose when the contract was stated only in the packet. Repeating the canonical wording at the END of the prompt (last text seen) maximizes compliance likelihood.

### Part 2: Compliance Strengthening ✓

**Conclusion:** The Part 1 fix IS the compliance strengthening mechanism. No additional prompt-level levers remain.

The contract is now stated THREE times:
1. In the packet (anvil/runner.py) - canonical Output contract section
2. In reviewer PROMPT.md files (loopback round 1) - Output Format section
3. **At the END** (tools/claude_station.py) - canonical wording repeated verbatim (Part 1 fix)

The Part 1 fix puts the canonical wording as the final text before the station responds, which addresses the 4-of-5 failure rate from loopback round 1.

### Tests: All Pass ✓

- **21/21** review parsing integrity tests pass
- **17/17** execution tests pass (no regressions)
- Key L2 test verifies: no hybrid defect, shape (i) compliance confirmed

### Files Changed

1. **tools/claude_station.py** - L2 fix implementation
2. **tests/test_review_parsing_integrity.py** - Updated L2 test to handle function-based suffix
3. **runs/wo-gh-16/builder.output.md** - Complete implementation documentation

The implementation satisfies both loopback round 2 requirements and keeps the whole suite green as specified.
