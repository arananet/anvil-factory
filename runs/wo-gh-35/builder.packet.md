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


## Work order

- id: wo-gh-35
- kind: feature
- title: ANVIL landing page in the factory repo: a designed page that explains what ANVIL is
- source: github-issue
- description: Implement the spec in .openspec/specs/landing-page/spec.md. Owner's request 2026-11-07: a good looking page for ANVIL in its own repo that explains what it is. Pipeline for this order is sdlc-default (software domain, full reviewer set including reviewer-design), selected by the run workflow. The run creates site/index.html (one self contained page, inline CSS, no external assets, no JavaScript, English), docs/LANDING-PAGE.md (preview and hosting notes), and new test files. It changes no spine code.

STAGING: this order is filed and staged only. Execution starts on the owner's word. At filing time the AI Gateway Anthropic route answers 402 insufficient_balance (verified in the gateway logs on 2026-11-07), so no run can complete until the owner tops up the gateway; do not fire the run before that is resolved, and do not present a gateway failure as a page failure.

Build, per the spec requirements:

R1, the artifact: a single HTML file at site/index.html, inline CSS, zero external assets, zero JavaScript, descriptive title and meta description naming ANVIL (Agentic Network for Verified Implementation Lifecycle).

R2, the story, in order: hero (name, expansion, the one line promise that no agent approves its own work, calls to action to the repo and the quickstart); the problem (self approving agents, unauditable demos); how it works (the sdlc-default line as inline SVG centerpiece: intake, spec writer, test writer, builder, five reviewers in parallel, approver, human gate, deployer, observer; composable pipelines; spec before implementation); what makes it different (no self approval and one authoritative review file per reviewer; verified memory with provenance checked against the run record and proposals quarantined; the deterministic checks gate before model spend; rendered design review from captures; post deploy health verification; per run cost in the report); proof (Sentia, Platform25, this repo's own work orders, release v0.1.0, all linked); quickstart (the exact README commands); what ANVIL is not (not a single agent, not a prompt library, not unsupervised autonomy; the human gate as a feature); footer (Apache 2.0, Copyright Eduardo Arana, Developer Eduardo Arana, links to the repo, the release, the docs index and the run status page).

R3, claims hygiene: verify every printed number from the tree or the suite at build time (operator verified 27 stations and 8 pipelines on main at filing; re-verify, do not copy blindly). Describe only merged capabilities: issues 28 and 33 are staged and unmerged at filing time and must not appear as shipped capabilities unless they have merged into main before this run executes, with the merge as evidence. Name no employer of the owner; link no unpublished article or video.

R4, design bar: production quality landing in the Arananet dark palette (near black background, orange accent FF5C00, light text), oversized hero headline, consistent spacing scale, the line diagram as inline SVG with every label spelled correctly, cards for the differences, monospace only for code and labels. Responsive to a 360 px phone viewport with no horizontal scrolling, WCAG 4.5:1 text contrast, interactive targets at least 44 px. Produce desktop and mobile rendered captures of the finished page as run evidence for reviewer-design.

R5, deterministic checks: new suite tests read the real site/index.html and assert single document with viewport meta, no external asset loading, the eight section anchors in order, printed station and pipeline counts equal to the counts computed from the trees at test time, quickstart commands present in the README quickstart, and no em or en dash characters. Tests that never open the real page are facade tests and fail the order (issue 9's lesson).

R6, scope and hosting readiness: create only site/index.html, docs/LANDING-PAGE.md and the new test files. docs/LANDING-PAGE.md records the local preview steps and both hosting routes (Cloudflare Pages from site/, recommended, deployable by the operator with the vault credential; GitHub Pages, which the owner must enable in Settings because the vault token cannot), and states that this order deploys nothing and that the repo homepage update happens as operator follow up after the owner's gate approval.

Guardrails: Python standard library only for tests; no site generator, no framework, no new dependency. Frozen surfaces: the review parse contract, the reviewer prompts and their Output Format sections, the review producer mechanisms, the checks gate behavior, and the status page generator. Do not create, modify, or delete any file under tests/ that exists at the base ref (the checks gate protects base ref test files); new tests arrive as new files. No changes under anvil/, no README changes, no workflow changes, no status page changes. No em dash or en dash character in any produced file. The reviewer writes its review to the authoritative review file named in its packet; prose outside that file is not a review. Nothing in this order publishes or deploys anything.

GitHub issue: https://github.com/arananet/anvil-factory/issues/35
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
