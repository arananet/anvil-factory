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

- id: wo-gh-39
- kind: feature
- title: Configurable per-station timeout: the hardcoded 1500s station cap becomes project configuration with a 3600s producing default and honest timeout records
- source: github-issue
- description: Implement the spec in .openspec/specs/station-timeout/spec.md. Pipeline for this order is sdlc-default, selected by the run workflow.

ROOT CAUSE (operator located; the line must verify it and record the verification in the builder report):
At factory main 93ae03fc the 1500s cap lived as a module level constant TIMEOUT_SECONDS = 1500 in both station wrappers: tools/claude_station.py line 61 and tools/codex_station.py line 51, hardcoded, with no environment or configuration override anywhere in the repo. The codex wrapper killed its child at that value and printed "codex_station: station <id> timed out after 1500s", the verbatim reason recorded in the C64 wo-gh-3 run report.
At current factory main a011c14 the codex wrapper is gone (removed in 4c40ea3, decision 0008, one station runtime) and the same constant survives in the one remaining wrapper: tools/claude_station.py line 63, TIMEOUT_SECONDS = 1500, used as the subprocess timeout and in the message "claude_station: station <id> timed out after 1500s". Still no override exists. Two neighbouring layers do not save a long station and must be coordinated by the fix: the command executor timeout (anvil/executor.py, config timeout_seconds, default 300; the factory anvil.yaml sets runtime.timeout_seconds to 1800, which would become the binding cap the moment the station cap rises above it), and the anvil-line.yml job timeout of 180 minutes.
Evidence trail of the defect: Mochi Paint wo-gh-1 era, test-writer and builder killed at 1500s after deliverables were already on disk; Mochi Paint wo-gh-3 run 43123553143, builder killed before its report, gate no_reviews; Mochi Paint wo-gh-4 run 43130769702, builder killed a fourth time; C64 wo-gh-3 run 43589402657, builder via the codex wrapper, "station builder timed out after 1500s", duration 1,500,238 ms, executed_model null, usage unmeasured, after building the whole product. A killed station records executed_model null and usage unmeasured. Project side mitigation does not reach the cap: the C64 filing raised the job timeout to 240 minutes and the per station cap did not move.

BUILD, per the spec scenarios:
S1 Diagnosis recorded: the builder report states where the cap lived in both historical wrappers and where it lives now, with file and line, verified against the tree at the run base.
S2 Configurable per station timeout, following the factory existing configuration patterns (anvil.yaml values handed to the wrapper through the environment by the executor, like ANVIL_MAX_RUNTIME_TURNS and ANVIL_RUNTIME): the environment override is named ANVIL_STATION_TIMEOUT_SECONDS and wins over project configuration in anvil.yaml, which wins over the class default. Producing stations (the wrapper WRITE_STATIONS set: builder, test-writer, spec-writer, blueprint, brief-writer, researcher, writer, media-producer) default to at least 3600 seconds. Other stations keep a default of at least 1500 seconds. A hard ceiling of 7200 seconds remains: a configured value above the ceiling is clamped to 7200 or rejected with the ceiling named, so a runaway station still dies. The executor layer is coordinated: the effective command executor timeout is never lower than the largest station timeout in effect, and the factory anvil.yaml runtime.timeout_seconds is updated to prove it. The anvil-line.yml job timeout is raised to 360 minutes so one long producing station plus the rest of the pipeline fits in one job.
S3 Honest timeout records: a station killed by the timeout still records what is knowable in the run record and usage artifact: the station id, the elapsed milliseconds measured, the configured timeout value as the recorded reason, the model that was dispatched, and partial usage when the runtime exposes it (the TimeoutExpired stdout path). Not nulls across the record: executed_model for a timed out station names the model that ran with status timed_out.
S4 Regression evidence: the full factory test suite green, plus NEW test files under tests/ proving the mechanism deterministically at scaled values: (a) a producing station whose work runs past a scaled old cap (for example work of 2 seconds against a scaled legacy cap of 1 second) completes under the new configuration and is counted; (b) a station exceeding its configured cap still dies and the timeout is recorded with elapsed, timeout value and status; (c) configuration resolution: producing default 3600, environment override wins over project config, values above the 7200 ceiling are clamped or rejected. Scaled mechanism tests are the evidence form for the past cap completion; no live run past 1500 seconds is claimed.
S5 Decision and docs: a new record brain/decisions/0011-station-timeout.md capturing the change, CHANGELOG.md updated, and every factory doc that states the old cap or the timeout behaviour (docs/EXECUTION.md at minimum) updated to the configurable behaviour.

BUILDER REPORT REQUIRED LITERALS: the builder report (runs/wo-gh-39/builder.output.md) must contain each of these in full, unabbreviated: ANVIL_STATION_TIMEOUT_SECONDS, 3600, 7200, station-timeout. It must also state the verified root cause with file and line, the configuration keys and defaults per station class, the ceiling behaviour, the timeout record fields, the exact form of the regression evidence (scaled mechanism tests), and the full factory test count from the suite run.

GUARDRAILS: implement in the wrapper and spine (tools/claude_station.py, tools/dispatch_station.py if needed, anvil/executor.py, anvil/runner.py, anvil/telemetry.py, anvil/config.py as needed) plus anvil.yaml, .github/workflows/anvil-line.yml, docs, CHANGELOG.md and the new decision record. Pipeline files under pipelines/ are protected paths in anvil.json; the fix must hold without editing them. anvil.json itself is protected; do not edit it. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. Python standard library only, no new dependency. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/39


GitHub issue: https://github.com/arananet/anvil-factory/issues/39
- risk_hints: 
- status: new

## Upstream steps

- (none)
