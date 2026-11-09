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

<!-- source: .openspec/specs/station-artifact-contract/spec.md -->
# Station Artifact Contract

Status: approved
Slug: station-artifact-contract

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
A station's contract with the line is a file: the builder writes a report, a reviewer writes its review JSON. The runner, however, has been accepting the station channel's conversational output as the station result. On the runtimes whose channel returns prose or nothing, that produces three observed failures: a reviewer's review is written but the station is marked failed and its vote silently dropped; the builder's chat summary lands in the run tree as if it were the builder report, false claims included; and the approver approves on the remaining votes without naming the missing ones. This spec makes the artifact the result, validates artifacts deterministically before any reviewer is paid for, and makes the approver honest about uncounted stations. The defect record with run ids and exact failure strings lives in issue 37.

## Requirements
- A station's result is the artifact file or files named in its packet, read back from the run tree after the station finishes. Conversational stdout from the station channel is diagnostic text only; it is never accepted as, or substituted for, the artifact.
- When a station produced its artifact, the run record names the real executed model for that station. executed_model is null only when no model ran.
- If a station's artifact is missing, empty, or fails its shape check, the station fails fast: the failure and its reason are recorded in report.json (station, expected artifact, observed state, executed model when one ran), and the run proceeds under the approver rules below rather than discovering the loss at aggregation time.
- A reviewer writing working files outside its review file (for example an .output.md beside it) does not by itself destroy the review: the harness still collects the review artifact. If the review artifact itself is absent or unparseable, the station fails with the scope or parse reason recorded in report.json, in place of an executor exit code surfacing as silence.
- The checks gate gains a deterministic artifact validation step that runs after the builder station and before any reviewer station is spawned. It verifies that the builder report artifact exists and is non-empty, and that every literal the work order declares as required in the builder report (for example a sha256 pin, a blob id, or test totals) appears in it in full, unabbreviated. A failed validation returns the work to the builder station with the validation log attached, consumes a loopback like a gate failure does today, and no reviewer station is spawned for that attempt.
- A work order declares its required builder-report literals in an optional top-level field `required_literals`, a list of non-empty strings. Matching is exact substring containment on the report text, with no abbreviation, ellipsis or case folding accepted. When the field is absent or empty, validation checks only that the report exists and is non-empty, so work orders that declare nothing behave as before.
- The same validation family checks reviewer artifacts as they are collected: each expected review JSON exists and parses before the approver aggregates.
- Approver honesty: when a pipeline expects a reviewer station and that station failed, produced no countable artifact, or was routed out after being expected, the approver cannot return a silent approved. The verdict becomes human_required (or changes_requested) and the decision text in report.json names the uncounted stations and the reason each was not counted.
- The contract is implemented in the spine (the runner, the checks gate, the approver) so it holds for every pipeline and every station runtime, without editing pipeline definition files and without special-casing a model brand or a channel.

## Scenarios
- S1 Station result = artifact: given a station whose channel returns prose but writes the artifact named in its packet, the station result is the artifact's content, and report.json records the real executed model. Given a station whose artifact is missing, empty, or fails its shape check, the station is recorded failed fast with the reason in report.json.
- S2 Deterministic artifact validation before reviewer spend: given a work order that declares required literals for the builder report, when the builder artifact lacks one of them in full (including the case where it appears abbreviated), the checks gate validation fails, the work returns to the builder, and no reviewer station runs for that attempt. Given a builder artifact containing every required literal in full, validation passes and the line proceeds.
- S3 Approver honesty: given a run where an expected reviewer was not counted, the approver verdict is human_required or changes_requested, never a silent approved, and the decision text names the uncounted station and why it was not counted. Given a run where every expected reviewer was counted, the approver behaves exactly as before.
- S4 Regression fixtures for the three observed modes: (a) a reviewer channel returning empty captured output while a valid review JSON was written is counted, or fails loudly per S1 and S3, and is never silently dropped; (b) a reviewer that also writes an extra .output.md outside its review file still has its review collected, or the station fails with the scope reason recorded in report.json; (c) a builder channel returning a first-person chat summary lacking a required literal is bounced by the S2 validation deterministically, before any reviewer runs.
- S5 No regressions: the factory's existing test suite stays green, existing pipelines run unchanged, and counted-review behavior for healthy stations is identical to before this change.


## Diff summary

- .openspec/specs/station-artifact-contract/spec.md: +1, -0
- anvil/approver.py: +51, -15
- anvil/executor.py: +5, -0
- anvil/gates.py: +85, -0
- anvil/model.py: +18, -1
- anvil/runner.py: +127, -9
- tools/claude_station.py: +22, -2
- tools/codex_station.py: +49, -7
- work_orders/wo-gh-37.json: +11, -7

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- .openspec/specs/station-artifact-contract/spec.md
- .openspec/specs/station-artifact-contract/spec.md
- anvil/approver.py
- anvil/executor.py
- anvil/gates.py
- anvil/model.py
- anvil/runner.py
- tools/claude_station.py
- tools/codex_station.py
- work_orders/wo-gh-37.json

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

## Rendered evidence

This run captured screenshots of the served project at the following breakpoints:

- `screenshot-1440x900.png` at `runs/wo-gh-37/evidence/screenshot-1440x900.png`
- `screenshot-390x844.png` at `runs/wo-gh-37/evidence/screenshot-390x844.png`

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

