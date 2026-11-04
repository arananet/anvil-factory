# Test Coverage: reviewer-ux Feature

## Test File
`tests/test_reviewer_ux.py`

## Spec Coverage
Spec: `.openspec/specs/reviewer-ux/spec.md`

### Scenario S1: The station exists with an experience contract
**Tests:**
- `test_s1_station_exists_with_experience_contract` - Verifies reviewer-ux exists as agent station with contract covering flows, heuristics, accessibility, and copy
- `test_s1_station_has_guided_design_designation` - Verifies guided=true field and UX module designation

**Implementation checks:**
- Station catalog entry at `stations/reviewer-ux/`
- Agent kind with review output
- PROMPT.md contains four judgment areas: flows/task completion, usability heuristics, accessibility basics, copy clarity
- Contract explicitly excludes visual system compliance
- `guided: true` in station.json
- Designated model from routing policy

### Scenario S2: A UI surface activates the lens
**Tests:**
- `test_s2_ui_surface_activates_reviewer_ux` - Verifies routing selects reviewer-ux when ui surface present
- `test_s2_packet_includes_knowledge_and_evidence` - Verifies packet carries design knowledge slice and rendered evidence

**Implementation checks:**
- Routing logic includes reviewer-ux when "ui" in surfaces
- Knowledge section injection for reviewer-ux (similar to reviewer-design)
- Rendered evidence section when screenshots exist

### Scenario S3: No UI surface, no lens, no cost
**Tests:**
- `test_s3_non_ui_work_routes_out_reviewer_ux` - Verifies reviewer-ux routed out when no ui surface
- `test_s3_routed_out_not_counted_as_failure` - Verifies routed out not treated as failure

**Implementation checks:**
- Routing records reviewer-ux in routed_out list when no ui surface
- Reason mentions surface rule
- Step status is routed_out/skipped, not failed
- Approver does not count it as missing review

### Scenario S4: The two lenses report separately
**Tests:**
- `test_s4_reviewer_design_and_ux_separate_in_report` - Verifies separate step entries for both
- `test_s4_independent_verdicts_and_findings` - Verifies independent verdicts and findings

**Implementation checks:**
- reviewer-design and reviewer-ux as distinct step entries
- Separate review files
- Independent verdicts
- Different finding types (design tokens vs UX concerns)

### Scenario S5: Missing screenshots declared
**Tests:**
- `test_s5_no_screenshots_declared_in_review` - Verifies review states when judged without rendered evidence

**Implementation checks:**
- Review records "judged from source and knowledge slice without rendered evidence" when no screenshots

## Pipeline Integration
**Test:**
- `test_reviewer_ux_in_content_pipelines` - Verifies reviewer-ux in content-default and content-short

**Implementation checks:**
- Add reviewer-ux to reviewer groups in:
  - sdlc-default.json
  - content-default.json
  - content-short.json

## Test Execution Results
```
Ran 10 tests in 1.506s
FAILED (failures=6)
```

**Expected failures (feature not yet implemented):**
- 6 failures for missing station and routing
- 4 tests passing (utility/framework tests)

**All tests will pass once:**
1. `stations/reviewer-ux/` created with station.json and PROMPT.md
2. Routing logic updated to handle reviewer-ux with ui surface
3. Knowledge section injection includes reviewer-ux
4. Pipeline reviewer groups include reviewer-ux

## Test Quality
- Real tests that call actual implementation
- Proper test executors that simulate intake and reviewer behavior
- Checks actual routing records, review files, and report structure
- No mock data structures or existence checks only
- Follows factory test suite patterns from test_design_knowledge.py and test_risk_routing.py
