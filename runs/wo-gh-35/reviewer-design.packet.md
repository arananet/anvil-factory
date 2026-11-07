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

<!-- source: .openspec/specs/landing-page/spec.md -->
# ANVIL Landing Page

Status: proposed
Slug: landing-page

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

The factory repo explains itself in pieces: a showcase README for readers who already arrived, a generated status page that reports runs, and a documentation set written for operators. Nothing in the repo is a front door: a page a visitor can land on that says what ANVIL is, what problem it solves, how the line works, and what makes it different from a single agent with a long prompt. The repo homepage still points at the run status page, a target the owner dismissed on 2026-11-04 because it does not tell the story and does not show the factory's products. This order builds that front door as a designed landing page living in this repo, written and reviewed by the line itself, with every claim on it verified the way the factory verifies everything else.

## Requirements

### R1. One self contained page in the repo
- The page is a single HTML file at site/index.html in this repo. Its CSS is inline in the file. It references no external asset: no webfonts, no CDN files, no external images, no external stylesheets or scripts. It contains no JavaScript and renders completely with scripts disabled.
- The page is in English. It carries a descriptive title and a meta description naming ANVIL and its expansion, Agentic Network for Verified Implementation Lifecycle.

### R2. Content: what the page must explain
- Sections, in this order, each with its own anchor: (1) Hero: the name ANVIL, its expansion, the one line promise (a software factory where no agent approves its own work), and two calls to action, the GitHub repo and the quickstart section. (2) The problem: agents that write, test and approve their own work, and demos nobody can audit after the fact. (3) How it works: the sdlc-default line as the visual centerpiece (intake, spec writer, test writer, builder, the five reviewers in parallel, approver, human gate, deployer, observer), plus the facts that pipelines are composable and that specs are written before implementation. (4) What makes it different: no self approval, with each reviewer writing only its own review file; verified memory, whose learnings enter station context only after deterministic code checks their provenance against the run record, with proposals quarantined until then; a deterministic checks gate that runs the project suite before any model station; rendered design review, where interface work is judged from rendered captures, not from code alone; post deploy health verification; and per run cost recorded in the run report. (5) Proof: ANVIL built real things, with links: Sentia, Platform25, this factory's own work orders, and release v0.1.0. (6) Quickstart: the exact commands from the README quickstart. (7) What ANVIL is not: not a single agent, not a prompt library, and not unsupervised autonomy; the human gate is presented as a feature. (8) Footer: Apache 2.0 license with Copyright Eduardo Arana, Developer Eduardo Arana, and links to the repo, the release, the documentation index and the run status page.

### R3. Claims hygiene
- Every number printed on the page (station count, pipeline count, reviewer count in sdlc-default, test suite size, release version) is verified at build time from the tree or by running the suite, and the page states counts as of its build. At filing time the operator verified 27 stations and 8 pipelines on main; those figures are a starting point for the builder to re-verify, not text to copy blindly.
- Only merged, shipped capabilities may be described as factory capabilities. Work that is filed or staged but unmerged at build time (at filing time: the deterministic preflight of issue 28 and the memory consolidation of issue 33) must not appear on the page as something ANVIL does today. The builder re-checks main at build time; if such work has merged by then, it may be included only with the merge as evidence.
- The page names no employer of the owner, links no unpublished article or video, and repeats no claim the README showcase pass already corrected.

### R4. Design bar
- Production quality landing page, not a styled report. It uses the Arananet dark palette the status page established (near black background, orange accent FF5C00, light text) with a real landing hierarchy: an oversized display headline in the hero, a consistent spacing scale, the line diagram rendered as inline SVG with every label spelled correctly, cards for the differences section, and monospace type reserved for code and labels.
- Responsive: the layout adapts down to a 360 px wide phone viewport with no horizontal scrolling. All text meets WCAG 4.5:1 contrast minimums. Interactive targets are at least 44 px. The builder produces desktop and mobile rendered captures of the finished page as run evidence, and reviewer-design judges the page from those captures like any other interface work.

### R5. Deterministic page checks
- New tests in the factory suite read the real site/index.html and assert: the file exists and is one HTML document with a viewport meta; it loads no external asset (no script or stylesheet references and no externally hosted image, font or media source); the eight section anchors of R2 are present in order; the station and pipeline counts printed on the page equal the counts computed from the stations and pipelines trees at test time; the quickstart commands printed on the page appear in the README quickstart; and the file contains no em dash or en dash character.
- The tests must read the page and the trees themselves. A test that asserts against a copy of the content, or that never opens site/index.html, is a facade test and fails this spec on sight (the lesson of issue 9).

### R6. Scope limits and hosting readiness
- This order creates site/index.html, docs/LANDING-PAGE.md and the new test files. It changes nothing under anvil/, nothing in the status page or its generator, nothing in the README, and no workflow. It deploys nothing, enables no GitHub Pages, and changes no repo metadata.
- docs/LANDING-PAGE.md records how to preview the page locally and the two hosting routes with their exact steps: (a) Cloudflare Pages serving the site/ folder, the route the run status page already uses, deployable by the operator with the vault credential; (b) GitHub Pages, which the owner must enable in the repo Settings because the vault token cannot (see docs/OPERATOR-REQUIREMENTS.md). The document recommends route (a) and records that, after the owner approves the page at the human gate, the operator deploys it and updates the repo homepage to the page URL, retiring the status page URL the owner dismissed. Those steps are operator follow up after this order, not part of its run.

### Guardrails
- Python standard library only for the tests, consistent with the factory spine. No new dependency, no site generator, no framework.
- Frozen surfaces: the review parse contract, the reviewer prompts and their Output Format sections, the review producer mechanisms, the checks gate behavior, and the status page generator.
- No em dash or en dash character in any produced file (project style rule).
- Nothing in this order publishes or deploys anything, and no page content goes live anywhere during the run.

## Scenarios

### Scenario: The page exists and stands alone
- S1: Given the run has completed, when a reader opens site/index.html from a plain file server with scripts disabled, then the page renders completely, loads no external asset, and every image or diagram it shows is inline in the file.

### Scenario: The story is complete and in order
- S2: Given the finished page, when its anchors are listed, then the eight sections of R2 appear in the specified order, the hero names ANVIL and its expansion, and the footer carries the Apache 2.0 license line with Copyright Eduardo Arana.

### Scenario: Printed counts equal the tree
- S3: Given the factory suite runs, when the R5 tests compute the station and pipeline counts from the trees, then the counts printed on the page equal those computed counts, and a page edited to a wrong count fails the suite.

### Scenario: Quickstart commands are the real ones
- S4: Given the finished page, when its quickstart block is compared with the README, then every command it prints appears in the README quickstart section.

### Scenario: The design evidence is rendered, not asserted
- S5: Given the finished page, when the run evidence is inspected, then it contains desktop and mobile captures of the page itself, the mobile capture shows no horizontal scrolling at phone width, and reviewer-design's review cites the captures.

### Scenario: The run stays inside its fence
- S6: Given the run delta, when the changed files are listed, then every change is inside site/, docs/LANDING-PAGE.md, or the new test files; no file under anvil/, no workflow, no README and no status page file changed.

### Scenario: Hosting is documented and nothing was deployed
- S7: Given docs/LANDING-PAGE.md, when it is read, then it names both hosting routes and their steps, recommends Cloudflare Pages, and states that this order deployed nothing and that the homepage update happens after the owner's gate approval.


## Diff summary

- docs/LANDING-PAGE.md: +20, -19
- runs/wo-gh-35/builder.output.md: +2, -4
- runs/wo-gh-35/checks-gate.pre-review.output.md: +30, -74
- runs/wo-gh-35/envelopes/builder.envelope.json: +1, -1
- runs/wo-gh-35/envelopes/checks-gate.envelope.json: +5, -50
- runs/wo-gh-35/envelopes/intake.envelope.json: +1, -1
- runs/wo-gh-35/envelopes/reviewer-architecture.envelope.json: +2, -2
- runs/wo-gh-35/envelopes/reviewer-security.envelope.json: +2, -2
- runs/wo-gh-35/envelopes/reviewer-spec.envelope.json: +22, -4
- runs/wo-gh-35/envelopes/reviewer-tests.envelope.json: +22, -4
- runs/wo-gh-35/envelopes/spec-writer.envelope.json: +1, -1
- runs/wo-gh-35/envelopes/test-writer.envelope.json: +1, -1
- runs/wo-gh-35/evidence/browser-checks.json: +3, -3
- runs/wo-gh-35/evidence/build-facts.json: +5, -1
- runs/wo-gh-35/evidence/landing-desktop.png.comparison.json: +6, -5
- runs/wo-gh-35/evidence/landing-mobile.png.comparison.json: +6, -5
- runs/wo-gh-35/evidence/validation.json: +11, -19
- runs/wo-gh-35/reviewer-architecture.packet.md: +4, -5
- runs/wo-gh-35/reviewer-security.packet.md: +2, -3
- runs/wo-gh-35/reviewer-spec.packet.md: +1, -2
- runs/wo-gh-35/reviewer-tests.packet.md: +3, -4
- runs/wo-gh-35/routing.json: +2, -2
- runs/wo-gh-35/spec-writer.output.md: +11, -9
- runs/wo-gh-35/test-writer.output.md: +11, -17
- site/index.html: +3, -0

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- .openspec/specs/landing-page/spec.md
- docs/LANDING-PAGE.md
- runs/wo-gh-35/builder.output.md
- runs/wo-gh-35/checks-gate.pre-review.output.md
- runs/wo-gh-35/envelopes/builder.envelope.json
- runs/wo-gh-35/envelopes/checks-gate.envelope.json
- runs/wo-gh-35/envelopes/intake.envelope.json
- runs/wo-gh-35/envelopes/reviewer-architecture.envelope.json
- runs/wo-gh-35/envelopes/reviewer-security.envelope.json
- runs/wo-gh-35/envelopes/reviewer-spec.envelope.json
- runs/wo-gh-35/envelopes/reviewer-tests.envelope.json
- runs/wo-gh-35/envelopes/spec-writer.envelope.json
- runs/wo-gh-35/envelopes/test-writer.envelope.json
- runs/wo-gh-35/evidence/browser-checks.json
- runs/wo-gh-35/evidence/build-facts.json
- runs/wo-gh-35/evidence/landing-desktop.png.comparison.json
- runs/wo-gh-35/evidence/landing-mobile.png.comparison.json
- runs/wo-gh-35/evidence/validation.json
- runs/wo-gh-35/reviewer-architecture.packet.md
- runs/wo-gh-35/reviewer-security.packet.md
- runs/wo-gh-35/reviewer-spec.packet.md
- runs/wo-gh-35/reviewer-tests.packet.md
- runs/wo-gh-35/routing.json
- runs/wo-gh-35/spec-writer.output.md
- runs/wo-gh-35/test-writer.output.md
- site/index.html

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

## Rendered evidence

This run captured screenshots of the served project at the following breakpoints:

- `screenshot-1440x900.png` at `runs/wo-gh-35/evidence/screenshot-1440x900.png`
- `screenshot-390x844.png` at `runs/wo-gh-35/evidence/screenshot-390x844.png`

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

