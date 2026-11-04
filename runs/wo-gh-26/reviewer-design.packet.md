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
- Focus on the design system the project has defined. Do not impose external design opinions or preferences that are not documented in the project's design system.
- A design token marked as "TODO" or placeholder means the project hasn't defined that value yet. Flag missing values as findings only if the interface output actually uses undefined tokens.
- Findings should be specific and actionable: cite which quality bar was violated, which token was used incorrectly, or which rule was not followed.
- Your verdict must be one of: `pass`, `fail`, or `changes_requested`.
- Produce the output as a JSON object, not as chat text.

## Output Format

Return a JSON object with this structure:

{
  "station": "reviewer-design",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-design", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.

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

<!-- source: .openspec/specs/declared-evidence-review/spec.md -->
# Declared Evidence Review

Status: proposed
Slug: declared-evidence-review

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

Reviewer-design can only judge what its packet puts in front of it, and today the packet's contact sheet is assembled only from files named capture-*.png inside the run directory (anvil/runner.py, the reviewer-design step). Anything that already exists before the run, or is produced outside a station session, never becomes a capture. Two executed runs proved the consequences from opposite sides:

1. The wo-gh-21 proof run (Sentia design audit, arananet/sentia run 41609958154): the audit's captures were produced by the builder during its session, while the runner assembled the reviewer-design packet from the run's declared capture inputs, which were empty for that order. The packet therefore referenced no contact sheet (measured packet: 904 tokens) and reviewer-design declined to judge the design.
2. The wo-gh-18 polish run (arananet/anvil-factory run 41741357479): the workflow ran the content line twice with the identical command, so the film review pass repeated authoring behavior. reviewer-design's counted review states it did not view the finished film and deferred each of the four polish advisories to a second pass; reviewer-facts left claim C11 open for the same reason. The run's own publisher and observer recorded the round INCOMPLETE. Judging that film needs a dedicated review execution whose evidence is declared up front, not produced mid-session.

A work order can already declare evidence_images (anvil/model.py): the paths are validated to resolve inside the project (validate_work_order_paths) and are listed in the builder packet, but they never reach reviewer-design. This order closes that gap and adds the review only pipeline the film review execution runs on.

Staged inputs, not product: the film evidence under content/youtube-anvil-v2/ is staged in this order's run branch byte identical from anvil/run-youtube-video-v2 at 312e606 (the film anvil-youtube-v2.mp4 is sha256 a277ce32c3ac7c30de5679524f49b1017ff028cfea2d38277deed73c4b44ecac, 21,401,761 bytes). No station in this order modifies anything under content/.

## Requirements

- Declared captures for reviewer-design. When a work order declares evidence_images, the reviewer-design step's capture set for contact sheet assembly is the declared PNG images plus any capture-*.png files present in the run directory. Declared images join the set in declaration order. Only files whose name ends in .png join the capture set; other declared files are still listed in packets under the packet requirements below.
- Loud failure on missing declared evidence. Before the reviewer-design step executes, every declared evidence image is checked: it must resolve inside the project tree and exist as a file. A declared image that is missing or escapes the tree fails the step with the named error declared_evidence_missing and the offending path recorded in the step detail. No review from that step is counted, and the run never proceeds with a silently empty evidence set when the work order declared evidence.
- The packet names every declared original. The reviewer-design packet's Evidence section lists the assembled contact sheet path and each declared evidence image path individually, so the reviewer can open every original at full resolution and cite it by path.
- Declared evidence in reviewer packets generally. When a work order declares evidence_images, the packet prepared for any reviewer station carries a "Declared evidence inputs" section listing each declared path. This is additive: existing packet sections, budgets and trimming behavior are unchanged.
- Review only content pipeline. A new pipeline file pipelines/content-film-review.json defines exactly these stages: intake; reviewer-design and reviewer-facts in parallel; approver; triage-human; publisher; observer. No authoring stations (intake is the deterministic normalizer, not an authoring station): no brief-writer, researcher, writer, media-producer or builder stage appears anywhere in it.
- Frozen surfaces. parse_review semantics and its file channel, the canonical review contract wording in anvil/runner.py, the reviewer prompts' Output Format sections, the verbatim review_suffix in tools/claude_station.py, and the wo-gh-24 review producer channel (scoped write, stdout never transcribed, review_file_missing distinguished from review_parse_failed, one in-session correction) stay untouched. The PNG hardening from wo-gh-21 (size and dimension caps, CRC verification, decompression hard cap, path validation) is reused, not weakened. No file under content/ changes. Python stays on the standard library only.
- Style. No em dash or en dash character in any produced file (project style rule). Add a CHANGELOG Unreleased entry.

## Scenarios

### Scenario: Declared images reach reviewer-design as a contact sheet
- S1: Given a work order declaring two PNG evidence images that exist in the project and an empty run directory (no capture-*.png), when the reviewer-design step is prepared, then a contact sheet is assembled from the declared images at the run directory contact sheet path, and the step's packet references it.

### Scenario: A missing declared image fails the step by name
- S2: Given a work order declaring an evidence image that does not exist, when the reviewer-design step is prepared, then the step fails with declared_evidence_missing and the missing path in the step detail, and no review from that step is counted.

### Scenario: The packet names each declared original
- S3: Given a work order declaring three evidence images, when the reviewer-design packet is built, then its Evidence section lists the contact sheet path and all three declared paths individually.

### Scenario: Reviewer packets generally carry the declared inputs
- S4: Given a work order declaring evidence images, when a packet is prepared for any other reviewer station (for example reviewer-facts), then the packet contains a Declared evidence inputs section listing each declared path.

### Scenario: The review only pipeline contains exactly the review stations
- S5: Given pipelines/content-film-review.json, when the pipeline is loaded and its topological order computed, then the order is intake, then reviewer-design and reviewer-facts as the parallel review stage, then approver, triage-human, publisher, observer, and no authoring station appears.

### Scenario: Relative project paths work identically to absolute paths
- S6: Given a work order declaring evidence images and a relative project path argument (the CLI form: project argument '.', invoked from inside the project directory), when the reviewer-design step is prepared, then the preparation succeeds and the packet lists each declared path, computed against the resolved project root rather than raising ValueError from mixing absolute and relative paths.

## Tests

Deterministic tests in the factory suite (tests/), named for their scenarios, using small PNG fixtures generated through the codebase's own PNG writing helpers or fixtures in the style of tests/test_astra_consumption.py. No model calls, no network.

- T1 (S1): declared PNG fixtures with no run directory captures produce an assembled contact sheet through the reviewer-design preparation path, and the returned packet references the contact sheet path.
- T2 (S2): a declared image that does not exist makes the preparation fail with the named declared_evidence_missing error carrying the missing path.
- T3 (S3): the built reviewer-design packet lists the contact sheet and each declared path individually.
- T4 (S4): a packet prepared for another reviewer station contains the Declared evidence inputs section with each declared path.
- T5 (S5): the new pipeline file loads, validates, and its topological order matches S5 exactly.
- T6 (S6): a reviewer-design step prepared with a relative project path (project argument '.', from inside a tmp project) and declared PNG fixtures returns a packet listing the declared paths without raising.
- The full factory suite stays green and all pipelines stay valid (the count grows by the one new pipeline).


## Diff summary

- .openspec/specs/declared-evidence-review/spec.md: +4, -0
- anvil/runner.py: +1, -1
- runs/wo-gh-26/builder.output.md: +7, -15
- runs/wo-gh-26/builder.packet.md: +12, -0
- runs/wo-gh-26/envelopes/builder.envelope.json: +1, -1
- runs/wo-gh-26/envelopes/intake.envelope.json: +1, -1
- runs/wo-gh-26/envelopes/reviewer-architecture.envelope.json: +1, -1
- runs/wo-gh-26/envelopes/reviewer-security.envelope.json: +1, -1
- runs/wo-gh-26/envelopes/reviewer-spec.envelope.json: +1, -1
- runs/wo-gh-26/envelopes/reviewer-tests.envelope.json: +1, -1
- runs/wo-gh-26/envelopes/spec-writer.envelope.json: +1, -1
- runs/wo-gh-26/envelopes/test-writer.envelope.json: +1, -1
- runs/wo-gh-26/reviewer-architecture.output.md: +29, -34
- runs/wo-gh-26/reviewer-architecture.packet.md: +12, -0
- runs/wo-gh-26/reviewer-security.output.md: +7, -14
- runs/wo-gh-26/reviewer-security.packet.md: +12, -0
- runs/wo-gh-26/reviewer-spec.output.md: +23, -6
- runs/wo-gh-26/reviewer-spec.packet.md: +12, -0
- runs/wo-gh-26/reviewer-tests.output.md: +1, -20
- runs/wo-gh-26/reviewer-tests.packet.md: +12, -0
- runs/wo-gh-26/spec-writer.output.md: +1, -11
- runs/wo-gh-26/spec-writer.packet.md: +12, -0
- runs/wo-gh-26/test-writer.output.md: +22, -1
- runs/wo-gh-26/test-writer.packet.md: +12, -0
- tests/test_declared_evidence_review.py: +91, -0

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- .openspec/specs/declared-evidence-review/spec.md
- .openspec/specs/declared-evidence-review/spec.md
- anvil/runner.py
- runs/wo-gh-26/builder.output.md
- runs/wo-gh-26/builder.packet.md
- runs/wo-gh-26/envelopes/builder.envelope.json
- runs/wo-gh-26/envelopes/intake.envelope.json
- runs/wo-gh-26/envelopes/reviewer-architecture.envelope.json
- runs/wo-gh-26/envelopes/reviewer-security.envelope.json
- runs/wo-gh-26/envelopes/reviewer-spec.envelope.json
- runs/wo-gh-26/envelopes/reviewer-tests.envelope.json
- runs/wo-gh-26/envelopes/spec-writer.envelope.json
- runs/wo-gh-26/envelopes/test-writer.envelope.json
- runs/wo-gh-26/reviewer-architecture.output.md
- runs/wo-gh-26/reviewer-architecture.packet.md
- runs/wo-gh-26/reviewer-security.output.md
- runs/wo-gh-26/reviewer-security.packet.md
- runs/wo-gh-26/reviewer-spec.output.md
- runs/wo-gh-26/reviewer-spec.packet.md
- runs/wo-gh-26/reviewer-tests.output.md
- runs/wo-gh-26/reviewer-tests.packet.md
- runs/wo-gh-26/spec-writer.output.md
- runs/wo-gh-26/spec-writer.packet.md
- runs/wo-gh-26/test-writer.output.md
- runs/wo-gh-26/test-writer.packet.md
- tests/test_declared_evidence_review.py
