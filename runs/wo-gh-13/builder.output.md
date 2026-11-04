## Implementation Complete

I've successfully implemented the status dashboard lifecycle stages feature according to the spec in `.openspec/specs/status-lifecycle-stages/spec.md`. All 9 scenario tests pass, and the entire test suite (328 tests) remains green.

### Changes Made

**1. Core Implementation** (`anvil/statuspage.py`):
- Added `LIFECYCLE_STAGES` constant defining the stage vocabulary
- Implemented `load_merge_records()` to read merge records from `merge_records/` folder
- Implemented `derive_lifecycle_stage()` to extract stages from run report evidence:
  - SPEC from spec-writer step executed
  - BUILD from builder step executed
  - REVIEW from reviewer steps executed
  - APPROVED from approved verdict
  - MERGED from merge records only (never inferred)
  - Handles intake states (PARKED, REJECTED) that replace stage progression
  - Detects NEEDS HUMAN from decision.human_gate.required flag
- Implemented `render_lifecycle_board()` to generate HTML board with one row per work order
- Added comprehensive CSS styles for the board, stages, badges, and intake states
- Modified `render_status_page()` to load merge records and render the lifecycle board

**2. Documentation Updates**:
- `CHANGELOG.md`: Added entry describing the lifecycle stages feature under Unreleased
- `docs/STATUS-PAGE.md`: Added "Lifecycle board" section explaining stage derivation and board layout

### Feature Coverage (All Scenarios Pass)

- **S1**: Stage derivation from evidence ✓
- **S2**: MERGED only from merge records, not approval ✓
- **S3**: NEEDS HUMAN badge from decision flag ✓
- **S4**: Intake states (PARKED/REJECTED) compose with stages ✓
- **S5**: One board, one row per job, reproducible, with links ✓

### Compliance with Work Order Constraints

- ✓ No modifications to `.github/workflows/`
- ✓ No modifications to `tests/`, `anvil.json`, or `pipelines/`
- ✓ All tests call real implementation (derive stages, render board, check HTML output)
- ✓ All 328 existing tests still pass
- ✓ Feature is pure function of run data and merge records (no network calls, no inference)

The lifecycle board is now live in the factory's status page generator and will appear on every generated status page, showing work order progress at a glance.
