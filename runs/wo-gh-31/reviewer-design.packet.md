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
- **Authority**: The project's own design system (design/DESIGN.md, design/tokens.json) is the authority for this project. The Design knowledge section in your packet (when present) is reference material that the design system may draw from. On any conflict between the project's design system and the knowledge base, the project's design system wins. A deviation from the knowledge base alone is never a finding; a deviation from the project's design system is.
- Focus on the design system the project has defined. Do not impose external design opinions or preferences that are not documented in the project's design system.
- A design token marked as "TODO" or placeholder means the project hasn't defined that value yet. Flag missing values as findings only if the interface output actually uses undefined tokens.
- Findings should be specific and actionable: cite which quality bar was violated, which token was used incorrectly, or which rule was not followed. When referencing the Design knowledge base in a finding or suggestion, name the specific knowledge entry (e.g., "metrics-blue palette", "data-dense style", "accessibility guideline for contrast").
- Your verdict must be one of: `pass`, `fail`, or `changes_requested`.
- Produce the output as a JSON object, not as chat text.

## Output Format

For visual runs (when Quality Charter is present in your packet), return a JSON object with dual-section structure:

{
  "station": "reviewer-design",
  "verdict": "pass | fail | changes_requested",
  "compliance": {
    "verdict": "pass | fail | changes_requested",
    "findings": [
      "Design system compliance findings (tokens, rules, component patterns)"
    ]
  },
  "quality": {
    "verdict": "pass | fail | changes_requested",
    "findings": [
      "Quality findings comparing output against reference anchors and charter criteria"
    ],
    "anchor": "path/to/anchor/file or 'charter floor only' when no anchors"
  }
}

For non-visual runs (no Quality Charter in packet), return the simple structure:

{
  "station": "reviewer-design",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar"
  ]
}

### Dual-Section Review (Visual Runs)

For visual runs:

1. **Compliance section**: Judge design system adherence - tokens, component patterns, layout rules, motion guidelines.

2. **Quality section**: Judge visual quality by comparing the output against reference anchors and charter criteria. This is a separate judgment from compliance.
   - When reference anchors are present: Compare the output against the anchors. Name gap categories from the charter criteria (materials, light, scale, contact for physical products; stated criteria for games/illustrations).
   - When no anchors: Judge against charter floor alone.
   - Cite the anchor used in comparison or state "charter floor only" when no anchors available.

The overall verdict is the stricter of the two section verdicts. An output can pass compliance but fail quality, and such a case must be reported as changes_requested or fail at the overall level.

**Same-Subject Identity Consistency (S7)**: When the work order declares an `identity_reference` for runs producing multiple related visual outputs, the quality section may extend beyond individual anchor evaluation to include same-subject identity consistency verification across deliverable outputs. Your packet will specify this requirement when applicable. You must verify that all outputs maintain identical subject identity traits enumerated in the work order (examples for physical products: finish, detail colors, mounting or attachment, proportions and markings; stated equivalents apply for other product types). Divergence in these traits constitutes a quality failure even when each output individually meets anchor criteria. Such failures must name the specific output and trait in your findings, with ruling and evidence recorded in the quality section. This verification is part of quality section judgment, not a separate verdict.

### Quality Criteria by Product Type

When judging quality section findings, name specific criteria gaps:

**Physical products**: materials, light, contact, scale
**Games/Illustrations**: Apply the project's stated standard from the design system

The station field must equal "reviewer-design", and both the overall verdict and section verdicts must be one of pass, fail, or changes_requested.

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

<!-- source: .openspec/specs/model-tier-map/spec.md -->
# Tier map totality

## Problem

The model migration (issue 29) added MODEL_TIER_MAP in anvil/config.py to
resolve abstract tier labels to concrete models at hand-off. The map is not
total: anvil/routing.py assigns the label review-cheap to the reduced
reviewer panel at low risk, and MODEL_HIERARCHY includes review-cheap, but
the map has no review-cheap entry. resolve_model passes the label through
and the station dispatcher fails loudly on it, so any low-risk run that
routes reviewers at the reduced panel breaks at dispatch. The wo-gh-30
verification run on merged main showed reviewer steps configured
review-cheap, unresolved.

## Requirements

R1. MODEL_TIER_MAP resolves review-cheap to claude-sonnet-5-5, the same
concrete model as the other reviewer tiers (the owner's policy: every
non-design reviewer runs claude-sonnet-5-5).

R2. Totality is proven by test, not by inspection: a regression test
enumerates every tier label the factory can produce from the routing
module's own vocabulary (MODEL_HIERARCHY plus every model value the routing
rules can select, including the reduced panel assignment) and asserts each
one resolves through resolve_model to a member of CONCRETE_MODELS. If a
future change adds a label anywhere in that vocabulary without a map entry,
the test fails.

R3. Nothing else changes: the dispatcher still fails loudly on values that
are neither concrete models nor mapped labels; routing's vocabulary and
rules are unchanged; the full suite stays green.


## Diff summary

- runs/wo-gh-31/builder.output.md: +23, -11
- runs/wo-gh-31/builder.packet.md: +4, -0
- runs/wo-gh-31/checks-gate.pre-review.output.md: +3, -3
- runs/wo-gh-31/envelopes/builder.envelope.json: +1, -1
- runs/wo-gh-31/envelopes/checks-gate.envelope.json: +1, -1
- runs/wo-gh-31/envelopes/intake.envelope.json: +1, -1
- runs/wo-gh-31/envelopes/reviewer-architecture.envelope.json: +1, -1
- runs/wo-gh-31/envelopes/reviewer-security.envelope.json: +1, -1
- runs/wo-gh-31/envelopes/reviewer-spec.envelope.json: +15, -6
- runs/wo-gh-31/envelopes/reviewer-tests.envelope.json: +16, -6
- runs/wo-gh-31/envelopes/spec-writer.envelope.json: +1, -1
- runs/wo-gh-31/envelopes/test-writer.envelope.json: +1, -1
- runs/wo-gh-31/intake.output.md: +1, -7
- runs/wo-gh-31/intake.packet.md: +4, -0
- runs/wo-gh-31/reviewer-architecture.packet.md: +6, -2
- runs/wo-gh-31/reviewer-security.packet.md: +5, -1
- runs/wo-gh-31/reviewer-spec.packet.md: +4, -0
- runs/wo-gh-31/reviewer-tests.packet.md: +5, -1
- runs/wo-gh-31/routing.json: +3, -3
- runs/wo-gh-31/spec-writer.output.md: +6, -6
- runs/wo-gh-31/spec-writer.packet.md: +4, -0
- runs/wo-gh-31/test-writer.output.md: +13, -5
- runs/wo-gh-31/test-writer.packet.md: +4, -0
- work_orders/wo-gh-31.json: +1, -2

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- .openspec/specs/model-tier-map/spec.md
- runs/wo-gh-31/builder.output.md
- runs/wo-gh-31/builder.packet.md
- runs/wo-gh-31/checks-gate.pre-review.output.md
- runs/wo-gh-31/envelopes/builder.envelope.json
- runs/wo-gh-31/envelopes/checks-gate.envelope.json
- runs/wo-gh-31/envelopes/intake.envelope.json
- runs/wo-gh-31/envelopes/reviewer-architecture.envelope.json
- runs/wo-gh-31/envelopes/reviewer-security.envelope.json
- runs/wo-gh-31/envelopes/reviewer-spec.envelope.json
- runs/wo-gh-31/envelopes/reviewer-tests.envelope.json
- runs/wo-gh-31/envelopes/spec-writer.envelope.json
- runs/wo-gh-31/envelopes/test-writer.envelope.json
- runs/wo-gh-31/intake.output.md
- runs/wo-gh-31/intake.packet.md
- runs/wo-gh-31/reviewer-architecture.packet.md
- runs/wo-gh-31/reviewer-security.packet.md
- runs/wo-gh-31/reviewer-spec.packet.md
- runs/wo-gh-31/reviewer-tests.packet.md
- runs/wo-gh-31/routing.json
- runs/wo-gh-31/spec-writer.output.md
- runs/wo-gh-31/spec-writer.packet.md
- runs/wo-gh-31/test-writer.output.md
- runs/wo-gh-31/test-writer.packet.md
- work_orders/wo-gh-31.json

## Work order

- id: wo-gh-31
- kind: feature
- title: Tier map totality: resolve review-cheap
- source: github-issue
- description: Implement the spec in .openspec/specs/model-tier-map/spec.md. One bounded fix on merged main:

1. Add the missing entry to MODEL_TIER_MAP in anvil/config.py: review-cheap resolves to claude-sonnet-5-5 (owner policy: every non-design reviewer runs claude-sonnet-5-5).
2. Add a totality regression test in a NEW test file: enumerate every tier label from the routing module's own vocabulary (anvil.routing MODEL_HIERARCHY plus every model value the routing rules can select, including the reduced panel's review-cheap assignment in the default routing table) and assert resolve_model maps each to a member of CONCRETE_MODELS. The test must read the vocabulary from the routing module, not hardcode a copy of the label list, so a future unmapped label fails the suite.
3. CHANGELOG Unreleased entry.

Guardrails: do not modify or delete any existing file under tests/ (new tests only in new files; the checks gate protects base ref test files). Routing's vocabulary and rules unchanged; the dispatcher keeps failing loudly on unmapped non-concrete values. Full suite green. No em dash or en dash characters in any produced file.

GitHub issue: https://github.com/arananet/anvil-factory/issues/31

PURE VERIFICATION ROUND (round 2). Round 1 verdict: no_reviews, with the expected self-reference shape, disclosed in full: the builder implemented the fix (MODEL_TIER_MAP gained review-cheap -> claude-sonnet-5-5, plus the totality regression test enumerating the routing vocabulary), the checks gate PASSED on the new tree (the totality test runs in a fresh process and proves the map), but this order's own two selected reviewers (reviewer-spec and reviewer-tests, reduced panel at low risk) still failed at dispatch with the unresolved review-cheap label, because the runner process of round 1 loaded the pre-fix map at startup. A fix to the hand-off cannot prove itself inside the run that carries it; that is what this round is for.

The standing tree at this round's start contains the complete fix with the gate green. THIS ROUND MAKES NO CHANGES: the builder is barred from modifying, adding or deleting any file; its task is verification and reporting only. The run starts on the fixed code, so routing's review-cheap assignments now resolve at hand-off. Reviewers: judge the standing tree against the spec (R1 the map entry, R2 the vocabulary-enumerating totality test, R3 nothing else changed, dispatcher still loud on unmapped values). If the tree is genuinely incomplete against the spec, name the specific gap for the record rather than requesting changes this round is barred from making.
- risk_hints: 
- status: new

## Rendered evidence

This run captured screenshots of the served project at the following breakpoints:

- `screenshot-1440x900.png` at `runs/wo-gh-31/evidence/screenshot-1440x900.png`
- `screenshot-390x844.png` at `runs/wo-gh-31/evidence/screenshot-390x844.png`

**Design review instruction:** When judging layout, scale, spacing, or visual hierarchy findings, cite the rendered evidence screenshots where applicable. The screenshots show what the page actually looks like at each breakpoint, not just what the source implies.


## Design knowledge

**Authority**: The project's own design system (design/DESIGN.md, design/tokens.json) is the authority for this project. The knowledge base below is reference material that the design system may draw from. On any conflict, the project's design system wins. A deviation from the knowledge base alone is not a finding; a deviation from the project's design system is.

**Note**: No product type slice matched. General guidelines only.

### Product Type: Undeclared

No specific product type declared. Using general guidelines only.

### UX Guidelines

**Accessibility:**
- Maintain minimum 4.5:1 contrast ratio for normal text, 3:1 for large text (18pt+)
- Touch targets must be at least 44x44px on mobile devices

**Feedback:**
- Loading states should appear after 300ms delay to avoid flashing
- Provide immediate visual feedback for user actions

**Forms:**
- Form fields should have clear labels and validation feedback
- Error messages should explain what went wrong and how to fix it

**Hierarchy:**
- Establish clear visual hierarchy using size, weight, and color
- Important actions should be visually prominent and easy to locate

**Motion:**
- Keep animation durations between 200-400ms for most transitions
- Provide reduced motion alternatives for users with vestibular sensitivity

**Responsive:**
- Test layouts at mobile (320-768px), tablet (768-1024px), and desktop (1024px+) breakpoints
- Avoid horizontal scrolling on standard viewports

**Spacing:**
- Use consistent spacing scale throughout (e.g., 4px, 8px, 16px, 24px, 32px)
- Group related elements together with whitespace separating distinct sections


## Quality Charter

Product type: physical_product

Observable criteria:

- **Materials**: Surfaces read as the materials the product is actually made of
- **Light**: One coherent light story, with shadows and reflections that agree with it
- **Contact**: Objects meet skin, surfaces and each other the way physical things do
- **Scale**: The object's size reads true against its context and human anatomy


## Reference Anchors

⚠️ **WARNING**: This run has no reference anchors.

The review will proceed under the charter floor alone.

