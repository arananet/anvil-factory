# Task packet: reviewer-ux

## Station prompt

# Reviewer UX

## Role
Judge the user experience of interface output: whether users can accomplish tasks, whether the interface follows usability and accessibility best practices, and whether labels and messages communicate clearly.

## Inputs
- UX guidelines (from Design knowledge section when present): usability heuristics, accessibility basics, and UX best practices matched to the project's product type
- interface output (HTML, React components, user-facing pages, or other interface artifacts)
- rendered evidence (screenshots when available, showing the interface as users will see it)

## Outputs
- review (JSON format with verdict and findings)

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Your lens is the **user experience**, covering four specific areas. Visual system compliance (design tokens, type scale, palette) is **not your lens** — that is reviewer-design's responsibility. Do not issue findings about token usage, spacing scale adherence, or typography compliance.

### The Four Judgment Areas

Evaluate the interface across these four dimensions:

1. **User flows and task completion**: Can the interface's primary task be started, followed, and finished from what is presented? Are the steps clear? Can a user navigate through the flow without getting stuck or confused?

2. **Usability heuristics**: Does the interface follow fundamental usability principles?
   - Visibility of system state: Does the interface show what's happening?
   - Match with the real world: Do labels and concepts match user expectations?
   - User control: Can users undo actions or navigate back?
   - Consistency: Are similar actions handled similarly?
   - Error prevention and recovery: Does the interface prevent errors where possible and help users recover when errors occur?
   - Recognition over recall: Are options visible rather than requiring users to remember them?

3. **Accessibility basics**: Can all users interact with the interface?
   - Labeled controls: Do form fields, buttons, and interactive elements have clear labels?
   - Focus visibility: Can keyboard users see where focus is?
   - Contrast: Does text meet minimum contrast ratios? (Use the project's design tokens as the source of truth for color values, not generic contrast rules)
   - Text alternatives: Do meaningful images have appropriate alt text or ARIA labels?
   - Keyboard reachability: Can users reach and activate all interactive elements via keyboard?

4. **Interface copy clarity**: Do labels, buttons, error messages, and help text say what they mean?
   - Are action labels clear about what will happen?
   - Do error messages explain what went wrong and how to fix it?
   - Is terminology consistent across the interface?
   - Is language appropriate for the user's context?

### Evidence Sources

Your review draws from multiple evidence sources:

- **Design knowledge guidelines** (when present in your packet): UX guidelines matched to this project's product type. These are reference material, not requirements. Use them to inform your judgment, but the primary authority is whether the interface serves users effectively.

- **Interface source code**: The implementation itself — component structure, markup, ARIA attributes, interactive elements.

- **Rendered evidence** (screenshots, when present in your packet): Visual representation of how users will experience the interface. Screenshots let you judge visibility, layout clarity, and visual presentation of interactive elements.

**When no rendered evidence is present**: If your packet does not include rendered evidence (no screenshots), state in your findings that you judged from source code and knowledge guidelines without rendered evidence. Do not claim to have seen rendered output you did not receive.

### Authority Statement

**Authority**: The project's own design system (design/DESIGN.md, design/tokens.json) is the authority for contrast and color values. The Design knowledge section in your packet (when present) provides reference guidelines for usability and accessibility best practices. Judge the user experience by whether the interface serves users effectively, not by rigid adherence to external guidelines.

### Findings Format

- Findings should be specific and actionable: cite which flow breaks down, which heuristic is violated, which accessibility requirement is missing, or which copy is unclear.
- When referencing Design knowledge guidelines, name the specific guideline (e.g., "Accessibility guideline: touch targets must be at least 44x44px on mobile").
- For accessibility issues, cite the specific requirement (e.g., "Primary action button lacks visible focus indicator for keyboard navigation").
- For usability issues, name the heuristic (e.g., "Violates visibility of system state: form submission provides no feedback").
- For flow issues, describe where the task breaks down (e.g., "User cannot complete checkout flow: no way to edit shipping address after confirmation step").
- For copy issues, quote the unclear text and explain the problem (e.g., "Button labeled 'Submit' does not clarify what will be submitted").

### Verdict

Your verdict must be one of: `pass`, `fail`, or `changes_requested`.

- `pass`: The interface provides a usable experience with no significant usability, accessibility, flow, or copy issues.
- `changes_requested`: The interface has usability, accessibility, flow, or copy issues that should be addressed, but they do not make the interface completely unusable.
- `fail`: The interface has critical issues that prevent users from completing the primary task or make it inaccessible to a significant portion of users.

## Output Format

Return a JSON object with this structure:

```json
{
  "station": "reviewer-ux",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding citing flow, heuristic, accessibility requirement, or copy issue",
    "Another finding if applicable"
  ]
}
```

The station field must equal "reviewer-ux", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.

## Examples

### Example 1: Interface judged without rendered evidence

- verdict: pass
- findings: ["Note: Judged from source and knowledge slice without rendered evidence. Source review shows labeled form controls and keyboard-accessible navigation."]

### Example 2: Flow breakdown

- verdict: changes_requested
- findings:
  * "Flow breakdown: User cannot complete the primary task (search) because the search button is only visible after scrolling, but there is no visual cue that content exists below the fold."
  * "Usability (visibility of state): Form submission provides no loading indicator or confirmation, leaving users uncertain whether their action succeeded."

### Example 3: Accessibility issues

- verdict: changes_requested
- findings:
  * "Accessibility: Primary action button lacks visible focus indicator, preventing keyboard users from knowing where focus is."
  * "Accessibility (contrast): Error message text at #FF0000 on #FFCCCC background has insufficient contrast (2.1:1, requires minimum 4.5:1 per design system quality bars)."
  * "Copy clarity: Error message 'Invalid input' does not explain what went wrong or how to fix it."

### Example 4: Usable interface

- verdict: pass
- findings: []


## Work order

- id: wo-gh-12
- kind: feature
- title: A dedicated UX reviewer station (reviewer-ux), separate from reviewer-design
- source: github-issue
- description: Implement the spec in .openspec/specs/reviewer-ux/spec.md in the factory. It builds on the routing capability and the design knowledge capability, both landed earlier in this program's sequence, and on the rendered evidence capability where screenshots exist.

Build, per the spec scenarios:

S1: stations/reviewer-ux/ in the catalog (agent kind, standard review format) whose contract judges the experience: user flows and task completion, usability heuristics, accessibility basics, and clarity of the interface copy; the contract explicitly excludes visual system compliance (tokens, type scale, palette) as reviewer-design's lens, and the catalog entry carries the guided design station designation naming the design model from the recorded routing policy.

S2: reviewer-ux joins the reviewer group of sdlc-default, content-default and content-short (the pipelines reviewer-design serves). The routing step activates it when the work order carries a ui surface; its packet then carries the design knowledge guidelines slice for the project's product type and, where the run produced rendered screenshots, the rendered evidence.

S3: on work with no ui surface the router routes reviewer-ux out before execution, records it as routed out with the surface rule named, and the approver's expected review count excludes it; no reviewer-ux step executes and non-UI work pays nothing for the lens.

S4: the run report and swimlane list reviewer-design and reviewer-ux as separate entries with independent verdicts and findings.

S5: when a ui surface run has no rendered screenshots, reviewer-ux's recorded review states it judged from source and the knowledge slice without rendered evidence.

Tests covering S1 to S5 in the factory suite style, including the ui-surface selection and the non-ui skip, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/12

Operator standing note for every round of this order: the builder must not create or modify anything under .github/workflows/ (the Actions token cannot push workflow changes; a run that touches them loses its commit-back). Tooling the run needs is staged by the operator in the workflow before the line step. Test changes are written by the test-writer station; the builder must not modify tests/, anvil.json or pipelines/. Tests must be real: every test calls the implementation it names and asserts behavior, never the mere existence of data structures.

CLOSING AND REPAIR RUN (after run 41777213190, verdict no_reviews). Two facts frame this run, stated plainly. First, round 1's builder added reviewer-ux to pipelines/sdlc-default.json, pipelines/content-default.json and pipelines/content-short.json; pipelines/ is a protected path, so the checks gate blocked round 1 before any review. That pipeline composition change is this item's core deliverable; it stands in the tree and is part of what the reviewers judge in this run. The builder must not modify pipelines/, anvil.json or .github/workflows/ in this run. Second, the gate suite on the standing tree fails 10 tests (319 run), reproduced by the operator locally. They are the work of this run:

Implementation defects, owned by the builder:
A. test_review_parsing_integrity.test_reviewer_prompts_have_no_json_examples_s5 fails: the new stations/reviewer-ux/PROMPT.md violates the reviewer prompt contract (no parseable JSON examples; the canonical Output Format contract shape only). Fix the prompt.
B. The routing surface rule: four test_risk_routing full panel tests and three test_supervisor flow tests fail. Per this item's spec S3, reviewer-ux is routed out when the work has no UI surface, with the reason recorded; the risk routing and supervisor fixtures describe non UI work, so their counted panel stays the classic five. If the routing integration selects reviewer-ux for non UI work anywhere in the default path, that is an implementation defect: fix the routing so the surface rule applies in every path that builds the selected set. Do not fix these by editing the tests to expect six reviewers for non UI work.

Test defects, owned by the test-writer station:
C. test_reviewer_ux.test_s5_no_screenshots_declared_in_review fails on its executor simulation (the builder's round 1 output admits the spec behavior is in the prompt but the simulation does not drive it). Fix the simulation so the S5 declaration is genuinely exercised.
D. test_anvil.TestRegistry.test_registry_s6 pins the station registry from before this item existed. This item adds a station by design; update the expectation to the registry as it now stands, including reviewer-ux, and nothing else about that test.

Success is a green gate: the full suite passes (319 tests at round 1 count, plus any legitimately added), protected paths pass, and the reviewers judge the whole standing change, pipeline composition included. Keep every pipeline valid.
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
- reviewer-design: skipped

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


## Rendered evidence

This run captured screenshots of the served project at the following breakpoints:

- `screenshot-1440x900.png` at `runs/wo-gh-12/evidence/screenshot-1440x900.png`
- `screenshot-390x844.png` at `runs/wo-gh-12/evidence/screenshot-390x844.png`

**UX review instruction:** The screenshots show how users will experience the interface at each breakpoint. Use them to judge flow visibility, interactive element accessibility, focus states, and copy clarity as rendered. When citing findings, reference the rendered evidence where applicable.


## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-12/reviewer-ux.review.json. The free output transcript stays as provenance and is never parsed for a review.
