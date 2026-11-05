Perfect. I've completed the verification. Let me document my findings.

## Verification Summary

I have verified the standing implementation for work order wo-gh-12. All components are correct and the full test suite passes.

### Verification Results

**Test Suite**: ✅ All 319 tests pass (1 skipped)

**Pipeline Validation**: ✅ All 8 pipelines are valid JSON

**Implementation Verification**:

1. **reviewer-ux Station** (S1):
   - `stations/reviewer-ux/station.json`: Correct agent kind, review output format, guided design designation
   - `stations/reviewer-ux/PROMPT.md`: Contract compliance verified - no JSON examples, canonical Output Format structure only, covers four judgment areas (flows, heuristics, accessibility, copy), explicitly excludes visual system compliance, addresses S5 no-screenshots scenario

2. **Pipeline Composition** (S2):
   - `pipelines/sdlc-default.json`: reviewer-ux present (line 26)
   - `pipelines/content-default.json`: reviewer-ux present (line 9)
   - `pipelines/content-short.json`: reviewer-ux present (line 7)

3. **Routing Surface Rule** (S2, S3):
   - `anvil/routing.py`: Surface rule correctly implemented
   - reviewer-ux in full_panel_reviewers (lines 115-116)
   - Routes in when UI surface present (lines 282-289, 351-356)
   - Routes out with reason "Routed out: no UI surface" when no UI surface (lines 357-369)

4. **Test Fixtures**:
   - `tests/test_risk_routing.py`: Null risk fixture correctly describes non-UI work (surfaces: ["api"])
   - `tests/test_supervisor.py`: REVIEWERS constant includes reviewer-ux
   - `tests/test_reviewer_ux.py`: S5 test properly simulates no-screenshots scenario
   - `tests/test_anvil.py`: test_registry_s6 correctly expects 27 stations including reviewer-ux

**No defects found.** The implementation is complete and correct. Ready for reviewer judgment.
