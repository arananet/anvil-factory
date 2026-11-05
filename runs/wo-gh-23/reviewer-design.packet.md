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



## Diff summary

- README.md: +89, -7

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- README.md

## Work order

- id: wo-gh-23
- kind: task
- title: Showcase README: first screen demo, Built by ANVIL, quickstart, trust section
- source: github-issue
- description: Implement the spec in .openspec/specs/readme-showcase/spec.md: rewrite README.md of this repository into the launch showcase, keeping the existing documentation below the fold. Pipeline for this order is sdlc-default (software domain, full reviewer set), selected by the run workflow. The run touches README.md, README assets under docs/ or assets/ as the builder judges cleanest, and run evidence only. No factory code changes.

SEQUENCING GATE: execute this order only from a main that already carries the capability minimum, issues 6 to 10 (wo-gh-6 checks gate with the S4 base ref fix, wo-gh-7 intake outcomes, wo-gh-8 risk and surface routing, wo-gh-9 rendered design review, wo-gh-10 per job cost) merged. Verify their presence in the branch history before building (the checks gate code and docs, the intake outcomes, the routing, the rendered review and the cost fields in run reports). If the minimum is not in the history, stop and report instead of running.

Build, per the spec requirements:

R1, first screen: house template header (title, stack badges plus OpenSpec and Apache 2.0 badges, the quoted one line description), then in order: (1) the animated demo of one real run cycle (work order, spec, tests, build, reviews, human gate, merged), GIF or embedded MP4 under 90 seconds, produced from a real run's own evidence (captures and report data of runs already on record in this repo, for example a capability run or wo-gh-20), never a mockup or a staged animation of events that did not happen; if a truthful animated demo cannot be produced inside the line, say so plainly in the run output and ship the README with the strongest truthful static evidence instead; (2) the Built by ANVIL block with live links to Sentia (https://sentia.info-693.workers.dev), Platform25 (https://platform25.pages.dev) and the status board (https://anvil-status.pages.dev), one line each on what it proves; (3) the quickstart against arananet/anvil-example-taskline, under 5 minutes, which the line EXECUTES from a clean clone during the run and records (commands, duration, output tail) as evidence.

R2, trust section: the three mechanisms (no station approves its own work, with verdicts read from authoritative review files and parsing that fails closed; memory promoted only with run report provenance, the CONTAM-Bench answer; a human gate before publishing or production deploys), each claim linked to the repo file, test or report that backs it.

R3, claim hygiene: verify every number against the tree at run time (station count, pipeline count, factory suite size measured fresh, reviewer counts corrected to five wherever the current README says four, including the approver line in the station table). Cite S4 and the capability items only as merged fact, because the gate above guarantees they are in main; anything not in main goes to a roadmap section labelled as roadmap or stays out.

R4, metadata is an OPERATOR step after the merge, not the line's: the line's part is only to produce the social preview image (1280 by 640, ANVIL wordmark, simplified station line, the one line quote, production quality, any generated text verified letter by letter) as a run evidence file named social-preview.png, and to record in its output that the homepage, topics and image upload are operator steps. The line does not call the GitHub settings API and does not change the repo description.

R5, closing: the house template sections (Contributing pointing at OpenSpec, Documentation, License Apache 2.0 with Copyright Eduardo Arana, Developer Eduardo Arana, the ko-fi block), and exactly one star call to action, worded exactly as the spec states, at the end of the first screen and repeated at the close.

Tests and evidence, per the spec: a link and claim check over the produced README recorded in the run evidence (relative links resolve in the tree, the three showcase links answer live during the run, the R3 claim list item by item against the tree); a capture of the rendered README from the real GitHub view of the run branch at desktop width; the quickstart execution record. The factory suite must stay green; any suite change is reported, not fixed inside this order.

Guardrails: no em dash or en dash character in any produced file (project style rule). The reviewer writes its review to the authoritative review file named in its packet; prose outside that file is not a review. Nothing in this order publishes anything: no posts, no release, no metadata changes by the line.

GitHub issue: https://github.com/arananet/anvil-factory/issues/23
- risk_hints: 
- status: new

## Rendered evidence

**Note:** Rendered evidence could not be captured for this run. Reason: capture failed for 390x844: Playwright not installed. Install with: pip install playwright && playwright install chromium. This review judged source only.


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

