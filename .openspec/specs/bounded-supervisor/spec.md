# Bounded Supervisor

Status: approved
Slug: bounded-supervisor

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
Fixed teams stall: the same reviewer keeps failing, loopbacks run out, runs end with no reviews, a deploy lands unverified. A supervisor that watches run reports and reorganizes the line is the known answer, but a supervisor that can invent anything is unauditable. This spec bounds it: the supervisor proposes recompositions built only from the existing station catalog, the proposal must pass the same pipeline validation as any hand written pipeline plus a constitution check, and nothing applies itself. The gates, the risk hints and the triage rules are deterministic code and are not the supervisor's to amend.

## Requirements
- The supervisor is a station in the catalog (stations/supervisor/, agent kind) with a prompt that states its bounds: catalog station ids only, one recomposition per proposal, and gates, risk hints and triage rules are out of bounds. It is not part of any shipped pipeline; it runs between runs, not inside one.
- Stall detection is deterministic code over runs/*/report.json. Signals: a reviewer station with verdict fail in 2 or more runs; the latest run exhausted its loopbacks (loopbacks at or over max_loopbacks); verdict no_reviews in 2 or more of the last 3 runs; the latest run ended deployed_unverified. Each signal carries its kind, a detail sentence and the evidence run ids.
- `anvil supervise <project>` with no signals prints "no stalls detected" and writes nothing.
- With signals, packet mode writes a supervisor packet and a work order (work-orders/supervisor-proposal.json, kind task) whose title names the first signal.
- With `--execute`, the packet goes to the configured runtime like any other station packet. The supervisor answers with one JSON proposal: {"name", "pipeline", "rationale", "addresses"}.
- Proposal validation is deterministic and two layered: the pipeline object must pass the existing pipeline validator against the catalog, and it must pass the constitution: it includes intake, approver and triage-human, and its reviewer station set is a superset of (or equal to) the reviewer set of the pipeline it would replace (the project's default from anvil.json, falling back to sdlc-default).
- An accepted proposal is written to pipelines/proposals/<name>.json with a PROPOSAL.md carrying the rationale, the signal addressed, the evidence run ids, the validation result, and the plain statement that nothing auto applies: a human points anvil.json or a run at the proposal to use it.
- A rejected proposal is written to pipelines/proposals/rejected-<name>.json with a REJECTED.md naming each failed check.

## Scenarios

### Scenario: Stall detection reads the run record
- S1: Given run reports on disk, when stall detection runs, then each present stall (a reviewer failing in 2 or more runs, an exhausted loopback budget on the latest run, no_reviews in 2 or more of the last 3 runs, a latest run deployed_unverified) is returned as a signal with kind, detail and evidence run ids, and absent stalls are not reported.

### Scenario: No stalls means no writes
- S2: Given a project whose run reports show no stall, when supervise runs, then it reports "no stalls detected" and writes no packet, no work order and no proposal.

### Scenario: Packet mode prepares the proposal work
- S3: Given a detected stall, when supervise runs without --execute, then it writes a supervisor packet describing the signals and a work order of kind task whose title names the first signal.

### Scenario: A valid proposal is accepted and filed, not applied
- S4: Given an executed supervisor proposal that passes pipeline validation and the constitution (for example the default line with reviewer order changed and scout added before spec-writer), when supervise validates it, then pipelines/proposals/<name>.json and its PROPOSAL.md exist, the PROPOSAL.md records the rationale, signal, evidence and validation result, and anvil.json is unchanged.

### Scenario: Constitution violations are rejected with reasons
- S5: Given an executed supervisor proposal that drops triage-human, or drops a reviewer the base pipeline has, or names a station outside the catalog, when supervise validates it, then the proposal is written as pipelines/proposals/rejected-<name>.json with a REJECTED.md naming each failed check, and no accepted proposal file is written for it.

### Scenario: The constitution itself is out of bounds
- S6: Given the supervisor station and the supervise command, when their surfaces are inspected, then the prompt states that gates, risk hints and triage rules are code and out of bounds, no code path lets a proposal modify them, and no proposal is ever applied automatically.
