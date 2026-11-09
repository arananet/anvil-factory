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

### Visual Output Quality Verification

When your packet includes a Quality Charter section (visual runs only), you must verify each produced output against the run's reference anchors and charter criteria before the review step:

1. **Read the output**: Examine each visual deliverable you produce (images, UI components, rendered interfaces).

2. **Compare against anchors**: If reference anchors are provided, compare your output against them. Check how your output measures up to the anchor's quality bar across the charter criteria.

3. **Check charter criteria**: Evaluate your output against the observable criteria from the Quality Charter:
   - For physical products: materials, light, contact, scale
   - For games/illustrations: the stated standard from the project design system

4. **Record the comparison**: Document your findings in the run evidence directory (runs/{work_order_id}/evidence/) as a JSON file named `{output_filename}.comparison.json` with this structure:

```json
{
  "output": "path/to/generated/output.png",
  "anchor_cited": "path/to/reference/anchor.png or null if none",
  "criteria_checked": ["materials", "light", "contact", "scale"],
  "gaps": [
    {
      "criterion": "materials",
      "description": "Surfaces read as plastic rather than the metal shown in anchor"
    }
  ],
  "statement": "Explicit statement: 'No gaps found at charter bar' or description of gaps identified"
}
```

5. **Evidence, not verdict**: Your comparison is evidence for reviewers, not a final verdict. Record what you observe; reviewers are not bound by your self-assessment.

This verification step only applies when the Quality Charter section is present in your packet. For non-visual work, this step does not apply.


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


## Work order

- id: wo-gh-37
- kind: feature
- title: Station artifact contract: station results are artifacts, validated deterministically, and failed reviewers are never silently dropped
- source: github-issue
- description: Implement the spec in .openspec/specs/station-artifact-contract/spec.md. Owner's instruction 2026-11-09, verbatim: "arreglemos anvil y esto, si es un software factory es una castana". Pipeline for this order is sdlc-default, selected by the run workflow.

THE DEFECT FAMILY (full evidence with run ids and exact failure strings in issue 37): across every run of two consumer projects (arananet/foryou-lab and arananet/giana-3d), station channels returned conversation or nothing where file artifacts were expected, and the approver silently approved on the remaining votes. Reviewer-design and reviewer-ux were never counted in any run: design failed with "Codex empty output" although its review.json existed with substantive findings; ux failed with "changed files outside its review file: runs/wo-gh-1/reviewer-*.output.md", executor exited 8, configured openai/gpt-6.1-sol, executed_model null. The builder station's chat reply landed AS runs/<wo>/builder.output.md twice in Dreamrun: R7 a 263 byte stub falsely claiming all 159 tests pass, and R8 (a loopback filed only to restore that report) a first-person chat summary that abbreviates the required sha256 as 67217b9d...c83b86f so the full literal never appears.

BUILD, per the spec scenarios:
S1: a station result is the artifact file or files named in its packet, read back from the run tree; conversational stdout is never the result; missing, empty or shape-failing artifacts fail the station fast with the reason and the real executed model recorded in report.json.
S2: deterministic artifact validation in the checks gate after the builder and before any reviewer spend (owner preflight doctrine, 2026-11-04): builder report exists and contains every work-order-declared required literal in full; reviewer review.json files exist and parse. Failure returns the work to the builder without launching reviewers.
S3: approver honesty: an expected reviewer that failed or was not counted makes the verdict human_required (or changes_requested), never a silent approved, with the uncounted stations named in the decision text.
S4: regression tests as NEW files under tests/ reproducing the three observed modes with fixtures: empty captured output with a valid review.json written; a reviewer writing an extra .output.md outside its review file; a builder chat summary lacking a required literal bounced by the S2 check.
S5: no regressions: the existing factory suite stays green, pipelines unchanged, healthy-station behavior identical.

GUARDRAILS: implement in the spine (anvil/: runner, checks gate, approver). Pipeline files under pipelines/ are protected paths in anvil.json; the contract must hold without editing them. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. Python standard library only, no new dependency. Channel-agnostic: validate artifacts, never special-case a model brand. Do not weaken the review parse contract or the existing protected-path gate behavior. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner's human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/37
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
