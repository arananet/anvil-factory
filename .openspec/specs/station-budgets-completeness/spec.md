# Per-Station Token Budgets and a Completeness Gate Before Review

Status: proposed
Slug: station-budgets-completeness

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

ANVIL's run budget is a single shared pool: anvil.yaml sets max_run_tokens to 6000000 for the whole run, and the token-efficiency capability stops later calls once that pool is gone. Nothing partitions the pool, so the first heavy station can starve every station behind it. The C64 blueprint chain measured the cost of that shape: in wo-gh-6 the builder's single call measured 6,359,529 cache-inclusive tokens against the 6,000,000 cap and the run died at the cap; across the five order chain the factory consumed about 24.5M tokens for one showcase page. The same chain showed the second waste this order closes: reviewer spend launched on incomplete attempts (in wo-gh-7 the builder station recorded failed with exit 1 while its artifacts existed, and the run's accounting of what was complete had to be reconstructed by hand). The comparison against other software factories (factory research of 2026-11-15, section "Mechanisms ANVIL Does Not Have", mechanisms 19 to 32) shows the standard controls: mini-SWE-agent checks a per-instance cost limit before each query is paid for; Spotify runs its deterministic verifiers before any review artifact exists, and on failure no pull request is opened at all; ZazenCodes joins on all expected files existing before the approver runs. This order partitions the run cap per station with a check before each dispatch and an in-flight ceiling per dispatch, and makes the reviewer stage conditional on a deterministic completeness check, so expensive judgment is only ever spent on complete work and no single station or call can consume the pool.

## Requirements

### R1. Per-station partitions in configuration
- The project configuration (anvil.yaml, efficiency section) gains two keys: station_budgets, a map from station id to a token cap, and default_station_budget, the cap for a station the map does not name. The checks gate and other deterministic stages make no model call and need no partition.
- Configuration loading validates the partition set against every pipeline the project can run: the sum of the named partitions plus the default applied to each unnamed model station of a pipeline must not exceed max_run_tokens. A set whose worst case exceeds the run cap fails to load, naming the excess. The run cap stays the outer bound, and the token-efficiency run threshold keeps working unchanged.
- The factory's own anvil.yaml ships partitions for sdlc-default that sum to exactly 6000000: intake 200000, spec-writer 400000, test-writer 600000, builder 2400000, reviewer-spec 300000, reviewer-security 300000, reviewer-tests 300000, reviewer-architecture 300000, reviewer-design 300000, reviewer-ux 300000, approver 200000, triage-human 100000, deployer 150000, observer 150000.

### R2. Pre-call check before every dispatch
- Before the spine dispatches any station invocation (a first attempt, an in-session correction re-dispatch, or a loopback re-dispatch), it reads the station's measured consumption for this run from the per-attempt usage artifacts the token-efficiency capability writes, and refuses the dispatch when the station has exhausted its partition.
- A refused dispatch is recorded as a budget outcome for that station (station, partition, consumed, refused at) in the run report, the run stops forward progress for that round, and no partial dispatch happens: a refusal costs zero model calls.
- Unmeasured consumption is handled honestly, never as zero: when a station's prior dispatch returned unmeasured usage and the project configuration sets require_usage, the station is treated as exhausted until its usage is measured; when require_usage is off, the pre-call check records that it proceeded on unmeasured usage.

### R3. In-flight ceiling per dispatch
- A single dispatch cannot consume the pool either: the station wrapper terminates a station session whose measured usage crosses the station's partition, the same mechanism shape as the station timeout kill, and records the station outcome as budget_exceeded with the partial usage the runtime exposed, using the station-timeout capability's honest record fields (station, elapsed, configured limit as the reason, dispatched model, partial usage when exposed).
- Work left undone by a ceiling kill is not resumed inside that dispatch; the station's outcome stands as recorded and the run proceeds under the normal gate rules.

### R4. Deterministic completeness gate before review
- After the builder station and the checks gate, and before any reviewer station is dispatched, the runner evaluates a completeness precondition in deterministic code: (a) every expected artifact for the attempt exists and is non-empty: the builder report (already validated for required literals by the station artifact contract's checks gate step), the test-writer's test files for the attempt, and the run delta file list; (b) the checks gate verdict for the attempt is pass, which includes the deterministic preflight outcome when the staged wo-gh-28 preflight has landed, and is the checks verdict as it exists when it has not; (c) no station the pipeline expects before the reviewer stage is recorded failed without its artifact.
- A failed precondition returns the named gaps to the builder as a gate loopback, consuming a loopback exactly as a checks failure does and bounded by the existing max loopbacks, and dispatches zero reviewer stations.
- The precondition's outcome and named gaps are recorded in the run report in a field set of its own, distinct from the checks result and from any review verdict.
- The precondition consumes existing verdicts and artifacts; it does not re-run the project suite, does not duplicate the artifact contract's literal validation, and does not change the checks gate's own behavior.

### R5. Money framing where the factory supports it
- Where the cost-measurement price table covers a station's executed model, the run report's cost section shows per-station budget consumption in money next to the token figures (partition, consumed, priced amount), labelled as priced from the recorded price table, never as an invoice. A station whose model has no price entry shows tokens only and stays unmeasured in money, exactly as the cost-measurement spec requires.

### R6. Regression tests
- The order's own tests are new files under tests/ and encode: (a) a scripted run whose builder partition is set below its scripted consumption: the in-flight ceiling stops the dispatch at the partition, the outcome is budget_exceeded with partial usage recorded, and the reviewer stations' partitions are untouched in the run record; (b) a station that exhausted its partition on a first attempt is refused re-dispatch by the pre-call check, the refusal is recorded, and the refusal made zero model calls; (c) a configuration whose partitions plus defaults exceed max_run_tokens fails to load naming the excess, and the factory's shipped anvil.yaml partitions load and sum to exactly 6000000; (d) completeness: a builder attempt missing its report artifact, or carrying a failing checks verdict, dispatches zero reviewer stations and returns the named gaps as a loopback, while a complete attempt with a passing checks verdict dispatches the reviewer stage.

### Guardrails
- Python standard library only, consistent with the factory spine. No new dependency.
- Frozen surfaces: the checks gate's own verdicts, loopback accounting and S4 base ref behavior; the station artifact contract's validation step and required literals mechanism; the token-efficiency usage artifacts and run threshold; the station-timeout keys and behavior (ANVIL_STATION_TIMEOUT_SECONDS and the timeout records are untouched; token partitions are additive configuration); cost-measurement semantics; pipeline definition files (protected in anvil.json); anvil.json itself (protected).
- Relationship to the staged deterministic preflight order (wo-gh-28): preflight judges whether the changed code is alive (imports, execution, wiring, smoke); completeness judges whether the attempt's expected artifacts exist and the gate passed. Each works whether or not the other has landed, and neither duplicates the other's checks. Execution order between the two orders is the owner's decision.
- Relationship to the station-timeout capability (wo-gh-39): that order partitions wall-clock time per station class; this order partitions tokens per station. They share the wrapper's kill-and-record mechanism shape and neither changes the other's keys.
- Existing test files at the base ref are not modified or deleted; new tests arrive as new files.
- No em dash or en dash character in any produced file (project style rule).
- Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

## Scenarios

### Scenario: One station cannot eat the pool
- S1: Given a scripted run whose builder partition is below the builder's scripted consumption, when the builder dispatch runs, then the in-flight ceiling stops it at the partition, the station outcome is budget_exceeded with partial usage recorded, and the run record shows the reviewer stations' partitions untouched.

### Scenario: An exhausted station is refused before any model call
- S2: Given a station that exhausted its partition on a first attempt, when the spine would dispatch it again (a correction or a loopback), then the pre-call check refuses the dispatch, records the budget outcome with partition and consumed figures, and makes zero model calls for the refusal.

### Scenario: Partitions are validated against the run cap at load
- S3: Given a configuration whose named partitions plus defaults for a pipeline exceed max_run_tokens, when the configuration loads, then loading fails naming the excess; and given the factory's shipped anvil.yaml, when it loads, then the sdlc-default partitions sum to exactly 6000000 and loading succeeds.

### Scenario: Incomplete work never reaches the reviewers
- S4: Given a builder attempt whose report artifact is missing, or whose checks verdict failed, when the completeness precondition evaluates, then it fails naming the gaps, the gaps return to the builder as a gate loopback, and zero reviewer stations are dispatched for that attempt.

### Scenario: Complete work proceeds to review
- S5: Given a builder attempt with every expected artifact present and a passing checks verdict, when the completeness precondition evaluates, then it passes, its outcome is recorded in its own field set, and the reviewer stage is dispatched as the pipeline defines.

### Scenario: Budget consumption is visible in money where priced
- S6: Given a run whose stations executed models covered by the price table, when the run report's cost section is read, then each such station shows its partition, its consumed tokens and its priced amount labelled with the table as its source; and given a station whose model has no price entry, then it shows tokens only and is recorded as unmeasured in money.
