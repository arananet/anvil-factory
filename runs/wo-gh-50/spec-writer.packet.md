# Task packet: spec-writer

## Station prompt

# Spec Writer

## Role
Write or revise an OpenSpec spec from a work order.

## Inputs
- work order
- brain

## Outputs
- spec

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the spec scoped to the work order. Do not add requirements the order did not ask for.

## Definition of done
- The spec is written to the spec file for this order (the path the work order or the run context names, otherwise under .openspec/specs/). A spec described only in your reply does not exist.
- Every requirement has an id and at least one scenario that names it. Every scenario is a concrete example a test or named evidence can check.
- No soft words stand in for a bar. Anything a person will see or use carries its acceptance criteria: the reference or direction, the sizes, the states, the floor.
- Out of scope and the allowed write set are stated.
- When your packet carries a Craft skills section, hold the spec to it.

## Before you hand off
Re-read the work order line by line against the spec and confirm nothing in the order is missing from it. In your reply, list the requirement and scenario ids you wrote or changed, and anything the order left open that the owner must decide.

## Consumption discipline

Read the spec and the relevant upstream artifacts first. Search before opening files; read only the relevant ranges. Bound command output and summarize long test logs with failures and a path to the full log. Run focused checks while editing and the required project checks at handoff. Reuse valid upstream work. Keep the final handoff concise, with changed files, evidence and unresolved issues. Preserve the required output contract.


## Practices

Promoted practices that resolved for this station. Follow each rule.

- P-15 (Filing completeness for protected surfaces): When an order's substance touches protected paths, packet contents or existing tests, the filing must enumerate the complete authorized write set up front: protected_paths changes, named test adaptations and packet inclusions; an under-authorized filing is returned before the run fires.

## Craft skills

Curated craft guidance resolved for this station and this work order. Order of authority: the work order and its spec, then the project design system and decisions, then promoted practices, then these skills. Where a skill conflicts with any of those, the skill yields. Apply what fits the work in front of you; a skill is a bar to meet, not a checklist to recite.

### Skill: architecture-fundamentals

Good architecture is the cheapest structure that makes the next change easy. Judge every structural choice by what it costs the next person who has to read or change it.

**Start from what exists**
- Read the project brain (brain/project.md, brain/decisions/) and the neighbouring code before you propose anything. Follow the existing structure and naming unless you can name the concrete problem that breaking it solves.
- A decision record that is already accepted is a constraint. If the work needs to break one, say so and record a new decision; do not quietly work around it.

**Boundaries**
- Give each module one reason to exist and a small interface that hides how it works. A module is deep when a lot of behaviour sits behind few entry points.
- Dependencies point one way: domain logic knows nothing about delivery (HTTP, CLI, UI) or storage; the edges depend on the core, never the reverse.
- Keep input and output at the edges. Parse and validate once at the boundary, then pass typed, trusted data inward. Pure functions in the middle are the ones you can test without a harness.
- One source of truth for every fact: a constant, a schema, a config value. A second copy is a future bug.

**Size the design to the problem**
- Choose the smallest stack and the fewest moving parts that ship the stated scope. Name what version one deliberately leaves out.
- Do not build for a requirement nobody has stated. No plugin system for one plugin, no abstraction with one implementation, no config flag for a value that never changes.
- Prefer boring, well documented technology already used in the project over a new dependency. Every new dependency needs a reason that a standard library or existing module cannot meet.

**State, failure and operation**
- Say where every piece of state lives, who owns it and how long it lives. Shared mutable state is the first place to look for a defect.
- Fail closed and loudly: an unknown input, a missing file or a malformed record is an error with a named reason, never a silent default.
- Make behaviour deterministic where it can be. Anything that can be decided by plain code should not be left to a model or to timing.
- Configuration comes from the environment or a config file, secrets never from the tree.

**Record the decision**
- When you make a choice that a reasonable engineer could have made differently, write down the context, the decision and the consequence in a few lines, where the project keeps decisions.
- State the trade off honestly: what this choice makes harder.

**Before you hand off, check**
- Can you describe each new module in one sentence without the word "and"?
- Does any new code reach across a boundary it should not?
- Is there a simpler structure that satisfies the same spec scenarios? If yes, use it.

### Skill: spec-writing

The spec is the contract the whole line works from. A vague spec produces a vague build that still passes review, because reviewers judge against the spec. Every quality problem you leave open here is paid for downstream.

**Before writing**
- Read the existing specs and the project brain. Reuse the project's terms; do not invent a second name for a thing that already has one.
- Look for conflicts with specs that are already accepted. If this order contradicts one, name both clauses and resolve it in the spec instead of leaving it for the builder to discover.
- If the work order is missing something you need to state a requirement, say exactly what is missing. Do not fill the gap with a guess dressed as a requirement.

**Requirements**
- One requirement states one obligation. Give each a stable id (R1, R2) so tests and reviews can cite it.
- Write observable behaviour, not implementation: what the system does for which input, not which class does it. Constrain the implementation only where the order requires it.
- Replace every soft word with a number or a named condition. "Fast", "good looking", "robust", "user friendly", "responsive" are not requirements until they say what is measured: "renders with no horizontal scroll at 360 px", "p95 under 200 ms", "body text contrast at least 4.5:1".
- Use a plain trigger form where it helps: "When <trigger>, the system shall <response>." "While <state>, ...". "If <unwanted condition>, then ...".

**Scenarios**
- Every requirement has at least one scenario, and every scenario names the requirement it proves. A requirement with no scenario will not be tested.
- Write each scenario as a concrete example: given this state, when this happens, then this observable result. Use real values, not placeholders.
- Cover the unhappy paths on purpose: empty input, the boundary value, the malformed record, the missing dependency, the second call. Most defects live there.
- A scenario must be checkable by a test or by named evidence. If you cannot say how it would be checked, rewrite it.

**Quality bars belong in the spec**
- For anything a person will see or use, state the quality bar as acceptance criteria: the reference to match, the viewport range, the states that must exist, the performance or accessibility floor. If it is not written here, no reviewer can hold the build to it.
- Name the evidence the run must produce (captures, measurements, a traversal proof) so the builder knows to produce it.

**Scope**
- State what is out of scope and which files or surfaces must not change. Enumerate the full write set when protected paths are involved, including test adaptations.
- Keep the spec as short as the contract allows. Rationale goes in one Purpose paragraph, not in every requirement.

**Before you hand off, check**
- Could two builders read this and ship materially different things? Then it is not specific enough.
- Does every R have an S, and every S a named R?
- Is every number in the spec one you verified or one the owner stated?

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

## Run context

Read the upstream work before you start; it is the input your station builds on.

- Output of intake: runs/wo-gh-50/intake.output.md
