# Station Timeout

Status: approved
Slug: station-timeout

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
A producing station that needs more than 1500 seconds of wall clock is killed by a hardcoded constant in the station wrapper, after it has already done the work. The kill is recorded as a bare failure with executed_model null and usage unmeasured, so the run loses the station, the reviewers never count, and the gate reports no_reviews. The defect record with run ids and exact failure strings lives in issue 39. This spec makes the per station timeout configurable project configuration with a raised producing default, keeps a hard ceiling so a runaway station still dies, coordinates the neighbouring timeout layers so the wrapper cap is the binding one, and makes a timeout kill record what is knowable instead of nulls.

## Requirements
- R1 Root cause verified: the builder report states, verified against the tree at the run base, that at 93ae03fc the cap was the module level constant TIMEOUT_SECONDS = 1500 in tools/claude_station.py line 61 and tools/codex_station.py line 51 with no override anywhere in the repo, and that at the base a011c14 the codex wrapper no longer exists (removed in 4c40ea3, decision 0008) and the constant survives at tools/claude_station.py line 63 as the subprocess timeout and in the message "claude_station: station <id> timed out after 1500s", with no override.
- R2 Configurable: the per station timeout follows the existing pattern (anvil.yaml values handed to the wrapper through the environment by the executor, like ANVIL_MAX_RUNTIME_TURNS and ANVIL_RUNTIME). Resolution order: environment variable ANVIL_STATION_TIMEOUT_SECONDS, then project configuration in anvil.yaml, then the station class default. A per station override may exist in addition.
- R3 Defaults: stations in the wrapper WRITE_STATIONS set (builder, test-writer, spec-writer, blueprint, brief-writer, researcher, writer, media-producer) default to at least 3600 seconds; every other station defaults to at least 1500 seconds.
- R4 Ceiling: the hard ceiling is 7200 seconds. A configured value above 7200 is clamped to 7200 or rejected with an error that names 7200. No configuration path yields an effective station timeout above 7200. A non-numeric or non-positive value is rejected with a named reason, never silently defaulted.
- R5 Executor coordination: the effective command executor timeout is never lower than the largest station timeout in effect for the run. The factory anvil.yaml runtime.timeout_seconds is set to at least 7200, or the executor derives its timeout from the station configuration.
- R6 Job timeout: .github/workflows/anvil-line.yml job timeout-minutes (line 66) is raised from 180 to 360.
- R7 Honest timeout record: when a station is killed by its timeout, the run record and the usage artifact carry the station id, the elapsed milliseconds measured around the call, the configured timeout value as the recorded reason, the dispatched model, status timed_out (executed_model is not null), and partial usage when the runtime exposed it (the TimeoutExpired stdout path). When no usage was exposed, usage is recorded as unmeasured with that reason.
- R8 Healthy behaviour unchanged: a station that finishes within its cap records exactly what it recorded before this change, and existing pipelines run unchanged.
- R9 Regression evidence: new test files under tests/ prove the mechanism at scaled values; the full factory suite stays green. The builder report states the exact evidence form (scaled mechanism tests, no live run past 1500 seconds claimed) and the full suite test count.
- R10 Decision and docs: brain/decisions/0011-station-timeout.md records the change and its trade off; CHANGELOG.md is updated; docs/EXECUTION.md and every other factory doc that states the old cap or the timeout behaviour describe the configurable behaviour, the defaults, the ceiling and ANVIL_STATION_TIMEOUT_SECONDS.
- R11 Builder report literals: runs/wo-gh-39/builder.output.md contains in full ANVIL_STATION_TIMEOUT_SECONDS, 3600, 7200 and station-timeout, plus the configuration keys and defaults per station class, the ceiling behaviour and the timeout record fields.

## Scenarios
- S1 (R1) Given the tree at the run base, the builder report names file and line for the constant in both historical wrappers and in tools/claude_station.py today, and each cited line matches `git show` of the named commit.
- S2 (R2) Given ANVIL_STATION_TIMEOUT_SECONDS=100 in the environment and anvil.yaml configuring 200, a builder station resolves to 100. Given only the anvil.yaml value 200, it resolves to 200. Given neither, it resolves to the class default.
- S3 (R3) Given no configuration, resolution for builder returns at least 3600 and for intake returns at least 1500; each of the eight WRITE_STATIONS ids returns at least 3600.
- S4 (R4) Given ANVIL_STATION_TIMEOUT_SECONDS=9000, resolution returns 7200 or raises an error containing "7200". Given the value 7200 it returns 7200. Given "abc", "0" or "-5" it raises an error naming the bad value.
- S5 (R5) Given a station configured at 3600 and runtime.timeout_seconds unset, the effective executor timeout is at least 3600. Given runtime.timeout_seconds 1800 and a station at 3600, the effective executor timeout is at least 3600. The factory anvil.yaml value is at least 7200.
- S6 (R6) Given .github/workflows/anvil-line.yml, the job at line 66 reads timeout-minutes: 360 and no job timeout of 180 remains.
- S7 (R7) Given a station command that sleeps past a scaled cap of 1 second, the wrapper exits non-zero, the run record step shows status timed_out, executed_model equal to the dispatched model (not null), elapsed_ms at least 1000, and a reason containing the configured timeout value; the usage artifact carries the same station id, elapsed and timeout. Given the TimeoutExpired stdout carried usage, that partial usage appears in the artifact.
- S8 (R8) Given a station that finishes in under its cap, its run record and usage artifact are identical in shape and values to those produced at the base for the same inputs, and the existing suite passes unmodified.
- S9 (R9) Given a producing station whose work takes 2 seconds under a scaled legacy cap of 1 second and a configured cap of 5 seconds, it completes and is counted in the run record. Given a station whose work takes 3 seconds under a configured cap of 1 second, it dies and the S7 record is produced. Given the suite run, the count and a zero failure total appear in the builder report.
- S10 (R10) Given the finished tree, brain/decisions/0011-station-timeout.md exists, CHANGELOG.md has an entry naming station-timeout, docs/EXECUTION.md names ANVIL_STATION_TIMEOUT_SECONDS, 3600 and 7200, and a search of docs/ for "1500" finds no statement of the old cap as current behaviour.
- S11 (R11) Given runs/wo-gh-39/builder.output.md, a search finds each of ANVIL_STATION_TIMEOUT_SECONDS, 3600, 7200 and station-timeout.

## Out of scope
- Any live run longer than 1500 seconds; merging, publishing or deploying anything.
- Changing station prompts, pipeline stage order, model selection, or retry behaviour.
- New dependencies; Python standard library only. No em dash or en dash character in any produced file.

## Allowed write set
- tools/claude_station.py, tools/dispatch_station.py (if needed), anvil/executor.py, anvil/runner.py, anvil/telemetry.py, anvil/config.py (as needed).
- anvil.yaml, .github/workflows/anvil-line.yml, CHANGELOG.md, docs/EXECUTION.md and other docs that state the old cap, brain/decisions/0011-station-timeout.md.
- NEW test files under tests/ (for example tests/test_station_timeout.py). tests/ is a protected path: existing test files at the base ref are not modified or deleted; only new files are added.
- runs/wo-gh-39/ outputs for the stations.
- Not to be edited: anvil.json, anything under pipelines/, existing files under tests/.
