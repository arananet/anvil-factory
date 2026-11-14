# Builder report: wo-gh-39 station-timeout

Spec: .openspec/specs/station-timeout/spec.md (R1 to R11, S1 to S11). The implementation from the earlier attempt on this branch already meets every scenario. This attempt makes no code changes. I re-verified it on the final tree (HEAD c4f77b3, which includes operator fix 36c18c4) and rewrote this report, which was missing from the run tree.

## Change since the last attempt: checks gate environment

Last time the checks gate failed on 5 approval tests that already failed before this order: test_autonomous_line.TestHumanGate x3 and test_governed_delivery.TestApprovalPolicy x2. The cause was the CI host identity (GITHUB_ACTOR=arananet) leaking into the check command.

Operator commit 36c18c4 fixed this in anvil/gates.py. `_run_shell` now removes HOST_IDENTITY_ENV (GITHUB_ACTIONS, GITHUB_ACTOR, GITHUB_ACTOR_ID, GITHUB_TRIGGERING_ACTOR) from the check subprocess (anvil/gates.py:102 and :106). That change came from the operator, not from this station.

## S1 Root cause, verified against the tree

Checked with `git show <ref>:<file> | grep -n "TIMEOUT_SECONDS\|timed out after"`:

| Ref | File:line | Content |
|---|---|---|
| 93ae03fc (historical) | tools/claude_station.py:61 | `TIMEOUT_SECONDS = 1500`; subprocess timeout at :246; message at :250 |
| 93ae03fc (historical) | tools/codex_station.py:51 | `TIMEOUT_SECONDS = 1500`; used at :203 and :411; message at :415 "codex_station: station <id> timed out after 1500s" |
| a011c14 (main, after the codex wrapper was removed) | tools/claude_station.py:63 | `TIMEOUT_SECONDS = 1500`; subprocess timeout at :272; message at :276 |

- Neither wrapper had an environment or configuration override at either ref.
- tools/codex_station.py does not exist at a011c14.
- On the final tree the hardcoded constant is gone from tools/claude_station.py. It now calls `resolve_station_timeout` at tools/claude_station.py:211.

## What changed, by scenario

### S2 Configuration (anvil/config.py)

`resolve_station_timeout(station, environ, configured)` resolves the timeout in this order:

1. The environment variable `ANVIL_STATION_TIMEOUT_SECONDS`.
2. anvil.yaml `runtime.station_timeout_seconds`.
3. The class default.

Class defaults:

| Station class | Stations | Default |
|---|---|---|
| Producing (`PRODUCING_STATIONS`, which mirrors the wrapper's WRITE_STATIONS; a test checks the two sets match) | builder, test-writer, spec-writer, blueprint, brief-writer, researcher, writer, media-producer | **3600** seconds |
| Every other station | all others | 1500 seconds |

### S2 Ceiling

- `STATION_TIMEOUT_CEILING` is **7200**.
- A value above 7200 is **clamped** to 7200 whatever its source. The record keeps the requested value, and the wrapper prints that the station runs with 7200s. Decision 0011 records clamping as the choice.
- A value that is not an integer, or is boolean, zero or negative, is rejected. The ValueError names the source and the value, for example `ANVIL_STATION_TIMEOUT_SECONDS must be a positive integer number of seconds, got 'abc'`. The wrapper exits 10 and the executor raises at construction.

### S2 Handoff and executor coordination (anvil/executor.py, anvil.yaml, workflow)

- The executor validates `runtime.station_timeout_seconds`. It passes the value to the wrapper as `ANVIL_STATION_TIMEOUT_SECONDS` unless the environment already sets it, the same pattern as ANVIL_MAX_RUNTIME_TURNS and ANVIL_RUNTIME (anvil/executor.py:95 to :134).
- `effective_executor_timeout` returns max(runtime.timeout_seconds, largest station timeout in effect + 60). The command executor timeout is therefore never lower than any station timeout, and the wrapper stays the binding cap.
- The factory anvil.yaml `runtime.timeout_seconds` went from 1800 to 7200.
- `.github/workflows/anvil-line.yml:66` sets `timeout-minutes: 360`.

### S2 Wrapper (tools/claude_station.py)

The timeout is resolved per station and bounds the whole invocation, including the correction attempt. Each subprocess gets the time remaining.

### S3 Honest timeout records

- **Usage artifact** (wrapper plus anvil/telemetry.py `UsageRecorder.record(extra=...)`). A killed station appends an attempt with these fields:
  - `status: timed_out`
  - `station`
  - `duration_ms` (elapsed time, measured)
  - `timeout_seconds`
  - `reason`, for example "station timeout of 3600s reached (class default)"
  - `configured_model` (the model that was dispatched)

  Partial usage is parsed from the TimeoutExpired stdout. When the runtime exposed nothing, `usage_reason` says so instead of leaving a null.
- **Run record** (anvil/runner.py `_timeout_record`). The step records `status: timed_out` and `step["timeout"] = {station, source, timeout_seconds, elapsed_ms, reason}`. For a timed-out station, `executed_model` names the dispatched model instead of null.
- **Executor timeout.** If the executor's own timeout fires, it writes a `source: executor` record with the elapsed time and the reason.
- **Telemetry.** `summarize_steps` counts timed_out steps as calls.

### S4 Regression evidence

The evidence is **scaled mechanism tests**: deterministic, using a fake runtime CLI, at scaled values. No live run past 1500 seconds is claimed.

- tests/test_station_timeout.py (new, test-writer) covers:
  - (a) a producing station with 2s of work against a scaled legacy cap of 1s completes and is counted in the run record
  - (b) a station past its configured cap still dies, with timed_out, elapsed and the timeout value recorded
  - (c) the resolution order, the 3600 producing default, the 7200 ceiling clamp and rejection of bad values
  - executor coordination, the anvil.yaml value, the 360-minute job timeout and the docs
- tests/test_station_timeout_config.py (new) covers:
  - the PRODUCING_STATIONS and WRITE_STATIONS sets agree
  - the executor hands the project value to the wrapper environment
  - the environment value wins over the project value
  - a project value above 7200 is clamped before handoff
  - an invalid value is rejected
  - a timed_out usage attempt becomes an executor timeout record
- No existing test file was modified or deleted.

### S5 Decision and docs

- brain/decisions/0011-station-timeout.md (new)
- CHANGELOG.md
- docs/EXECUTION.md: configurable timeout, station classes, ceiling, executor coordination, timeout record
- docs/COST-MEASUREMENT.md: timed_out attempts and usage_reason

## Verification (final tree, real summary lines)

- Full factory suite, with the host identity removed the same way the gate now does it:
  - Command: `env -u GITHUB_ACTIONS -u GITHUB_ACTOR -u GITHUB_ACTOR_ID -u GITHUB_TRIGGERING_ACTOR python -m unittest discover -s tests -p 'test_*.py'`
  - Result: `Ran 736 tests in 76.030s` / `OK (skipped=6)`
  - **Full factory test count: 736, all passing (6 skipped).**
- The same command run raw in this Actions shell, where GITHUB_ACTOR=arananet is set: `Ran 736 tests` / `FAILED (failures=5, skipped=6)`. These are only the 5 pre-existing approval tests. The checks gate no longer passes the host identity to the check command (operator fix 36c18c4).
- `python -m unittest tests.test_station_timeout tests.test_station_timeout_config`: `Ran 26 tests` / `OK`.
- Called directly:

| Call | Result |
|---|---|
| builder, no overrides | 3600 (class default) |
| intake, no overrides | 1500 (class default) |
| `ANVIL_STATION_TIMEOUT_SECONDS=9000` | 7200 (requested 9000) |
| project value 2400 | 2400 (source runtime.station_timeout_seconds) |
| `effective_executor_timeout`, configured 1800 | 3660 |
| `effective_executor_timeout`, configured 7200 | 7200 |
| `ANVIL_STATION_TIMEOUT_SECONDS=abc` | rejected with the name and the value |

- Hygiene checks:
  - No U+2013 or U+2014 in any file changed on this branch (grep -P).
  - No changes under pipelines/, in anvil.json, or to existing tests (`git diff --diff-filter=MD aa8a7f8 HEAD -- tests` is empty).

## Unmet or open

- No live station has run past 1500 seconds. The evidence is the scaled mechanism tests, as S4 specifies.
- `effective_executor_timeout` takes the builder's timeout as the largest in effect. That holds because any override applies to every station alike and the producing default is the larger class default. A per-station override map, which the spec does not ask for, would need this revisited.
- The branch diff against the spec commit also includes operator-owned changes this station did not write: anvil/gates.py, status/*, and tools/model_route_smoke.py.
{"model": "claude-opus-5-5"}
