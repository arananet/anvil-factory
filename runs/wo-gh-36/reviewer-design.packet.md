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

<!-- source: .openspec/specs/practice-skills/spec.md -->
# Practice Skills Base

Status: proposed

## Purpose

ANVIL has no skills system. Best practices today live as prose inside station prompts, as verified learnings in the brain, or in the operator's head. There is no way to add a practice once and have it reach exactly the stations it applies to, and no protection against two practices contradicting each other inside the same packet. This spec adds a practice skills base to the factory brain: a quarantined, provenance checked set of development best practices with explicit scope, resolved deterministically per work order before any model sees them.

## Design

Three layers, as designed with the owner on 2026-10-29:

1. A quarantined practice base that reuses the brain's promotion pattern: proposals with provenance, promotion only after a consistency check, one rule per topic per scope.
2. Deterministic resolution before any model: the runner assembles the conflict free practice set for a work order by scope matching and records it in the run report.
3. Written precedence: the project's own constitution and design system beat the base, through an explicit override list, never through model judgment.

One split runs through the whole design: a practice that can be checked mechanically belongs to the checks gate, not to a prompt.

## Requirements

R1. Practice base and quarantine. Promoted practices live in brain/practices.md, one entry per practice, with fields: Id, Topic, Rule, Scope (Languages, Surfaces, Stations), Enforcement (prompt or gate), Source, and Status (active or superseded). Proposals enter only through a propose operation in the brain module that mirrors propose_learning, and land in brain/inbox/ and nowhere else. Promotion happens only through a promote operation that mirrors promote_learning. The CLI gains propose-practice and promote-practice commands alongside the existing learning commands.

R2. Consistency check at promotion. Promotion refuses, naming the reason, when: the provenance does not verify to the same standard the learnings gate uses (the cited run report exists and supports the practice, or the source is an owner decision record under brain/decisions/); another active practice with the same Topic and an overlapping scope exists and the proposal does not supersede it; or the entry is malformed. A proposal may carry a Supersedes field naming one active practice; on promotion that practice is marked superseded and stops resolving. Scope overlap means at least one shared value, or an unrestricted dimension, on every scope dimension. The existing check-brain validation is extended to practices: it fails on a malformed practices.md and on any pair of active practices with the same topic and overlapping scope, and it passes on a repository with no practices base.

R3. Deterministic resolution. Before any packet is built, the runner computes the practices that apply to the work order from its surfaces, its pipeline's station list, and the language signals in the work order and the project config. A practice applies when every non-empty scope dimension matches: conjunctive across dimensions, disjunctive within a dimension, an empty dimension unrestricted. Resolution is deterministic Python standard library code; no model takes part in it.

R4. Recording. report.json gains a practices field holding the resolved practice ids per station, the topics excluded by project override, and the number of active practices in the base at run start. The run's routing record carries the same resolution, so what each station was given is auditable from the run evidence alone.

R5. Precedence by explicit override. A project may declare practice_overrides in its anvil.yaml: a list of topics the project governs itself through its constitution or design system. Practices whose topic is overridden are excluded from resolution for that project, and the exclusion is recorded per R4. Overrides are explicit topic names only; nothing infers an override from document content.

R6. Enforcement split. A practice with Enforcement prompt is injected into the packets of the stations it resolved for, in a dedicated Practices section, and into no other packet. A practice with Enforcement gate is never injected as prompt text; the checks gate lists it by id and topic in its pre-review output, so reviewers can see what the gate is accountable for. Authoring an automated checker for an individual gate practice is out of scope for this order; the gate listing is the contract.

R7. Empty base by design. This order ships the mechanism with no promoted practices. Test fixtures live in the test suite only. Seeding a real best practice catalog is follow-on work that enters through the same proposal and promotion gate as any other practice.

R8. Backward compatibility and coordination. A project with no brain/practices.md behaves exactly as today, apart from the report field recording an empty resolution. If the scoped learnings work (issue 33) has merged before this order executes, its scope matching helper is reused for R3 instead of writing a second matcher; if it has not merged, matching is implemented in the brain module and the parallel is recorded in the run report.

## Scenarios

S1. A proposal written through the propose operation lands in brain/inbox/; brain/practices.md is unchanged.

S2. A proposal whose source is a run report that exists and supports it promotes successfully and the practice then resolves for a matching work order.

S3. Promotion is refused, naming the conflicting practice, when an active practice with the same topic and overlapping scope exists and the proposal carries no Supersedes.

S4. A proposal with Supersedes promotes; the replaced practice is marked superseded, no longer resolves, and check-brain passes.

S5. Resolution respects scope: a practice scoped to one language reaches the in-scope stations of a matching work order and not a work order of another language; a practice scoped to one station reaches only that station's packet.

S6. A gate enforced practice appears in the checks gate pre-review output and in no station packet; a prompt enforced practice appears in its stations' packets and is not presented as a gate item.

S7. A project whose anvil.yaml overrides a topic resolves no base practice on that topic, and report.json records the exclusion.

S8. With no practices base present, a run's packets and verdict are unchanged and report.json records an empty practices resolution.

S9. check-brain fails on a practices.md that was hand edited to hold two active practices with the same topic and overlapping scope.

## Scope limits

Python standard library only. No pipeline membership changes, no station prompt rewrites, no changes to how learnings are proposed, promoted, demoted or injected beyond the coordination note in R8. No practice content is authored by this order. No em dash or en dash characters in any produced file.


## Diff summary

- anvil/brain.py: +377, -1
- anvil/cli.py: +21, -2
- anvil/runner.py: +42, -11

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- .openspec/specs/practice-skills/spec.md
- anvil/brain.py
- anvil/cli.py
- anvil/runner.py

## Work order

- id: wo-gh-36
- kind: feature
- title: Practice skills base: quarantined best practices with scoped, deterministic resolution
- source: github-issue
- description: Implement the spec in .openspec/specs/practice-skills/spec.md. Owner's idea 2026-10-29 (capability program item 11), decided 2026-11-08: a skills system for ANVIL, a quarantined base of development best practices with scoped, deterministic resolution. Pipeline for this order is sdlc-default, selected by the run workflow.

STAGING: this order is filed and staged only. Execution starts on the owner's word, like issues 28 and 33.

Build, per the spec requirements:

R1, the base: brain/practices.md with one entry per practice (Id, Topic, Rule, Scope with Languages, Surfaces and Stations, Enforcement prompt or gate, Source, Status active or superseded). Proposals enter only through a propose operation in the brain module mirroring propose_learning, landing in brain/inbox/; promotion only through a promote operation mirroring promote_learning. CLI gains propose-practice and promote-practice next to promote-learning and check-brain.

R2, the consistency check: promotion refuses with the reason named when provenance does not verify to the learnings standard (cited run report exists and supports the practice, or an owner decision record under brain/decisions/), when an active practice with the same topic and overlapping scope exists without a Supersedes, or when the entry is malformed. Supersedes marks the replaced practice superseded so it stops resolving. check-brain extends to practices: malformed base fails, any active topic and scope conflict fails, absent base passes.

R3, deterministic resolution: before packets are built, the runner resolves applicable practices from the work order surfaces, the pipeline station list and language signals. Matching is conjunctive across scope dimensions, disjunctive within a dimension, empty dimension unrestricted. Standard library only, no model in the resolution.

R4, recording: report.json gains a practices field (resolved ids per station, topics excluded by override, active base count at run start); the routing record carries the same resolution.

R5, precedence: anvil.yaml may declare practice_overrides, a list of topics the project governs itself. Overridden topics resolve nothing from the base and the exclusion is recorded. Explicit topic names only, no inference from document content.

R6, enforcement split: Enforcement prompt practices are injected into a dedicated Practices section of the packets of the stations they resolved for, and nowhere else. Enforcement gate practices are never prompt text; the checks gate lists them by id and topic in its pre-review output. Authoring automated checkers for individual gate practices is out of scope.

R7, empty base: ship the mechanism with no promoted practices; fixtures live in tests only. Seeding a catalog is follow-on work through the same gate.

R8, compatibility and coordination: no practices base means behavior identical to today apart from the report field recording an empty resolution. If issue 33 (scoped learnings) has merged before this run executes, reuse its scope matching helper for R3; if not, implement matching in the brain module and record the parallel in the run report.

Guardrails: Python standard library only; no new dependency. Do not change pipeline membership, station prompts, or the learnings mechanisms' behavior. Do not create, modify, or delete any file under tests/ that exists at the base ref; new tests arrive as new files, and they must exercise the real brain module and runner paths (facade tests that never touch the mechanism fail the order). No em dash or en dash character in any produced file. The reviewer writes its review to the authoritative review file named in its packet; prose outside that file is not a review. Nothing in this order publishes or deploys anything.

GitHub issue: https://github.com/arananet/anvil-factory/issues/36
- risk_hints: 
- status: new

## Rendered evidence

This run captured screenshots of the served project at the following breakpoints:

- `screenshot-1440x900.png` at `runs/wo-gh-36/evidence/screenshot-1440x900.png`
- `screenshot-390x844.png` at `runs/wo-gh-36/evidence/screenshot-390x844.png`

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

