# Review Parsing Integrity

Status: approved
Slug: review-parsing-integrity

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
A run verdict is a claim about what independent reviewers said. Today the runner finds reviews by scanning the executor's free output for the first JSON object that carries a verdict key, so the verdict depends on whatever verdict shaped text reaches the output. Prose answers go uncounted (issue 2), and a worked example shipped inside a reviewer station prompt can be counted as the station's answer: on platform25 wo-gh-1 round 2 the parser counted reviewer-design's prompt Example 1, a changes_requested review about a missing design system, instead of the station's actual answer of pass with no findings, and the approver produced a changes_requested verdict on a finding that was false against the run's own tree. The count even looked complete, five of five, so the counted versus expected fields could not flag it. The same mechanism could ingest a pass example and approve work nobody approved. This spec gives every reviewer exactly one authoritative channel, makes the parser read only that channel as one whole document, removes mistakable examples from the prompts, and makes every failure to produce a valid review visible and fail closed.

## Requirements
- One authoritative channel per reviewer. For each reviewer station step in execute mode, the runner designates a review file at runs/<work-order-id>/<station-id>.review.json in the run directory. When the step executes, the runner writes the executor's returned output text for that step to the review file verbatim, before any parsing, and the review file is kept as run evidence either way. The review file is the only text the review parser reads for that station. The free output transcript (<station-id>.output.md) remains provenance and is never parsed for a review.
- Whole document parse, no scanning. The parser parses the review file as exactly one JSON document: the whole file content, allowing surrounding whitespace and one surrounding markdown code fence, must be a single JSON object with station (a string equal to the step's station id), verdict (one of pass, fail, changes_requested) and findings (a list of strings). Anything else is not a review. The first match scanning of free text is removed from the review path, and no code path counts a review from scanned text. Model provenance scanning (the executed model reported by a runtime) is a different mechanism and is untouched.
- Fail closed and reported. If the review file is missing, empty, not one JSON document, has an invalid verdict, a station that does not match the step, or findings that are not a list of strings, the step envelope records review_parse_failed, the station contributes no review to the run, and the failure stays visible in the run report. A verdict is never guessed from prose or from a partial object.
- Shrinkage is flagged in the rule sentence. The approver decision object already records the counted reviews and the expected reviewers. When the counted set is smaller than the expected set, the approver rule sentence stored in the decision object states both numbers, so a shrunken review set is flagged in the rule text itself and not only in the count fields (this closes item 3 of issue 2).
- The packet and every reviewer prompt carry the contract. The packet for a reviewer station names its review file path and states that the station's complete answer is exactly one review JSON object for that file, in the shape of templates/review.json. Every reviewer station PROMPT.md in the factory catalog carries the same output contract. No reviewer prompt contains a worked example that parses as a review: examples are removed or rewritten in non JSON form, as prose or as a field table whose values are placeholder words. This includes reviewer-design, whose prompt ships three JSON examples and names verdicts (approved, comment) that the review vocabulary does not contain; its vocabulary is corrected to pass, fail, changes_requested.
- The executor wrapper states the same contract and no second channel. tools/claude_station.py keeps restating the output contract for reviewer stations at runtime, worded to name the single JSON object answer and the review file discipline. It must not introduce another channel or another shape.
- The deterministic reviewer-design rule for projects with no design system (project-design-system S5) is spine behavior that never passes through the parser. It is unchanged by this spec.
- Regression tests ship in the factory suite, named for their scenarios, covering: an example verdict object appearing in executor output before the station's real review counts the real verdict; a prose only reviewer output counts zero for that station, records review_parse_failed, and the decision rule sentence states the counted and expected numbers; the platform25 round 2 evidence shape (the missing design system example plus a real pass with empty findings) counts as pass; and a catalog test asserting every reviewer prompt carries the contract and none contains a JSON object that parses as a review.
- Docs and changelog follow the factory discipline: docs/EXECUTION.md states the new contract (the review file, the whole document parse, the fail closed counting), and the CHANGELOG Unreleased section gains an entry.
- No collateral change. The eight pipelines validate unchanged, no station is added, removed or renamed, model routing is untouched, and review provenance recording (configured model, executed model) is untouched.

## Scenarios

### Scenario: The review file is the only parse source
- S1: Given a reviewer station step in execute mode, when the step finishes, then runs/<work-order-id>/<station-id>.review.json exists holding the step's output verbatim, and any review counted for that station comes only from parsing that file as one JSON document.

### Scenario: An example in the output cannot be counted
- S2: Given a reviewer step whose executor output contains a verdict shaped example object (a changes_requested review stating that no design system exists) before the station's actual review, when the run counts reviews, then the counted verdict is the station's actual verdict, not the example's.

### Scenario: A prose only review fails closed and is reported
- S3: Given a reviewer step whose output is prose only, when the run counts reviews, then that station contributes zero reviews, its step envelope records review_parse_failed, and the approver rule sentence in the decision object states the counted and expected numbers.

### Scenario: The platform25 round 2 evidence shape counts as pass
- S4: Given a reviewer-design step whose output reproduces the platform25 wo-gh-1 round 2 shape (the missing design system example object plus the station's real review of pass with empty findings in the authoritative channel), when the run counts reviews, then reviewer-design counts as pass.

### Scenario: Prompts carry the contract and no parseable example
- S5: Given the shipped station catalog, when every reviewer station prompt is read, then each carries the output contract naming the review file and the vocabulary pass, fail, changes_requested, and none contains a JSON object that parses as a review.

### Scenario: The suite and the pipelines stay whole
- S6: Given the change is complete, when the factory suite runs and every pipeline is validated, then the whole suite passes, including the new regression tests, and all eight pipelines validate.
