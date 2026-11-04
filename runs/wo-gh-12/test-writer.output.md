## Summary

I've written comprehensive tests for the reviewer-ux feature covering all five scenarios from the spec:

### Test File Created
**`tests/test_reviewer_ux.py`** - 10 test cases covering:

**S1: Station exists with experience contract**
- Verifies reviewer-ux station catalog entry
- Checks contract covers flows, usability heuristics, accessibility, copy clarity
- Validates guided design station designation

**S2: UI surface activates the lens**
- Tests routing selection when ui surface present
- Verifies packet includes design knowledge slice and rendered evidence

**S3: No UI surface, no lens, no cost**
- Tests reviewer-ux routed out when no ui surface
- Verifies routed out not counted as failure

**S4: Two lenses report separately**
- Tests reviewer-design and reviewer-ux as separate step entries
- Verifies independent verdicts and findings

**S5: Missing screenshots declared**
- Tests review states when judged without rendered evidence

### Test Results
```
Ran 10 tests in 1.506s
FAILED (failures=6)
```

The 6 failures are **expected** - they correctly detect that the reviewer-ux station doesn't exist yet and routing logic hasn't been implemented. These tests will pass once the builder implements the feature per the spec.

### Test Quality
- Real tests that call actual implementations (not just data structure checks)
- Follow factory suite patterns from test_design_knowledge.py and test_risk_routing.py
- Include proper test executors simulating intake and reviewer behavior
- Check actual routing records, review files, and report structure
- Cover both positive cases (ui surface) and negative cases (no ui surface)

The tests are production-ready and properly validate all spec scenarios.
