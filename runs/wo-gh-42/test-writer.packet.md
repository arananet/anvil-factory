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

- id: wo-gh-42
- kind: feature
- title: Per-station token budgets with pre-call checks, and a deterministic completeness gate before the reviewer stage
- source: github-issue
- description: Implement the spec in .openspec/specs/station-budgets-completeness/spec.md. Pipeline for this order is sdlc-default (software domain, the factory repo itself), selected by the run workflow.

RELEASE (owner decision, 2026-11-21): this order is released for execution with the correction below. It was filed and staged on 2026-11-15 against a run cap of 6000000. Run configuration baseline now: the order is parented on factory main 72a84126a600fafb99446946694b5de809e01e66 (which carries wo-gh-41 continuous run accounting, the factory CI fix and the runtime refusal stop), whose anvil.yaml carries max_run_tokens 15000000, max_runtime_turns 100 and max_packet_tokens 48000, and whose anvil.json wires the checks command (python -m unittest discover -s tests -p 'test_*.py'). This order's partitions divide that existing 15000000 pool; they do not raise it.

CORRECTION OF 2026-11-21: the shipped partition table is replaced. The filed table summed to 6000000 and was too small for a large order: the approved run of wo-gh-41 used 725210 tokens in the test-writer against a filed partition of 600000. The new table sums to 15000000 and covers the largest consumption measured per station across the runs of wo-gh-39, wo-gh-43 and wo-gh-41. The spec carries the same correction.

OWNER RULING OF 2026-11-22 (after run 44912754341, verdict changes_requested on one finding): the completeness precondition of R4 applies only in a project whose configuration sets efficiency partitions (efficiency.station_budgets or efficiency.default_station_budget). That is the scope the build of that run implements, and it is the intended one: an unconditional precondition fails 22 existing protected tests (21 failures and 2 errors, measured by the builder). A project that configures no partitions keeps its present behavior. The factory's own anvil.yaml ships partitions, so the factory's own runs are gated. The spec on the run branch carries this ruling in R4 and in scenarios S4, S5 and S8 (commit eb22a19648b44a45f4fa464ab775f9ac2115806b). No code change is asked for by this ruling; an unconditional precondition is left to an order of its own.

EVIDENCE (the defects this order closes):
The C64 blueprint chain (project c64-retro-hardware) consumed about 24.5M tokens across five work orders for one showcase page. In wo-gh-6 (run 43668712644) the builder's single call measured 6,359,529 cache-inclusive tokens against the 6,000,000 run cap: one station ate the whole pool and the run died at the cap, because ANVIL's budget is one shared pool with a between-calls run threshold (token-efficiency) and no per-station partition. The same chain wasted review spend on incomplete attempts: in wo-gh-7 (run 43673692204) the builder station recorded failed with exit 1 while its artifacts existed, and what was complete had to be reconstructed by hand before anyone could judge the attempt. The comparison against other software factories (factory research of 2026-11-15, report section "Mechanisms ANVIL Does Not Have", mechanisms 19 to 25 for failure mode 4 and 26 to 32 for failure mode 5) shows the standard controls: mini-SWE-agent checks a per-instance cost limit before each query is paid for; Spotify runs deterministic verifiers before any review artifact exists, and on failure no pull request is opened; ZazenCodes joins on all expected files existing before the approver runs.

BUILD, per the spec requirements:
R1: anvil.yaml's efficiency section gains station_budgets (a map from station id to a token cap) and default_station_budget. Configuration loading validates the worst case per pipeline (named partitions plus the default applied to unnamed model stations) against max_run_tokens and fails naming any excess. The factory's own anvil.yaml ships sdlc-default partitions summing to exactly 15000000: intake 200000, spec-writer 600000, test-writer 3200000, builder 6400000, reviewer-spec 600000, reviewer-security 600000, reviewer-tests 600000, reviewer-architecture 600000, reviewer-design 600000, reviewer-ux 600000, approver 200000, triage-human 100000, deployer 300000, observer 400000. Deterministic stages (the checks gate) take no partition.
R2: before every station dispatch the spine makes (first attempt, correction re-dispatch, loopback re-dispatch), it reads the station's measured consumption for this run from the token-efficiency per-attempt usage artifacts and refuses the dispatch when the partition is exhausted. A refusal is recorded as a budget outcome (station, partition, consumed, refused at), stops forward progress for the round, and costs zero model calls. Unmeasured usage is never treated as zero: with require_usage set, an unmeasured station counts as exhausted until measured; without it, the check records that it proceeded on unmeasured usage.
R3: the station wrapper terminates a session whose measured usage crosses its partition, the station-timeout kill mechanism's shape, and records the outcome as budget_exceeded with the partial usage exposed, using wo-gh-39's honest record fields. Undone work is not resumed inside that dispatch.
R4: in a project whose configuration sets efficiency partitions, after the builder and the checks gate, before any reviewer dispatch, the runner evaluates a deterministic completeness precondition: (a) every expected artifact for the attempt exists and is non-empty (the builder report, already literal-validated by the station artifact contract's gate step; the test-writer's test files for the attempt; the run delta file list); (b) the checks gate verdict for the attempt is pass (including the deterministic preflight outcome when staged wo-gh-28 has landed; the checks verdict as it exists when it has not); (c) no pre-review station the pipeline expects is recorded failed without its artifact. A failed precondition returns the named gaps to the builder as a gate loopback (bounded by the existing max loopbacks) and dispatches zero reviewers. The outcome and gaps land in the run report in a field set of their own. The precondition consumes existing verdicts and artifacts; it does not re-run the suite and does not duplicate the artifact contract's literal validation.
R5: where the cost-measurement price table covers a station's executed model, the report's cost section shows per-station consumption in money next to the tokens (partition, consumed, priced amount), labelled as priced from the recorded table, never as an invoice; unpriced stations show tokens only and stay unmeasured in money.
R6: regression tests as new files under tests/: (a) a scripted builder partition below scripted consumption ends in the in-flight ceiling, a budget_exceeded outcome with partial usage, and untouched reviewer partitions; (b) an exhausted station is refused re-dispatch with zero model calls and the refusal recorded; (c) an over-cap configuration fails to load naming the excess, and the factory anvil.yaml loads with partitions summing to exactly 15000000; (d) a missing builder report or a failing checks verdict dispatches zero reviewers and returns the named gaps as a loopback, while a complete attempt with a passing verdict dispatches the reviewer stage.

RECONCILIATION WITH ACTIVE SPECS (read before building; these are decisions, not discoveries for the line to make):
The checks gate (spec checks-gate) already returns failing work to the builder with no reviewer spawned; R4 does not modify the gate, its verdicts, its loopback accounting or its S4 base ref behavior, and adds no second suite run: completeness is a runner-level launch precondition that consumes the gate's verdict. The station artifact contract's builder report validation is the base mechanism for R4(a), extended to the attempt's full expected artifact inventory, not duplicated. Token-efficiency R4's run threshold stays as the outer bound; R1 to R3 partition the pool inside it. Station-timeout (wo-gh-39) partitions wall-clock time; this order partitions tokens, sharing the kill-and-record mechanism shape and changing none of its keys. Continuous run accounting (wo-gh-41) landed on 2026-11-20: a refused dispatch and an in-flight ceiling kill end the run through the exit path that order added (exit_status budget_exceeded, a termination_reason naming the station and its partition, unrun stations recorded as not_run); this order adds no second way of ending a run, and tests/test_continuous_run_accounting.py is a protected existing test. The existing top level station_budgets key of anvil.yaml (astra-consumption, read by anvil.config.get_station_budget) caps a station's packet size; it is a different quantity, it stays where it is, and its behavior and tests (tests/test_astra_consumption.py) are frozen. The keys this order adds live inside the efficiency section, and the documentation names both and states the difference. Relationship to staged wo-gh-28 (deterministic preflight): preflight judges whether the changed code is alive; completeness judges whether the attempt's artifacts exist and the gate passed. Each works whether or not the other has landed, neither duplicates the other's checks, and execution order between the two orders is the owner's decision.

BUILDER REPORT REQUIRED LITERALS: the builder report (runs/wo-gh-42/builder.output.md) must contain each of these in full, unabbreviated: 72a84126a600fafb99446946694b5de809e01e66, station-budgets-completeness, 15000000, completeness. It must also state the base ref it verified the tree against, the partition table it shipped with its sum, the exact full factory test count from the suite run, and the names of the new test files added.

GUARDRAILS: authorized surface for this order: anvil/config.py, anvil.yaml (the efficiency keys and the factory's own partitions only), anvil/executor.py, anvil/runner.py, anvil/gates.py, anvil/telemetry.py, tools/claude_station.py (the in-flight ceiling), tools/dispatch_station.py if needed, the factory docs that describe budgets or the checks flow (docs/EXECUTION.md at minimum), CHANGELOG.md, one new decision record under brain/decisions/, and new test files under tests/. Pipeline files under pipelines/ are protected paths in anvil.json; the fix must hold without editing them. anvil.json itself is protected; do not edit it. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. Frozen: the checks gate's verdicts and S4 behavior, the artifact contract's literal validation, token-efficiency's usage artifacts, the station-timeout keys, cost-measurement semantics, the review parse contract, the reviewer prompts. Python standard library only, no new dependency. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/42


GitHub issue: https://github.com/arananet/anvil-factory/issues/42
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed

## Run context

Read the upstream work before you start; it is the input your station builds on.
The checks gate runs the project checks listed here; run them yourself before you hand off.

- Output of intake: runs/wo-gh-42/intake.output.md
- Output of spec-writer: runs/wo-gh-42/spec-writer.output.md
- Project check: `python -m unittest discover -s tests -p 'test_*.py'`
