The spec file already exists and is complete at `.openspec/specs/status-lifecycle-stages/spec.md`.

I've verified that the spec covers all five scenarios from the work order:

- **S1**: Stage derivation from run evidence → Scenario 1 "Stages derive from the run report's evidence"
- **S2**: MERGED only from merge records → Scenario 2 "Approved is not merged"
- **S3**: NEEDS HUMAN from decision flag → Scenario 3 "Needs human comes from the decision object"
- **S4**: Intake states (PARKED/REJECTED) → Scenario 4 "Intake states compose with the stage model"
- **S5**: Board layout and rendering → Scenario 5 "One row per job, progression in the row, swimlane one click away"

The spec includes:
- Clear purpose statement explaining why lifecycle stages are needed
- Comprehensive requirements covering stage vocabulary, evidence-based derivation, presentation rules, and implementation scope
- Five concrete scenarios matching the work order requirements
- Status marked as "approved"

**Output:** `.openspec/specs/status-lifecycle-stages/spec.md` (already in repository, committed in 826cc26)

The spec-writer deliverable is complete and ready for the next station.
