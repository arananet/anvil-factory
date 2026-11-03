# Task packet: reviewer-design

## Station prompt

# Reviewer Design

## Role
Judge interface output against the project's own design system: its design tokens, component and layout rules, motion rules, and quality bars.

## Inputs
- design system (tokens, rules, quality bars from design/DESIGN.md and design/tokens.json)
- interface output (HTML, React components, CSS, user-facing pages, or other interface artifacts)

## Outputs
- review (JSON format with verdict and findings)

## Rules
- Work only from the inputs listed above and the work order in the packet.
- If the project has no design system (no design/DESIGN.md), your verdict MUST be `changes_requested` with a finding stating that no design system exists for the project.
- If the project has a design system, review the interface output against:
  - Design tokens: Are the correct colors, typography, spacing values being used?
  - Component and layout rules: Do components follow the documented patterns?
  - Motion rules: Does any animation or transition follow the motion guidelines?
  - Quality bars: Does the interface meet the stated quality bars for visual hierarchy, scale contrast, spacing rhythm, and responsive behavior?
- Focus on the design system the project has defined. Do not impose external design opinions or preferences that are not documented in the project's design system.
- A design token marked as "TODO" or placeholder means the project hasn't defined that value yet. Flag missing values as findings only if the interface output actually uses undefined tokens.
- Findings should be specific and actionable: cite which quality bar was violated, which token was used incorrectly, or which rule was not followed.
- Your verdict must be one of: `pass`, `fail`, or `changes_requested`.
- Produce the output as a JSON object, not as chat text.

## Output Format

Return a JSON object with this structure:

{
  "station": "reviewer-design",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-design", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.

## Examples

Example 1: No design system exists
- verdict: changes_requested
- finding: "No design system exists for this project. The project must define design/DESIGN.md and design/tokens.json before interface output can be reviewed against design standards."

Example 2: Interface violates quality bar
- verdict: changes_requested
- findings:
  * "Quality bar violation: Scale Contrast - The button text has only 2.8:1 contrast ratio against its background, failing the minimum 4.5:1 requirement stated in the quality bars."
  * "Token usage: The page uses hardcoded color '#FF5733' instead of the defined primary color token."

Example 3: Interface meets design system
- verdict: pass
- findings: (empty list)


## Work order

- id: wo-gh-24
- kind: bug
- title: Review producer: reviewers write their own review file (one scoped path, one in-session correction)
- source: github-issue
- description: Implement the spec in .openspec/specs/review-producer/spec.md in the factory. Pipeline for this order is sdlc-default, selected by the run workflow.

The defect: reviewer stations run with Edit, Write and NotebookEdit disallowed in tools/claude_station.py, so a reviewer cannot write its own runs/<work-order-id>/<station-id>.review.json. The runner transcribes the executor returned output into that file verbatim (anvil/runner.py, the reviewer step handling) and parses the transcript. The authoritative review therefore depends on the model final chat message being exactly one JSON object. Measured cost of that dependence: wo-gh-16 closing loopback counted 2 of 5 (three reviewers answered in prose), wo-gh-20 counted 1 of 5, wo-gh-21 round 1 counted 0 of 5, and the wo-gh-6 loopback counted 0 of 5 with all five reviewers substantively passing in prose on a complete implementation, so the capability program item 1 verdict is unreachable. The parser merged in wo-gh-16 is proven and is not the defect: it fails closed correctly on whatever the channel contains.

Build, per the spec scenarios:

S1, scoped write: in tools/claude_station.py, a reviewer station may write exactly one path, its own runs/<work-order-id>/<station-id>.review.json for the run in progress. Every other write or edit through the file editing tools stays disallowed at the tool permission layer. The mechanism (path scoped tool rules, a per run permission configuration, or an equivalent the wrapper constructs) is the builder choice; the observable behavior is the spec: the one path writable, a write attempt to any other path refused. Builder and test-writer keep their existing access; Bash availability for reviewers is unchanged (it is how a tests reviewer runs the suite today).

S2, the channel is the file: in anvil/runner.py, remove the transcription of executor output into the review file. The runner reads the review file the station wrote and parses its content with parse_review (semantics unchanged). Before a reviewer step executes, remove any pre-existing file at that station review path so presence at exit means produced in this run. The special handling for reviewer-design when no design system exists stays as it is.

S3, review_file_missing: when no review file exists at station exit, record a producer failure named review_file_missing in the step record, distinct from review_parse_failed, contributing zero reviews. The run report preserves the distinction per station.

S4, one in-session correction: at station exit the wrapper validates the review file with the same acceptance rules parse_review applies (exists; parses as exactly one JSON object with surrounding whitespace and one surrounding code fence allowed; station field matches; verdict one of pass, fail, changes_requested). On a missing or malformed file it returns the specific error to the same station session once and asks for the file to be written correctly. A second failure stands. The correction is bounded at one per station and the run report records for each reviewer station whether it fired (through whatever step record channel the implementation establishes; state it in the builder output).

Frozen surfaces (S5): parse_review semantics; the canonical contract wording in anvil/runner.py; the Output Format sections of all nine reviewer prompts; the wrapper review_suffix repeating the canonical wording word for word. The review-parsing-integrity regression and catalog tests keep passing unmodified in what they assert.

Tests (S6), named for their scenarios in the factory suite: a reviewer that writes a valid file is counted from the file content; a reviewer whose stdout holds a valid review object but writes no file yields review_file_missing and counts zero; a reviewer that writes prose into the file fails closed as review_parse_failed; a missing or malformed first attempt rescued by the correction loop counts and the correction is recorded; a write attempt outside the allowed path is refused by the permission configuration the wrapper builds for a reviewer station. Update docs/EXECUTION.md to state the new producer contract and add a CHANGELOG Unreleased entry. Keep the whole suite green, all eight pipelines valid, no station added, removed or renamed, and model routing untouched. Runtime code stays on the Python standard library only. No em dash or en dash character in any produced file (project style rule).

Review channel discipline, restated for every reviewer station in this run: your review is exactly one JSON object that YOU write to runs/wo-gh-24/<your station>.review.json, and nothing else in that file. Prose and narrative belong in your .output.md only. Under the change this very order builds, a review you only say in chat is not produced at all: if you do not write the file, the run records review_file_missing against your station.

GitHub issue: https://github.com/arananet/anvil-factory/issues/24

LOOPBACK ROUND (gate round 2, operator brief). Round 1 executed the full line (Actions run 41586666849): every station executed and the builder implemented the scope, but the workflow commit back step failed (a tracked run-diff.txt, rewritten by the step after staging, blocked its rebase), so NOTHING from round 1 landed on this branch. This tree is still main plus the order setup. Rebuild the full spec scope in this round; do not assume any round 1 code exists. The operator has repaired the commit back step in this branch workflow (one added staging line); do not modify the workflow.

Round 1's reviews were counted 0 of 5 under the producer loaded at run start (all five answered in prose), so there is no verdict of record; but the five reviewers' substantive findings were recovered from the run evidence and are this round's additional scope, quoted in substance:

F1, dual correction (reviewer-spec and reviewer-architecture): round 1 implemented the correction in BOTH tools/claude_station.py and anvil/runner.py, so a station could receive two corrections, violating the spec bound of one. In this round the correction lives in exactly one place: the wrapper, at station exit, as spec S4 states. The runner contains no correction logic: it reads the file that stands when the step returns and records review_file_missing or review_parse_failed accordingly.

F2, frozen suite not green (reviewer-tests and reviewer-architecture): round 1 left 12 tests failing in tests/test_review_parsing_integrity.py, while the builder output claimed all regression tests passing. The failure mode, per reviewer-tests: the old fixtures still expect the runner to transcribe output. Resolution rule for this round: fixtures that simulate the old production mechanism may be adapted so the fixture produces the review the way the new producer does (the fake executor writes the file, or the fixture pre-writes it), while every assertion about parse semantics, fail closed behavior, the shrinkage sentence and the contract wording stays exactly as wo-gh-16 merged it. Weakening, renaming away or deleting an assertion is a spec violation. Success measure: the FULL factory suite green in this run, as executed and reported by reviewer-tests, not as summarized by the builder. If the builder believes a specific wo-gh-16 assertion is genuinely incompatible with the new producer, it must name that assertion in its output and leave the test untouched rather than editing it silently.

F3, path traversal (reviewer-security, critical): the scoped write path is derived from the work order id parsed out of the packet; an id carrying path separators or parent references could make the one allowed path escape runs/<work-order-id>/. In this round, validate every packet derived value used to build a filesystem path (work order id, station id): reject or neutralize anything that would resolve outside the intended directory, with a regression test that attempts the escape. Audit the new wrapper and runner path construction for the same class, not only the one call site.

Review channel discipline for THIS run, read carefully: this run is still counted by the producer loaded at its start, which transcribes stdout. Your complete stdout answer must therefore be exactly one review JSON object (one surrounding markdown code fence allowed) and nothing else; prose in stdout is not counted, which is how round 1 reached 0 of 5. Separately, the wrapper rebuilt in this run is live from the builder step onward, so you will be able to write your review file yourself: write the same single JSON object to runs/wo-gh-24/<your station>.review.json. Both channels carry the same object; narrative belongs in your .output.md only.

LOOPBACK ROUND 3 (final gate loopback, operator dispatched 2026-11-03). Round 2 outcome: verdict approved, but only 1 of 5 reviews counted (reviewer-design, pass), because the runner process loaded at run start was still the pre-fix runner, which transcribed reviewer stdout over the review files the reviewers had written with the rebuilt wrapper. The round 2 implementation stands and is the base of this round. This run starts with the fixed producer governing from run start, so its counted reviews are the first full live test of the fix. Two bounded findings from the round 2 reviews are this round's only scope; fix them and nothing else.

Finding 1 (reviewer-spec): spec S3 assigns removal of a pre-existing review file to the runner, and anvil/runner.py does it before invoking the executor. The wrapper in tools/claude_station.py also removes it (the block near lines 178 to 184 in the round 2 tree). Remove the wrapper's duplicate removal so the responsibility lives in exactly one place, as S3 states. Keep the runner behavior unchanged.

Finding 2 (reviewer-architecture): validate_path_component is duplicated between anvil/model.py and tools/claude_station.py. Resolve the duplication risk in the smallest sound way: either one shared implementation both sides use, or, if the wrapper must stay standalone, explicit synchronization notes in both copies plus a test that pins the two implementations to identical behavior on the traversal cases. Do not weaken any validation case.

Everything else is frozen: parse_review semantics, the canonical contract wording in anvil/runner.py, the nine reviewer prompts' Output Format sections, the wrapper's verbatim review_suffix, model routing, the station set, and every existing test assertion. Full factory suite green and all eight pipelines valid. Reviewer discipline in this run: your review file is the channel. Write exactly one JSON object to your own runs/wo-gh-24/<station>.review.json and keep narrative in your .output.md.
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: executed
- test-writer: executed
- builder: executed
- reviewer-spec: executed
- reviewer-security: executed
- reviewer-tests: executed
- reviewer-architecture: executed

## Project design

### Design tokens

```json
{
  "colors": {
    "primary": "TODO",
    "secondary": "TODO",
    "accent": "TODO",
    "background": "TODO",
    "surface": "TODO",
    "text": "TODO",
    "text-secondary": "TODO",
    "error": "TODO",
    "warning": "TODO",
    "success": "TODO",
    "info": "TODO"
  },
  "typography": {
    "font-family-base": "TODO",
    "font-family-heading": "TODO",
    "font-family-mono": "TODO",
    "font-size-base": "TODO",
    "font-size-scale": "TODO",
    "line-height-base": "TODO",
    "line-height-heading": "TODO"
  },
  "spacing": {
    "unit": "TODO",
    "scale": [
      "TODO"
    ]
  },
  "layout": {
    "max-width": "TODO",
    "breakpoint-mobile": "TODO",
    "breakpoint-tablet": "TODO",
    "breakpoint-desktop": "TODO"
  },
  "motion": {
    "duration-fast": "TODO",
    "duration-base": "TODO",
    "duration-slow": "TODO",
    "easing-standard": "TODO",
    "easing-enter": "TODO",
    "easing-exit": "TODO"
  }
}
```

### Quality bars

for Product Pages

These bars apply to every product page or interface this project ships.

### Visual Hierarchy
- [ ] Clear content hierarchy with size, weight, and spacing
- [ ] Important actions are visually prominent
- [ ] Related elements are grouped

### Scale Contrast
- [ ] Minimum 4.5:1 contrast ratio for normal text
- [ ] Minimum 3:1 contrast ratio for large text (18pt+)
- [ ] Interactive elements have sufficient contrast

### Spacing Rhythm
- [ ] Consistent spacing scale used throughout
- [ ] Whitespace creates clear content boundaries
- [ ] Spacing adapts appropriately to different screen sizes

### Responsive Behavior
- [ ] Layout works on mobile, tablet, and desktop
- [ ] Touch targets are at least 44x44px on mobile
- [ ] Text is readable without zooming on any device
- [ ] No horizontal scrolling on standard viewports


## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-24/reviewer-design.review.json. The free output transcript stays as provenance and is never parsed for a review.
