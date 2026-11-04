Perfect! I've created comprehensive integration tests for the quality standard wiring. Here's a summary:

## Tests Created

**File:** `tests/test_quality_wiring.py` (14 tests)

### Coverage of Gate Loopback Round 2, Item 5:

1. **Packet Wiring** - Integration test runs full pipeline and verifies:
   - Visual run packets contain Quality Charter section
   - Visual run packets contain Reference Anchors section
   - All four criteria present (materials, light, contact, scale)
   
2. **Missing Anchor Warning** - Verifies:
   - Report contains visible warning when no anchors available
   - Charter floor still present in packets
   
3. **Non-Visual Exclusion (S3)** - Full pipeline test:
   - API-only work orders receive no charter in any packet
   - No quality-related text in report
   
4. **Dual-Section Contract** - Four tests validating:
   - Separate compliance and quality sections
   - Quality can fail while compliance passes
   - Anchor citation required
   - Criteria categories must be named
   
5. **Path Traversal Protection** - Seven tests covering:
   - Parent traversal rejection (..)
   - Absolute path rejection (/)
   - Backslash traversal rejection (\\)
   - All three quality path fields validated
   - WorkOrder.from_dict validation

The tests follow factory suite patterns and complement the existing unit tests in `test_quality_standard.py`. Updated coverage documentation in `tests/test_quality_standard_coverage.md`.
