# Stop Futile Loops: the Line Does Not Spend on What It Cannot Resolve

Status: proposed
Slug: stop-futile-loops
Work order: wo-gh-49 (https://github.com/arananet/anvil-factory/issues/49)
Base ref: factory main d74c83aefff95fba777ca04505116cfb63c6c8f3 (wo-gh-41, wo-gh-42 and wo-gh-47 merged, plus the operator fix setting the intake partition to 400000 and the builder partition to 5600000)

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

A loopback sends work back to the builder. It pays for itself when the builder can fix what was found. Twice in three days it could not, and the line spent anyway.

wo-gh-41, run 44682387438 (2026-11-20): the builder completed three attempts and the checks gate failed three times on the same single test, tests/test_governed_delivery.py test_crash_and_stall_are_visible_s1, an existing protected test that asserted the opposite of what the order required. No builder attempt could pass it. Three builder calls (1230114, 462988 and 771972 tokens) bought the same failure three times.

wo-gh-42, run 44912754341 (2026-11-21): the gate passed three times and all five reviewers requested changes three times on one finding, in their own words "needs an owner ruling" and "the line cannot resolve it". The third builder attempt changed no code and said so. The run used 14913271 tokens of a 15000000 cap, about 13 USD by the runtime's own estimate, and two of its three rounds could not change the outcome.

In both runs the signal was on the record before the money was spent: the same gate failure twice, a builder attempt with nothing in it, reviewers saying the owner must decide. This order makes the line read those signals and stop, handing the owner the question instead of another round.

## Terms
- counted review: a review the approver counts toward the attempt's verdict today (unchanged by this order).
- loopback: the existing return of work from the checks gate or the approver to the builder.
- stop: one of the three exits this order adds: owner_ruling_needed, no_progress, checks_stuck.

## Requirements

### R1. A reviewer can say the owner must decide
- R1.1: A review object (anvil/model.py Review) may carry one optional field, owner_ruling: a string stating the question only the owner can settle and the options the reviewer sees. Its verdict stays one of pass, fail, changes_requested. A review without the field means what it means today.
- R1.2: The reviewer packet the runner builds gains one instruction: set owner_ruling when a finding cannot be resolved by the builder inside the order's guardrails, namely when a requirement contradicts a protected path or an existing protected test, when two requirements conflict, or when the fix needs an authorization the order does not give; a finding the builder can fix is never an owner ruling. Each stations/reviewer-*/PROMPT.md gains the same instruction as one added sentence, nothing removed. The instruction does not go in review_suffix, whose wording is frozen.
- R1.3: parse_review (anvil/runner.py) and validate_review_file (tools/claude_station.py) accept the field and keep it. A value that is not a string, or is a string that is empty after stripping whitespace, is dropped, the review still counts with its verdict and findings unchanged, and the review's step record carries owner_ruling_ignored with the reason (for example "not a string: int" or "empty"). Nothing else about review parsing changes.

### R2. An owner ruling ends the run instead of looping
- R2.1: When any counted review of an attempt carries a kept owner_ruling, the approver's verdict for that attempt is computed exactly as today, no loopback is made, and the run ends with exit_status owner_ruling_needed. The termination_reason names each station that asked and its question.
- R2.2: The run report carries a top level owner_rulings list, one entry per asking station, each an object with station (the reviewer station id) and question (the owner_ruling string). The key is absent or an empty list on runs that did not end this way.
- R2.3: The human gate entry of the decision is closed with a rule sentence that contains the words "owner ruling needed".
- R2.4: tools/line_comment.py prints the questions in the final comment under a heading of their own, "Owner ruling needed", one line per entry naming the station and its question.
- R2.5: The verdict vocabulary does not grow: the run verdict is the one the reviews produce today (changes_requested or rejected, or approved if every counted review passes), so the approval rules of anvil/line.py are unchanged.

### R3. An attempt that changes nothing ends the run
- R3.1: After a loopback to the builder, the runner compares the working tree outside runs/ before and after that builder attempt: a file created, deleted or changed in content anywhere outside runs/ (files ignored by .gitignore excluded) counts as a change. The first builder attempt of a run never ends the run, and an unchanged attempt ends it only when an earlier builder attempt of the same run did change the tree outside runs/: a builder that has not moved at all is judged by the gate and the reviewers as before (operator amendment of 2026-11-23, decision 0016).
- R3.2: When nothing changed, no checks gate and no reviewer is dispatched for that attempt and the run ends with exit_status no_progress, the termination_reason naming the attempt number and the loopback source (checks gate or approver) that was not answered.
- R3.3: The comparison is deterministic and makes no model call.

### R4. The same gate failure twice ends the run
- R4.1: The checks gate computes a failure signature for each attempt whose checks fail: the sorted set of distinct output lines (stripped of trailing whitespace) that match a configured failure pattern. The default patterns are regular expressions matching lines that begin with FAIL: or ERROR: (unittest), FAILED (pytest) and not ok (TAP output of node --test). A project replaces them with efficiency.gate_failure_patterns, a list of regular expression strings; a value that is not a list of strings, or a pattern that does not compile, is a configuration error naming the key, never a silent default.
- R4.2: When the gate fails on an attempt with a non-empty signature equal to the signature of the immediately previous attempt's gate failure, no further loopback is made and the run ends with exit_status checks_stuck, the termination_reason listing the repeated lines, truncated to at most 2000 characters.
- R4.3: An empty signature (a failure the patterns do not recognize) never triggers the stop, and neither does a failure whose previous attempt passed the gate or had no gate run; the gate behaves as today. The gate's pass or fail decision and its loopback accounting are unchanged whenever no stop applies; the existing checks_stopped exit (attempts exhausted) is unchanged.

### R5. The stops are exits like the others
- R5.1: owner_ruling_needed, no_progress and checks_stuck are exit statuses in the sense of continuous run accounting: each is added to the runner's closed set of exit statuses (as runtime_refused was), the record is completed through the existing exit path, every unrun station is recorded as not_run, and report.json is valid JSON at every moment.
- R5.2: Each stop can be turned off per project under efficiency: stop_on_owner_ruling, stop_on_no_progress, stop_on_repeated_gate_failure, booleans, all true by default. Their defaults and gate_failure_patterns' defaults live in anvil/config.py. With a switch false, the run behaves as before this change for that condition (owner_ruling is still kept on the review and reported, but causes no stop).
- R5.3: The run report carries a top level next_human_action, a non-empty string, on every run that ends in one of the three stops: for owner_ruling_needed, answer the questions listed and refile or amend the order; for no_progress, read the unanswered loopback and decide whether the order is buildable as filed; for checks_stuck, inspect the repeated failing lines and decide whether a protected test or the order must change. exit_status names the stop that ended the run.
- R5.4: The three new exit statuses reach the live progress comment through the existing exit path (anvil/observe.py passing exit_status to the configured sinks) with no change to anvil/sinks.py. The events contract is unchanged: the stops add no event kind.

### R6. Regression tests
- R6.1: New test files under tests/ drive scripted runs through the runner with a fake runtime (no network, no real model) in the manner of tests/test_continuous_run_accounting.py, covering: (a) S1; (b) S2; (c) S3; (d) S4 and S5; (e) S6; (f) S7 for each of the three switches; (g) S8; plus S9 and S10. Each test method names its scenario id in its name or docstring.
- R6.2: Any test that asserts a fact about this order's own run (the tree compared with the base ref, files untouched, lines this order adds) skips unless the environment variable ANVIL_WORK_ORDER_ID equals wo-gh-49, in the manner of tests/test_live_progress_sinks.py. No test compares wall clock figures (durations, timestamps) between two runs for equality.
- R6.3: The full factory suite (python -m unittest discover -s tests -p 'test_*.py') passes with the new files added and no test file present at the base ref modified or deleted.

### R7. Builder report
- R7.1: The builder report contains each of these strings in full: stop-futile-loops, owner_ruling_needed, no_progress, checks_stuck. It states the base ref it verified the tree against (d74c83aefff95fba777ca04505116cfb63c6c8f3), the exact full factory test count from the suite run, and the names of the new test files added.
- R7.2: If an existing protected test contradicts a requirement of this order, the builder says so in its report on the first attempt, naming the test and the requirement, and stops; it does not work around it.

## Scenarios

### Scenario: A reviewer asks for the owner and the line stops
- S1 (R1.1, R2.1, R2.2, R2.3, R2.4, R5.1, R5.3, R6.1a): Given a scripted sdlc-default run whose reviewer-spec returns changes_requested with owner_ruling "R2 contradicts protected test tests/test_example.py::test_x; options: amend the test or drop R2" on the first attempt, when the approver runs, then the fake runtime received exactly one builder call; report.json has exit_status owner_ruling_needed, termination_reason containing reviewer-spec and the question, owner_rulings equal to [{"station": "reviewer-spec", "question": "<that string>"}], a non-empty next_human_action, a human gate rule containing "owner ruling needed", the verdict changes_requested, and every station after the approver recorded not_run; and tools/line_comment.py output on that report contains the heading "Owner ruling needed" followed by the question.

### Scenario: An ordinary finding still loops back
- S2 (R2.1, R6.1b): Given the same scripted run and review without owner_ruling, when the approver runs, then the work returns to the builder (the fake runtime receives a second builder call) and the run does not end with owner_ruling_needed.

### Scenario: A builder that changes nothing ends the run
- S3 (R3.1, R3.2, R3.3, R5.1, R6.1c): Given a scripted run whose first builder attempt writes app.py and whose approver loops back, when the second builder attempt writes no file outside runs/, then no checks gate and no reviewer is dispatched for attempt 2 (fake runtime reviewer call count unchanged after the second builder call), exit_status is no_progress, termination_reason names attempt 2, and unrun stations are not_run. A second attempt that writes only under runs/ also ends with no_progress.

### Scenario: The same test failing twice ends the run
- S4 (R4.1, R4.2, R5.1, R6.1d): Given a checks gate whose output on attempts 1 and 2 both contain the line "FAIL: test_x (tests.test_example.T.test_x)", when the second failure is recorded, then no third builder call is made, exit_status is checks_stuck, and termination_reason contains that line. Given a repeated signature whose lines total more than 2000 characters, termination_reason is at most 2000 characters.

### Scenario: A different failure is progress
- S5 (R4.2, R4.3, R6.1d): Given a checks gate failing with "FAIL: test_x (tests.test_example.T.test_x)" on attempt 1 and "FAIL: test_y (tests.test_example.T.test_y)" on attempt 2, when the second failure is recorded, then the line loops back to the builder for attempt 3 as today.

### Scenario: An unrecognized failure never stops the line early
- S6 (R4.3, R6.1e): Given a checks gate failing twice with the same output "Segmentation fault" and no line matching a failure pattern, when the second failure is recorded, then the run does not end with checks_stuck and loopback accounting matches today's (it ends with checks_stopped once attempts are exhausted).

### Scenario: Each stop can be turned off
- S7 (R5.2, R6.1f): Given efficiency.stop_on_owner_ruling false, the S1 run loops back as in S2 (owner_rulings still recorded on the review); given efficiency.stop_on_no_progress false, the S3 run dispatches the gate and reviewers for attempt 2; given efficiency.stop_on_repeated_gate_failure false, the S4 run makes a third builder attempt. Given efficiency.gate_failure_patterns set to ["^BROKEN "], a gate failing twice with "BROKEN widget" ends with checks_stuck and one failing twice with "FAIL: test_x" does not; given gate_failure_patterns "(" (does not compile), configuration loading raises an error naming efficiency.gate_failure_patterns.

### Scenario: The review contract still holds
- S8 (R1.3, R6.1g): Given a review file {"verdict": "changes_requested", "findings": ["f1"], "owner_ruling": "Q?"}, when validate_review_file validates it and parse_review parses it, then both accept it with verdict changes_requested, findings ["f1"] and owner_ruling "Q?". Given owner_ruling 7, or "   ", then the field is dropped, the review still counts with its verdict and findings unchanged, and owner_ruling_ignored is recorded with its reason. review_suffix returns the same text as at the base ref.

### Scenario: The stops reach the live progress comment
- S9 (R5.4, R6.1): Given a scripted run with a recording fake sink that ends in each of owner_ruling_needed, no_progress and checks_stuck, when the run exits, then the last record handed to the sink carries that exit_status, and the event kinds emitted are a subset of the kinds emitted at the base ref.

### Scenario: The suite stays green and the run's own facts are guarded
- S10 (R6.2, R6.3, R7.1): Given the tree after the build, when python -m unittest discover -s tests -p 'test_*.py' runs without ANVIL_WORK_ORDER_ID set, then it passes and every run evidence test is reported skipped; with ANVIL_WORK_ORDER_ID=wo-gh-49, git diff --diff-filter=MD d74c83aefff95fba777ca04505116cfb63c6c8f3 lists no file under tests/, no file under .github/workflows or pipelines/ and not anvil.json, and no produced file contains U+2014 or U+2013.

## Out of scope
- Any new review verdict or run verdict; any change to approval rules in anvil/line.py.
- Any change to the wording of review_suffix, to correction logic location (the wrapper), or any use of the word "retry" in anvil/runner.py.
- Any new event kind or change to the events contract; any change to anvil/sinks.py or anvil/observe.py.
- Any change to cost-measurement semantics, station budgets or partitions.
- Model-based judgement of futility; stops other than the three named here.
- Merging, publishing or deploying anything; the run stops at the owner human gate.

## Allowed write set
- anvil/runner.py, anvil/approver.py, anvil/model.py (the optional field on Review), anvil/gates.py (the failure signature), anvil/config.py (the three switches and the patterns)
- tools/claude_station.py (validate_review_file accepts the field; no other change)
- tools/line_comment.py
- stations/reviewer-*/PROMPT.md (one added instruction each, nothing removed)
- docs/EXECUTION.md, docs/OPERATIONS.md, CHANGELOG.md
- one new decision record under brain/decisions/ (next number after 0015)
- new test files under tests/
- Protected and not touched: files under .github/workflows; pipelines/; anvil.json; every test file present at the base ref; anvil/sinks.py; anvil/telemetry.py.

## Guardrails
- Python standard library only. No new dependency.
- Known constraints from existing tests, stated so the line does not discover them: tests/test_review_parsing_integrity.py and tests/test_review_producer.py pin the review_suffix wording and that correction logic lives in the wrapper, and the second asserts the word "retry" does not occur in anvil/runner.py; tests/test_continuous_run_accounting.py asserts the report's shape on every exit path and keeps its own list of exit statuses; tests/test_governed_delivery.py asserts the event sequence.
- No em dash or en dash character in any produced file (project style rule).
