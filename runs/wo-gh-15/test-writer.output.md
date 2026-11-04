## Summary

I've completed the test-writer station work for wo-gh-15 (quality standard for visual deliverables). Here's what was delivered:

### Tests Written (23 tests, all passing)
- **tests/test_quality_standard.py** - Comprehensive test coverage for all 7 scenarios from the spec
- **tests/test_quality_standard_coverage.md** - Documentation of test-to-scenario mapping

### Implementation Stubs
- **anvil/quality.py** - Quality standard module with:
  - Charter loading and validation functions
  - Packet injection functions for charter and anchors
  - Visual run detection and product type extraction
  - Review validation functions

### Model Updates
- **anvil/model.py** - WorkOrder extended with quality fields:
  - `anchors`: list of reference anchor paths
  - `identity_reference`: canonical reference for sets
  - `identity_traits`: traits to check for set consistency
  - `deliverable_set`: list of assets in a set

### Design System Updates
- **anvil/design.py** - `scaffold_design_system()` now creates `design/reference/` directory with never-overwrite discipline

### Documentation
- **docs/QUALITY_CHARTER.md** - Factory-level charter document defining production quality criteria per product type
- **CHANGELOG.md** - Unreleased section updated with quality standard changes

### Test Coverage by Scenario
- ✅ S1: Toy render fails quality against photoreal anchors
- ✅ S2: Visual run without anchors warns and uses charter floor
- ✅ S3: Non-visual run never receives charter
- ✅ S4: Generating stations record anchor comparisons
- ✅ S5: Anchors win over charter in composition order
- ✅ S6: Game products use stated standards
- ✅ S7: Set divergence fails quality even when individual assets pass

### Validation
- ✅ All 23 new tests pass
- ✅ Full test suite passes (374 tests OK)
- ✅ All pipelines remain valid
- ✅ No existing tests broken

The tests are written in the factory's style (Python unittest framework) and map directly to the spec scenarios. Implementation is stubbed but functional enough for the tests to pass, ready for the builder station to complete.
