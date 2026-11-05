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

- id: wo-gh-13
- kind: feature
- title: Status dashboard shows the lifecycle stage per work order
- source: github-issue
- description: Implement the spec in .openspec/specs/status-lifecycle-stages/spec.md in the factory's status page generation.

Build, per the spec scenarios:

S1: stage derivation as a pure function of the job's latest run data: SPEC from the recorded spec stage, BUILD from the builder step, REVIEW from reviewer steps, APPROVED from the decision's approver verdict, the current stage being the furthest the evidence supports, and a job with no runs showing nothing reached.

S2: MERGED comes only from an actual merge record (merged pull request or merged run branch) in the merge data the generator consumes; an approved job with no merge record shows APPROVED and MERGED stays unmarked; with a merge record it shows MERGED. Derivation never infers merges from branch names or commit messages and never calls the network.

S3: NEEDS HUMAN derives from the decision's human_required flag for any reason it was set, rendered with a visually prominent badge treatment alongside the current stage; absent when the flag is false.

S4: intake states compose: a latest run that ended parked (waiting_info) shows PARKED and one that ended rejected shows REJECTED, instead of a stage progression.

S5: the generated page is one board: one row per work order carrying its id, title, the stage sequence with reached stages marked and the current stage highlighted, the NEEDS HUMAN badge when it applies, and a link from each row to that job's swimlane or run detail. Regenerating from the same data produces the same board. The derivation and rendering live in the factory's status page generator so every surface it generates (the factory status page and the example project's page) renders the board the same way.

Tests covering S1 to S5 from report fixtures in the factory suite style, including the approved-but-unmerged case and the human_required case, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/13

Operator standing note for every round of this order: the builder must not create or modify anything under .github/workflows/ (the Actions token cannot push workflow changes; a run that touches them loses its commit-back). Tooling the run needs is staged by the operator in the workflow before the line step. Test changes are written by the test-writer station; the builder must not modify tests/, anvil.json or pipelines/. Tests must be real: every test calls the implementation it names and asserts behavior, never the mere existence of data structures.

LOOPBACK 1 (after run 41783359038, verdict changes_requested, reviews counted 6 of 6, checks gate passed). The counted findings, verbatim in substance, all bounded:

A. Spec S5, also reviewer-ux's user flow and accessibility findings (reviewer-spec and reviewer-ux): board rows do not link to the job's detail. The work order ID renders as plain text in an h3, the row container carries the id, and the detailed run section has no id attribute, so anchor navigation is impossible and keyboard and screen reader users get no navigable element. Fix: each board row's work order ID becomes a real link, an a element with href pointing to that job's detailed run section (for example #wo-id-detail), and the detailed section carries the matching id attribute. Real links close the keyboard reachability and link semantics findings at the same time.

B. Contrast (reviewer-design): .muted (#9A9A9A at 13px), the footer (#8A8A8A at 13px) and .board-description (#9A9A9A at 13px) on the #0C0C0C background were flagged as possibly below the 4.5:1 minimum for normal text. Resolve with evidence: compute the WCAG contrast ratio for each of these foreground and background pairs from the actual CSS values; any pair below 4.5:1 gets its foreground lightened until it passes; the test-writer adds a test that computes the ratios from the stylesheet values and asserts every named pair is at least 4.5:1, so the bar is pinned either way.

C. Spacing rhythm (reviewer-design): the CSS hardcodes at least 15 different spacing values with no scale. Consolidate the board and status page spacing onto a small consistent spacing scale (CSS custom properties drawn from one scale) so spacing values come from the scale throughout.

D. Responsive behavior (reviewer-design): the .board-stages flex row of five stages can force horizontal scrolling below about 400px viewport width. Make the stages row wrap or adapt at narrow widths (flex-wrap or a media query) so no horizontal scrolling occurs on standard viewports.

E. Rendered evidence: the operator has staged Playwright and Chromium installation into this run's workflow before the line step, so the capture step can produce rendered evidence of the status page with the lifecycle board in this run; reviewer-design and reviewer-ux judge with those captures in their packets.

Discipline: the test-writer station writes the new and changed tests (the link structure assertions, the computed contrast test); the builder implements in the status page code and styles only and must not modify tests/, anvil.json, pipelines/ or .github/workflows/. Everything else from round 1 stands: the stage derivation, the NEEDS HUMAN badge, the intake state composition, and the docs and CHANGELOG updates were all confirmed correct by the counted reviews.
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

