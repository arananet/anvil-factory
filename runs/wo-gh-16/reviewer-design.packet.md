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
- Your verdict must be one of: `approved`, `changes_requested`, or `comment`.
- Produce the output as a JSON object, not as chat text.

## Output Format

Return a JSON object with this structure:

```json
{
  "station": "reviewer-design",
  "verdict": "approved | changes_requested | comment",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}
```

## Examples

### Example 1: No design system exists
```json
{
  "station": "reviewer-design",
  "verdict": "changes_requested",
  "findings": [
    "No design system exists for this project. The project must define design/DESIGN.md and design/tokens.json before interface output can be reviewed against design standards."
  ]
}
```

### Example 2: Interface violates quality bar
```json
{
  "station": "reviewer-design",
  "verdict": "changes_requested",
  "findings": [
    "Quality bar violation: Scale Contrast - The button text has only 2.8:1 contrast ratio against its background, failing the minimum 4.5:1 requirement stated in the quality bars.",
    "Token usage: The page uses hardcoded color '#FF5733' instead of the defined primary color token."
  ]
}
```

### Example 3: Interface meets design system
```json
{
  "station": "reviewer-design",
  "verdict": "approved",
  "findings": []
}
```


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

