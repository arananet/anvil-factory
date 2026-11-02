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
- Keep the change small and mapped to a spec scenario where one applies.


## Work order

- id: wo-gh-16
- kind: bug
- title: Review parsing integrity: one authoritative review channel, counted fail closed
- source: github-issue
- description: Spec: .openspec/specs/review-parsing-integrity/spec.md (slug review-parsing-integrity), approved and written before this implementation. Implement it in the factory.

The problem it solves: the runner counts reviews by scanning the executor free output for the first JSON object with a verdict key. Prose answers go uncounted (issue 2), and verdict shaped text that is not the station answer can be counted instead: on platform25 wo-gh-1 round 2 the parser counted the worked Example 1 inside stations/reviewer-design/PROMPT.md (a changes_requested review about a missing design system) instead of reviewer-design actual answer of pass with no findings, and the approver produced changes_requested on a finding that was false against the run own tree. The count looked complete, so counted versus expected could not flag it.

What to build, per the spec scenarios:

S1: One authoritative channel. For each reviewer station step in execute mode the runner designates runs/<work-order-id>/<station-id>.review.json, writes the executor returned output for that step to it verbatim before parsing, and counts reviews only by parsing that file. The free output transcript stays as provenance and is never parsed for a review.

S2: Whole document parse, no scanning. The review file must parse as exactly one JSON object (surrounding whitespace and one surrounding markdown code fence allowed) with station equal to the step station id, verdict one of pass, fail, changes_requested, and findings a list of strings. Remove the first match scanning from the review path; no code path counts a review from scanned text. Model provenance scanning is a different mechanism and stays untouched.

S3: Fail closed and reported, with shrinkage flagged in prose. A missing, empty or malformed review file records review_parse_failed in the step envelope and contributes zero reviews; a verdict is never guessed. When the counted review set is smaller than the expected set, the approver rule sentence in the run report decision object states both numbers (this closes item 3 of issue 2).

S4: The platform25 round 2 evidence shape counts as pass: output carrying the missing design system example object plus the station real pass review with empty findings in the authoritative channel counts reviewer-design as pass.

S5: Packet and prompt contract. Reviewer packets name the review file path and state that the station complete answer is exactly one review JSON object for that file. Every reviewer station PROMPT.md carries the same output contract. No reviewer prompt contains a worked example that parses as a review: remove such examples or rewrite them in non JSON form. Fix reviewer-design in particular: remove its three JSON examples and correct its verdict vocabulary to pass, fail, changes_requested. Align tools/claude_station.py so its runtime restatement names the same single JSON object contract and introduces no second channel. The deterministic reviewer-design rule for projects with no design system (project-design-system S5) is spine behavior outside the parser and stays unchanged.

S6: Regression tests in the factory suite, named for their scenarios: example object before the real review counts the real verdict; prose only output counts zero with review_parse_failed and the decision rule sentence stating counted and expected numbers; the platform25 evidence shape counts as pass; a catalog test that every reviewer prompt carries the contract and none contains a JSON object that parses as a review. Update docs/EXECUTION.md to state the new contract and add a CHANGELOG Unreleased entry. Keep the whole suite green, all eight pipelines valid, no station added, removed or renamed, and model routing untouched.

GitHub issue: https://github.com/arananet/anvil-factory/issues/16
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: executed
