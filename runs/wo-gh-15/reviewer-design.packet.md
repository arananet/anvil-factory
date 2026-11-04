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

When reviewing visual deliverables:

1. **Compliance section**: Judge design system adherence - tokens, component patterns, layout rules, motion guidelines.

2. **Quality section**: Judge visual quality by comparing the output against reference anchors and charter criteria. This is a separate judgment from compliance.
   - When reference anchors are present: Compare the output against the anchors. Name gap categories from the charter criteria (materials, light, scale, contact for physical products; stated criteria for games/illustrations).
   - When no anchors: Judge against charter floor alone.
   - Cite the anchor used in comparison or state "charter floor only" when no anchors available.

The overall verdict is the stricter of the two section verdicts. A deliverable can pass compliance but fail quality, and such a case must be reported as changes_requested or fail at the overall level.

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


## Work order

- id: wo-gh-15
- kind: feature
- title: A standing quality standard for visual deliverables
- source: github-issue
- description: Implement the spec in .openspec/specs/quality-standard/spec.md in the factory. It is the tenth work order of the capability program and runs after the post-deploy health work in the same sequence.

Build, per the spec scenarios:

S1: reviewer-design's contract gains the anchor comparison duty as a separate, named quality section of its recorded review, alongside design system compliance. On a fixture visual run for a physical consumer product whose anchors show photoreal product boards, a stylized toy-like output must fail the quality section, naming gap categories from materials, light, scale and contact measured against the cited anchor, even when the compliance section passes. reviewer-ux carries the same duty for the experiential side once it exists in the catalog.

S2: a visual run with no anchors under design/reference/ and none named by the work order proceeds under the charter floor alone: the charter criteria for the product type are present in the generating and reviewing packets, and the run report carries a visible warning that the run had no reference anchors.

S3: a run with no visual surfaces never receives the charter: no packet contains the charter text or its criteria and the report makes no mention of the quality standard.

S4: a station that produces imagery verifies each output by reading it against the run's anchors and the charter criteria before the review step runs, and the comparison lands in the run evidence per output (anchor cited, criteria checked, gaps found or an explicit none at the charter bar). The record is evidence, not a verdict, and reviewers are not bound by it.

S5: composition order is anchors first, then the project design system and verified brain learnings, then the charter floor. Anchors showing a deliberately stylized product make the stylized reading the bar; anything below the charter floor is a named floor gap, never silently waived.

S6: for a game or illustration product, the charter requires the project's own standard stated in observable terms and the review applies that standard; the physical product photorealism criteria are absent from the judgment.

Also build the charter itself: a versioned factory level charter document stating production quality as the default bar for visual deliverables, defined per product type with observable criteria (materials, light, contact and scale for a physical consumer product; a stated per product standard for game and illustration work), included by reference in the packets of imagery generating and imagery reviewing stations on visual runs. Project design system scaffolding creates design/reference/ under the never overwrite discipline and visual work orders name or inherit the project's anchors.

S7: a work order producing a set of related visual deliverables designates one canonical identity reference inside the set, the generating stations work from it, and reviewer-design runs a same subject test across the whole set against it on the identity traits the work order's spec enumerates (finish, detail colors, mounting or attachment, proportions and markings for a physical product, equivalents stated per product type). Any divergence fails the quality judgment with the divergent asset and trait named, even when every asset individually passes the anchor comparison, and such a run does not approve.

Tests covering S1 to S7 in the factory suite style, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/15

GATE LOOPBACK (round 2). Round 1 verdict was changes_requested with 5 of 5 reviews counted after routing (reviewer-spec and reviewer-tests pass; reviewer-security, reviewer-architecture and reviewer-design changes_requested). Close exactly the counted findings:

1. WIRE THE QUALITY MODULE INTO THE RUNNER (reviewer-architecture). anvil/quality.py defines packet_quality_charter_section() and packet_anchor_section() but anvil/runner.py never calls them; the module is orphaned. packet_step() must call both and pass their results to _packet_text(), which gains quality_charter_section and anchor_section parameters, following the established pattern of packet_design_section, packet_rendered_evidence_section and packet_knowledge_section. Wire the S2 warning the same way: on a visual run with no anchors, the run report carries the visible no-reference-anchors warning the quality module generates.

2. STATION CONTRACTS (reviewer-architecture, spec S1 and S4). stations/reviewer-design/PROMPT.md must document the dual-section review structure the code validates ({compliance: {verdict, findings}, quality: {verdict, findings, anchor}} per validate_reviewer_quality_section), the anchor comparison duty as a separate named quality section, and the requirement to name gap categories by criterion (materials, light, scale, contact). The imagery generating station prompts (stations/builder/, stations/media-producer/, stations/brief-writer/) gain the S4 duty: verify each produced output against the run's anchors and charter criteria before the review step and record the comparison in the run evidence per output. reviewer-ux's prompt carries the same quality section duty for the experiential side, per S1.

3. PATH AND INPUT VALIDATION (reviewer-security). WorkOrder.from_dict must validate the anchors, identity_reference and deliverable_set path fields: relative paths only, no parent traversal, no absolute paths, following the validate_path_component discipline already in the codebase; malformed values are rejected with a named error. quality.py is_visual_run and get_product_type must not assume attribute presence or types (defensive access or structural validation). Work order controlled strings interpolated into packet output are sanitized of control characters.

4. RENDERED SURFACE (reviewer-design). In the surface rendered as this run's evidence: secondary text (the 'configured:' lines) must reach at least 4.5:1 contrast against the dark background at both breakpoints, and the station data table at 390x844 needs responsive treatment (no horizontal scrolling; touch targets at least 44x44px; card layout, scrollable region with clear affordance, or progressive disclosure). Capture rendered evidence at 390x844 and 1440x900 in this run showing both fixed.

5. TESTS. Add regression tests in the factory suite style proving the wiring: a visual run's generating and reviewing packets contain the charter section and the anchor section; a visual run with no anchors produces the report warning; a non-visual run contains no charter text anywhere (S3); the reviewer-design dual-section output validates against the contract; traversal paths in the new WorkOrder fields are rejected.

Guardrails: the charter document and quality.py's criteria content were not faulted; do not rewrite them beyond the wiring. No changes to the review parsing contract beyond the reviewer-design dual-section contract item 2 names (the parser and producer mechanisms themselves are frozen), the checks gate base ref behavior, or other items' modules. Keep the full suite green and every pipeline valid; docs and CHANGELOG Unreleased updated for the wiring. No em dash or en dash characters in any produced file.


PURE VERIFICATION ROUND (round 3). Full history, disclosed: round 1 built anvil/quality.py and the charter but left the module orphaned (runner never called it, station contracts not updated, no path validation); verdict changes_requested, 5 of 5 counted after routing (spec and tests pass; security, architecture, design changes_requested). Round 2 implemented the loopback scope: runner wiring for the charter and anchor sections and the S2 report warning, the reviewer-design and reviewer-ux dual-section contracts, the generating stations' S4 self-comparison duty, WorkOrder path validation, the rendered surface contrast and responsive fixes, plus 14 real pipeline integration tests in tests/test_quality_wiring.py. Its checks gate shows the suite green on that tree (388 tests, OK) but failed the run on protected path violations, because round 2 modified three files that existed in its recorded base ref: tests/test_quality_standard.py (two call sites updated for the new packet_anchor_section signature, assertions unchanged), tests/test_quality_standard_coverage.md (additive documentation), and tests/test_review_parsing_integrity.py. All reviewers were skipped (no_reviews).

One round 2 change is named here for explicit reviewer judgment: tests/test_review_parsing_integrity.py previously required every reviewer prompt's Output Format section to be identical modulo station id (the wo-gh-16 contract). Round 2 scoped that identity assertion to the non-visual reviewers and carved out reviewer-design and reviewer-ux, whose formats this item's spec S1 deliberately extends with the dual-section quality structure; the carve-out is documented in the test with its reason. Reviewer-tests and reviewer-spec: judge whether that scoping is the honest reconciliation of the two contracts or an impermissible weakening, and record the judgment.

The standing tree at this round's start contains the complete item with the suite green. THIS ROUND MAKES NO CHANGES. The builder is barred from modifying, adding or deleting any file; its task is verification and reporting only. Reviewers: judge the standing tree against the spec scenarios S1 to S7 and the round 1 findings list (runner wiring, station contracts, path and input validation, rendered surface contrast and 390x844 responsive behavior with this run's rendered evidence). The verdict of this round is the item's verdict of record. If a reviewer finds the standing tree genuinely incomplete against the spec, name the specific gap for the record rather than requesting changes this round is barred from making.


GATE LOOPBACK (round 4). Round 3 was a pure verification round of the standing tree: verdict changes_requested, 5 of 5 counted after routing (reviewer-ux routed out). reviewer-spec, reviewer-security, reviewer-tests and reviewer-architecture all PASS: the round 1 findings (orphaned module, station contracts, path validation, rendered surface contrast and responsive behavior) are resolved. The parsing integrity carve-out for reviewer-design and reviewer-ux was explicitly judged by reviewer-design: HONEST RECONCILIATION, the correct resolution of the two conflicting contracts. That question is closed; do not revisit it.

Exactly one finding remains, from reviewer-design's quality section, verbatim in substance: S7 is incompletely implemented. The WorkOrder model carries identity_reference, identity_traits and deliverable_set with path validation (complete), and docs/QUALITY_CHARTER.md documents the same-subject test requirement (complete). However, stations/reviewer-design/PROMPT.md does not document the same-subject test duty that S7 requires reviewer-design to perform, and packet_quality_charter_section injects only the observable criteria, not the station duties. A reviewer receiving a work order with identity_reference and deliverable_set would not know from the packet or the prompt that a same-subject test is required.

Loopback scope, exactly this and nothing else:
1. Document the S7 same-subject test duty in stations/reviewer-design/PROMPT.md: when the run declares an identity reference and a deliverable set, the review performs the same-subject comparison across the set against the identity reference and records the ruling with its evidence in the review's quality section.
2. Make the duty travel with the packet: when a work order declares identity_reference or deliverable_set, the quality sections injected into the reviewer-design packet state the same-subject test duty explicitly (not only the observable criteria).
3. Prove it with a test that exercises the duty's presence end to end (packet content when the fields are declared, and its absence when they are not).

HARD CONSTRAINTS: the full factory suite must remain green. Do NOT modify or delete any existing file under tests/ (the checks gate treats base ref test files as protected; two earlier rounds died on exactly that). Any new test goes in a NEW test file. Do not change the review parsing contract, the dual-section structure, or any behavior outside this finding.

- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: passed
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

Product type: game

Observable criteria:

- **Stated Standard**: Project must state observable criteria in design system


## Reference Anchors

⚠️ **WARNING**: This run has no reference anchors.

The review will proceed under the charter floor alone.


## Rendered evidence

This run captured screenshots of the served project at the following breakpoints:

- `screenshot-1440x900.png` at `runs/wo-gh-15/evidence/screenshot-1440x900.png`
- `screenshot-390x844.png` at `runs/wo-gh-15/evidence/screenshot-390x844.png`

**Design review instruction:** When judging layout, scale, spacing, or visual hierarchy findings, cite the rendered evidence screenshots where applicable. The screenshots show what the page actually looks like at each breakpoint, not just what the source implies.


## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-15/reviewer-design.review.json. The free output transcript stays as provenance and is never parsed for a review.
