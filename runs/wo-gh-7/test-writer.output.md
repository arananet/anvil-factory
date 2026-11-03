## Test-writer station output complete

I've written comprehensive tests for the intake outcomes feature in `/home/runner/work/anvil-factory/anvil-factory/tests/test_intake_outcomes.py`.

### Test Coverage (9 tests covering all 5 spec scenarios):

**S1 - Rejection:** `test_rejected_work_stops_pipeline_with_reasons_s1`
- Verifies rejected work stops the pipeline, records reasons, updates status, and renders honestly

**S2 - Rescoping:** `test_rescoped_work_carries_new_description_downstream_s2`
- Verifies rescoped description carries downstream with recorded cuts and reasons

**S3 - Waiting for info:** 
- `test_waiting_info_parks_work_with_questions_s3` - verifies parking with questions
- `test_waiting_work_can_resume_after_answers_s3` - verifies resume workflow

**S4 - Risk & surfaces:**
- `test_accepted_work_carries_risk_and_surfaces_s4` - high risk, multiple surfaces
- `test_low_risk_accepted_work_s4` - low risk, single surface

**S5 - Honest rendering:**
- `test_rejected_run_renders_honestly_s5` - rejected runs render truthfully
- `test_waiting_run_renders_honestly_s5` - waiting runs show questions, not pass/fail

### Files created:
1. `tests/test_intake_outcomes.py` - Test suite (370 lines)
2. `tests/test_intake_outcomes_map.md` - Documentation mapping tests to spec scenarios

The tests follow the factory's existing patterns and use a fake executor to simulate intake outcomes. They will fail until the implementation is built (expected TDD workflow).
