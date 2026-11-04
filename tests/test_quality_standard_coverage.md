# Quality Standard Test Coverage

This document maps test coverage to the scenarios in `.openspec/specs/quality-standard/spec.md`.

## Test File
`tests/test_quality_standard.py` - 23 tests covering all 7 scenarios

## Scenario Coverage

### S1: Anchored realism makes a toy render fail the quality judgment
✅ Covered by:
- `ReviewerQualitySectionTests.test_s1_toy_render_fails_quality_against_photoreal_anchor`
  - Validates that toy-like output fails when anchors show photorealism
  - Verifies quality section is separate from compliance section
  - Ensures findings cite specific criteria (materials, light, scale, contact)
- `ReviewerQualitySectionTests.test_quality_section_can_pass_compliance_fail_quality`
  - Confirms a deliverable can pass compliance yet fail quality

### S2: Visual run without anchors applies the floor and warns
✅ Covered by:
- `PacketInjectionTests.test_s2_visual_run_without_anchors_warns`
  - Verifies warning appears when no anchors available
  - Confirms charter criteria are still present
- `PacketInjectionTests.test_s2_visual_run_with_anchors_includes_anchor_section`
  - Validates anchor section when anchors exist

### S3: Non-visual run never receives the charter
✅ Covered by:
- `PacketInjectionTests.test_s3_non_visual_run_never_receives_charter`
  - Confirms no charter in packets for non-visual work
  - Tests API-only work order (no UI surface)

### S4: Generating station records anchor comparison before review
✅ Covered by:
- `GeneratingStationTests.test_s4_generating_station_records_comparison_before_review`
  - Validates self-comparison structure
  - Confirms explicit statement required even when no gaps
- `GeneratingStationTests.test_s4_generating_station_records_gaps`
  - Tests gap recording with criterion and description

### S5: Anchor wins over charter default
✅ Covered by:
- `CompositionOrderTests.test_s5_stylized_anchor_wins_over_charter_realism`
  - Verifies stylized anchors override charter realism criteria
- `CompositionOrderTests.test_s5_floor_gap_is_named`
  - Confirms floor gaps are explicitly named

### S6: Game product judged by stated standard
✅ Covered by:
- `ProductTypeTests.test_s6_game_product_uses_stated_standard`
  - Validates game products use project-stated criteria
  - Confirms photorealism criteria absent for games
- `ProductTypeTests.test_physical_product_gets_realism_criteria`
  - Verifies physical products get realism criteria
- `ProductTypeTests.test_product_type_detection`
  - Tests product type detection from work order

### S7: Set consistency - divergence fails quality
✅ Covered by:
- `SetConsistencyTests.test_s7_set_divergence_fails_quality`
  - Tests assets that pass individually but diverge from each other
  - Validates same-subject test naming divergent asset and trait
- `SetConsistencyTests.test_s7_identity_traits_enumerated`
  - Confirms identity traits are enumerated in work order
- `SetConsistencyTests.test_s7_set_passes_when_consistent`
  - Tests set that passes all consistency checks

## Additional Coverage

### Charter Structure
- `QualityCharterTests.test_charter_exists`
- `QualityCharterTests.test_charter_has_physical_product_criteria`
- `QualityCharterTests.test_charter_has_game_criteria`

### Packet Injection
- `PacketInjectionTests.test_visual_run_receives_charter_in_generating_packets`
- `PacketInjectionTests.test_visual_run_receives_charter_in_reviewer_packets`

### Design System Integration
- `DesignReferenceDirectoryTests.test_design_reference_created_by_scaffold`
- `DesignReferenceDirectoryTests.test_design_reference_never_overwritten`

### Review Validation
- `ReviewerQualitySectionTests.test_quality_section_requires_anchor_citation`

## Test Results
All 23 tests pass. Full suite: 374 tests OK (skipped=1).

## Implementation Files
- `anvil/quality.py` - Quality standard module with charter loading and validation
- `anvil/model.py` - WorkOrder model updated with quality fields
- `anvil/design.py` - Scaffolding updated to create design/reference/
- `docs/QUALITY_CHARTER.md` - Factory-level charter document
- `CHANGELOG.md` - Updated with quality standard changes
