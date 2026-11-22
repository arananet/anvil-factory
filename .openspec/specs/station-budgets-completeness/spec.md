# Per-Station Token Budgets and a Completeness Gate Before Review

Status: proposed
Slug: station-budgets-completeness
Work order: wo-gh-42 (https://github.com/arananet/anvil-factory/issues/42)
Base ref: factory main 72a84126a600fafb99446946694b5de809e01e66 (carries wo-gh-41 continuous run accounting, the factory CI fix and the runtime refusal stop; its anvil.yaml sets max_run_tokens 15000000, max_runtime_turns 100, max_packet_tokens 48000; its anvil.json wires the checks command python -m unittest discover -s tests -p 'test_*.py'). The partitions in R1 divide the existing 15000000 pool; they do not raise it.

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

ANVIL's run budget is a single shared pool: anvil.yaml sets one max_run_tokens for the whole run (6000000 when this order was filed, 15000000 since the recalibration of 2026-11-20), and the token-efficiency capability stops later calls once that pool is gone. Nothing partitions the pool, so the first heavy station can starve every station behind it. The C64 blueprint chain measured the cost of that shape: in wo-gh-6 the builder's single call measured 6,359,529 cache-inclusive tokens against the 6,000,000 cap and the run died at the cap; across the five order chain the factory consumed about 24.5M tokens for one showcase page. The same chain showed the second waste this order closes: reviewer spend launched on incomplete attempts (in wo-gh-7 the builder station recorded failed with exit 1 while its artifacts existed, and the run's accounting of what was complete had to be reconstructed by hand). The comparison against other software factories (factory research of 2026-11-15, section "Mechanisms ANVIL Does Not Have", mechanisms 19 to 32) shows the standard controls: mini-SWE-agent checks a per-instance cost limit before each query is paid for; Spotify runs its deterministic verifiers before any review artifact exists, and on failure no pull request is opened at all; ZazenCodes joins on all expected files existing before the approver runs. This order partitions the run cap per station with a check before each dispatch and an in-flight ceiling per dispatch, and makes the reviewer stage conditional on a deterministic completeness check, so expensive judgment is only ever spent on complete work and no single station or call can consume the pool.

## Requirements

### R1. Per-station partitions in configuration
- The project configuration (anvil.yaml, efficiency section) gains two keys: station_budgets, a map from station id to a token cap, and default_station_budget, the cap for a station the map does not name. The checks gate and other deterministic stages make no model call and need no partition.
- Configuration loading validates the partition set against every pipeline the project can run: the sum of the named partitions plus the default applied to each unnamed model station of a pipeline must not exceed max_run_tokens. A set whose worst case exceeds the run cap fails to load, naming the excess. The run cap stays the outer bound, and the token-efficiency run threshold keeps working unchanged.
- The factory's own anvil.yaml ships partitions for sdlc-default that sum to exactly 15000000: intake 200000, spec-writer 600000, test-writer 3200000, builder 6400000, reviewer-spec 600000, reviewer-security 600000, reviewer-tests 600000, reviewer-architecture 600000, reviewer-design 600000, reviewer-ux 600000, approver 200000, triage-human 100000, deployer 300000, observer 400000. Each figure covers the largest consumption measured for that station across the runs of wo-gh-39, wo-gh-43 and wo-gh-41 (test-writer 2764842, one builder call 4524497, one reviewer 438127, spec-writer 273344, observer 189834), with room for the loopback attempts of the builder.

### R2. Pre-call check before every dispatch
- Before the spine dispatches any station invocation (a first attempt, an in-session correction re-dispatch, or a loopback re-dispatch), it reads the station's measured consumption for this run from the per-attempt usage artifacts the token-efficiency capability writes, and refuses the dispatch when the station has exhausted its partition.
- A refused dispatch is recorded as a budget outcome for that station (station, partition, consumed, refused at) in the run report, the run stops forward progress for that round, and no partial dispatch happens: a refusal costs zero model calls.
- Unmeasured consumption is handled honestly, never as zero: when a station's prior dispatch returned unmeasured usage and the project configuration sets require_usage, the station is treated as exhausted until its usage is measured; when require_usage is off, the pre-call check records that it proceeded on unmeasured usage.

### R3. In-flight ceiling per dispatch
- A single dispatch cannot consume the pool either: the station wrapper terminates a station session whose measured usage crosses the station's partition, the same mechanism shape as the station timeout kill, and records the station outcome as budget_exceeded with the partial usage the runtime exposed, using the station-timeout capability's honest record fields (station, elapsed, configured limit as the reason, dispatched model, partial usage when exposed).
- Work left undone by a ceiling kill is not resumed inside that dispatch; the station's outcome stands as recorded and the run proceeds under the normal gate rules.

### R4. Deterministic completeness gate before review
- In a project whose configuration sets efficiency partitions (efficiency.station_budgets or efficiency.default_station_budget), after the builder station and the checks gate, and before any reviewer station is dispatched, the runner evaluates a completeness precondition in deterministic code: (a) every expected artifact for the attempt exists and is non-empty: the builder report (already validated for required literals by the station artifact contract's checks gate step), the test-writer's test files for the attempt, and the run delta file list; (b) the checks gate verdict for the attempt is pass, which includes the deterministic preflight outcome when the staged wo-gh-28 preflight has landed, and is the checks verdict as it exists when it has not; (c) no station the pipeline expects before the reviewer stage is recorded failed without its artifact.
- A failed precondition returns the named gaps to the builder as a gate loopback, consuming a loopback exactly as a checks failure does and bounded by the existing max loopbacks, and dispatches zero reviewer stations.
- The precondition's outcome and named gaps are recorded in the run report in a field set of its own, distinct from the checks result and from any review verdict.
- The precondition consumes existing verdicts and artifacts; it does not re-run the project suite, does not duplicate the artifact contract's literal validation, and does not change the checks gate's own behavior.
- Scope (owner ruling of 2026-11-22): the precondition is active only where efficiency partitions are configured. A project that configures none keeps its present behavior and its attempts reach the reviewer stage as they did before this order. The factory's own anvil.yaml ships partitions, so the factory's own runs are gated. An unconditional precondition would require changing 22 existing protected tests (measured by the builder in run 44912754341: 21 failures and 2 errors with the precondition forced on); that change is left to an order of its own.

### R5. Money framing where the factory supports it
- Where the cost-measurement price table covers a station's executed model, the run report's cost section shows per-station budget consumption in money next to the token figures (partition, consumed, priced amount), labelled as priced from the recorded price table, never as an invoice. A station whose model has no price entry shows tokens only and stays unmeasured in money, exactly as the cost-measurement spec requires.

### R6. Regression tests
- The order's own tests are new files under tests/ and encode: (a) a scripted run whose builder partition is set below its scripted consumption: the in-flight ceiling stops the dispatch at the partition, the outcome is budget_exceeded with partial usage recorded, and the reviewer stations' partitions are untouched in the run record; (b) a station that exhausted its partition on a first attempt is refused re-dispatch by the pre-call check, the refusal is recorded, and the refusal made zero model calls; (c) a configuration whose partitions plus defaults exceed max_run_tokens fails to load naming the excess, and the factory's shipped anvil.yaml partitions load and sum to exactly 15000000; (d) completeness: a builder attempt missing its report artifact, or carrying a failing checks verdict, dispatches zero reviewer stations and returns the named gaps as a loopback, while a complete attempt with a passing checks verdict dispatches the reviewer stage.

### R7. Documentation names both budget keys
- docs/EXECUTION.md describes efficiency.station_budgets, efficiency.default_station_budget, the load time validation against max_run_tokens, the pre-call check, the in-flight ceiling and the completeness precondition, and names the top level station_budgets key (astra-consumption packet size cap) stating that it caps packet tokens while the efficiency keys cap run consumption per station. CHANGELOG.md carries an entry for this order, and one new decision record under brain/decisions/ records the partition decision and what it makes harder.

### R8. Builder report evidence
- The builder report (runs/wo-gh-42/builder.output.md) contains each of these literals in full, unabbreviated: 72a84126a600fafb99446946694b5de809e01e66, station-budgets-completeness, 15000000, completeness. It also states the base ref it verified the tree against, the partition table it shipped with its sum, the exact full factory test count from the suite run, and the names of the new test files added.

### Allowed write set
Only these paths may change; every other path is out of bounds:
- anvil/config.py
- anvil.yaml (the efficiency section's station_budgets and default_station_budget keys and the factory's own partitions only; max_run_tokens, require_usage, the top level station_budgets and every other key unchanged)
- anvil/executor.py, anvil/runner.py, anvil/gates.py, anvil/telemetry.py
- tools/claude_station.py (the in-flight ceiling), tools/dispatch_station.py only if needed
- docs/EXECUTION.md (required), and any other factory doc under docs/ only where it describes budgets or the checks flow (for example docs/CHECKS-GATE.md, docs/COST-MEASUREMENT.md)
- CHANGELOG.md
- one new file under brain/decisions/ (next free number after 0013)
- new test files under tests/ (no existing test file modified or deleted)
- runs/wo-gh-42/ station artifacts the line itself writes
Protected and not edited: pipelines/ (all pipeline files), anvil.json, every existing file under tests/.

### Out of scope
- Raising or changing max_run_tokens, max_runtime_turns or max_packet_tokens.
- Partitions for pipelines other than sdlc-default in the factory's anvil.yaml (they are validated with the default applied, not given named tables).
- Changing the checks gate, its verdicts, loopback accounting or S4 base ref behavior; adding a second suite run.
- Changing the station artifact contract's literal validation, token-efficiency usage artifacts or run threshold, station-timeout keys, cost-measurement semantics, the review parse contract or reviewer prompts.
- Implementing or depending on wo-gh-28 preflight.
- Any merge, publish or deploy.

### Guardrails
- Python standard library only, consistent with the factory spine. No new dependency.
- Frozen surfaces: the checks gate's own verdicts, loopback accounting and S4 base ref behavior; the station artifact contract's validation step and required literals mechanism; the token-efficiency usage artifacts and run threshold; the station-timeout keys and behavior (ANVIL_STATION_TIMEOUT_SECONDS and the timeout records are untouched; token partitions are additive configuration); cost-measurement semantics; pipeline definition files (protected in anvil.json); anvil.json itself (protected).
- Relationship to the staged deterministic preflight order (wo-gh-28): preflight judges whether the changed code is alive (imports, execution, wiring, smoke); completeness judges whether the attempt's expected artifacts exist and the gate passed. Each works whether or not the other has landed, and neither duplicates the other's checks. Execution order between the two orders is the owner's decision.
- Relationship to the station-timeout capability (wo-gh-39): that order partitions wall-clock time per station class; this order partitions tokens per station. They share the wrapper's kill-and-record mechanism shape and neither changes the other's keys.
- Relationship to continuous run accounting (wo-gh-41, landed 2026-11-20): a partition stop is one more exit path. A refused dispatch and an in-flight ceiling kill complete the run record through the mechanism that order added (exit_status budget_exceeded, a termination_reason naming the station and its partition, unrun stations recorded as not_run); this order adds no second way of ending a run. tests/test_continuous_run_accounting.py is an existing test file and is protected.
- Relationship to the existing station_budgets key (astra-consumption): anvil.yaml already accepts a top level station_budgets map, read by anvil.config.get_station_budget, that caps the size of a station's packet. It is a different quantity (packet tokens, not run consumption), it stays where it is, and its behavior and tests (tests/test_astra_consumption.py) are frozen. The keys this order adds live inside the efficiency section; the documentation names both and states the difference.
- Existing test files at the base ref are not modified or deleted; new tests arrive as new files. The full factory suite (python -m unittest discover -s tests -p 'test_*.py') passes at handoff, including tests/test_continuous_run_accounting.py and tests/test_astra_consumption.py unmodified.
- No em dash or en dash character in any produced file (project style rule).
- Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

## Scenarios

### Scenario: One station cannot eat the pool
- S1 (R3, R6a): Given a scripted run whose builder partition is below the builder's scripted consumption, when the builder dispatch runs, then the in-flight ceiling stops it at the partition, the station outcome is budget_exceeded with partial usage recorded, and the run record shows the reviewer stations' partitions untouched (consumed 0); the run ends through the wo-gh-41 exit path with exit_status budget_exceeded, a termination_reason naming builder and its partition, and unrun stations recorded as not_run.

### Scenario: An exhausted station is refused before any model call
- S2 (R2, R6b): Given a station that exhausted its partition on a first attempt, when the spine would dispatch it again (a correction or a loopback), then the pre-call check refuses the dispatch, records the budget outcome with partition and consumed figures, and makes zero model calls for the refusal (the scripted runtime's call count is unchanged across the refusal); the run ends with exit_status budget_exceeded and a termination_reason naming the station and its partition.

### Scenario: Partitions are validated against the run cap at load
- S3 (R1, R6c): Given a configuration (for example max_run_tokens 1000000, station_budgets builder 900000 and reviewer-spec 200000) whose named partitions plus defaults for a pipeline exceed max_run_tokens, when the configuration loads, then loading fails with an error naming the pipeline and the excess (100000 in the example, more when the default applies to unnamed model stations); and given the factory's shipped anvil.yaml, when it loads, then the sdlc-default partitions sum to exactly 15000000 and loading succeeds.

### Scenario: Incomplete work never reaches the reviewers
- S4 (R4, R6d): Given a project with efficiency partitions configured and a builder attempt whose report artifact is missing, or whose checks verdict failed, when the completeness precondition evaluates, then it fails naming the gaps, the gaps return to the builder as a gate loopback, and zero reviewer stations are dispatched for that attempt.

### Scenario: Complete work proceeds to review
- S5 (R4, R6d): Given a project with efficiency partitions configured and a builder attempt with every expected artifact present and a passing checks verdict, when the completeness precondition evaluates, then it passes, its outcome is recorded in its own field set, and the reviewer stage is dispatched as the pipeline defines.

### Scenario: Budget consumption is visible in money where priced
- S6 (R5): Given a run whose stations executed models covered by the price table, when the run report's cost section is read, then each such station shows its partition, its consumed tokens and its priced amount labelled with the table as its source; and given a station whose model has no price entry, then it shows tokens only and is recorded as unmeasured in money.

### Scenario: Unmeasured usage is never counted as zero
- S7 (R2): Given a station whose prior dispatch recorded unmeasured usage and require_usage true, when the spine would dispatch it again, then the pre-call check refuses it as exhausted until measured and records the refusal; given the same state with require_usage false (the factory default at the base ref), then the dispatch proceeds and the budget record for that check states it proceeded on unmeasured usage.

### Scenario: A failed station without its artifact blocks review
- S8 (R4): Given a project with efficiency partitions configured and a pipeline run where the test-writer is recorded failed and its test files for the attempt are absent, or the run delta file list is empty, when the completeness precondition evaluates, then it fails naming each gap (station or artifact path), returns them to the builder as a gate loopback, and dispatches zero reviewer stations; given the loopback count already at max loopbacks, then no further builder loopback is made, as for a checks failure.

### Scenario: Completeness consumes, never re-runs
- S9 (R4): Given any completeness evaluation, when it runs, then the project suite command is invoked zero additional times beyond the checks gate's own run, and the builder report literal validation is performed only by the artifact contract step (verified by a test counting suite invocations and by code review of gates.py).

### Scenario: Documentation and evidence are present
- S10 (R7, R8): Given the built branch, when docs/EXECUTION.md is read, then it names efficiency.station_budgets, efficiency.default_station_budget and the top level station_budgets key and states the difference; CHANGELOG.md has a wo-gh-42 entry; exactly one new file exists under brain/decisions/; and runs/wo-gh-42/builder.output.md contains the four required literals, the verified base ref, the partition table with its sum 15000000, the full suite test count and the new test file names.

### Scenario: Protected surfaces untouched
- S11 (Allowed write set, Guardrails): Given git diff 72a84126a600fafb99446946694b5de809e01e66..HEAD --name-only, then every listed path is in the allowed write set, no path under pipelines/ or anvil.json appears, no existing test file appears as modified or deleted, and grep for the em dash and en dash characters across the changed files finds none.

## Correction of 2026-11-21 (owner decision, before the first run)

The order was filed on 2026-11-15 against a run cap of 6000000 and shipped partitions summing to that figure. On 2026-11-20 the cap was recalibrated to 15000000 (max_runtime_turns to 100) after wo-gh-41 could not be built inside the old limits, and the measured runs showed the filed partitions were too small for a large order: the approved run of wo-gh-41 used 725210 tokens in the test-writer against a filed partition of 600000. This correction replaces the shipped partition table in R1, R6 and S3, pins the order to the current factory main, and records its relationship to wo-gh-41 and to the existing packet budget key. Nothing else in the order changes.
