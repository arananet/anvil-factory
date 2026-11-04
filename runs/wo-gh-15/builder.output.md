## Summary

Implementation of S7 same-subject test duty is complete. All changes align with the gate loopback round 4 scope.

### Changes Made

**1. Station Contract Documentation** (`stations/reviewer-design/PROMPT.md`)
- Added note that Quality Charter section may include additional duties beyond standard criteria comparison
- Avoids static documentation that would appear in all packets

**2. Dynamic Duty Injection** (`anvil/quality.py`)
- Enhanced `packet_quality_charter_section()` to inject same-subject test duty when both `identity_reference` AND `deliverable_set` are declared in work order
- Injection includes:
  - Identity reference path
  - Enumerated identity traits to verify
  - Step-by-step duty instructions
  - Requirement to record findings in quality section
- Only applies to reviewing stations (reviewer-design, reviewer-ux)
- Only appears on visual runs with complete set declarations

**3. Test Coverage** (`tests/test_quality_same_subject.py` - new file)
- 5 comprehensive tests proving duty injection works correctly:
  - ✅ Duty present when both fields declared
  - ✅ Duty absent when neither field declared
  - ✅ Duty absent with only identity_reference
  - ✅ Duty absent with only deliverable_set
  - ✅ Duty references identity traits when declared

### Verification

- **Full test suite**: 393 tests pass (100% green)
- **New test suite**: 5/5 tests pass
- **No protected files modified**: test_quality_same_subject.py is a new untracked file
- **No changes to**: review parsing contract, dual-section structure, or unrelated behaviors

The same-subject test duty now travels with packets exactly when needed, providing reviewers with complete instructions to verify identity consistency across deliverable sets.
