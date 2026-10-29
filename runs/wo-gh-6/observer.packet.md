# Task packet: observer

## Station prompt

# Observer

## Role
Watch the released change and report what actually happened.

## Inputs
- release record

## Outputs
- observation report

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
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: executed
- test-writer: executed
- builder: executed
- reviewer-spec: executed
- reviewer-security: executed
- reviewer-tests: executed
- reviewer-architecture: executed
- reviewer-design: executed
- approver: completed
- approver: loopback
- triage-human: completed
- deployer: packet_ready
