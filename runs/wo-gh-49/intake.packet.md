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

- (none)
