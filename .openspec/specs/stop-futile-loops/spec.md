# Stop Futile Loops: the Line Does Not Spend on What It Cannot Resolve

Status: proposed
Slug: stop-futile-loops

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

A loopback sends work back to the builder. It pays for itself when the builder can fix what was found. Twice in three days it could not, and the line spent anyway.

wo-gh-41, run 44682387438 (2026-11-20): the builder completed three attempts and the checks gate failed three times on the same single test, tests/test_governed_delivery.py test_crash_and_stall_are_visible_s1, an existing protected test that asserted the opposite of what the order required. No builder attempt could pass it. Three builder calls (1230114, 462988 and 771972 tokens) bought the same failure three times.

wo-gh-42, run 44912754341 (2026-11-21): the gate passed three times and all five reviewers requested changes three times on one finding, in their own words "needs an owner ruling" and "the line cannot resolve it": the spec required an unconditional precondition and making it unconditional failed 22 protected tests. The third builder attempt changed no code and said so. The run used 14913271 tokens of a 15000000 cap, about 13 USD by the runtime's own estimate, and two of its three rounds could not change the outcome.

In both runs the signal was on the record before the money was spent: the same gate failure twice, a builder attempt with nothing in it, reviewers saying the owner must decide. This order makes the line read those signals and stop, handing the owner the question instead of another round.

## Requirements

### R1. A reviewer can say the owner must decide
- A review object may carry one optional field, owner_ruling: a string stating the question only the owner can settle and the options the reviewer sees. Its verdict stays one of pass, fail, changes_requested. A review without the field means what it means today.
- Reviewer packets gain one short instruction: set owner_ruling when a finding cannot be resolved by the builder inside the order's guardrails, for example when a requirement contradicts a protected path or an existing protected test, when two requirements conflict, or when the fix needs an authorization the order does not give. A finding the builder can fix is never an owner ruling.
- parse_review and the wrapper's review file validation accept the field and keep it; a non-string or empty value is ignored and recorded as ignored. Nothing else about review parsing changes.

### R2. An owner ruling ends the run instead of looping
- When any counted review of an attempt carries owner_ruling, the approver's verdict for that attempt is computed as today, no loopback is made, and the run ends with exit_status owner_ruling_needed. The termination reason names each station that asked and its question.
- The run report records the rulings asked (station, question) in a field set of their own, the human gate is closed with a rule sentence that says an owner ruling is needed, and tools/line_comment.py prints the questions in the final comment under their own heading.
- The verdict vocabulary does not grow: the verdict is the one the reviews produce (changes_requested or rejected), so approval rules are unchanged.

### R3. An attempt that changes nothing ends the run
- After a loopback to the builder, the runner compares the tree outside runs/ before and after the builder attempt. When nothing changed, no gate and no reviewer is dispatched for that attempt and the run ends with exit_status no_progress, the termination reason naming the loopback that was not answered.
- The comparison is deterministic and makes no model call.

### R4. The same gate failure twice ends the run
- The checks gate keeps a failure signature per attempt: the sorted set of lines of its output that match the configured failure patterns. The default patterns cover unittest (lines beginning FAIL: or ERROR:), pytest (lines beginning FAILED) and the TAP output of node --test (lines beginning not ok). A project sets its own under efficiency.gate_failure_patterns.
- When the gate fails on an attempt with a non-empty signature equal to the signature of the previous attempt's failure, no further loopback is made and the run ends with exit_status checks_stuck, the termination reason listing the repeated lines, bounded in length.
- An empty signature (a failure the patterns do not recognize) never triggers the stop; the gate behaves as today.

### R5. The stops are exits like the others
- owner_ruling_needed, no_progress and checks_stuck are exit statuses in the sense of continuous run accounting: the record is completed through the existing exit path, unrun stations are recorded as not_run, and the report is valid at every moment.
- Each stop can be turned off per project under efficiency (stop_on_owner_ruling, stop_on_no_progress, stop_on_repeated_gate_failure, all on by default), so a project that prefers the old behavior keeps it.
- The run report states which stop ended the run and what the next human action is.

### R6. Regression tests
- New test files under tests/, driving scripted runs through the runner with a fake runtime in the manner of tests/test_continuous_run_accounting.py: (a) a reviewer returning changes_requested with owner_ruling on the first attempt ends the run with exit_status owner_ruling_needed, the builder is called once, and the report and the comment carry the question; (b) the same review without the field loops back as today; (c) a second builder attempt that changes no file ends the run with no_progress and dispatches no reviewer for that attempt; (d) a gate that fails twice with the same unittest FAIL line ends the run with checks_stuck after the second attempt, and a gate whose second failure differs loops on; (e) a gate failure with no recognizable line never triggers checks_stuck; (f) with each stop turned off in configuration the run behaves as before this change; (g) a review file carrying owner_ruling passes the wrapper's validation and parse_review, and a non-string value is ignored.

### Guardrails
- Python standard library only. No new dependency.
- Authorized surface: anvil/runner.py, anvil/approver.py, anvil/model.py (the optional field on Review), anvil/gates.py (the failure signature), anvil/config.py (the three switches and the patterns), tools/claude_station.py (validate_review_file accepts the field; no other change), tools/line_comment.py, the reviewer station prompts under stations/reviewer-*/PROMPT.md (one added instruction each, nothing removed), docs/EXECUTION.md, docs/OPERATIONS.md, CHANGELOG.md, one new decision record under brain/decisions/, and new test files under tests/.
- Not touched: files under .github/workflows; pipeline files under pipelines/ and anvil.json (protected paths).
- Frozen: the review verdict vocabulary (pass, fail, changes_requested) and the run verdict vocabulary; the wording returned by review_suffix in tools/claude_station.py; the checks gate's pass or fail decision and its loopback accounting when no stop applies; the approval rules of anvil/line.py; cost-measurement semantics; the events contract.
- Known constraints from existing tests, stated here so the line does not discover them: tests/test_review_parsing_integrity.py and tests/test_review_producer.py pin the review contract wording and where correction logic lives (the wrapper, not the runner), and the second asserts that the word "retry" does not occur in anvil/runner.py; tests/test_continuous_run_accounting.py asserts the report's shape on every exit path and keeps its own list of exit statuses for the scenarios it covers; tests/test_governed_delivery.py asserts the event sequence. The instruction to reviewers goes in the packet the runner builds, not in review_suffix.
- If an existing protected test contradicts a requirement of this order, the builder says so in its report on the first attempt and stops; it does not work around it.
- Existing test files at the base ref are not modified or deleted; new tests arrive as new files.
- No em dash or en dash character in any produced file (project style rule).
- Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

## Scenarios

### Scenario: A reviewer asks for the owner and the line stops
- S1: Given a reviewer that returns changes_requested with an owner_ruling on the first attempt, when the approver runs, then no loopback is made, the run ends with exit_status owner_ruling_needed, the builder was called once, and the report and the final comment state the question.

### Scenario: An ordinary finding still loops back
- S2: Given the same review without owner_ruling, when the approver runs, then the work returns to the builder as it does today.

### Scenario: A builder that changes nothing ends the run
- S3: Given a loopback to the builder, when the next attempt leaves the tree outside runs/ unchanged, then no gate and no reviewer is dispatched for it and the run ends with exit_status no_progress.

### Scenario: The same test failing twice ends the run
- S4: Given a checks gate that fails on two consecutive attempts with the same recognized failure line, when the second failure is recorded, then no third attempt is made and the run ends with exit_status checks_stuck naming the line.

### Scenario: A different failure is progress
- S5: Given a checks gate whose second failure has a different signature from the first, when it is recorded, then the line loops back as today.

### Scenario: An unrecognized failure never stops the line early
- S6: Given a gate failure whose output matches no failure pattern, when it repeats, then the gate behaves as today.

### Scenario: Each stop can be turned off
- S7: Given a project that turns a stop off under efficiency, when its condition occurs, then the run behaves as it did before this change.

### Scenario: The review contract still holds
- S8: Given a review file carrying owner_ruling, when the wrapper validates it and the runner parses it, then it is accepted with its verdict and findings unchanged; given a non-string owner_ruling, then the field is ignored and the review still counts.
