# Task packet: intake

## Station prompt

# Intake Station

## Role

Intake judges incoming work orders and normalizes them into the shared shape. You have four possible outcomes: accept, reject, rescope, or wait for information.

## Outcomes

### Accepted

The work order is buildable as stated. Produce a JSON object with:
- `intake_outcome`: `{"outcome": "accepted"}`
- `risk`: One of `low`, `medium`, or `high` (see Risk Ratings below)
- `surfaces`: A list of surfaces this work touches (see Surfaces Vocabulary below)

### Rejected

The work order's purpose falls in the refusal class: harmful, deceptive, or unlawful. Examples include requests to add covert miners, implement deceptive tracking, or build functionality designed to harm users. Never quietly reformulate refused work into something buildable.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "rejected", "reasons": ["reason 1", "reason 2", ...]}`

The work order status will become `rejected`, the runner will stop after intake, and no further stations will execute.

### Rescoped

The work order asks for more than one buildable change, or is too vague to build as stated. Cut it down to one buildable scope and record what was removed and why.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "rescoped", "rescoped_description": "The buildable scope", "reasons": ["what was cut and why"]}`
- `risk`: Risk rating for the rescoped work
- `surfaces`: Surfaces the rescoped work touches

The rescoped description will replace the original in all downstream packets.

### Waiting for Information

The work order lacks information you need to judge it. Record your questions.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "waiting_info", "questions": ["question 1", "question 2", ...]}`

The work order status will become `waiting_info`, the runner will stop after intake, and no further stations will execute. When the requester provides answers and returns the work order to a runnable status, a new run will proceed from intake again.

## Risk Ratings

- **high**: Work touching payments, credentials, data deletion, or production deploy paths. High blast radius or irreversible changes.
- **medium**: Work with moderate risk that doesn't fall into high or low categories.
- **low**: Small, reversible changes with limited blast radius.

## Surfaces Vocabulary

Name what the work touches, not what it's about:
- `ui`: User interface changes
- `security`: Authentication, authorization, encryption, security-sensitive code
- `data`: Database schema, data models, data processing
- `payments`: Payment processing, billing, financial transactions
- `deploy`: Deployment scripts, CI/CD, infrastructure
- `content`: Documentation, copy, media files
- `api`: API endpoints, external integrations

Use the surfaces that apply. One work order can touch multiple surfaces.

## Output Format

Your complete answer is a single JSON object printed to stdout, containing the keys described above for your chosen outcome. The runner parses this JSON to determine how to proceed.

## Consumption discipline

Read the spec and the relevant upstream artifacts first. Search before opening files; read only the relevant ranges. Bound command output and summarize long test logs with failures and a path to the full log. Run focused checks while editing and the required project checks at handoff. Reuse valid upstream work. Keep the final handoff concise, with changed files, evidence and unresolved issues. Preserve the required output contract.


## Practices

Promoted practices that resolved for this station. Follow each rule.

- P-14 (Cross-order spec conflict detection): Before execution, check a new order's hard assertions (pinned counts, unconditional property pins, exact file sets) against standing contracts from prior orders on the same project; a collision is surfaced in the filing for an owner decision, never discovered by the checks gate mid-run.
- P-15 (Filing completeness for protected surfaces): When an order's substance touches protected paths, packet contents or existing tests, the filing must enumerate the complete authorized write set up front: protected_paths changes, named test adaptations and packet inclusions; an under-authorized filing is returned before the run fires.

## Work order

- id: wo-gh-41
- kind: feature
- title: Continuous run accounting: the run record is checkpointed after every station and completed on every exit path, budget death included
- source: github-issue
- description: Implement the spec in .openspec/specs/continuous-run-accounting/spec.md. Pipeline for this order is sdlc-default (software domain, the factory repo itself), selected by the run workflow.

STAGING: this order is filed and staged only. The spec and this work order record sit on the branch anvil/run-continuous-run-accounting, the issue carries no anvil label, and no run is fired. Execution starts on the owner's word. Run configuration baseline, unchanged by this filing: the order is parented on factory main 4675a131eb9aa88097741dc3cdc9772c3db17550 (the fixed spine merged by wo-gh-39), whose anvil.yaml carries max_run_tokens 6000000, max_runtime_turns 40 and max_packet_tokens 48000, and whose anvil.json wires the checks command (python -m unittest discover -s tests -p 'test_*.py').

EVIDENCE (the defect this order closes):
In the C64 blueprint chain (project c64-retro-hardware), work order wo-gh-6 (run 43668712644) exhausted its budget: the builder's single call measured 6,359,529 cache-inclusive tokens against the 6,000,000 run cap, and the run died with status budget_exceeded before the builder wrote its report. The branch held finished product but no builder report and no complete run record: 0 of 6 reviewers counted, and the run's own accounting did not exist. Work order wo-gh-7 then spent a second run (5,697,863 tokens measured) largely to write the paperwork wo-gh-6 never wrote, the builder report and the comparison records for work that already existed. The comparison against other software factories (factory research of 2026-11-15, report section "Mechanisms ANVIL Does Not Have", mechanisms 7 to 12 for failure mode 2) shows the standard shape elsewhere: mini-SWE-agent saves its trajectory in a finally block after every step and converts limit exceptions into recorded exit outcomes; Attractor checkpoints after every node and resumes from the last checkpoint; OpenHands treats an append-only event log as the run record.

BUILD, per the spec requirements:
R1: the runner writes the run record (runs/<work-order-id>/report.json with its step records) after every station completes, fails or is skipped, in the final report's shape plus a checkpoint field set (last completed station, elapsed milliseconds, measured usage so far). Writes are atomic (sibling temporary file, then rename), so a mid-run read always sees a valid report complete as of the last finished station. Checkpointing adds no station and no model call.
R2: every termination path completes the record before the process exits: normal completion, a verdict, budget exhausted (exit status budget_exceeded), a station timeout (using wo-gh-39's honest timeout records), the runtime turn limit, a checks gate stop, an intake stop, an uncaught exception in spine code, and the trappable external signals (SIGTERM, SIGINT). The completed record names the exit status, the termination reason, every station that ran with its outcome and executed model, every station that never ran as not run, and the cost section under cost-measurement semantics. A budget death is a complete recorded outcome carrying the measured consumption that crossed the cap and the station in flight, with its partial usage when exposed.
R3: inspecting or resuming after a killed run reads the checkpointed record as the run's accounting; tools/line_comment.py and the swimlane render a killed run's record with no station executing. A later run of the same work order preserves the killed run's record in the run history and never overwrites it.
R4: regression tests as new files under tests/, driving scripted runs through the runner with a fake runtime: (a) a run killed at the token cap mid-builder leaves a complete, parseable record (exit status budget_exceeded, per-station outcomes, the builder's measured partial usage, unrun stations named not run); (b) the same completeness holds for a station timeout death and for an injected uncaught error, each with its own exit status and reason; (c) a healthy scripted run checkpoints after each station and its final report equals the last checkpoint plus the verdict sections; (d) SIGTERM leaves a completed record naming the signal.

RECONCILIATION WITH ACTIVE SPECS (read before building; these are decisions, not discoveries for the line to make):
No active spec conflicts. The token-efficiency spec already requires per-attempt usage artifacts and that a budget stop preserves the report; this order generalizes that preservation to every exit path and makes it a runner property, using those artifacts as inputs. Cost-measurement semantics are frozen and reused as they stand (totals are sums of measured steps; unmeasured stays unmeasured with its reason). The station artifact contract's executed model honesty and the station-timeout record fields are inputs, unchanged.

BUILDER REPORT REQUIRED LITERALS: the builder report (runs/wo-gh-41/builder.output.md) must contain each of these in full, unabbreviated: 4675a131eb9aa88097741dc3cdc9772c3db17550, continuous-run-accounting, checkpoint, budget_exceeded. It must also state the base ref it verified the tree against, the exact full factory test count from the suite run, and the names of the new test files added.

GUARDRAILS: authorized surface for this order: anvil/runner.py, anvil/line.py, anvil/telemetry.py, anvil/cost.py, anvil/executor.py, anvil/cli.py (the resume and inspect paths), tools/line_comment.py, anvil/statuspage.py if it reads run reports, the factory docs that describe run reports or resume (docs/EXECUTION.md at minimum), CHANGELOG.md, one new decision record under brain/decisions/, and new test files under tests/. Pipeline files under pipelines/ are protected paths in anvil.json; the fix must hold without editing them. anvil.json itself is protected; do not edit it. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. Frozen: cost-measurement semantics, the station-timeout record fields, the review parse contract, the reviewer prompts. Python standard library only, no new dependency. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/41


GitHub issue: https://github.com/arananet/anvil-factory/issues/41
- risk_hints: 
- status: new

## Upstream steps

- (none)
