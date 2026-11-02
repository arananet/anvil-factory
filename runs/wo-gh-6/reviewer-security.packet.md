# Task packet: reviewer-security

## Station prompt

# Reviewer Security

## Role
Check the change for security risks and unsafe defaults.

## Inputs
- code change

## Outputs
- review

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
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: failed
- test-writer: failed
- builder: failed
- checks-gate: passed
- reviewer-spec: failed

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-6/reviewer-security.review.json. The free output transcript stays as provenance and is never parsed for a review.
