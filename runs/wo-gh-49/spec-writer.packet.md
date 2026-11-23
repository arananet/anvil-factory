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

- id: wo-gh-49
- kind: feature
- title: Stop futile loops: an owner ruling, an empty attempt or the same gate failure twice ends the run
- source: github-issue
- description: Implement the spec in .openspec/specs/stop-futile-loops/spec.md. Pipeline for this order is sdlc-default (software domain, the factory repo itself), selected by the run workflow.

RELEASE OF 2026-11-22: this order is released by the owner. wo-gh-41, wo-gh-42 and wo-gh-47 are merged. Base ref: factory main d74c83aefff95fba777ca04505116cfb63c6c8f3 (wo-gh-47 merged, plus the operator fix that sets the intake partition to 400000 and the builder partition to 5600000). The run spine now includes anvil/sinks.py and the progress calls in anvil/observe.py: the three new exit statuses must reach the live progress comment through the existing exit path, with no change to anvil/sinks.py.

RUN EVIDENCE TESTS (operator rule, learned on wo-gh-42 and wo-gh-47): any test that asserts a fact about this order's own run (the tree compared with the base ref, files untouched, lines this order adds) must skip unless the environment variable ANVIL_WORK_ORDER_ID equals wo-gh-49, in the manner of tests/test_live_progress_sinks.py. Such a test left unconditional blocks every later order at the checks gate. No test may compare wall clock figures (durations, timestamps) between two runs for equality.

EVIDENCE (the defect this order closes):
wo-gh-41, run 44682387438 (2026-11-20): three builder attempts (1230114, 462988 and 771972 tokens) and three gate failures on the same single test, tests/test_governed_delivery.py test_crash_and_stall_are_visible_s1, an existing protected test that asserted the opposite of what the order required. No attempt could pass it.
wo-gh-42, run 44912754341 (2026-11-21): the gate passed three times and all five reviewers requested changes three times on one finding, in their words "needs an owner ruling" and "the line cannot resolve it". The third builder attempt changed no code and said so. The run used 14913271 tokens of a 15000000 cap, about 13 USD by the runtime's own estimate; two of its three rounds could not change the outcome.
In both runs the signal was on the record before the money was spent.

BUILD, per the spec requirements:
R1: a review object may carry one optional field, owner_ruling, a string with the question only the owner can settle and the options seen. Verdicts stay pass, fail, changes_requested. Reviewer packets gain one instruction: set it when a finding cannot be resolved by the builder inside the order's guardrails (a requirement contradicts a protected path or an existing protected test, two requirements conflict, or an authorization is missing). parse_review and the wrapper's validation accept and keep the field; a non-string or empty value is ignored and recorded as ignored.
R2: when any counted review of an attempt carries owner_ruling, the approver's verdict is computed as today, no loopback is made, and the run ends with exit_status owner_ruling_needed, the termination reason naming each station and its question. The report records the rulings in a field set of their own, the human gate is closed with a rule sentence saying so, and tools/line_comment.py prints the questions under their own heading. The verdict vocabulary does not grow.
R3: after a loopback to the builder, the runner compares the tree outside runs/ before and after the attempt. When nothing changed, no gate and no reviewer is dispatched for it and the run ends with exit_status no_progress. Deterministic, no model call.
R4: the checks gate keeps a failure signature per attempt: the sorted set of output lines matching the configured failure patterns (defaults: unittest FAIL: and ERROR:, pytest FAILED, node --test not ok; a project sets efficiency.gate_failure_patterns). A failure whose non-empty signature equals the previous attempt's ends the run with exit_status checks_stuck, listing the repeated lines. An empty signature never triggers the stop.
R5: the three stops are exit statuses in the sense of continuous run accounting (record completed through the existing exit path, unrun stations not_run). Each can be turned off per project under efficiency (stop_on_owner_ruling, stop_on_no_progress, stop_on_repeated_gate_failure; on by default). The report states which stop ended the run and the next human action.
R6: regression tests as new files under tests/, with a fake runtime in the manner of tests/test_continuous_run_accounting.py: (a) owner_ruling on the first attempt ends the run with owner_ruling_needed, one builder call, the question in report and comment; (b) the same review without the field loops back; (c) a second builder attempt changing no file ends with no_progress and no reviewer dispatch; (d) the same unittest FAIL line twice ends with checks_stuck after the second attempt, a different second failure loops on; (e) an unrecognized failure never triggers checks_stuck; (f) each stop turned off restores the previous behavior; (g) a review file with owner_ruling passes validation and parsing, a non-string value is ignored.

RECONCILIATION WITH ACTIVE SPECS AND EXISTING TESTS (read before building; these are decisions, not discoveries for the line to make):
The review parse contract is extended by one optional field and nothing else: both parse_review (anvil/runner.py) and validate_review_file (tools/claude_station.py) already ignore unknown keys, so existing reviews stay valid. tests/test_review_parsing_integrity.py and tests/test_review_producer.py pin the wording returned by review_suffix and the rule that correction logic lives in the wrapper, and the second asserts that the word "retry" does not occur in anvil/runner.py: the new reviewer instruction goes in the packet the runner builds, never in review_suffix. tests/test_continuous_run_accounting.py asserts the report's shape on every exit path; the new exit statuses are additions, as runtime_refused was. tests/test_governed_delivery.py asserts the event sequence: stops add no event kind. The approval rules of anvil/line.py are untouched because the run verdict vocabulary does not grow. If an existing protected test contradicts a requirement of this order, the builder says so in its report on the first attempt and stops; it does not work around it.

BUILDER REPORT: the builder report must contain each of these in full: stop-futile-loops, owner_ruling_needed, no_progress, checks_stuck. It must also state the base ref it verified the tree against, the exact full factory test count from the suite run, and the names of the new test files added.

GUARDRAILS: authorized surface for this order: anvil/runner.py, anvil/approver.py, anvil/model.py (the optional field on Review), anvil/gates.py (the failure signature), anvil/config.py (the three switches and the patterns), tools/claude_station.py (validate_review_file accepts the field; no other change), tools/line_comment.py, the reviewer station prompts under stations/reviewer-*/PROMPT.md (one added instruction each, nothing removed), docs/EXECUTION.md, docs/OPERATIONS.md, CHANGELOG.md, one new decision record under brain/decisions/, and new test files under tests/. Do not touch files under .github/workflows. Pipeline files under pipelines/ and anvil.json are protected paths. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. Frozen: the review verdict vocabulary and the run verdict vocabulary, the wording of review_suffix, the checks gate's pass or fail decision and its loopback accounting when no stop applies, cost-measurement semantics, the events contract. Python standard library only, no new dependency. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/49
- risk_hints: 
- status: new

## Upstream steps

- intake: executed

## Run context

Read the upstream work before you start; it is the input your station builds on.

- Output of intake: runs/wo-gh-49/intake.output.md
