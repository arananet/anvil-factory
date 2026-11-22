# Task packet: spec-writer

## Station prompt

# Spec Writer

## Role
Write or revise an OpenSpec spec from a work order.

## Inputs
- work order
- brain

## Outputs
- spec

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the spec scoped to the work order. Do not add requirements the order did not ask for.

## Definition of done
- The spec is written to the spec file for this order (the path the work order or the run context names, otherwise under .openspec/specs/). A spec described only in your reply does not exist.
- Every requirement has an id and at least one scenario that names it. Every scenario is a concrete example a test or named evidence can check.
- No soft words stand in for a bar. Anything a person will see or use carries its acceptance criteria: the reference or direction, the sizes, the states, the floor.
- Out of scope and the allowed write set are stated.
- When your packet carries a Craft skills section, hold the spec to it.

## Before you hand off
Re-read the work order line by line against the spec and confirm nothing in the order is missing from it. In your reply, list the requirement and scenario ids you wrote or changed, and anything the order left open that the owner must decide.

## Consumption discipline

Read the spec and the relevant upstream artifacts first. Search before opening files; read only the relevant ranges. Bound command output and summarize long test logs with failures and a path to the full log. Run focused checks while editing and the required project checks at handoff. Reuse valid upstream work. Keep the final handoff concise, with changed files, evidence and unresolved issues. Preserve the required output contract.


## Practices

Promoted practices that resolved for this station. Follow each rule.

- P-15 (Filing completeness for protected surfaces): When an order's substance touches protected paths, packet contents or existing tests, the filing must enumerate the complete authorized write set up front: protected_paths changes, named test adaptations and packet inclusions; an under-authorized filing is returned before the run fires.

## Craft skills

Curated craft guidance resolved for this station and this work order. Order of authority: the work order and its spec, then the project design system and decisions, then promoted practices, then these skills. Where a skill conflicts with any of those, the skill yields. Apply what fits the work in front of you; a skill is a bar to meet, not a checklist to recite.

### Skill: architecture-fundamentals

Good architecture is the cheapest structure that makes the next change easy. Judge every structural choice by what it costs the next person who has to read or change it.

**Start from what exists**
- Read the project brain (brain/project.md, brain/decisions/) and the neighbouring code before you propose anything. Follow the existing structure and naming unless you can name the concrete problem that breaking it solves.
- A decision record that is already accepted is a constraint. If the work needs to break one, say so and record a new decision; do not quietly work around it.

**Boundaries**
- Give each module one reason to exist and a small interface that hides how it works. A module is deep when a lot of behaviour sits behind few entry points.
- Dependencies point one way: domain logic knows nothing about delivery (HTTP, CLI, UI) or storage; the edges depend on the core, never the reverse.
- Keep input and output at the edges. Parse and validate once at the boundary, then pass typed, trusted data inward. Pure functions in the middle are the ones you can test without a harness.
- One source of truth for every fact: a constant, a schema, a config value. A second copy is a future bug.

**Size the design to the problem**
- Choose the smallest stack and the fewest moving parts that ship the stated scope. Name what version one deliberately leaves out.
- Do not build for a requirement nobody has stated. No plugin system for one plugin, no abstraction with one implementation, no config flag for a value that never changes.
- Prefer boring, well documented technology already used in the project over a new dependency. Every new dependency needs a reason that a standard library or existing module cannot meet.

**State, failure and operation**
- Say where every piece of state lives, who owns it and how long it lives. Shared mutable state is the first place to look for a defect.
- Fail closed and loudly: an unknown input, a missing file or a malformed record is an error with a named reason, never a silent default.
- Make behaviour deterministic where it can be. Anything that can be decided by plain code should not be left to a model or to timing.
- Configuration comes from the environment or a config file, secrets never from the tree.

**Record the decision**
- When you make a choice that a reasonable engineer could have made differently, write down the context, the decision and the consequence in a few lines, where the project keeps decisions.
- State the trade off honestly: what this choice makes harder.

**Before you hand off, check**
- Can you describe each new module in one sentence without the word "and"?
- Does any new code reach across a boundary it should not?
- Is there a simpler structure that satisfies the same spec scenarios? If yes, use it.

### Skill: spec-writing

The spec is the contract the whole line works from. A vague spec produces a vague build that still passes review, because reviewers judge against the spec. Every quality problem you leave open here is paid for downstream.

**Before writing**
- Read the existing specs and the project brain. Reuse the project's terms; do not invent a second name for a thing that already has one.
- Look for conflicts with specs that are already accepted. If this order contradicts one, name both clauses and resolve it in the spec instead of leaving it for the builder to discover.
- If the work order is missing something you need to state a requirement, say exactly what is missing. Do not fill the gap with a guess dressed as a requirement.

**Requirements**
- One requirement states one obligation. Give each a stable id (R1, R2) so tests and reviews can cite it.
- Write observable behaviour, not implementation: what the system does for which input, not which class does it. Constrain the implementation only where the order requires it.
- Replace every soft word with a number or a named condition. "Fast", "good looking", "robust", "user friendly", "responsive" are not requirements until they say what is measured: "renders with no horizontal scroll at 360 px", "p95 under 200 ms", "body text contrast at least 4.5:1".
- Use a plain trigger form where it helps: "When <trigger>, the system shall <response>." "While <state>, ...". "If <unwanted condition>, then ...".

**Scenarios**
- Every requirement has at least one scenario, and every scenario names the requirement it proves. A requirement with no scenario will not be tested.
- Write each scenario as a concrete example: given this state, when this happens, then this observable result. Use real values, not placeholders.
- Cover the unhappy paths on purpose: empty input, the boundary value, the malformed record, the missing dependency, the second call. Most defects live there.
- A scenario must be checkable by a test or by named evidence. If you cannot say how it would be checked, rewrite it.

**Quality bars belong in the spec**
- For anything a person will see or use, state the quality bar as acceptance criteria: the reference to match, the viewport range, the states that must exist, the performance or accessibility floor. If it is not written here, no reviewer can hold the build to it.
- Name the evidence the run must produce (captures, measurements, a traversal proof) so the builder knows to produce it.

**Scope**
- State what is out of scope and which files or surfaces must not change. Enumerate the full write set when protected paths are involved, including test adaptations.
- Keep the spec as short as the contract allows. Rationale goes in one Purpose paragraph, not in every requirement.

**Before you hand off, check**
- Could two builders read this and ship materially different things? Then it is not specific enough.
- Does every R have an S, and every S a named R?
- Is every number in the spec one you verified or one the owner stated?

## Work order

- id: wo-gh-47
- kind: feature
- title: Live progress sinks: a run seen while it runs, on the work order's issue and optionally on a GitHub Projects board
- source: github-issue
- description: Implement the spec in .openspec/specs/live-progress-sinks/spec.md. Pipeline for this order is sdlc-default (software domain, the factory repo itself), selected by the run workflow.

RELEASE (owner decision, 2026-11-22): this order is released for execution. It was filed on 2026-11-21 and staged until wo-gh-42 landed, which it did on 2026-11-22 (merge 6191e8c1f235b4cd248a51203d40177834dc4ae2). Baseline now: factory main ae0bbfb2af95b41d96d8e2af7c9f8b787f54d83b, whose anvil.yaml carries max_run_tokens 15000000, max_runtime_turns 100, max_packet_tokens 48000 and the efficiency station partitions of wo-gh-42, and whose anvil.json wires the checks command (python -m unittest discover -s tests -p 'test_*.py'). First run of this order (45042545362) was stopped in the spec-writer by its token partition, since recalibrated (spec-writer 1200000, builder 5800000); the run branch carries that fix. The exit statuses now on main include runtime_refused; a sink must be able to show any exit status as a final state without knowing the list.

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

BUILDER REPORT: the builder report must contain each of these in full: ae0bbfb2af95b41d96d8e2af7c9f8b787f54d83b, live-progress-sinks, github-issue, github-project. It must also state the base ref it verified the tree against, the exact full factory test count from the suite run, and the names of the new test files added.

GUARDRAILS: authorized surface for this order: anvil/observe.py, a new module beside it for the sinks, anvil/config.py (validation of observability.sinks), anvil/scaffold.py (the default for new projects), anvil.yaml (the factory's own sink entry), docs/OPERATIONS.md, docs/EXECUTION.md, README.md (one short section on watching a run), CHANGELOG.md, one new decision record under brain/decisions/, and new test files under tests/. anvil/runner.py may change only where the recorder is constructed or told the pipeline order, and gains no network code. Do not touch any file under .github/workflows: the run's own token cannot push workflow changes and none are needed, because the line step already carries GH_TOKEN. Pipeline files under pipelines/ and anvil.json are protected paths. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. A test that asserts something about this order's own run (which paths it changed, what its builder report says, a comparison against a fixed base ref) must skip unless ANVIL_WORK_ORDER_ID names this order: left unconditional, such a test fails for every order after this one, as the tree evidence of wo-gh-42 did. Frozen: the events contract, the OTLP trace, the existing fields of the run-state schema, the rule that export never decides a run, the station environment reduction, tools/line_comment.py. Python standard library only, no new dependency. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/47
- risk_hints: 
- status: new

## Upstream steps

- intake: executed

## Run context

Read the upstream work before you start; it is the input your station builds on.

- Output of intake: runs/wo-gh-47/intake.output.md
