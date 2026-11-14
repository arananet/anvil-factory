# Builder report: wo-gh-39 station-timeout (attempt 3 of 3)

Spec: .openspec/specs/station-timeout/spec.md. Attempt 3 keeps the attempt 2 implementation unchanged (it already satisfies every scenario and its tests pass). This attempt investigated the checks-gate failure, verified the implementation again and wrote this report, which was missing from the run tree.

## Checks-gate finding from attempt 2: diagnosis

The gate reported 5 failing tests, all in the approval code path:

- test_autonomous_line.TestHumanGate.test_approval_rules_s4
- test_autonomous_line.TestHumanGate.test_approve_and_resume_deploys_s4
- test_autonomous_line.TestHumanGate.test_publisher_held_until_approved_s5
- test_governed_delivery.TestApprovalPolicy.test_identity_and_policy_s5
- test_governed_delivery.TestApprovalPolicy.test_policy_comes_from_the_operator_checkout_s5

These failures come from the environment, not from this change, and they were already there before it:

- The line runs inside GitHub Actions with GITHUB_ACTIONS=true and GITHUB_ACTOR=arananet. anvil/line.py approver_identity (line 151 onward) reads GITHUB_ACTOR. These tests either do not patch the environment or patch GITHUB_ACTOR without clearing the host values. So "--by ana" is refused with "does not match the authenticated GitHub actor arananet". Example from the gate: 'Approval refused: --by bo does not match the authenticated GitHub actor arananet'.
- I reproduced it on a clean detached worktree of HEAD (c673c25), which has none of this order's changes. The same 5 tests fail there.
- With the host identity removed, the full suite on the final tree is green (see Verification).

I did not fix it. The code involved (anvil/line.py, anvil/gates.py) is outside this order's write set. The tests are protected and may not be edited. Loosening the approval identity check to make them pass would weaken a security control. **Open item for the operator:** run the check command without the host GitHub identity variables, or make those tests isolate the environment in a separate order. Until then, checks-gate will keep reporting these 5 failures in the Actions environment whatever this order contains.

## S1 Root cause, verified against the tree

| Ref | File:line | Content |
|---|---|---|
| 93ae03fc (historical) | tools/claude_station.py:61 | `TIMEOUT_SECONDS = 1500`, used at :246 (subprocess timeout) and :250 (message) |
| 93ae03fc (historical) | tools/codex_station.py:51 | `TIMEOUT_SECONDS = 1500`, used at :203, :411 (subprocess timeout) and :415 "codex_station: station <id> timed out after 1500s" |
| a011c14 (current main, codex wrapper removed) | tools/claude_station.py:63 | `TIMEOUT_SECONDS = 1500`, used at :272 and :276 |
| run base 472812b / HEAD c673c25 | tools/claude_station.py:63 | same constant, same uses at :272 and :276 |

Verified with `git show <ref>:<file> | grep -n TIMEOUT_SECONDS`. Neither historical wrapper had an environment or configuration override. On the final tree the constant is gone from tools/claude_station.py.

## What changed, by scenario

- **S2 configuration** (anvil/config.py). `resolve_station_timeout(station, environ, configured)` resolves in this order:
  1. the environment variable `ANVIL_STATION_TIMEOUT_SECONDS`
  2. anvil.yaml `runtime.station_timeout_seconds`
  3. the class default

  Class defaults:
  - Producing stations (builder, test-writer, spec-writer, blueprint, brief-writer, researcher, writer, media-producer): **3600** seconds.
  - Every other station: 1500 seconds.

  `PRODUCING_STATIONS` mirrors the wrapper's WRITE_STATIONS. There is a SYNC comment at the shared site, and a test checks that the two sets match.
- **S2 ceiling.** The ceiling is **7200** seconds (`STATION_TIMEOUT_CEILING`).
  - A configured value above it is clamped to 7200 whatever its source. The wrapper prints that the requested value is above the 7200s ceiling and that the station runs with 7200s.
  - A non-integer, boolean, zero or negative value is rejected. The ValueError names the value and its source. The wrapper exits 10, and the executor raises at construction.
- **S2 handoff** (anvil/executor.py). The executor validates `runtime.station_timeout_seconds` at the boundary. It hands the value to the wrapper as `ANVIL_STATION_TIMEOUT_SECONDS` unless the environment already sets it, the same pattern as ANVIL_MAX_RUNTIME_TURNS and ANVIL_RUNTIME.
- **S2 executor coordination** (anvil/config.py `effective_executor_timeout`). The executor timeout is max(runtime.timeout_seconds, largest station timeout in effect + 60s margin). The wrapper is therefore always the binding cap and writes its record first. The factory anvil.yaml `runtime.timeout_seconds` went from 1800 to 7200.
- **S2 job timeout.** .github/workflows/anvil-line.yml `timeout-minutes: 360`, already applied by operator commit 472812b and verified at line 66.
- **S2 wrapper** (tools/claude_station.py). The timeout is resolved per station and bounds the whole invocation, including the correction attempt: each subprocess gets the time remaining.
- **S3 honest timeout records:**
  - **Wrapper** (tools/claude_station.py and anvil/telemetry.py `UsageRecorder.record(extra=...)`). A killed station appends an attempt with `status: timed_out`, `station`, `duration_ms` (elapsed measured), `timeout_seconds`, `reason` (for example "station timeout of 3600s reached (class default)"), and `configured_model` (the model dispatched). Partial usage is parsed from TimeoutExpired stdout, which is decoded from bytes. When the runtime exposed nothing, `usage_reason` says so instead of leaving a bare null.
  - **Executor.** It surfaces that attempt as `result["timeout"]`. Its own timeout produces a `source: executor` record with elapsed_ms and the reason.
  - **Runner** (anvil/runner.py `_timeout_record`). The step gets `status: timed_out`, `step["timeout"] = {station, source, timeout_seconds, elapsed_ms, reason}`, and `executed_model` falls back to the dispatched model, so it is never null.
  - **Telemetry.** `summarize_steps` counts timed_out steps as calls.
- **S4 regression evidence.** These are scaled mechanism tests, deterministic, using a fake runtime CLI. No live run past 1500 seconds is claimed.
  - tests/test_station_timeout.py (test-writer, 19 tests):
    - a producing station with 2s of work against a scaled legacy cap of 1s completes and is counted
    - a station past its configured cap still dies, and timed_out is recorded with elapsed and the timeout value
    - resolution order, class defaults, ceiling and bad values
    - executor coordination, the anvil.yaml value, and the docs
  - tests/test_station_timeout_config.py (builder, new file, 7 tests):
    - PRODUCING_STATIONS matches WRITE_STATIONS
    - the project value reaches the wrapper env
    - the environment wins over the project value
    - a project value above the ceiling is clamped before handoff
    - nothing is handed when unset
    - an invalid project value is rejected with its key
    - a timed_out usage attempt becomes an executor timeout record
- **S5 decision and docs.**
  - brain/decisions/0011-station-timeout.md (new)
  - CHANGELOG.md
  - docs/EXECUTION.md (configurable timeout, classes, ceiling, executor coordination, timeout record)
  - docs/COST-MEASUREMENT.md (timed_out attempts and usage_reason)
  - docs/OPERATIONS.md only shows `timeout_seconds` in an example config, so it needed no change.

## Verification (real summary lines, final tree)

- `env -u GITHUB_ACTIONS -u GITHUB_ACTOR -u GITHUB_ACTOR_ID -u GITHUB_TRIGGERING_ACTOR python -m unittest discover -s tests -p 'test_*.py'` gives `Ran 736 tests in 59.343s` / `OK (skipped=6)`. **Full factory test count: 736, all passing.**
- `python -m unittest discover -s tests -p 'test_*.py'` in the Actions environment as is gives `Ran 736 tests` / `FAILED (failures=5, skipped=6)`. These are the 5 approval tests above.
- The same command on a clean worktree of HEAD c673c25, before this change: `Ran 729 tests` / `FAILED (failures=12, errors=5, skipped=6)`. That is the same 5 approval failures plus the not-yet-implemented station-timeout tests.
- `python -m unittest tests.test_station_timeout tests.test_station_timeout_config` gives `Ran 26 tests` / `OK`.
- Exercised the resolution directly:
  - builder resolves to 3600 (class default) and intake to 1500.
  - env 9000 resolves to 7200 (requested 9000, source ANVIL_STATION_TIMEOUT_SECONDS).
  - project value 2400 resolves to 2400.
  - executor timeout is 3660 with the configured 1800, and 7200 with the configured 7200.
  - env "abc" is rejected with the variable name and the value.
- No en dash or em dash in any changed or new file (checked with grep -P for U+2013 and U+2014). Protected paths (pipelines/, anvil.json, existing tests) are untouched.

## Unmet or open

- The 5 environment-dependent approval tests fail when the check runs under the Actions identity. They also fail without this change, and fixing them is outside the write set (see the diagnosis above).
- No live station has run past 1500 seconds. The evidence is the scaled mechanism tests, as S4 specifies.
- `effective_executor_timeout` takes the builder's timeout as the largest in effect. That is correct because any override applies to all stations alike and the producing default is the larger class default. A per-station config map would need this revisited; the spec does not ask for one.
{"model": "claude-opus-5-5"}
