## Implementation Complete

I've successfully implemented the quality standard for visual deliverables per the spec. All 23 tests pass, covering scenarios S1-S7.

### What was built:

**Core Implementation:**
- **anvil/quality.py** (new): Quality standard module with:
  - Charter loading from docs/QUALITY_CHARTER.md
  - Visual run detection (UI/content surfaces)
  - Product type detection (physical_product, game, illustration)
  - Charter section generation for station packets
  - Anchor section generation with warnings when missing
  - Validation functions for generating station comparisons and reviewer quality sections

- **docs/QUALITY_CHARTER.md** (new): Factory-level charter document defining:
  - Observable criteria per product type
  - Materials, light, contact, scale for physical products
  - Stated standard requirement for game/illustration
  - Composition order (anchors → design system → charter floor)
  - Station duties for generating and reviewing
  - Set consistency requirements (amendment 2026-10-30)

**Model Updates:**
- **anvil/model.py**: WorkOrder class gains quality fields:
  - `anchors`: reference image paths
  - `identity_reference`: canonical reference for sets
  - `identity_traits`: traits that must stay consistent
  - `deliverable_set`: list of related deliverables

**Design System:**
- **anvil/design.py**: scaffold_design_system() now creates `design/reference/` directory alongside DESIGN.md and tokens.json, under never-overwrite discipline

**Tests & Documentation:**
- **tests/test_quality_standard.py**: 23 tests covering all scenarios
- **tests/test_quality_standard_coverage.md**: Scenario-to-test mapping
- **CHANGELOG.md**: Comprehensive quality standard entry in Unreleased section

### Test Results:
- ✅ All 374 tests pass (1 skipped)
- ✅ All 23 quality standard tests pass
- ✅ All 7 scenarios (S1-S7) covered
- ✅ All pipelines valid

The implementation follows the spec's requirements: charter criteria are injected only into visual runs, anchors override charter defaults, generating stations self-verify, reviewers maintain separate quality sections, and set consistency is enforced through identity references and enumerated traits.
