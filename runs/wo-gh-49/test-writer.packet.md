# Task packet: test-writer

## Station prompt

# Test Writer

## Role
Write tests that map to spec scenarios before implementation.

## Inputs
- spec

## Outputs
- tests

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the tests scoped to the spec scenarios for this work order.

## Definition of done
- Each spec scenario has at least one test that names it, written as a file in the project's test layout and framework.
- The tests exercise the real artifact the order produces (the real file, function or command). A test that never touches the real artifact is a facade and fails the order.
- The new tests fail now, before the build, for the right reason. Run them and confirm.
- Existing tests are not weakened, skipped or deleted.
- When your packet carries a Craft skills section, hold the tests to it.

## Before you hand off
Run the project check command and record the real result. In your reply, map each scenario id to its test, state the baseline count and what you added, and name any scenario you could not cover and why.

## Consumption discipline

Read the spec and the relevant upstream artifacts first. Search before opening files; read only the relevant ranges. Bound command output and summarize long test logs with failures and a path to the full log. Run focused checks while editing and the required project checks at handoff. Reuse valid upstream work. Keep the final handoff concise, with changed files, evidence and unresolved issues. Preserve the required output contract.


## Craft skills

Curated craft guidance resolved for this station and this work order. Order of authority: the work order and its spec, then the project design system and decisions, then promoted practices, then these skills. Where a skill conflicts with any of those, the skill yields. Apply what fits the work in front of you; a skill is a bar to meet, not a checklist to recite.

### Skill: test-design

A test is evidence only if it would fail when the behaviour is wrong. A suite that passes against an empty implementation, or that never touches the real artifact, is a facade and is worse than no suite because it is trusted.

**Map to the spec**
- One spec scenario, at least one test, named after the scenario it proves (S3 in the test name or docstring). A reader should be able to go from a scenario id to its test and back.
- Test the behaviour the scenario states, through the public interface. Do not assert private structure, call order or exact log text unless the spec requires it.

**Make the test able to fail**
- Before the implementation exists the new tests must fail, and fail for the right reason (the behaviour is missing, not an import error). Run them and record that.
- Exercise the real thing: read the real file the order produces, call the real function, run the real command. A test that builds its own copy of the expected output and checks the copy proves nothing.
- Assert specific values. `assertTrue(result)` and "does not raise" are rarely enough; state the expected value, count or message.
- Do not mock the unit under test, and do not mock so much that the test only checks the mocks. Fake the edges (network, clock, randomness), keep the logic real.

**Cover what breaks**
- For each scenario ask: empty, one, many; the boundary and one past it; malformed input; missing file or dependency; repeated call; wrong type. Write the cases that could plausibly fail.
- For every validation rule, test one input that passes and one that is rejected with the named reason.
- For anything computed from the tree (counts, lists, versions), compute the expected value in the test at run time instead of hard coding a number that will go stale.

**Keep tests trustworthy**
- Deterministic: no dependence on wall clock, test order, network or leftover files. Use temporary directories and fixed seeds.
- Isolated: each test sets up what it needs and cleans up. No test depends on another having run.
- Fast and readable: arrange, act, assert, with one clear reason to fail per test. Use helpers for setup so the body shows only what matters.
- Follow the project's existing test framework, layout and naming. Do not add a test dependency the project does not already use.

**Account for the suite honestly**
- State the baseline count before your change, the tests you added and the tests you edited, and why each edit was needed.
- Never weaken, skip or delete an existing test to make a run pass. If an existing test is wrong, say so and name it; that is a finding, not a cleanup.
- Reported results must reproduce against the final tree. Run the full project check command last and quote its real summary line.

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
- spec-writer: executed

## Run context

Read the upstream work before you start; it is the input your station builds on.
The checks gate runs the project checks listed here; run them yourself before you hand off.

- Output of intake: runs/wo-gh-49/intake.output.md
- Output of spec-writer: runs/wo-gh-49/spec-writer.output.md
- Project check: `python -m unittest discover -s tests -p 'test_*.py'`
