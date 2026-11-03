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


## Work order

- id: wo-gh-6
- kind: feature
- title: Deterministic checks gate with protected paths
- source: github-issue
- description: Implement the spec in .openspec/specs/checks-gate/spec.md in the factory.

Build, per the spec scenarios:

S1 and S2: a checks gate in the runner that runs the project's configured check commands after the builder and before the reviewer stage; passing checks let the reviewers run; failing checks return the work to the builder with the gate log in the builder feedback, spawn no reviewer, and consume one loopback.

S3: protected paths, configurable per project, defaulting to the checks configuration itself and the project's tests directory; a run whose changed files touch a protected path fails the gate automatically with a protected path finding naming the path, whatever the checks say. Deleting a protected file counts as touching it.

S4: check commands and protected paths are resolved from the base ref snapshot taken at run start, never from files the builder changed during the run.

S5: the gate runs a second time before the deployer or publisher station after any merge sync; a failure there stops the run before deploy or publish and is recorded as the blocking reason.

S6: a project with no checks configured records the gate as not configured and proceeds as today; the absence is visible in the report.

Every gate run is recorded in the run report (stage, commands, exit codes, protected path verdict, gate verdict) and shown as its own step in the swimlane. This gate complements the scenario-to-test gates; it does not change them. The factory dogfoods where the existing patterns call for it: the factory project config declares its own checks (the unittest suite and pipeline validation) and the default protected paths. Tests covering S1 to S6 in the factory suite style, docs updated in the style of the existing capability docs, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/6

LOOPBACK ROUND (gate loopback, authorized by the owner on 2026-11-01 after the round 1 verdict of changes_requested). The round 1 implementation stands: the checks gate station, the pre-review and pre-deploy gate runs, protected path findings, loopback on gate failure, and the S1 to S6 tests. This round closes the findings below and nothing else.

FIRST AND CRITICAL, S4 base ref enforcement (from the round 1 reviewer-security output, uncounted in round 1 because its review did not parse; it is preserved in runs/wo-gh-6/reviewer-security.output.md and counts as a finding of this round). Operator verification of the allegation against the round 1 code: in anvil/runner.py the base ref configuration is loaded by reading the anvil.json file from the working tree at run start. That is a file snapshot, not a base ref resolution: the working tree at run start is the run branch tip, which carries earlier builder commits committed back by previous rounds, so a branch can modify the checks it will be judged by, and those check commands then execute through shell=True with that provenance. Fix: at run start the runner records the base ref the work branched from and resolves the check commands and the protected paths from that ref's snapshot (through git where a repo is present), never from the working tree file; the working tree read may remain only as a documented fallback for projects with no git repo. Prove it with regression tests in the checks gate test module that mutate the checks configuration after the base ref is recorded, once as an uncommitted working tree change and once as a commit on top of the base, and assert the gate still runs the base ref commands and reports the protected path. The shell=True concern is answered by this provenance fix: check commands are shell strings by design and are safe to execute only because they now come from the base ref; state that reasoning in docs/CHECKS-GATE.md.

HYGIENE, the counted round 1 findings: (a) add docs/CHECKS-GATE.md in the style of the existing capability docs, covering purpose, configuration, the base ref rule, protected paths and the two gate phases; (b) add the CHANGELOG Unreleased entry for the checks gate; (c) move the gate evaluation logic out of anvil/runner.py into a pure function checks_gate in anvil/gates.py, keeping only orchestration in the runner, in the shape the round 1 approver named: checks_gate(phase, base_ref_config, changed_files, project_dir, work_order_id, timeout) returning the gate result dict; (d) the protected paths default must reference the checks configuration file path from the project configuration instead of the hardcoded anvil.json entry, keeping tests/ in the default; (e) the checks-gate station kind: use kind deterministic like the other deterministic stations, or document the gate kind in docs/ARCHITECTURE.md; pick one and make the suite assert it.

Keep the whole suite green, all eight pipelines valid, no station added, removed or renamed beyond what item (e) allows, and model routing untouched. Every reviewer writes its review to the authoritative review file named in its packet; prose outside that file is not a review.

LOOPBACK ROUND 2 (gate loopback, the second and final one for this order; authorized by the owner on 2026-11-02 after the loopback round's executed run). The loopback round implementation stands and is verified by its own run evidence (Actions run 41576137718): the S4 base ref enforcement with both regression tests passing, the pure checks_gate function in anvil/gates.py, docs/CHECKS-GATE.md, the CHANGELOG entry and the station kind alignment all landed, and the configured check command passed with 137 tests at exit 0. That run still ended no_reviews for one reason: the checks gate failed the run on protected path findings naming tests/test_checks_gate.py and tests/test_gates.py, which the run's own test-writer station wrote from the spec (the S4 regression tests and the pure function tests). The builder touched no test file. Under the run cumulative changed file reading the gate now implements, the sdlc line can never pass its own gate, because the test-writer writes scenario tests under tests/ before the builder on every run.

This round changes only the protected path semantics, per the binding clarification in the spec's Loopback round 2 section: the protected path check judges the builder station's changes for the current attempt (the working tree delta across the builder execution, computed by the runner), never the test-writer's writes; a violation is the builder modifying or deleting a base ref file under a protected prefix; builder additions are recorded in the gate output as observed additions, not violations; each attempt is judged on its own delta; the gate output records the basis judged. Check commands and protected paths still resolve from the base ref snapshot (S4 unchanged), and the pre-deploy gate applies the same basis.

Regression tests proving the clarified semantics, in the factory suite style: (1) test-writer adds and modifies test files while the builder changes only source, gate protected verdict passes and the reviewers spawn; (2) the builder modifies an existing base ref test file, gate fails naming the path and no reviewer spawns; (3) the builder deletes a test file, gate fails; (4) the builder modifies the checks configuration, gate fails and the commands still resolve from the base ref (the existing S4 tests keep passing); (5) a first builder attempt that touches a protected file fails the gate, and the loopback attempt whose builder does not touch one passes on its own delta. Update docs/CHECKS-GATE.md with the clarified semantics and the threat model reasoning (what judges the work cannot be altered by the work under review; test-writer output is part of the judging apparatus). Add a CHANGELOG Unreleased note for the clarification. Keep the whole suite green, all eight pipelines valid, no station added, removed or renamed, and model routing untouched. Every reviewer writes its review to the authoritative review file named in its packet; prose outside that file is not a review.
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: failed
- loopback: loopback
- reviewer-spec: skipped
- reviewer-security: skipped
- reviewer-tests: skipped
- reviewer-architecture: skipped

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


## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-6/reviewer-design.review.json. The free output transcript stays as provenance and is never parsed for a review.
