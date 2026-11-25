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
- A test that asserts a fact about this order's own run (the tree compared with a base ref, files this order must not touch, lines this order adds) skips unless the environment variable ANVIL_WORK_ORDER_ID names this order. Left unconditional, it fails every later order at the checks gate. The suite enforces this (tests/test_run_evidence_scoping.py).
- No test compares wall clock figures (durations, timestamps) between two runs for equality.
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

- id: wo-gh-50
- kind: feature
- title: Proven patterns: a new project starts from what already worked (structure, dead ends and measured cost harvested from finished projects)
- source: github-issue
- description: Implement the spec in .openspec/specs/proven-patterns/spec.md. Pipeline for this order is sdlc-default (software domain, the factory repo itself), selected by the run workflow.

RELEASE OF 2026-11-25: this order is released by the owner. wo-gh-47 and wo-gh-49 are merged. Base ref: factory main 13244db35475b9a19dbd041bc69cf6487d806a45. Since this order was filed the factory gained: live progress sinks (decision 0015), three deterministic stops (decision 0016), budget tokens with efficiency.cache_read_weight (decision 0017, the station partitions in anvil.yaml are budget tokens), the run evidence check tests/test_run_evidence_scoping.py (decision 0018) and selective re-review (decision 0019). A calibration.json of a pattern states for each token figure whether it is raw tokens or budget tokens and at which cache_read_weight.

EVIDENCE (the defect this order closes):
The factory remembers inside a project (brain learnings and practices) and forgets between projects. The case: Retro Explainers, a channel of short explainer videos that began as a draft from this factory and was developed in its own repository between 2026-11-15 and 2026-11-22 (handover note of 2026-11-22, operator copy). In one week it settled a gated stage order (script, proof, master, pack), deterministic checks that run before any reviewer, an independent reviewer limited to one automatic revision, a needs-owner stop, cost measured per stage, a board that tracks every episode, and five visual routes that were each built, rejected and are now banned and checked by a tool. Four episodes are published. None of it has come back to the factory: the next project of that kind would pay again to explore the rejected routes, and the factory is only now filing orders for a board (wo-gh-47) and for stopping futile loops (wo-gh-49) that the child project already has. Owner direction of 2026-11-22: the factory must learn from projects that succeeded instead of exploring again and consuming tokens again.

BUILD, per the spec requirements:
R1: a pattern pack at patterns/<id>/: pattern.json (id, title, version, product types served, blueprint it builds on, source project and commits, success evidence), structure.md (stages, gates, layout), dead-ends.json (each route tried and rejected, why, and the evidence), calibration.json (measured cost and tokens per stage, each figure with its source), optional guardrails/ and a list of curated skills relied on. Loading validates it; a dead end without evidence or a figure without its source fails loading. A pack carries process, guardrails, dead ends and measurements and never a project's content or identity: no media, brand asset, design token file, copy or credential; the validator enforces that.
R2: anvil harvest <project-path> --as <pattern-id> reads a finished project on disk and writes a proposal to patterns/inbox/<pattern-id>/: the files named in a harvest manifest, copied with source path, commit and sha256, plus a skeleton of the pack with every field that needs judgment marked open. Deterministic, no model call. A proposal in the inbox is never selected, injected or used by scaffolding. The provenance record states whether the line produced the source work or it was authored outside the line (decision 0006).
R3: anvil promote-pattern <pattern-id> --by <name> promotes only when no field is open, every copied file still matches its hash, the success evidence names at least one verifiable outcome and the content rule holds; otherwise it refuses naming what is missing. anvil check-patterns validates every promoted pack. A new version is a new harvest and promotion; the previous version stays on record.
R4: selection at intake is deterministic by the project's declared product type (brain/project.md, "Product type:"); with more than one candidate the highest version of the most specific match wins and the rule is recorded. The run report records the pattern id and version, or that none matched. No match means nothing is injected.
R5: spec-writer and builder packets gain a Proven pattern section with structure and dead ends; reviewer packets gain the dead ends as statements to check; intake gains the pattern title and version. Packet budgets apply and trims are recorded. A dead end naming a guardrail check is enforced by it; one that does not is prompt text and the pack says so. anvil init --pattern <id> creates a project with the pattern's structure, its checks wired in, and its calibration as starting efficiency partitions when the factory supports them.
R6: the project's own brain, practices and specs win over a pattern on any conflict; a deviation from a pattern alone is not a finding.
R7: regression tests as new files under tests/ with fixture projects and packs, covering each of the above (see the spec for the nine cases).

RECONCILIATION WITH ACTIVE SPECS AND EXISTING TESTS (read before building; these are decisions, not discoveries for the line to make):
The memory gate and the practices door are the model for quarantine, provenance and promotion and are not changed. The design knowledge loader already does deterministic slice matching by product type; patterns follow the same discipline with their own loader. A blueprint names a stack, a pattern names a proven project shape and may build on a blueprint; existing blueprints are untouched. The blueprint guardrails draft defines the check pack format a pattern may carry; each works without the other. The scaffold and onboarding tests (tests/test_greenfield.py, tests/test_onboard.py) fix what a new project contains: the default init must be unchanged and --pattern is additive. tests/test_review_producer.py asserts the word "retry" does not occur in anvil/runner.py. tests/test_governed_delivery.py asserts the event sequence. tests/test_astra_consumption.py fixes packet trimming order. If an existing protected test contradicts a requirement of this order, the builder says so in its report on the first attempt and stops.

SCOPE: this order ships the mechanism and no promoted pattern. The first harvest, from Retro Explainers, is done by the operator with the tool once it exists, and its promotion is the owner's.

BUILDER REPORT: the builder report must contain each of these in full: proven-patterns, promote-pattern, dead-ends.json, calibration.json. It must also state the base ref it verified the tree against, the exact full factory test count from the suite run, and the names of the new test files added.

GUARDRAILS: authorized surface for this order: a new module anvil/patterns.py, anvil/cli.py (harvest, promote-pattern, check-patterns, the --pattern option of init), anvil/scaffold.py, anvil/runner.py only where packets are assembled and the selection is recorded, anvil/config.py if needed, a new top level patterns/ directory with its README and an empty inbox, docs/PATTERNS.md and a short section in docs/ARCHITECTURE.md, CHANGELOG.md, one new decision record under brain/decisions/, and new test files under tests/. Do not touch files under .github/workflows. Pipeline files under pipelines/ and anvil.json are protected paths. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. Python standard library only, no new dependency and no database. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/50
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed

## Run context

Read the upstream work before you start; it is the input your station builds on.
The checks gate runs the project checks listed here; run them yourself before you hand off.

- Output of intake: runs/wo-gh-50/intake.output.md
- Output of spec-writer: runs/wo-gh-50/spec-writer.output.md
- Project check: `python -m unittest discover -s tests -p 'test_*.py'`
