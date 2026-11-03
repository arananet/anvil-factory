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

- id: wo-gh-7
- kind: feature
- title: Intake outcomes: reject, rescope, needs-info parking, risk and surfaces
- source: github-issue
- description: Implement the spec in .openspec/specs/intake-outcomes/spec.md in the factory.

Build, per the spec scenarios:

S1: intake can REJECT a work order whose purpose is harmful, deceptive or unlawful, with reasons recorded on the work order; rejection is terminal, the runner spawns no further station, the work order status becomes rejected, and the report and swimlane show the rejection and its reasons.

S2: intake can RESCOPE an oversized or vague work order: the description becomes the buildable scope, the outcome record states what was cut and why, and downstream packets carry the rescoped description.

S3: intake can answer NEEDS-INFO: outcome waiting_info, questions recorded, work order status waiting_info, nothing further spawns, and the report records a waiting state rather than a pass or a failure. When answers are recorded and the work order returns to a runnable status, a later run proceeds from intake again.

S4: accepted and rescoped work orders carry intake's risk rating (low, medium, high) and surfaces list from the spec's vocabulary; both appear in the run report.

S5: rejected and waiting runs render honestly: no station beyond intake listed as executed, reasons and questions shown, neither rendered as approved.

The work order model gains the intake outcome record (outcome, reasons, questions, rescoped description, risk, surfaces). Intake's station prompt and contract describe all four outcomes, the refusal class, the rescope discipline and the risk and surface vocabulary. Tests covering S1 to S5 in the factory suite style, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/7

LOOPBACK ROUND (operator note, 2026-11-03). The first execute run of this order (41600186914) implemented S1 to S5 and four of five reviewers passed with all five reviews counted. reviewer-security requested changes with five findings, quoted verbatim below. This round fixes exactly these findings and nothing else; the S1 to S5 behavior the other reviewers passed stays as it stands.

Finding 1: "Missing input validation for intake_outcome structure in WorkOrder model (anvil/model.py:45): The intake_outcome dict accepts arbitrary keys and values without validation. An executor could inject invalid outcome values (not in accepted/rejected/rescoped/waiting_info), missing required fields (reasons for rejected, questions for waiting_info), or wrong types. The __post_init__ method validates work order ID but not intake_outcome structure."
Finding 2: "Missing input validation for risk field in WorkOrder model (anvil/model.py:46): The risk field accepts any string value but should be constrained to {low, medium, high, None}. Invalid risk values like 'CRITICAL' or 'javascript:alert(1)' are accepted and would be written to work order files and reports."
Finding 3: "Missing input validation for surfaces field in WorkOrder model (anvil/model.py:47): The surfaces list accepts arbitrary string values but should be constrained to the vocabulary {ui, security, data, payments, deploy, content, api} per the spec. Invalid or malicious surface names are accepted and included in reports."
Finding 4: "Unsafe trust of executor output in runner.py:449-465: The code directly assigns executor-parsed JSON to work_order fields without validation. Lines 450, 463, 465 trust that intake_data contains well-formed outcome/risk/surfaces data. A compromised or buggy executor could inject malformed data that bypasses validation since the WorkOrder fields lack validation in __post_init__."
Finding 5: "Potential content injection in report markdown rendering (runner.py:919-949): The intake outcome reasons, questions, and rescoped_description are written directly to report.md without sanitization. If these contain markdown syntax or HTML, they render as-is. Example: a reason containing [malicious link](javascript:...) or backticks with command injection syntax would be written verbatim to the markdown report."

Fix shape: validate in the WorkOrder model (single owner of the vocabularies: outcome values, per outcome required fields, risk set, surfaces set) so both direct construction and the runner's executor parsed assignment are covered by the same validation; invalid data fails loudly with a named error, never silently coerced. Render intake text in report markdown safely (escaped or fenced as data) so reasons, questions and the rescoped description cannot inject markdown or links. Add tests in the factory suite style covering each rejected shape and the safe rendering. Update the CHANGELOG Unreleased note if the first round added one. Keep the whole suite green and every pipeline valid. Every reviewer writes its review to the authoritative review file named in its packet, as one JSON document the parser can read whole; prose in that file is not a review and fails the run closed.
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: failed
- loopback: loopback
- reviewer-spec: skipped
- reviewer-security: skipped
- reviewer-tests: skipped
- reviewer-architecture: skipped

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

Your complete answer is exactly one review JSON object written to runs/wo-gh-7/reviewer-design.review.json. The free output transcript stays as provenance and is never parsed for a review.
