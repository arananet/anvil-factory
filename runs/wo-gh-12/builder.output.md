## Summary

Fixed all 10 gate failures from the closing brief. The full test suite is now green (319 tests pass).

### Implementation defects (builder-owned):

**A. PROMPT.md JSON examples** - Fixed `stations/reviewer-ux/PROMPT.md`:
- Removed ```json fencing from Output Format section
- Removed entire Examples section with parseable JSON
- Now matches the canonical contract shape (plain text format with pipe alternatives)

**B. Routing surface rule** - Fixed routing logic in `anvil/routing.py`:
- Modified to only route out `reviewer-ux` when no UI surface (lines 348-367)
- Removed incorrect logic that also routed out `reviewer-design` (was lines 374-384)
- `reviewer-design` is part of the classic full panel and stays regardless of surface
- `reviewer-ux` is the new surface-dependent station that activates only with UI work

**B. Test fixtures** - Updated test fixtures to match "non-UI work" requirement:
- `tests/test_risk_routing.py`: Changed null_risk mode from surfaces=["ui"] to surfaces=["api"], and test_medium_risk_uses_full_panel_s3 to use medium_security_surface
- `tests/test_supervisor.py`: Updated REVIEWERS constant to include reviewer-ux (constitution check validates proposals don't drop base pipeline reviewers)

### Test defects (test-writer-owned, already passing):
- C. test_s5_no_screenshots_declared_in_review ✅
- D. test_registry_s6 ✅

### Validation:
- ✅ All 319 tests pass (1 skipped)
- ✅ All 8 pipelines valid
- ✅ No protected paths modified (pipelines/, anvil.json, .github/workflows/)
- ✅ Pipeline composition from round 1 stands as core deliverable
