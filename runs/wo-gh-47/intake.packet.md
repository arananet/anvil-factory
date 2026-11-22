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

- id: wo-gh-47
- kind: feature
- title: Live progress sinks: a run seen while it runs, on the work order's issue and optionally on a GitHub Projects board
- source: github-issue
- description: Implement the spec in .openspec/specs/live-progress-sinks/spec.md. Pipeline for this order is sdlc-default (software domain, the factory repo itself), selected by the run workflow.

RELEASE (owner decision, 2026-11-22): this order is released for execution. It was filed on 2026-11-21 and staged until wo-gh-42 landed, which it did on 2026-11-22 (merge 6191e8c1f235b4cd248a51203d40177834dc4ae2). Baseline now: factory main 10168fa560af7284b23f99e4e639621cf47eacd2, whose anvil.yaml carries max_run_tokens 15000000, max_runtime_turns 100, max_packet_tokens 48000 and the efficiency station partitions of wo-gh-42, and whose anvil.json wires the checks command (python -m unittest discover -s tests -p 'test_*.py'). First run of this order (45042545362) was stopped in the spec-writer by its token partition, since recalibrated (spec-writer 1200000, builder 5800000); the run branch carries that fix. The exit statuses now on main include runtime_refused; a sink must be able to show any exit status as a final state without knowing the list.

EVIDENCE (the defect this order closes):
A run cannot be watched. state.json is rewritten before every station and report.json is checkpointed after every station (wo-gh-41), but both stay on the disk of the machine that runs the line until the run ends. The five runs of wo-gh-41 on 2026-11-20 and the run of wo-gh-42 on 2026-11-21 each showed only "In progress" for 5 to 27 minutes; the owner asked what the line was doing and nobody could tell from outside. The existing export (observability.events_url and otlp_endpoint) needs a receiver someone must build and host. Owner direction of 2026-11-21: no dependence on one vendor for this, and a person who copies ANVIL must see their runs without standing anything up. Every work order is already a GitHub issue and every run already holds a token that can write to it.

BUILD, per the spec requirements:
R1: anvil.yaml accepts observability.sinks, an ordered and validated list of sink entries. A sink is called with the run state record (schema anvil/run-state@1) every time the recorder rewrites the state: at the start, before each station, after the last one, and when the run ends, crashes or is stopped early. No new event kind; events.jsonl is unchanged. A sink that raises, times out or is refused is recorded in export_errors under its type and the line goes on; each call is bounded by observability.timeout_seconds. No sinks configured means no additional network call. The sink code lives beside the recorder, outside anvil/runner.py.
R2: the github-issue sink, entry {"type": "github-issue"} with optional token_env (default GH_TOKEN). Active only when the work order id is wo-gh-<number>, GITHUB_REPOSITORY is set and the token variable is set; otherwise inactive with the reason recorded once and no network call. It creates one comment on the issue at its first call and edits that same comment on every later call, found again by a hidden marker carrying the run id. The comment shows the work order and pipeline, the run state, the verdict and exit status once known, one row per pipeline station in pipeline order (done, failed, running, pending, skipped, not run) with attempt and measured tokens, loopbacks used, tokens and priced cost so far, the time of the last update and the workflow run link when the environment gives one. Scalar facts only: no prompt, no station output, no path, no token value. The API base comes from GITHUB_API_URL when set.
R3: the github-project sink, entry {"type": "github-project", "owner": ..., "number": ...} with optional owner_type, status_field (default Status), token_env and columns. Phases and default option names: intake (Intake), spec (Spec), build (Build: test-writer and builder), checks (Checks), review (Review: reviewers and approver), human (Needs human), done (Done), failed (Failed). It sets the status of the issue's project item when the phase changes, adds the issue to the project when missing, and never alters the project's shape: a missing project, field or option is recorded by name and the sink goes inactive for the run. The workflow token cannot reach Projects; token_env names a variable holding one that can, and with it unset the sink is inactive and says so once.
R4: the factory's own anvil.yaml enables the github-issue sink; the scaffold for new projects enables it too; the github-project sink ships documented and off. The final ANVIL line report comment of the workflow is unchanged.
R5: sinks run in the line process and read their token there. Stations never receive it. No token value appears in state.json, events.jsonl, report.json, a comment or an export error.
R6: regression tests as new files under tests/, with a local HTTP collector in the manner of tests/test_governed_delivery.py: (a) one comment creation then only edits, the last showing every station done and the verdict; (b) the edit sent before the builder shows the builder running and later stations pending; (c) a collector answering 500 and an unreachable one leave verdict and report unchanged with one export error; (d) a non wo-gh id or a missing token gives zero network calls and one recorded reason; (e) the project sink sends a status change only when the phase changes, adds a missing item, and goes inactive naming a missing option; (f) no sink configured gives zero additional network calls; (g) a malformed sinks list fails loading naming the entry; (h) a token value in the environment appears in no file the run writes and in no request body.

RECONCILIATION WITH ACTIVE SPECS AND EXISTING TESTS (read before building; these are decisions, not discoveries for the line to make):
Governed delivery owns state.json, events.jsonl, the webhook and the OTLP trace; all four are frozen and this order only adds consumers of the state record. tests/test_governed_delivery.py asserts that the events POSTed to the webhook equal the events in events.jsonl and counts station.finished and loopback events against the report's steps: sinks must not add, remove or reorder events, which is why they are fed by the state and not by a new event. tests/test_review_producer.py asserts that the word "retry" does not occur in anvil/runner.py: keep network code and that word out of the runner. tests/test_continuous_run_accounting.py (wo-gh-41) asserts the report's shape after every exit path: a sink call on an exit path must not change what is written. wo-gh-42 (station partitions) may land before this order; its efficiency keys and this order's observability keys do not overlap. The runtime refusal stop (exit_status runtime_refused) is one more final state a sink must be able to show.

BUILDER REPORT: the builder report must contain each of these in full: 10168fa560af7284b23f99e4e639621cf47eacd2, live-progress-sinks, github-issue, github-project. It must also state the base ref it verified the tree against, the exact full factory test count from the suite run, and the names of the new test files added.

GUARDRAILS: authorized surface for this order: anvil/observe.py, a new module beside it for the sinks, anvil/config.py (validation of observability.sinks), anvil/scaffold.py (the default for new projects), anvil.yaml (the factory's own sink entry), docs/OPERATIONS.md, docs/EXECUTION.md, README.md (one short section on watching a run), CHANGELOG.md, one new decision record under brain/decisions/, and new test files under tests/. anvil/runner.py may change only where the recorder is constructed or told the pipeline order, and gains no network code. Do not touch any file under .github/workflows: the run's own token cannot push workflow changes and none are needed, because the line step already carries GH_TOKEN. Pipeline files under pipelines/ and anvil.json are protected paths. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. A test that asserts something about this order's own run (which paths it changed, what its builder report says, a comparison against a fixed base ref) must skip unless ANVIL_WORK_ORDER_ID names this order: left unconditional, such a test fails for every order after this one, as the tree evidence of wo-gh-42 did. Frozen: the events contract, the OTLP trace, the existing fields of the run-state schema, the rule that export never decides a run, the station environment reduction, tools/line_comment.py. Python standard library only, no new dependency. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/47
- risk_hints: 
- status: new

## Upstream steps

- (none)
