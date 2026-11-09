# Station Artifact Contract

Status: approved
Slug: station-artifact-contract

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
A station's contract with the line is a file: the builder writes a report, a reviewer writes its review JSON. The runner, however, has been accepting the station channel's conversational output as the station result. On the runtimes whose channel returns prose or nothing, that produces three observed failures: a reviewer's review is written but the station is marked failed and its vote silently dropped; the builder's chat summary lands in the run tree as if it were the builder report, false claims included; and the approver approves on the remaining votes without naming the missing ones. This spec makes the artifact the result, validates artifacts deterministically before any reviewer is paid for, and makes the approver honest about uncounted stations. The defect record with run ids and exact failure strings lives in issue 37.

## Requirements
- A station's result is the artifact file or files named in its packet, read back from the run tree after the station finishes. Conversational stdout from the station channel is diagnostic text only; it is never accepted as, or substituted for, the artifact.
- When a station produced its artifact, the run record names the real executed model for that station. executed_model is null only when no model ran.
- If a station's artifact is missing, empty, or fails its shape check, the station fails fast: the failure and its reason are recorded in report.json (station, expected artifact, observed state, executed model when one ran), and the run proceeds under the approver rules below rather than discovering the loss at aggregation time.
- A reviewer writing working files outside its review file (for example an .output.md beside it) does not by itself destroy the review: the harness still collects the review artifact. If the review artifact itself is absent or unparseable, the station fails with the scope or parse reason recorded in report.json, in place of an executor exit code surfacing as silence.
- The checks gate gains a deterministic artifact validation step that runs after the builder station and before any reviewer station is spawned. It verifies that the builder report artifact exists and is non-empty, and that every literal the work order declares as required in the builder report (for example a sha256 pin, a blob id, or test totals) appears in it in full, unabbreviated. A failed validation returns the work to the builder station with the validation log attached, consumes a loopback like a gate failure does today, and no reviewer station is spawned for that attempt.
- The same validation family checks reviewer artifacts as they are collected: each expected review JSON exists and parses before the approver aggregates.
- Approver honesty: when a pipeline expects a reviewer station and that station failed, produced no countable artifact, or was routed out after being expected, the approver cannot return a silent approved. The verdict becomes human_required (or changes_requested) and the decision text in report.json names the uncounted stations and the reason each was not counted.
- The contract is implemented in the spine (the runner, the checks gate, the approver) so it holds for every pipeline and every station runtime, without editing pipeline definition files and without special-casing a model brand or a channel.

## Scenarios
- S1 Station result = artifact: given a station whose channel returns prose but writes the artifact named in its packet, the station result is the artifact's content, and report.json records the real executed model. Given a station whose artifact is missing, empty, or fails its shape check, the station is recorded failed fast with the reason in report.json.
- S2 Deterministic artifact validation before reviewer spend: given a work order that declares required literals for the builder report, when the builder artifact lacks one of them in full (including the case where it appears abbreviated), the checks gate validation fails, the work returns to the builder, and no reviewer station runs for that attempt. Given a builder artifact containing every required literal in full, validation passes and the line proceeds.
- S3 Approver honesty: given a run where an expected reviewer was not counted, the approver verdict is human_required or changes_requested, never a silent approved, and the decision text names the uncounted station and why it was not counted. Given a run where every expected reviewer was counted, the approver behaves exactly as before.
- S4 Regression fixtures for the three observed modes: (a) a reviewer channel returning empty captured output while a valid review JSON was written is counted, or fails loudly per S1 and S3, and is never silently dropped; (b) a reviewer that also writes an extra .output.md outside its review file still has its review collected, or the station fails with the scope reason recorded in report.json; (c) a builder channel returning a first-person chat summary lacking a required literal is bounced by the S2 validation deterministically, before any reviewer runs.
- S5 No regressions: the factory's existing test suite stays green, existing pipelines run unchanged, and counted-review behavior for healthy stations is identical to before this change.
