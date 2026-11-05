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


<!-- source: design/DESIGN.md -->
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


## Spec



## Diff summary

- anvil/runner.py: +37, -4
- runs/wo-gh-21/builder.output.md: +13, -23
- runs/wo-gh-21/builder.packet.md: +10, -0
- runs/wo-gh-21/envelopes/builder.envelope.json: +1, -1
- runs/wo-gh-21/envelopes/intake.envelope.json: +1, -1
- runs/wo-gh-21/envelopes/reviewer-architecture.envelope.json: +1, -1
- runs/wo-gh-21/envelopes/reviewer-security.envelope.json: +3, -10
- runs/wo-gh-21/envelopes/reviewer-spec.envelope.json: +4, -5
- runs/wo-gh-21/envelopes/reviewer-tests.envelope.json: +1, -1
- runs/wo-gh-21/envelopes/spec-writer.envelope.json: +1, -1
- runs/wo-gh-21/envelopes/test-writer.envelope.json: +1, -1
- runs/wo-gh-21/reviewer-architecture.output.md: +8, -22
- runs/wo-gh-21/reviewer-architecture.packet.md: +10, -0
- runs/wo-gh-21/reviewer-security.output.md: +7, -27
- runs/wo-gh-21/reviewer-security.packet.md: +10, -0
- runs/wo-gh-21/reviewer-security.review.json: +2, -9
- runs/wo-gh-21/reviewer-spec.output.md: +8, -7
- runs/wo-gh-21/reviewer-spec.packet.md: +10, -0
- runs/wo-gh-21/reviewer-spec.review.json: +2, -4
- runs/wo-gh-21/reviewer-tests.output.md: +23, -16
- runs/wo-gh-21/reviewer-tests.packet.md: +10, -0
- runs/wo-gh-21/spec-writer.output.md: +23, -10
- runs/wo-gh-21/spec-writer.packet.md: +10, -0
- runs/wo-gh-21/test-writer.output.md: +18, -16
- runs/wo-gh-21/test-writer.packet.md: +10, -0
- tests/test_astra_consumption.py: +84, -41

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- anvil/runner.py
- runs/wo-gh-21/builder.output.md
- runs/wo-gh-21/builder.packet.md
- runs/wo-gh-21/envelopes/builder.envelope.json
- runs/wo-gh-21/envelopes/intake.envelope.json
- runs/wo-gh-21/envelopes/reviewer-architecture.envelope.json
- runs/wo-gh-21/envelopes/reviewer-security.envelope.json
- runs/wo-gh-21/envelopes/reviewer-spec.envelope.json
- runs/wo-gh-21/envelopes/reviewer-tests.envelope.json
- runs/wo-gh-21/envelopes/spec-writer.envelope.json
- runs/wo-gh-21/envelopes/test-writer.envelope.json
- runs/wo-gh-21/reviewer-architecture.output.md
- runs/wo-gh-21/reviewer-architecture.packet.md
- runs/wo-gh-21/reviewer-security.output.md
- runs/wo-gh-21/reviewer-security.packet.md
- runs/wo-gh-21/reviewer-security.review.json
- runs/wo-gh-21/reviewer-spec.output.md
- runs/wo-gh-21/reviewer-spec.packet.md
- runs/wo-gh-21/reviewer-spec.review.json
- runs/wo-gh-21/reviewer-tests.output.md
- runs/wo-gh-21/reviewer-tests.packet.md
- runs/wo-gh-21/spec-writer.output.md
- runs/wo-gh-21/spec-writer.packet.md
- runs/wo-gh-21/test-writer.output.md
- runs/wo-gh-21/test-writer.packet.md
- tests/test_astra_consumption.py
