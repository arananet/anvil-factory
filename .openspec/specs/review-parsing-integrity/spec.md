# Review Parsing Integrity

Status: approved
Slug: review-parsing-integrity

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
Establish one authoritative review channel per reviewer station step, parse the whole document without scanning, fail closed on malformed reviews, and report shrinkage when counted reviews are fewer than expected.

## Requirements
- For each reviewer station step in execute mode, the runner designates runs/<work-order-id>/<station-id>.review.json as the authoritative review channel, writes the executor returned output to it verbatim before parsing, and counts reviews only by parsing that file. The free output transcript stays as provenance and is never parsed for a review.
- The review file must parse as exactly one JSON object (surrounding whitespace and one surrounding markdown code fence allowed) with station equal to the step station id, verdict one of pass, fail, changes_requested, and findings a list of strings. No code path counts a review from scanned text. Model provenance scanning is a different mechanism and stays untouched.
- A missing, empty or malformed review file records review_parse_failed in the step envelope and contributes zero reviews; a verdict is never guessed.
- When the counted review set is smaller than the expected set, the approver rule sentence in the run report decision object states both numbers.
- Reviewer packets name the review file path and state that the station complete answer is exactly one review JSON object for that file.
- Every reviewer station PROMPT.md carries the same output contract. No reviewer prompt contains a worked example that parses as a review.
- The runtime restatement in tools/claude_station.py names the same single JSON object contract and introduces no second channel.
- The deterministic reviewer-design rule for projects with no design system (project-design-system S5) is spine behavior outside the parser and stays unchanged.

## Scenarios

### Scenario: One authoritative channel
- S1: Given a reviewer station step in execute mode, when the runner processes the step, then it writes the executor output to runs/<work-order-id>/<station-id>.review.json and counts reviews only by parsing that file, never from the free output transcript.

### Scenario: Whole document parse, no scanning
- S2: Given a review file, when the runner parses it, then it must parse as exactly one JSON object (surrounding whitespace and one surrounding markdown code fence allowed) with station equal to the step station id, verdict one of pass, fail, changes_requested, and findings a list of strings, with no code path counting a review from scanned text.

### Scenario: Fail closed and reported, with shrinkage flagged in prose
- S3: Given a missing, empty or malformed review file, when the runner processes it, then it records review_parse_failed in the step envelope, contributes zero reviews, and when counted reviews are fewer than expected, the approver rule sentence states both counted and expected numbers.

### Scenario: Platform25 round 2 evidence shape counts as pass
- S4: Given output carrying a non-review example object plus the station real pass review with empty findings in the authoritative channel, when the runner parses it, then it counts the reviewer station as pass.

### Scenario: Packet and prompt contract
- S5: Given reviewer packets and PROMPT.md files, when they are checked, then packets name the review file path and state the complete answer is exactly one review JSON object, every PROMPT.md carries the same output contract, no PROMPT.md contains a worked example that parses as a review, reviewer-design has its three JSON examples removed and verdict vocabulary corrected to pass, fail, changes_requested, and tools/claude_station.py runtime restatement names the same single JSON object contract.

### Scenario: Regression tests in the factory suite
- S6: Given the factory test suite, when it runs, then it includes tests named for their scenarios: example object before the real review counts the real verdict; prose only output counts zero with review_parse_failed and the decision rule sentence stating counted and expected numbers; the platform25 evidence shape counts as pass; and a catalog test that every reviewer prompt carries the contract and none contains a JSON object that parses as a review, while keeping the whole suite green, all eight pipelines valid, no station added, removed or renamed, and model routing untouched.

## Loopback round (final, authorized at the human gate 2026-11-01)

Round 1 landed the authoritative review channel, the whole document parser, the fail closed rule, the shrinkage sentence in the decision rule, the regression tests, and the reviewer-design prompt contract. Its verdict was changes_requested on two S5 items only, counted by reviewer-spec and reviewer-architecture. This loopback closes exactly those two items and nothing else:

- L1: Every reviewer station PROMPT.md carries the same output contract section. Round 1 added the section to stations/reviewer-design/PROMPT.md only (its Output Format section, with the worked examples rewritten in non JSON form and the verdict vocabulary corrected to pass, fail, changes_requested). Add the identical section to the other eight reviewer prompts: reviewer-spec, reviewer-security, reviewer-tests, reviewer-architecture, reviewer-platform, reviewer-voice, reviewer-brand, reviewer-facts. Identical means the same section text and structure, with only the station id changed where the section names it. After this change, no reviewer prompt in any station contains a worked example that parses as a review.
- L2: One canonical contract wording. The packet output contract in anvil/runner.py, the section that names the review file path runs/<work-order-id>/<station-id>.review.json, is the canonical statement of the contract. The runtime restatement in tools/claude_station.py must not state a second, divergent contract: it either repeats the canonical statement word for word or defers to the packet section without restating contract terms. After this change the two channels cannot diverge: no channel omits the review file path while presenting itself as the complete contract, and no channel words the verdict vocabulary differently.

Tests: extend the S5 catalog coverage in the factory suite so the suite itself asserts both items: every reviewer PROMPT.md carries the output contract section, and the wrapper restatement matches the canonical packet wording or defers to it. The whole suite stays green, all eight pipelines valid.

Frozen in this round: parser behavior and the review file format; the eight pipelines; the station set (none added, removed or renamed); model routing; the round 1 implementation in anvil/runner.py apart from wording alignment required by L2; and the substance of every requirement and scenario above. The spec is not condensed or rewritten in this round; this section is the operative scope.
