# Intake Outcomes Test Map

This document maps test cases to spec scenarios from `.openspec/specs/intake-outcomes/spec.md`.

## Scenario S1: Harmful work is rejected at the door with reasons

**Test**: `TestIntakeRejection.test_rejected_work_stops_pipeline_with_reasons_s1`

Verifies:
- Intake executes and produces rejected outcome
- Work order status becomes "rejected"
- Runner stops after intake (no spec-writer, test-writer, or builder executes)
- Reasons are recorded on work order
- Rejection appears in report.md with reasons
- Swimlane shows rejection

**Implementation**:
- `anvil/model.py`: WorkOrder gains `intake_outcome` field
- `anvil/runner.py`: Parses intake output, updates work order status, stops pipeline on rejection
- `anvil/runner.py`: Renders rejection in report.md and swimlane.md

## Scenario S2: Oversized work is rescoped with the cut recorded

**Test**: `TestIntakeRescope.test_rescoped_work_carries_new_description_downstream_s2`

Verifies:
- Intake executes and produces rescoped outcome
- Work order has rescoped_description in intake_outcome
- Reasons for the cut are recorded
- Downstream packets carry rescoped description

**Implementation**:
- `anvil/model.py`: WorkOrder.intake_outcome includes rescoped_description and reasons
- `anvil/runner.py`: `_packet_text()` uses rescoped_description for downstream stations

## Scenario S3: Unjudgeable work is parked until the requester answers

**Tests**: 
- `TestIntakeWaitingInfo.test_waiting_info_parks_work_with_questions_s3`
- `TestIntakeOutcomeWorkflow.test_waiting_work_can_resume_after_answers_s3`

Verifies:
- Intake produces waiting_info outcome with questions
- Work order status becomes "waiting_info"
- Runner stops after intake
- Report shows waiting state (not passed or failed)
- After answers provided and status returns to runnable, new run can proceed

**Implementation**:
- `anvil/runner.py`: Stops pipeline when outcome is waiting_info
- `anvil/runner.py`: Renders waiting state in report.md without approval/rejection claims

## Scenario S4: Accepted work carries a risk rating and surfaces

**Tests**:
- `TestIntakeRiskAndSurfaces.test_accepted_work_carries_risk_and_surfaces_s4`
- `TestIntakeRiskAndSurfaces.test_low_risk_accepted_work_s4`

Verifies:
- Accepted work order has risk field (low/medium/high)
- Accepted work order has surfaces list
- Risk and surfaces appear in report

**Implementation**:
- `anvil/model.py`: WorkOrder gains `risk` and `surfaces` fields
- `anvil/runner.py`: Parses risk and surfaces from intake output
- `anvil/runner.py`: Renders risk and surfaces in report.md

## Scenario S5: States render honestly in the report and the swimlane

**Tests**:
- `TestIntakeHonestRendering.test_rejected_run_renders_honestly_s5`
- `TestIntakeHonestRendering.test_waiting_run_renders_honestly_s5`

Verifies:
- Rejected run shows reasons, no downstream stations as executed, not claimed as approved
- Waiting run shows questions, no downstream stations as executed, not claimed as passed/failed
- Swimlane shows rejection/waiting status

**Implementation**:
- `anvil/runner.py`: report.md and swimlane.md render terminal outcomes honestly
- `anvil/runner.py`: Pipeline stops after intake for terminal outcomes, so no downstream stations execute

## Station Contract

**File**: `stations/intake/PROMPT.md`

Documents:
- All four outcomes (accepted, rejected, rescoped, waiting_info)
- Refusal class (harmful, deceptive, unlawful)
- Rescope discipline (cut recorded, never silent)
- Risk ratings (high: payments/credentials/data deletion/production deploys, medium, low: small reversible changes)
- Surfaces vocabulary (ui, security, data, payments, deploy, content, api)
- Output format (JSON with intake_outcome, risk, surfaces)

## Test Executor Mock

The test suite includes `INTAKE_OUTCOMES_EXECUTOR` which simulates intake station outputs for different outcome modes:
- `reject`: S1 rejection scenario
- `rescope`: S2 rescope scenario
- `waiting_info`: S3 waiting scenario
- `accept_high_risk`: S4 high risk acceptance
- `accept` (default): S4 low risk acceptance
