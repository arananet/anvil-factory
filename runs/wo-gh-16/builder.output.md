Perfect! All the verification tests pass. Let me create a summary of the implementation:

## Implementation Complete

I've successfully implemented the review parsing integrity spec (review-parsing-integrity) with the following changes:

### Core Changes

1. **One authoritative channel (S1)**:
   - Modified `runner.py` to write executor output to `runs/<work-order-id>/<station-id>.review.json` for reviewer stations
   - Reviews are parsed only from this file, never from free output

2. **Whole document parse (S2)**:
   - Replaced scanning logic in `parse_review()` with whole-document parsing
   - Accepts exactly one JSON object (with optional whitespace and markdown fence)
   - Validates: station matches, verdict is one of `pass`/`fail`/`changes_requested`, findings is a list

3. **Fail closed and reported (S3)**:
   - Malformed reviews record `review_parse_failed` in envelope
   - Contribute zero reviews to approver
   - Approver rule states both counted and expected numbers when there's shrinkage (in execute mode)

4. **Packet and prompt contract (S5)**:
   - Updated `_packet_text()` to include output contract for reviewer stations
   - Fixed `reviewer-design/PROMPT.md`: removed 3 JSON examples, fixed verdict vocabulary
   - Updated `tools/claude_station.py` REVIEW_SUFFIX to mention the single JSON object contract

5. **Documentation**:
   - Updated `docs/EXECUTION.md` with new review parsing contract
   - Added CHANGELOG entry

6. **Tests (S6)**:
   - All 111 tests passing
   - All 8 pipelines valid
   - No stations added/removed/renamed
   - Model routing unchanged

The implementation fixes the platform25 issue where the runner counted example JSON from prompts instead of actual reviews, and ensures reviews are fail-closed with clear shrinkage reporting.
