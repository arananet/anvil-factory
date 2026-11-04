# Task packet: builder

## Station prompt

# Builder

## Role
Implement the spec so the scenario tests pass.

## Inputs
- spec
- tests

## Outputs
- code change

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.
- **Design citation**: When authoring or revising design/DESIGN.md, include a "Design knowledge sources" note citing the knowledge entries you drew from by data kind and entry name (e.g., "Style: modern-minimal", "Palette: metrics-blue", "Guideline: accessibility - contrast ratio"). If the knowledge came from an operator-supplied pack, cite it as "operator-supplied pack entry" without naming the pack's origin.


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

- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed

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

