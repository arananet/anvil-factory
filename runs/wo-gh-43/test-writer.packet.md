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

- id: wo-gh-43
- kind: feature
- title: ANVIL attribution by default: every shipped web project credits the factory
- source: github-issue
- description: Implement the spec in .openspec/specs/attribution-default/spec.md. Pipeline for this order is sdlc-default (see anvil.json). Mode: brownfield, the factory improving itself. Domain: factory core, station guidance and project scaffolding.

OWNER RULE (stated 2026-11-15): every project the factory ships carries an ANVIL attribution by default. The owner audited the shipped projects and found the rule is not true today: Sentia carries a bespoke credit, and Doom Fire, Mochi Smash, Platform25 and the live C64 page carry none. This order makes the factory itself produce the attribution by default, so future projects ship compliant without a retrofit. Retrofits of already shipped projects are separate orders (the Doom Fire retrofit is filed in its own repo); this order changes only the factory.

DEFAULT WORDING AND COMPLIANCE:
- Default attribution text, exact: "Made with ANVIL, an open source software factory." with a link to the ANVIL landing https://anvil-landing-7x1.pages.dev (the factory repo link is an accepted alternative target).
- A project bespoke credit that names ANVIL as the builder counts as compliant. Precedent, Sentia: "Sentia is a concept product, designed and built end to end by ANVIL, an open source software factory. Developed by Eduardo Arana."
- Placement: the page footer or an equivalent visible spot. On a game surface, a credits or footer element that does not break gameplay.
- No em dashes in any text this order writes.

BUILD, per the spec requirements:
- R1, the rule and its wording, as above, recorded in the spec and in the decision record of R5.
- R2, scaffold and onboard: anvil/scaffold.py new_project seeds the attribution requirement for web blueprints (blueprints/static-site.json, and blueprints/cloudflare-worker.json where it ships pages), so the seeded site-shell spec and project brain carry the footer requirement from the first build. anvil/onboard.py records the same requirement for onboarded web projects in its onboard output, without overwriting any existing project file (onboard never overwrites).
- R3, station guidance: stations/builder/PROMPT.md and stations/publisher/PROMPT.md carry the rule, the default wording, the placement guidance and the exception path (an owner approved exception recorded in the project spec).
- R4, deterministic check: the checks gate (anvil/gates.py, checks_gate) verifies, for a shipped web deliverable, that the deliverable HTML carries an attribution naming ANVIL: the default line, or a bespoke credit naming ANVIL as the builder. The gate fails when no attribution is present. Web deliverables only: orders and projects without an HTML deliverable are unaffected. A recorded owner exception in the project spec or project configuration is honoured.
- R5, decision record: brain/decisions/0012-anvil-attribution-default.md captures the rule as a long term factory decision, in the format of the existing records.
- R6, tests: tests cover the check passing on the default line, passing on a bespoke Sentia style credit, failing when no attribution exists, and not applying to a non web deliverable. The full factory suite stays green: python -m unittest discover -s tests -p 'test_*.py'.

AUTHORISED SURFACE (full legitimate surface for this spec): anvil/scaffold.py, anvil/onboard.py, anvil/gates.py, a new anvil/ module for the check if the line prefers one, blueprints/static-site.json, blueprints/cloudflare-worker.json, stations/builder/PROMPT.md, stations/publisher/PROMPT.md, brain/decisions/0012-anvil-attribution-default.md, .openspec/specs/attribution-default/spec.md, and tests/ for the new attribution tests only (per spec exception to the anvil.json protected_paths entry for tests/: the new tests are written by the test-writer station; the builder does not edit existing tests). No other protected path changes: anvil.json and pipelines/ stay untouched.

TOKEN CAP: 6,000,000, the factory standing proven configuration in anvil.yaml (max_run_tokens 6000000, max_agent_calls 32, max_runtime_turns 40), left unchanged. Calibration basis: the comparable factory feature order wo-gh-39 (configurable station timeout, code plus tests) measured 1,504,285 tokens total and was approved; this order touches more files but the same order of magnitude, and the standing cap leaves headroom above the largest single station of every comparable factory run.

REQUIRED LITERALS in the builder report: "Made with ANVIL, an open source software factory.", "0012", ".openspec/specs/attribution-default/spec.md", "S1", "S2", "S3", "S4", "S5", and the full suite result line.

The run stops at the human gate. Nothing merges without the owner gate word reported back through the operator.

- risk_hints: checks gate changes can false-fail other projects runs; the spec confines the check to web deliverables, accepts bespoke ANVIL credits, and honours a recorded owner exception
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed

## Run context

Read the upstream work before you start; it is the input your station builds on.
The checks gate runs the project checks listed here; run them yourself before you hand off.

- Spec for this order: .openspec/specs/attribution-default/spec.md
- Output of intake: runs/wo-gh-43/intake.output.md
- Output of spec-writer: runs/wo-gh-43/spec-writer.output.md
- Project check: `python -m unittest discover -s tests -p 'test_*.py'`
