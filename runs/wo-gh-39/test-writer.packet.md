# Task packet: test-writer

## Station prompt

# Test Writer

## Role
Write tests that map to spec scenarios before implementation.

## Inputs
- spec

## Outputs
- tests

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the tests scoped to the spec scenarios for this work order.

## Definition of done
- Each spec scenario has at least one test that names it, written as a file in the project's test layout and framework.
- The tests exercise the real artifact the order produces (the real file, function or command). A test that never touches the real artifact is a facade and fails the order.
- The new tests fail now, before the build, for the right reason. Run them and confirm.
- Existing tests are not weakened, skipped or deleted.
- When your packet carries a Craft skills section, hold the tests to it.

## Before you hand off
Run the project check command and record the real result. In your reply, map each scenario id to its test, state the baseline count and what you added, and name any scenario you could not cover and why.

## Consumption discipline

Read the spec and the relevant upstream artifacts first. Search before opening files; read only the relevant ranges. Bound command output and summarize long test logs with failures and a path to the full log. Run focused checks while editing and the required project checks at handoff. Reuse valid upstream work. Keep the final handoff concise, with changed files, evidence and unresolved issues. Preserve the required output contract.


## Craft skills

Curated craft guidance resolved for this station and this work order. Order of authority: the work order and its spec, then the project design system and decisions, then promoted practices, then these skills. Where a skill conflicts with any of those, the skill yields. Apply what fits the work in front of you; a skill is a bar to meet, not a checklist to recite.

### Skill: test-design

A test is evidence only if it would fail when the behaviour is wrong. A suite that passes against an empty implementation, or that never touches the real artifact, is a facade and is worse than no suite because it is trusted.

**Map to the spec**
- One spec scenario, at least one test, named after the scenario it proves (S3 in the test name or docstring). A reader should be able to go from a scenario id to its test and back.
- Test the behaviour the scenario states, through the public interface. Do not assert private structure, call order or exact log text unless the spec requires it.

**Make the test able to fail**
- Before the implementation exists the new tests must fail, and fail for the right reason (the behaviour is missing, not an import error). Run them and record that.
- Exercise the real thing: read the real file the order produces, call the real function, run the real command. A test that builds its own copy of the expected output and checks the copy proves nothing.
- Assert specific values. `assertTrue(result)` and "does not raise" are rarely enough; state the expected value, count or message.
- Do not mock the unit under test, and do not mock so much that the test only checks the mocks. Fake the edges (network, clock, randomness), keep the logic real.

**Cover what breaks**
- For each scenario ask: empty, one, many; the boundary and one past it; malformed input; missing file or dependency; repeated call; wrong type. Write the cases that could plausibly fail.
- For every validation rule, test one input that passes and one that is rejected with the named reason.
- For anything computed from the tree (counts, lists, versions), compute the expected value in the test at run time instead of hard coding a number that will go stale.

**Keep tests trustworthy**
- Deterministic: no dependence on wall clock, test order, network or leftover files. Use temporary directories and fixed seeds.
- Isolated: each test sets up what it needs and cleans up. No test depends on another having run.
- Fast and readable: arrange, act, assert, with one clear reason to fail per test. Use helpers for setup so the body shows only what matters.
- Follow the project's existing test framework, layout and naming. Do not add a test dependency the project does not already use.

**Account for the suite honestly**
- State the baseline count before your change, the tests you added and the tests you edited, and why each edit was needed.
- Never weaken, skip or delete an existing test to make a run pass. If an existing test is wrong, say so and name it; that is a finding, not a cleanup.
- Reported results must reproduce against the final tree. Run the full project check command last and quote its real summary line.

## Work order

- id: wo-gh-39
- kind: feature
- title: Configurable per-station timeout: the hardcoded 1500s station cap becomes project configuration with a 3600s producing default and honest timeout records
- source: github-issue
- description: Implement the spec in .openspec/specs/station-timeout/spec.md. Pipeline for this order is sdlc-default, selected by the run workflow.

ROOT CAUSE (operator located; the line must verify it and record the verification in the builder report):
At factory main 93ae03fc the 1500s cap lived as a module level constant TIMEOUT_SECONDS = 1500 in both station wrappers: tools/claude_station.py line 61 and tools/codex_station.py line 51, hardcoded, with no environment or configuration override anywhere in the repo. The codex wrapper killed its child at that value and printed "codex_station: station <id> timed out after 1500s", the verbatim reason recorded in the C64 wo-gh-3 run report.
At current factory main a011c14 the codex wrapper is gone (removed in 4c40ea3, decision 0008, one station runtime) and the same constant survives in the one remaining wrapper: tools/claude_station.py line 63, TIMEOUT_SECONDS = 1500, used as the subprocess timeout and in the message "claude_station: station <id> timed out after 1500s". Still no override exists. Two neighbouring layers do not save a long station and must be coordinated by the fix: the command executor timeout (anvil/executor.py, config timeout_seconds, default 300; the factory anvil.yaml sets runtime.timeout_seconds to 1800, which would become the binding cap the moment the station cap rises above it), and the anvil-line.yml job timeout of 180 minutes.
Evidence trail of the defect: Mochi Paint wo-gh-1 era, test-writer and builder killed at 1500s after deliverables were already on disk; Mochi Paint wo-gh-3 run 43123553143, builder killed before its report, gate no_reviews; Mochi Paint wo-gh-4 run 43130769702, builder killed a fourth time; C64 wo-gh-3 run 43589402657, builder via the codex wrapper, "station builder timed out after 1500s", duration 1,500,238 ms, executed_model null, usage unmeasured, after building the whole product. A killed station records executed_model null and usage unmeasured. Project side mitigation does not reach the cap: the C64 filing raised the job timeout to 240 minutes and the per station cap did not move.

BUILD, per the spec scenarios:
S1 Diagnosis recorded: the builder report states where the cap lived in both historical wrappers and where it lives now, with file and line, verified against the tree at the run base.
S2 Configurable per station timeout, following the factory existing configuration patterns (anvil.yaml values handed to the wrapper through the environment by the executor, like ANVIL_MAX_RUNTIME_TURNS and ANVIL_RUNTIME): the environment override is named ANVIL_STATION_TIMEOUT_SECONDS and wins over project configuration in anvil.yaml, which wins over the class default. Producing stations (the wrapper WRITE_STATIONS set: builder, test-writer, spec-writer, blueprint, brief-writer, researcher, writer, media-producer) default to at least 3600 seconds. Other stations keep a default of at least 1500 seconds. A hard ceiling of 7200 seconds remains: a configured value above the ceiling is clamped to 7200 or rejected with the ceiling named, so a runaway station still dies. The executor layer is coordinated: the effective command executor timeout is never lower than the largest station timeout in effect, and the factory anvil.yaml runtime.timeout_seconds is updated to prove it. The anvil-line.yml job timeout is raised to 360 minutes so one long producing station plus the rest of the pipeline fits in one job.
S3 Honest timeout records: a station killed by the timeout still records what is knowable in the run record and usage artifact: the station id, the elapsed milliseconds measured, the configured timeout value as the recorded reason, the model that was dispatched, and partial usage when the runtime exposes it (the TimeoutExpired stdout path). Not nulls across the record: executed_model for a timed out station names the model that ran with status timed_out.
S4 Regression evidence: the full factory test suite green, plus NEW test files under tests/ proving the mechanism deterministically at scaled values: (a) a producing station whose work runs past a scaled old cap (for example work of 2 seconds against a scaled legacy cap of 1 second) completes under the new configuration and is counted; (b) a station exceeding its configured cap still dies and the timeout is recorded with elapsed, timeout value and status; (c) configuration resolution: producing default 3600, environment override wins over project config, values above the 7200 ceiling are clamped or rejected. Scaled mechanism tests are the evidence form for the past cap completion; no live run past 1500 seconds is claimed.
S5 Decision and docs: a new record brain/decisions/0011-station-timeout.md capturing the change, CHANGELOG.md updated, and every factory doc that states the old cap or the timeout behaviour (docs/EXECUTION.md at minimum) updated to the configurable behaviour.

BUILDER REPORT REQUIRED LITERALS: the builder report (runs/wo-gh-39/builder.output.md) must contain each of these in full, unabbreviated: ANVIL_STATION_TIMEOUT_SECONDS, 3600, 7200, station-timeout. It must also state the verified root cause with file and line, the configuration keys and defaults per station class, the ceiling behaviour, the timeout record fields, the exact form of the regression evidence (scaled mechanism tests), and the full factory test count from the suite run.

GUARDRAILS: implement in the wrapper and spine (tools/claude_station.py, tools/dispatch_station.py if needed, anvil/executor.py, anvil/runner.py, anvil/telemetry.py, anvil/config.py as needed) plus anvil.yaml, .github/workflows/anvil-line.yml, docs, CHANGELOG.md and the new decision record. Pipeline files under pipelines/ are protected paths in anvil.json; the fix must hold without editing them. anvil.json itself is protected; do not edit it. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. Python standard library only, no new dependency. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/39


GitHub issue: https://github.com/arananet/anvil-factory/issues/39
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed

## Run context

Read the upstream work before you start; it is the input your station builds on.
The checks gate runs the project checks listed here; run them yourself before you hand off.

- Output of intake: runs/wo-gh-39/intake.output.md
- Output of spec-writer: runs/wo-gh-39/spec-writer.output.md
- Project check: `python -m unittest discover -s tests -p 'test_*.py'`
