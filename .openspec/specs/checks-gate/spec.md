# Deterministic Checks Gate

Status: approved
Slug: checks-gate

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
Reviewers judge work, but nothing in the line first proves the work simply passes the project's own checks, and nothing stops a branch from quietly editing the checks it will be judged by. This spec adds a deterministic gate to the runner: a whole-suite check that runs before any reviewer sees the work, takes its check definitions from the base ref rather than the work branch, refuses branches that touch protected paths, and runs again before anything is deployed or published. The gate is a machine verdict, not a model opinion: the project's configured commands exit zero or they do not.

## Requirements
- Project configuration declares the checks: an ordered list of commands (the project's test and build commands) in the project config, plus a protected paths list. When a project declares no checks, the gate records itself as not configured and the run proceeds as today; the absence is visible in the report, never silent.
- Protected paths default to the checks configuration itself and the project's tests directory (tests/). A project may extend or replace the list in its config. Paths are matched as prefixes of repo relative paths.
- The pre-review gate runs after the builder station completes and before the parallel reviewer stage. The check commands and the protected path list are resolved from the base ref state of the project (the state the work order branched from, as recorded at run start), never from files the builder may have changed during the run. The runner snapshots the base ref check configuration at run start and the gate uses that snapshot.
- A gate failure (any check command exits non zero, or the run's changed file list touches a protected path) returns the work to the builder with the gate log attached to the builder feedback, and no reviewer station is spawned for that attempt. A gate failure consumes a loopback exactly like a reviewer changes_requested does, and the run's max loopbacks still bound the total.
- The gate runs a second time after any merge sync and before the deployer or publisher station executes. A failure at that point stops the run before deploy or publish and is recorded as the run's blocking reason.
- The changed file list for protected path checks is the set of files the run has written or modified relative to the base ref snapshot, tracked by the runner the same way it tracks station outputs. Deleting a protected file counts as touching it.
- Every gate run is recorded in the run report: when it ran (pre-review or pre-deploy), the commands run, each exit code, the protected path verdict, and the overall gate verdict. The swimlane shows the gate as its own step so a reader can see it without opening the report JSON.
- This gate complements the scenario-to-test gates, it does not replace or duplicate them: those gates map spec scenarios to tests; this gate is the project's whole-suite exit code plus the protected path rule.

## Scenarios

### Scenario: Passing checks let the reviewers run
- S1: Given a project whose configured checks all exit zero and a builder output that touches no protected path, when the pre-review gate runs, then the gate verdict is pass, the reviewer stage is spawned, and the run report records the gate with its commands and exit codes.

### Scenario: Failing checks return the work to the builder and no reviewer is spawned
- S2: Given a project whose configured checks exit non zero, when the pre-review gate runs, then no reviewer station executes for that attempt, the work returns to the builder with the gate log in the builder feedback, the loopback counter increases by one, and the report records the gate failure with the failing command and its exit code.

### Scenario: A branch that touches a protected path fails the gate automatically
- S3: Given a run whose changed files include a path under a protected prefix (by default the checks configuration or anything under tests/), when the gate runs, then the gate verdict is fail with a protected path finding naming the path, regardless of the check commands' exit codes, and the reviewer stage is not spawned.

### Scenario: Check definitions come from the base ref, not the work branch
- S4: Given a builder output that modifies the project's checks configuration on the work branch, when the gate resolves which commands to run, then it runs the commands from the base ref snapshot taken at run start, and the modification itself is reported through the protected path rule.

### Scenario: The gate runs again before deploy or publish
- S5: Given a run that passed review and reaches the deployer or publisher station after a merge sync, when the pre-deploy gate runs and any check fails, then the deployer or publisher station does not execute and the run report records the gate failure as the blocking reason; and given all checks pass, then the deploy or publish step proceeds.

### Scenario: A project with no checks configured records the gate as not configured
- S6: Given a project with no checks in its configuration, when a run executes, then the report records the gate as not configured, the run proceeds through the reviewer stage as it does today, and no gate failure is recorded.
