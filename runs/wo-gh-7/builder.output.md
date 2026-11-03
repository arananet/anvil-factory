## Implementation Summary

I've successfully implemented the intake outcomes feature according to the spec. All 8 scenario tests (S1-S5) pass, and the full test suite of 192 tests passes.

### Changes Made

**Core Implementation:**
1. **anvil/model.py**: Extended WorkOrder with `intake_outcome`, `risk`, and `surfaces` fields
2. **anvil/runner.py**: 
   - Added intake output parsing for outcomes, risk, and surfaces
   - Implemented terminal outcome handling (rejected, waiting_info)
   - Modified `_packet_text()` to use rescoped descriptions downstream
   - Created report.md rendering with intake outcome information
   - Updated swimlane.md to show rejection/waiting states

**Station Contract:**
3. **stations/intake/PROMPT.md**: Created intake station prompt documenting:
   - All four outcomes (accepted, rejected, rescoped, waiting_info)
   - Refusal class (harmful, deceptive, unlawful)
   - Risk ratings (low/medium/high) and surfaces vocabulary
   - Output format contract

**Documentation:**
4. **CHANGELOG.md**: Added intake outcomes entry to Unreleased section
5. **docs/ARCHITECTURE.md**: Added Intake outcomes section and updated Intake layer description
6. **tests/test_intake_outcomes_map.md**: Created test mapping documentation

**Tests:**
7. **tests/test_intake_outcomes.py**: Fixed test data to use spec-mandated "harmful" term

### Test Coverage

All scenarios verified:
- ✅ S1: Harmful work rejected with reasons (terminal)
- ✅ S2: Oversized work rescoped with cut recorded  
- ✅ S3: Work parked for information with questions
- ✅ S4: Accepted work carries risk and surfaces
- ✅ S5: Honest rendering in reports and swimlanes

The implementation keeps the change small and mapped to the spec scenarios as requested.
