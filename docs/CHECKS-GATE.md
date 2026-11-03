# Checks Gate

## Purpose

The checks gate is a deterministic station that runs the project's configured check commands and validates that protected paths haven't been touched. It acts as a machine verdict before any reviewer sees the work, ensuring that the project's own tests and validations pass before consuming reviewer resources.

Unlike reviewer stations which provide model-based opinions, the checks gate is binary: configured commands either exit zero or they don't. It complements the spec-to-test gates by providing whole-suite validation.

## Configuration

Projects configure the checks gate in their `anvil.json` file:

```json
{
  "checks": [
    "python -m unittest discover -s tests -p 'test_*.py'",
    "python validate-pipeline.py"
  ],
  "protected_paths": [
    "tests/",
    "anvil.json",
    "pipelines/"
  ]
}
```

### Checks

The `checks` field is an ordered list of shell commands. Each command runs with:
- `cwd`: the project root directory
- `ANVIL_WORK_ORDER_ID`: environment variable set to the current work order ID
- Default timeout: 300 seconds per command

All commands must exit with code 0 for the gate to pass.

### Protected Paths

The `protected_paths` field is a list of path prefixes (relative to project root) that are protected from modification during a run. Any change to a file matching a protected path causes the gate to fail automatically, regardless of check command results.

**Default protected paths** (when not explicitly configured):
- `tests/` - the project's test directory
- `anvil.json` - the checks configuration file itself

Projects can extend or replace the defaults by setting `protected_paths` in their configuration.

**Protected path matching**: Paths are matched as prefixes. A protected path of `tests/` matches `tests/test_foo.py`, `tests/unit/bar.py`, etc. Deleting a protected file counts as touching it.

## Base Ref Resolution

**Critical security property**: Check commands and protected paths are resolved from the **base ref** snapshot taken at run start, never from files the builder modified during the run.

This prevents a branch from modifying the checks it will be judged by. The runner:
1. Records the base ref (the commit the work order branched from) at run start
2. Uses `git show <base-ref>:anvil.json` to read the configuration from that ref
3. Falls back to reading the working tree file only when git is not present (non-git projects)

A run that modifies `anvil.json` will trigger the protected path rule (since the config file is protected by default), and the gate will still run the commands from the base ref, not the modified ones.

## Gate Phases

The checks gate runs twice in a full pipeline:

### Pre-Review Phase

Runs after the builder station and before the parallel reviewer stage.

**On failure**:
- No reviewer stations are spawned for that attempt
- Work returns to the builder with the gate log in the builder feedback
- Consumes one loopback (same as a reviewer's `changes_requested`)
- The run's `max_loopbacks` still bounds the total attempts

**On pass**:
- Reviewer stage proceeds normally

### Pre-Deploy Phase

Runs after the approver/triage-human stage and before the deployer or publisher station.

**On failure**:
- Deployer/publisher does not execute
- Run verdict is set to `gate_failed`
- Failure is recorded as the blocking reason

**On pass**:
- Deploy or publish proceeds (subject to other gates like human review)

## Not Configured

If a project has no `checks` configured, the gate records itself as `not_configured` and the run proceeds normally. This state is visible in the run report and swimlane - the absence is never silent.

This allows projects to adopt the gate incrementally without breaking existing pipelines.

## Run Report

Every gate run is recorded in the run report with:
- **phase**: `pre-review` or `pre-deploy`
- **status**: `passed`, `failed`, or `not_configured`
- **commands**: The list of check commands that were run
- **exit_codes**: Exit code for each command
- **protected_paths**: The protected paths list from base ref config
- **protected_path_verdict**: `pass` or `fail`
- **protected_path_findings**: List of protected path violations (if any)
- **gate_verdict**: Overall verdict (`pass`, `fail`, or `not_configured`)
- **output**: Full output from all check commands

The gate appears as its own step in the swimlane, making failures visible without opening the report JSON.

## Dogfooding

The anvil-factory project itself uses the checks gate:

```json
{
  "checks": [
    "python -m unittest discover -s tests -p 'test_*.py'"
  ],
  "protected_paths": [
    "tests/",
    "anvil.json",
    "pipelines/"
  ]
}
```

This ensures that every run:
1. Passes the full test suite before reviewers see it
2. Cannot modify the test suite without triggering the protected path rule
3. Cannot modify the pipeline definitions without explicit detection
4. Uses the test suite and checks from the base ref, not from builder modifications

## Relation to Other Gates

The checks gate complements but does not replace other gates:

- **Spec gate**: Verifies a spec exists with scenarios
- **TDD gate**: Verifies all spec scenarios are referenced in tests  
- **Checks gate**: Verifies the project's whole test suite passes
- **Review gate**: Verifies all four reviews exist and pass (used by `anvil check` on standing reviews)

Each gate has a distinct purpose. The checks gate is the only one that runs arbitrary shell commands and the only one that runs twice (pre-review and pre-deploy).

## Shell Command Safety

Check commands are shell strings executed with `shell=True`. This is safe because:
1. Commands are resolved from the base ref through git, never from working tree files the builder modified
2. The base ref is the state the work order branched from, controlled by the project maintainer
3. The `ANVIL_WORK_ORDER_ID` environment variable is set but command execution remains in the project directory context

Projects should write check commands that are safe to run in their CI environment. The gate does not sandbox or otherwise restrict command execution.
