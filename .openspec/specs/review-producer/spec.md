# Review Producer

Status: approved
Slug: review-producer

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

Fix how a review file is produced. Today a reviewer station cannot write its own runs/<work-order-id>/<station-id>.review.json: tools/claude_station.py disallows Edit, Write and NotebookEdit for reviewer stations, so the runner transcribes the executor returned output (the station stdout) into the review file verbatim and parses that. The authoritative review therefore depends on the model final chat message being exactly one JSON object, which measured runs show it usually is not: 2 of 5 counted on the wo-gh-16 closing loopback, 1 of 5 on wo-gh-20, 0 of 5 on wo-gh-21 round 1 and on the wo-gh-6 loopback, where all five reviewers substantively passed in prose and no verdict could be reached. The parser from review-parsing-integrity is proven and is not the defect: it fails closed correctly on whatever the channel contains. This spec changes production of the file, never its contract or its counting.

## Requirements

- A reviewer station may write exactly one path: its own runs/<work-order-id>/<station-id>.review.json for the run in progress. Every other write or edit through the file editing tools stays disallowed for reviewer stations, at the same tool permission layer that enforces the current denylist. The separation of duties the security reviews validated (a reviewer never modifies the tree it judges) is preserved.
- The runner never writes executor output into the review file. After the reviewer step executes, the runner reads the review file the station itself wrote and parses its content with parse_review, whose semantics are unchanged. The executor output remains in the station output record as provenance only.
- Absence is meaningful: before a reviewer step executes, the runner removes any pre-existing file at that station review path, so a file present at station exit was produced during this run. If no file exists when the station exits, the step records a producer failure named review_file_missing, distinct from review_parse_failed, and the station contributes zero reviews. The run report preserves the distinction per station so the approver and the reader see which stations failed to produce a file and which produced an unparsable one.
- At station exit the wrapper validates the review file with the same acceptance rules parse_review applies: the file exists, its content parses as exactly one JSON object (surrounding whitespace and one surrounding markdown code fence allowed), the station field equals the station id, and the verdict is one of pass, fail, changes_requested. On a missing or malformed file the wrapper returns the specific validation error to the same station session once and asks for the file to be written correctly. A second failure stands as the recorded review_file_missing or review_parse_failed. The correction is bounded at one per station, and the run report records for each reviewer station whether the correction fired.
- Frozen surfaces: parse_review semantics; the canonical contract wording in anvil/runner.py; the Output Format sections of the nine reviewer station prompts; the wrapper review_suffix that repeats the canonical wording word for word. The regression and catalog tests merged under review-parsing-integrity keep passing unchanged in what they assert.
- Builder and test-writer keep their existing write access. Non reviewer stations are unchanged. No station is added, removed or renamed; the eight pipelines stay valid; model routing is untouched.

## Scenarios

### Scenario: Scoped write for reviewers
- S1: Given a reviewer station step in execute mode, when the station runs, then it can write its own runs/<work-order-id>/<station-id>.review.json, and a write or edit attempt through the file editing tools to any other path is refused by the tool permission layer.

### Scenario: The channel is the file the reviewer wrote
- S2: Given a reviewer station step in execute mode, when the step completes, then the runner counts the review only by parsing the content of the review file present on disk, a file the runner did not write; the executor output text is kept as provenance and is never the parsed source, even when the output itself contains a valid review object.

### Scenario: Missing file is a named producer failure
- S3: Given a reviewer station that exits without writing its review file, when the runner processes the step, then it records review_file_missing for that station, the station contributes zero reviews, the failure is distinguishable from review_parse_failed in the step record and the run report, and a stale file from a previous run of the same work order never substitutes for the missing one.

### Scenario: One in-session correction
- S4: Given a reviewer station whose review file at exit is missing or fails validation, when the wrapper detects it, then it returns the specific error to the same station session once; if the station then writes a valid file, the review counts and the run report records that the correction fired for that station; if the file is still missing or malformed, the recorded review_file_missing or review_parse_failed stands and no further correction is attempted.

### Scenario: Frozen contract and counting
- S5: Given the factory after this change, when the review-parsing-integrity regression and catalog tests run, then they pass unmodified: the whole document parse, the fail closed rule, the shrinkage sentence and the prompt and wrapper wording assertions all behave exactly as merged at d6e503b3.

### Scenario: Regression tests in the factory suite
- S6: Given the factory test suite, when it runs, then it includes tests named for their scenarios: a reviewer that writes a valid file is counted from the file content; a reviewer whose stdout holds a valid review object but writes no file yields review_file_missing and counts zero; a reviewer that writes prose into the file fails closed as review_parse_failed; a missing first attempt rescued by the correction loop counts and records the correction; a write attempt outside the allowed path is refused by the permission configuration the wrapper builds for a reviewer station; and the whole suite stays green with all eight pipelines valid.
