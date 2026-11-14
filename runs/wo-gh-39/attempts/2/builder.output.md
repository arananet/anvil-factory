# Builder report: wo-gh-39 (station-timeout), attempt 2

Spec: .openspec/specs/station-timeout/spec.md. Decision: brain/decisions/0011-station-timeout.md.

## Loopback resolution

Attempt 1 was sent back because this report was missing and the suite was red.
- The report now exists at runs/wo-gh-39/builder.output.md.
- Suite red: the 5 failing tests are pre-existing and environment dependent, not caused by this change (evidence below). All station-timeout tests pass.
- Kept from attempt 1: the full implementation. Added in attempt 2: tests/test_station_timeout_config.py (new file, 7 tests). The CHANGELOG and config.py already referred to that file, but it did not exist yet.

## S1 Verified root cause (checked with git show against the tree)

- 93ae03fc: `TIMEOUT_SECONDS = 1500` at tools/claude_station.py line 61 and at tools/codex_station.py line 51. In codex_station.py it is used at line 203 (completion timeout) and line 411 (subprocess timeout), and line 415 prints "codex_station: station <id> timed out after 1500s".
- 4c40ea3 removed tools/codex_station.py (decision 0008, one station runtime).
- a011c14 (base before this order): `TIMEOUT_SECONDS = 1500` at tools/claude_station.py line 63. It was the subprocess timeout and appeared in "claude_station: station <id> timed out after 1500s". No environment or config override existed.
- Neighbouring layers: anvil/executor.py `timeout_seconds`, default 300, and factory anvil.yaml `runtime.timeout_seconds` 1800. Once the station cap rose, 1800 would have become the binding cap. The anvil-line.yml job allowed 180 minutes.
- Now: the constant is gone (tools/claude_station.py line 64 holds a comment pointing to the resolver). The timeout is resolved in anvil/config.py `resolve_station_timeout`.

## S2 Configuration (files: anvil/config.py, anvil/executor.py, tools/claude_station.py, anvil.yaml, .github/workflows/anvil-line.yml)

Resolution order, highest first:
1. Environment `ANVIL_STATION_TIMEOUT_SECONDS`.
2. anvil.yaml `runtime.station_timeout_seconds`. The CommandExecutor validates it and hands it to the wrapper as ANVIL_STATION_TIMEOUT_SECONDS unless the environment already sets that variable. This follows the ANVIL_RUNTIME pattern.
3. Class default:
   - 3600 s for producing stations: builder, test-writer, spec-writer, blueprint, brief-writer, researcher, writer, media-producer (anvil.config.PRODUCING_STATIONS, the same set as the wrapper WRITE_STATIONS).
   - 1500 s for every other station.

Ceiling:
- STATION_TIMEOUT_CEILING = 7200. A value above 7200 is clamped to 7200. The wrapper prints a stderr line naming the requested value and the ceiling.
- A value that is not a positive integer raises ValueError naming the value and its source. The executor refuses to construct, and the wrapper exits 10.
- The timeout bounds the whole wrapper invocation, including the correction attempt (the remaining budget is passed per call).

Executor coordination:
- `effective_executor_timeout` = max(runtime.timeout_seconds or 300, largest station timeout in effect + 60). The wrapper is therefore always the binding cap and writes its record first.
- Factory anvil.yaml `runtime.timeout_seconds` changed from 1800 to 7200.
- anvil-line.yml job `timeout-minutes: 360` (line 66). This was applied by operator commit 472812b and verified on the tree.

## S3 Honest timeout records (files: tools/claude_station.py, anvil/telemetry.py, anvil/executor.py, anvil/runner.py)

Usage artifact (`<station>.output.md.usage.json`): the attempt has these fields:
- `status: timed_out`
- `station`
- `duration_ms` (elapsed time measured around the call)
- `timeout_seconds`
- `reason` (e.g. "station timeout of 3600s reached (class default)")
- `configured_model`
- partial usage parsed from TimeoutExpired stdout (bytes are decoded), or `usage_complete: false` plus `usage_reason` when nothing was exposed.

Run record step:
- `status: timed_out`
- `executed_model` = the dispatched model, not null
- a `timeout` object: station, source (station or executor), timeout_seconds, elapsed_ms, reason.

An executor-level timeout records the same shape with source `executor`. telemetry.summarize_steps counts timed_out steps as calls.

## S4 Regression evidence: scaled mechanism tests (new files only; no existing test modified)

- tests/test_station_timeout.py, 19 tests. Uses the real wrapper with a fake claude CLI at scaled values:
  - (a) a producing station doing 2 s of work against a scaled legacy cap of 1 s completes under the new configuration and is counted in the run record;
  - (b) a station past its configured cap still dies, with the timeout recorded as elapsed, timeout value and status timed_out, including partial usage;
  - (c) resolution: producing default 3600, environment beats project config beats default, above 7200 clamped, bad values rejected. It also checks the executor coordination, anvil.yaml 7200, the job timeout 360, docs and that no dashes appear.
- tests/test_station_timeout_config.py, 7 tests:
  - the PRODUCING_STATIONS and WRITE_STATIONS sync guard;
  - executor handoff of the project value, with the environment winning;
  - clamping before handoff;
  - invalid project values rejected with the key named;
  - a usage artifact timed_out attempt surfacing as the executor timeout record.
- No live run past 1500 seconds is claimed; the scaled mechanism tests are the evidence.

## S5 Decision and docs

- brain/decisions/0011-station-timeout.md (new).
- CHANGELOG.md entry.
- docs/EXECUTION.md "Station timeout" section (order, defaults, ceiling, executor coordination, record fields).
- docs/COST-MEASUREMENT.md timed_out usage wording.

## Verification (run on the final tree)

- `python -m unittest discover -s tests -p 'test_*.py'` (in this CI environment):
  `Ran 736 tests`, `FAILED (failures=5, skipped=6)`. The failures:
  - test_autonomous_line.TestHumanGate: test_approval_rules_s4, test_approve_and_resume_deploys_s4, test_publisher_held_until_approved_s5
  - test_governed_delivery.TestApprovalPolicy: test_identity_and_policy_s5, test_policy_comes_from_the_operator_checkout_s5

  They fail with "Approval refused: --by bo does not match the authenticated GitHub actor arananet". The cause is GITHUB_ACTIONS=true and GITHUB_ACTOR=arananet in the station environment. The same 5 fail on an untouched `git archive HEAD` copy of the base. They are not caused by this change.
- `env -u GITHUB_ACTIONS -u GITHUB_ACTOR -u GITHUB_ACTOR_ID python -m unittest discover -s tests -p 'test_*.py'`: `Ran 736 tests`, `OK (skipped=6)`. Full factory test count: 736.
- `python -m unittest tests/test_station_timeout_config.py`: `Ran 7 tests`, `OK`. The station-timeout files (19 + 7) pass in both environments.
- I ran the real wrapper the way the line does, through the Wrapper harness in tests/test_station_timeout.py, which runs tools/claude_station.py as a subprocess.

## Open items

- The checks gate will see the same 5 environment-dependent approval failures unless it runs without the Actions identity variables. Fixing those tests is outside this order's write set, because existing tests are protected.
- The run artifacts under runs/wo-gh-39/ (from upstream stations) are modified in the tree. That is line bookkeeping, not part of this change.
{"model": "claude-opus-5-5"}
