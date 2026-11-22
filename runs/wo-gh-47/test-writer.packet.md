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

- id: wo-gh-47
- kind: feature
- title: Live progress sinks: a run seen while it runs, on the work order's issue and optionally on a GitHub Projects board
- source: github-issue
- description: Implement the spec in .openspec/specs/live-progress-sinks/spec.md. Pipeline for this order is sdlc-default (software domain, the factory repo itself), selected by the run workflow.

RELEASE (owner decision, 2026-11-22): this order is released for execution. It was filed on 2026-11-21 and staged until wo-gh-42 landed, which it did on 2026-11-22 (merge 6191e8c1f235b4cd248a51203d40177834dc4ae2). Baseline now: factory main 10168fa560af7284b23f99e4e639621cf47eacd2, whose anvil.yaml carries max_run_tokens 15000000, max_runtime_turns 100, max_packet_tokens 48000 and the efficiency station partitions of wo-gh-42, and whose anvil.json wires the checks command (python -m unittest discover -s tests -p 'test_*.py'). First run of this order (45042545362) was stopped in the spec-writer by its token partition, since recalibrated (spec-writer 1200000, builder 5800000); the run branch carries that fix. The exit statuses now on main include runtime_refused; a sink must be able to show any exit status as a final state without knowing the list.

EVIDENCE (the defect this order closes):
A run cannot be watched. state.json is rewritten before every station and report.json is checkpointed after every station (wo-gh-41), but both stay on the disk of the machine that runs the line until the run ends. The five runs of wo-gh-41 on 2026-11-20 and the run of wo-gh-42 on 2026-11-21 each showed only "In progress" for 5 to 27 minutes; the owner asked what the line was doing and nobody could tell from outside. The existing export (observability.events_url and otlp_endpoint) needs a receiver someone must build and host. Owner direction of 2026-11-21: no dependence on one vendor for this, and a person who copies ANVIL must see their runs without standing anything up. Every work order is already a GitHub issue and every run already holds a token that can write to it.

BUILD, per the spec requirements:
R1: anvil.yaml accepts observability.sinks, an ordered and validated list of sink entries. A sink is called with the run state record (schema anvil/run-state@1) every time the recorder rewrites the state: at the start, before each station, after the last one, and when the run ends, crashes or is stopped early. No new event kind; events.jsonl is unchanged. A sink that raises, times out or is refused is recorded in export_errors under its type and the line goes on; each call is bounded by observability.timeout_seconds. No sinks configured means no additional network call. The sink code lives beside the recorder, outside anvil/runner.py.
R2: the github-issue sink, entry {"type": "github-issue"} with optional token_env (default GH_TOKEN). Active only when the work order id is wo-gh-<number>, GITHUB_REPOSITORY is set and the token variable is set; otherwise inactive with the reason recorded once and no network call. It creates one comment on the issue at its first call and edits that same comment on every later call, found again by a hidden marker carrying the run id. The comment shows the work order and pipeline, the run state, the verdict and exit status once known, one row per pipeline station in pipeline order (done, failed, running, pending, skipped, not run) with attempt and measured tokens, loopbacks used, tokens and priced cost so far, the time of the last update and the workflow run link when the environment gives one. Scalar facts only: no prompt, no station output, no path, no token value. The API base comes from GITHUB_API_URL when set.
R3: the github-project sink, entry {"type": "github-project", "owner": ..., "number": ...} with optional owner_type, status_field (default Status), token_env and columns. Phases and default option names: intake (Intake), spec (Spec), build (Build: test-writer and builder), checks (Checks), review (Review: reviewers and approver), human (Needs human), done (Done), failed (Failed). It sets the status of the issue's project item when the phase changes, adds the issue to the project when missing, and never alters the project's shape: a missing project, field or option is recorded by name and the sink goes inactive for the run. The workflow token cannot reach Projects; token_env names a variable holding one that can, and with it unset the sink is inactive and says so once.
R4: the factory's own anvil.yaml enables the github-issue sink; the scaffold for new projects enables it too; the github-project sink ships documented and off. The final ANVIL line report comment of the workflow is unchanged.
R5: sinks run in the line process and read their token there. Stations never receive it. No token value appears in state.json, events.jsonl, report.json, a comment or an export error.
R6: regression tests as new files under tests/, with a local HTTP collector in the manner of tests/test_governed_delivery.py: (a) one comment creation then only edits, the last showing every station done and the verdict; (b) the edit sent before the builder shows the builder running and later stations pending; (c) a collector answering 500 and an unreachable one leave verdict and report unchanged with one export error; (d) a non wo-gh id or a missing token gives zero network calls and one recorded reason; (e) the project sink sends a status change only when the phase changes, adds a missing item, and goes inactive naming a missing option; (f) no sink configured gives zero additional network calls; (g) a malformed sinks list fails loading naming the entry; (h) a token value in the environment appears in no file the run writes and in no request body.

RECONCILIATION WITH ACTIVE SPECS AND EXISTING TESTS (read before building; these are decisions, not discoveries for the line to make):
Governed delivery owns state.json, events.jsonl, the webhook and the OTLP trace; all four are frozen and this order only adds consumers of the state record. tests/test_governed_delivery.py asserts that the events POSTed to the webhook equal the events in events.jsonl and counts station.finished and loopback events against the report's steps: sinks must not add, remove or reorder events, which is why they are fed by the state and not by a new event. tests/test_review_producer.py asserts that the word "retry" does not occur in anvil/runner.py: keep network code and that word out of the runner. tests/test_continuous_run_accounting.py (wo-gh-41) asserts the report's shape after every exit path: a sink call on an exit path must not change what is written. wo-gh-42 (station partitions) may land before this order; its efficiency keys and this order's observability keys do not overlap. The runtime refusal stop (exit_status runtime_refused) is one more final state a sink must be able to show.

BUILDER REPORT: the builder report must contain each of these in full: 10168fa560af7284b23f99e4e639621cf47eacd2, live-progress-sinks, github-issue, github-project. It must also state the base ref it verified the tree against, the exact full factory test count from the suite run, and the names of the new test files added.

GUARDRAILS: authorized surface for this order: anvil/observe.py, a new module beside it for the sinks, anvil/config.py (validation of observability.sinks), anvil/scaffold.py (the default for new projects), anvil.yaml (the factory's own sink entry), docs/OPERATIONS.md, docs/EXECUTION.md, README.md (one short section on watching a run), CHANGELOG.md, one new decision record under brain/decisions/, and new test files under tests/. anvil/runner.py may change only where the recorder is constructed or told the pipeline order, and gains no network code. Do not touch any file under .github/workflows: the run's own token cannot push workflow changes and none are needed, because the line step already carries GH_TOKEN. Pipeline files under pipelines/ and anvil.json are protected paths. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. A test that asserts something about this order's own run (which paths it changed, what its builder report says, a comparison against a fixed base ref) must skip unless ANVIL_WORK_ORDER_ID names this order: left unconditional, such a test fails for every order after this one, as the tree evidence of wo-gh-42 did. Frozen: the events contract, the OTLP trace, the existing fields of the run-state schema, the rule that export never decides a run, the station environment reduction, tools/line_comment.py. Python standard library only, no new dependency. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/47
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed

## Run context

Read the upstream work before you start; it is the input your station builds on.
The checks gate runs the project checks listed here; run them yourself before you hand off.

- Output of intake: runs/wo-gh-47/intake.output.md
- Output of spec-writer: runs/wo-gh-47/spec-writer.output.md
- Project check: `python -m unittest discover -s tests -p 'test_*.py'`
