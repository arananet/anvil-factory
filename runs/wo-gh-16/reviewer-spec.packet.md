# Task packet: reviewer-spec

## Station prompt

# Reviewer Spec

## Role
Check the implementation against the spec, nothing else.

## Inputs
- spec
- code change

## Outputs
- review

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.

## Output Format

Return a JSON object with this structure:

{
  "station": "reviewer-spec",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-spec", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.


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

LOOPBACK ROUND (final, authorized at the human gate on 2026-11-01). The round 1 implementation stands: authoritative review channel, whole document parse, fail closed, shrinkage sentence, regression tests, reviewer-design prompt contract. This round closes only the two counted S5 findings from round 1 and nothing else:
(a) Add the identical output contract section that stations/reviewer-design/PROMPT.md carries (its Output Format section) to the other eight reviewer station prompts: reviewer-spec, reviewer-security, reviewer-tests, reviewer-architecture, reviewer-platform, reviewer-voice, reviewer-brand, reviewer-facts, changing only the station id where the section names it. After this change no reviewer prompt contains a worked example that parses as a review.
(b) Resolve the packet versus wrapper wording tension: the packet output contract in anvil/runner.py, which names the review file path, is canonical. The runtime restatement in tools/claude_station.py either repeats that statement word for word or defers to the packet without restating contract terms, so the two channels cannot diverge.
Extend the S5 catalog tests so the suite asserts both items: every reviewer prompt carries the contract section, and the wrapper restatement matches or defers. Keep the whole suite green, all eight pipelines valid, no station added, removed or renamed, model routing untouched, parser behavior unchanged. Do not rewrite or condense the spec in this round.

LOOPBACK ROUND 2 (final, loopbacks 2 of max 2, recorded by the loopback round 1 run report itself with return_to builder; authorized because Edu ordered everything pending finished on 2026-11-02). The round 1 and loopback round 1 implementations stand: the authoritative review channel, the whole document parser, fail closed, the shrinkage sentence, the regression tests, and L1 (all nine reviewer prompts carry the identical Output Format section). This round closes only the one counted finding from the loopback round 1 run and the compliance defect that run exposed, and nothing else.

COUNTED FINDING (reviewer-security, the only review counted in the loopback round 1 run, quoted verbatim): "L2 incomplete: tools/claude_station.py REVIEW_SUFFIX defers to the packet ('The output contract is stated in the packet above') but then restates contract terms ('Your complete answer is exactly one review JSON object in this shape'). Per loopback spec L2, the wrapper must either repeat the canonical wording from anvil/runner.py word-for-word OR defer without restating. Currently it does both, creating divergent contract statements. Fix: either remove the restatement (keep only 'The output contract is stated in the packet above.') or repeat the canonical file path wording verbatim from anvil/runner.py lines 150-153."

Part 1, the L2 fix exactly as the counted finding prescribes. The finding offers two compliant shapes: (i) the wrapper repeats the canonical wording from anvil/runner.py word for word, or (ii) the wrapper defers to the packet without restating contract terms, keeping only 'The output contract is stated in the packet above.'. Choose one shape and state the reasoning in the builder output. Evidence the choice must weigh: in the loopback round 1 run, 4 of 5 reviewer stations ignored a contract stated once in the packet and answered in prose, so parse_review failed closed on their files and only 1 of 5 reviews counted; verbatim repetition at the wrapper level puts the canonical wording in the last text the station sees, which is the compliance argument for shape (i); pure deferral keeps a single source of the wording, which is the single source argument for shape (ii). Either shape is acceptable if implemented exactly. A hybrid that restates the contract in new words is the defect itself and must not recur: after this fix, every statement of the output contract anywhere in the prompt path is either the canonical wording verbatim or a deferral that states no contract terms. Note that the canonical packet wording in anvil/runner.py is parameterized by work order id and station id (it names runs/<work-order-id>/<station-id>.review.json); word for word means the same sentence with those parameters resolved the same way, not a hardcoded literal path. Extend the S5 catalog tests so the suite asserts the chosen shape exactly: for shape (i), that the wrapper suffix states the canonical packet sentence word for word including the review file path for the station being run; for shape (ii), that the wrapper suffix states no contract terms beyond the deferral sentence.

Part 2, reviewer compliance with the existing contract. The loopback round 1 run exposed the deeper defect: 4 of 5 reviewer stations wrote prose markdown into the authoritative channel (reviewer-spec, reviewer-tests, reviewer-architecture and reviewer-design .review.json files said pass in prose), parse_review failed closed on all four and named them as parse failures, and only 1 of 5 reviews counted. The parser behaved exactly as designed and is frozen in this round: no parsing prose, no extracting verdicts from text, no loosening parse_review, no change to the contract content and no change to the review file format. Within the station prompt surface only (the packet assembly and the packet closing line in anvil/runner.py, the wrapper suffix in tools/claude_station.py, and placement or repetition of the contract inside the reviewer station prompts), strengthen compliance so that in this re-run every reviewer station's complete answer is exactly one review JSON object (one surrounding markdown code fence allowed) and lands in its .review.json file in that form. Every repetition of the contract anywhere must be the canonical wording verbatim; no new wording of the contract may be introduced. If the builder concludes that no prompt level lever remains beyond part 1, it must say so plainly in its output rather than invent machinery.

Success measure for this round, to be read from the run report: the compliance count, how many of the 5 expected reviewers emit a review file that parses and counts, alongside the verdict. Keep the whole suite green, all eight pipelines valid, no station added, removed or renamed, model routing untouched, parser behavior unchanged. Do not rewrite or condense the spec in this round.
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: executed
- test-writer: executed
- builder: executed

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-16/reviewer-spec.review.json. The free output transcript stays as provenance and is never parsed for a review.
