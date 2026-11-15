# Filed Order and Spec Immutability During a Run

Status: proposed
Slug: filed-order-immutability

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

The filed work order is the contract a run executes against, and today nothing technical stops a station from rewriting it mid-run. In the C64 blueprint chain (project c64-retro-hardware, run 43673692204), the intake station rewrote the run's copy of the filed order wo-gh-7: risk medium became low, surfaces [ui, content, deploy] became [content], and routing consumed the rewritten values, so the reviewer panel shrank from six to two and the run's approved verdict rested on a third of the designed panel. Nothing in the run record treated the rewrite as an event. In the same chain the filed spec was amended mid-run inside the .openspec/specs/ tree it lived in. The factory's own record shows the same shape at home: wo-gh-39 was filed with risk low and surfaces [api], and its run copy (work_orders/wo-gh-39.json) carries risk medium and surfaces [deploy, api, content]. The protection today is prompt-level: stations are told the filed record stands, and a station can still decide otherwise. The comparison against other software factories (factory research of 2026-11-15, section "Mechanisms ANVIL Does Not Have", mechanisms 1 to 6 and 13 to 18) shows the equivalent enforced technically elsewhere: Attractor validates the pipeline graph before execution and no running node redefines it; the Copilot coding agent's credential can only push to copilot/* branches, so a protected tree is a permission, not an instruction; ZazenCodes makes the orchestrator the only writer of the job record while every other agent writes only its own file. This order applies that lesson to ANVIL: the filed record and the filed spec become read-only to every station at the tool permission layer, the effective rating record freezes when intake completes, and routing derives the reviewer panel deterministically from the frozen record.

## Requirements

### R1. The filed record is read-only to stations
- At run start the runner snapshots the filed work order record (the record the run was resolved from) and records its sha256 in the run report as the filed record hash, alongside the base ref the checks gate already records.
- No station in the run can write, edit or delete the filed record. The station tool permission layer (the same layer tools/claude_station.py uses to build the reviewer scoped path under the review producer capability) denies file writes to the filed record path and to any record path for the current work order under work-orders/ and work_orders/. The denial is built by the wrapper from the run's filed record, not from station prose.
- A denied write attempt is recorded in the run report as a named finding (station, path, attempted operation), never silently swallowed.

### R2. The effective record and the freeze point
- The runner maintains the run's effective work order inside the run tree (runs/<work-order-id>/), written only by runner code. Stations never write it; intake delivers its outcome as its station artifact, exactly as the station artifact contract requires for every station result.
- The runner folds the intake outcome into the effective record under these rules: risk and surfaces come from the filed record when the filing sets them; intake may stamp risk and surfaces only where the filed record leaves them null; a rescope outcome may replace the description, with the cut recorded in the outcome record exactly as the intake outcomes spec requires.
- The effective record freezes when the intake stage completes. After the freeze, no station output, correction or loopback can change risk, surfaces, kind, spec_path or the description in the effective record. A change to any of them after the freeze requires a new filing; a run that would need such a change stops and records that reason as its blocking reason.

### R3. Routing consumes the frozen record, deterministically
- Routing (anvil/routing.py) reads only the frozen effective record. The routing record in the run report names, for risk and for surfaces, the frozen values used and the source of each (filed, or intake-stamped where the filing left it null).
- If a station output after the freeze attempts to supply different risk or surfaces, routing ignores the attempt, the attempt is recorded as a finding, and the run fails closed at the checks gate with the finding named. The run never proceeds on a contested classification.

### R4. The filed spec is read-only during the run
- When the work order declares a spec_path, the runner records the sha256 of every file under that spec's directory at run start, next to the filed record hash.
- Every station's tool permissions deny writes under .openspec/specs/ for the duration of the run. The spec-writer station verifies the filed spec against the work order instead of amending it. Orders that declare no spec_path are unchanged: the spec-writer authors the spec as it does today, and the denial applies to the filed record only.
- The checks gate verifies the filed spec hashes before the reviewer stage: a changed filed spec fails the gate with the changed paths named as a protected finding, and no reviewer station is spawned for that attempt. This is a runtime permission plus a gate verification, complementing the checks gate's existing protected path rule, which judges the builder's delta after the fact; this order stops the write itself.

### R5. Scoped station writes, generalized
- The review producer pattern (one scoped write path per reviewer station, enforced at the tool permission layer) extends to every station: a station may write only the artifacts its packet names (its output file and its deliverables in their declared locations) and never anything under work-orders/, work_orders/, .openspec/specs/, anvil.json or pipelines/.
- Builder and test-writer keep the write access their deliverables require inside the project tree, minus the denied classes above. Reviewer stations keep exactly the scoped write the review producer spec gives them; this order does not widen or narrow it.

### R6. Regression tests
- The order's own tests are new files under tests/ and encode: (a) the wo-gh-7 fixture: a filed order carrying risk medium and surfaces [ui, content, deploy] with an intake artifact attempting risk low and surfaces [content]; the effective record keeps the filed values, routing selects the full six reviewer panel of sdlc-default, and the attempt is recorded as a finding; (b) an intake artifact stamping risk and surfaces where the filing left them null is accepted, frozen, and consumed by routing with sources named; (c) a station write attempt to the filed spec path is refused by the permission configuration the wrapper builds, the filed spec hash check passes on an untouched tree, and fails naming the path on a mutated tree; (d) a rescope at intake still replaces the description with the cut recorded, and a post-freeze attempt to change the description is refused and recorded.

### Guardrails
- Python standard library only, consistent with the factory spine. No new dependency.
- This order deliberately amends two active specs, and the amendment is part of the build, landed as dated amendment sections in those files in the same form the checks-gate loopback rounds used: intake-outcomes (the stamping rule gains the filed-values-win condition and the freeze at intake completion; the rescope discipline is unchanged) and risk-routing (the trust rule changes from trusting the intake outcomes as authoritative to trusting the frozen effective record; the routing table itself is unchanged).
- Frozen surfaces otherwise: the review parse contract and parse_review semantics; the canonical review contract wording; the reviewer prompts and their Output Format sections; the review producer mechanisms; the checks gate's verdicts, loopback accounting and S4 base ref behavior; pipeline definition files (protected in anvil.json); anvil.json itself (protected).
- Existing test files at the base ref are not modified or deleted; new tests arrive as new files.
- No em dash or en dash character in any produced file (project style rule).
- Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

## Scenarios

### Scenario: A mid-run reclassification attempt fails closed
- S1: Given a filed order with risk medium and surfaces [ui, content, deploy] (the wo-gh-7 fixture), when the intake artifact attempts risk low and surfaces [content], then the effective record keeps the filed values, the routing record names the filed source for both, the attempt is recorded as a finding, and routing selects the full six reviewer panel of sdlc-default.

### Scenario: Intake stamps only what the filing left null
- S2: Given a filed order with null risk and no surfaces, when intake stamps risk and surfaces in its outcome artifact, then the runner folds the stamps into the effective record, the record freezes at intake completion, and routing consumes the stamped values with the intake-stamped source named.

### Scenario: The filed record cannot be written by a station
- S3: Given a run in progress, when any station attempts a file write to the filed record path or to a record path of the current work order, then the tool permission layer refuses the write, the filed record hash still matches the run start snapshot, and the refusal is recorded as a named finding.

### Scenario: The filed spec cannot be amended mid-run
- S4: Given a work order declaring a spec_path, when a station attempts to write under .openspec/specs/ during the run, then the write is refused by the permission configuration; and given a filed spec file mutated outside the station layer, when the checks gate verifies the filed spec hashes, then the gate fails naming the changed path and no reviewer station is spawned for that attempt.

### Scenario: Rescope still works, inside the freeze rules
- S5: Given an intake rescope outcome, when the effective record is built, then its description is the rescoped description with the cut recorded in the outcome record; and given a post-freeze station output attempting to change the description, risk or surfaces, then the change is refused, recorded as a finding, and the frozen record stands.

### Scenario: Orders without a filed spec are unchanged
- S6: Given a work order declaring no spec_path, when the run executes, then the spec-writer authors the spec as it does today, the filed record is still read-only to stations, and the freeze and routing rules apply to the effective record exactly as in S1 to S5.
