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

LOOPBACK ROUND 3 (gate loopback, the final one for this order; authorized by the owner on 2026-11-02 after the verification run). Everything from rounds 1 and 2 stands and is verified: the checks gate passes on the builder delta basis (verification run 41579344085: gate passed, configured command exit 0, all five reviewers executed). This round closes exactly one finding, raised by reviewer-security in that run and verified by the operator against the tree at anvil/cli.py (the run_pipeline call), anvil/runner.py (run_pipeline's base_ref default of None) and anvil/gates.py (resolve_base_ref_config's working tree fallback): the S4 base ref control is not wired through the CLI execution path. The module tests inject base_ref directly, so they pass while every real CLI driven run resolves the checks configuration from the working tree at run start.

Fix, per the binding clarification in the spec's Loopback round 3 section: when a run starts in a git repository and no explicit base ref is supplied, the runner records the base ref at run start as the merge base of HEAD and the project's base branch (new optional base_branch key in the project configuration, defaulting to the repository's default branch), resolves the check commands and protected paths from that ref through git, and writes the base ref used into the run report. The run command gains a --base-ref option that overrides the derivation. The working tree read stays only as the documented fallback for projects with no git repository and is never used when a git repository is present.

One regression test through the CLI entry path, in the factory suite style: build a scratch git repo whose base branch carries a known checks configuration; on a work branch, first modify the configuration in the working tree, run the CLI path, and assert the gate used the base ref commands; then commit a modified configuration on top of the base, run the CLI path again, and assert the same, with the tamper reported through the protected path rule and the recorded base ref visible in the run report. The existing module level S4 tests keep passing unchanged. Update docs/CHECKS-GATE.md (base ref derivation, --base-ref, the recorded provenance, the non git fallback) and add a CHANGELOG Unreleased note. Keep the whole suite green, all eight pipelines valid, no station added, removed or renamed, and model routing untouched. Every reviewer writes its review to the authoritative review file named in its packet, as one JSON document the parser can read whole; prose in that file is not a review and fails the run closed.
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
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

