# Proven Patterns: a New Project Starts From What Already Worked

Status: proposed
Slug: proven-patterns

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

The factory remembers inside a project and forgets between projects. A project's brain holds its verified learnings and its practices; the curated skills hold craft; a blueprint names a stack. Nothing holds the thing a finished project proves: the shape that worked for that kind of product, the routes that were tried and rejected, and what each stage really cost.

The case that shows the gap is Retro Explainers, a channel of short explainer videos that began as a draft from this factory and was then developed in its own repository between 2026-11-15 and 2026-11-22 (handover note of 2026-11-22, operator copy). In one week that project settled a gated stage order (script, proof, master, pack), deterministic checks that run before any reviewer sees an output, an independent reviewer limited to one automatic revision, a needs-owner stop, cost measured per stage, a board that tracks every episode, and a written list of five visual routes that were each built, rejected and are now banned and checked by a tool. Four episodes are published. None of it has come back to the factory: the next project of that kind would pay again to explore the five rejected routes, and the factory itself is only now filing orders for a board (wo-gh-47) and for stopping futile loops (wo-gh-49) that the child project already has.

This order gives the factory a place for that knowledge and a discipline for letting it in. A pattern is a versioned pack, in plain files in the repository, harvested from a project that succeeded, held in quarantine until the owner promotes it, selected deterministically for a new project by its product type, and handed to each station as the slice that station needs. Plain files and no database: a pack is reviewed like any change, and a person who copies the factory gets the patterns with it.

## Requirements

### R1. The pattern pack
- A pattern lives at patterns/<id>/ and holds: pattern.json (id, title, version, the product types it serves, the blueprint it builds on when it has one, the source project and the commits it was harvested at, and the success evidence); structure.md (stages, gates, layout, what lives where); dead-ends.json (routes that were tried and rejected, each with what it was, why it was rejected and the evidence); calibration.json (measured cost and tokens per stage or station, each figure with the run or record it came from); and optionally guardrails/ (checks, in the form the blueprint guardrails order defines when it lands) and a list of curated skills the pattern relies on.
- Loading validates a pack: required files and fields, unique ids across packs, a dead end without evidence or a calibration figure without its source fails loading and names the entry.
- A pack carries process, guardrails, dead ends and measurements. It never carries a project's content or identity: no media file, no brand asset, no design token file, no copy, no credential. The validator rejects media and binary files and any file named like a secret, and fails a pack whose structure.md or dead-ends.json contains a value from the source project's design tokens when those are provided to the harvest.

### R2. Harvest into quarantine
- anvil harvest <project-path> --as <pattern-id> reads a finished project on disk and writes a proposal to patterns/inbox/<pattern-id>/: the files the operator names in a harvest manifest, copied with their source path, commit and sha256, and a skeleton of the pack files with every field that needs judgment left marked as open. The command is deterministic and makes no model call.
- A proposal in patterns/inbox/ is never selected, never injected and never used by scaffolding.
- The provenance record states plainly whether the line produced and reviewed the source work or whether it was authored outside the line (decision 0006).

### R3. Promotion is the owner's, on evidence
- anvil promote-pattern <pattern-id> --by <name> moves a proposal to patterns/<id>/ only when: no field is still marked open; every copied file still matches its recorded sha256; the success evidence names at least one verifiable outcome (an owner acceptance record, a merged and surviving change, a published artifact with its reference); and the content rule of R1 holds. Otherwise it refuses and names what is missing.
- anvil check-patterns validates every promoted pack and is part of what the factory's own checks can run.
- A new version of a pattern is a new harvest and a new promotion; the previous version stays on record.

### R4. Selection is deterministic
- A project declares its product type where it does today (brain/project.md, the line "Product type:"). At intake the runner selects the promoted pattern whose product types include it; with more than one candidate the highest version of the most specific match wins and the rule that decided is recorded.
- The run report records the pattern id and version selected, or that none matched. The same inputs always select the same pattern.
- No pattern matched means nothing is injected and the run behaves as today.

### R5. Each station gets its slice
- spec-writer and builder packets gain a Proven pattern section with the structure and the dead ends; reviewer packets gain the dead ends as statements to check; the intake packet gains the pattern's title and version. Packet budgets apply: a slice that does not fit is trimmed in a declared order and the trim is recorded, as packets do today.
- A dead end that names a guardrail check is enforced by that check; one that does not is prompt text and the pack says so, so the count of each is visible.
- anvil init --pattern <id> creates a project with the pattern's structure, its guardrail checks wired into the project's checks, and its calibration as the starting efficiency partitions when the factory supports partitions.

### R6. The authority order
- The project's own brain, practices and specs win over a pattern on any conflict; a deviation from a pattern alone is not a finding. A pattern is reference the project starts from, the same standing the design knowledge has.

### R7. Regression tests
- New test files under tests/, with fixture projects and fixture packs: (a) a pack with a dead end lacking evidence, or a calibration figure lacking its source, fails loading naming the entry; (b) a pack containing a media file or a design token value from the source project is rejected; (c) harvest writes a proposal with path, commit and sha256 for each copied file and makes no model call; (d) a proposal in the inbox is not selected for a matching project; (e) promote refuses a proposal with an open field, a changed file or no success evidence, and promotes a complete one; (f) two fixture patterns for one product type select the same one on every run and the rule is recorded; (g) spec-writer, builder and reviewer packets of a matching project carry their slices and a non matching project's packets are unchanged; (h) anvil init --pattern creates the structure and wires the checks; (i) a project without a pattern scaffolds and runs exactly as before.

### Guardrails
- Python standard library only. No new dependency and no database.
- Authorized surface: a new module anvil/patterns.py, anvil/cli.py (harvest, promote-pattern, check-patterns, the --pattern option of init), anvil/scaffold.py, anvil/runner.py only where packets are assembled and the selection is recorded, anvil/config.py if needed, a new top level patterns/ directory with its README and an empty inbox, docs (a new docs/PATTERNS.md and a short section in docs/ARCHITECTURE.md), CHANGELOG.md, one new decision record under brain/decisions/, and new test files under tests/.
- This order ships the mechanism and no promoted pattern. The first harvest, from Retro Explainers, is done by the operator with the tool once it exists, and its promotion is the owner's.
- Not touched: files under .github/workflows; pipeline files under pipelines/ and anvil.json (protected paths); existing blueprints.
- Frozen: the memory gate and the practices door (their quarantine, provenance and promotion rules are the model, not changed); the design knowledge loader and its slice matching; the curated skills catalog; packet budget semantics; the events contract.
- Relationships: a blueprint names a stack and a pattern names a proven project shape, and a pattern may build on a blueprint; practices are review rules inside one project and patterns carry knowledge between projects; the blueprint guardrails draft defines the check pack format a pattern may carry, and each works without the other.
- Known constraints from existing tests, stated here so the line does not discover them: the scaffold and onboarding tests (tests/test_greenfield.py, tests/test_onboard.py) fix what a new project contains, so the default init must be unchanged; tests/test_review_producer.py asserts the word "retry" does not occur in anvil/runner.py; tests/test_governed_delivery.py asserts the event sequence; tests/test_astra_consumption.py fixes packet trimming order. If an existing protected test contradicts a requirement of this order, the builder says so in its report on the first attempt and stops.
- Existing test files at the base ref are not modified or deleted; new tests arrive as new files.
- No em dash or en dash character in any produced file (project style rule).
- Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

## Scenarios

### Scenario: A pack must show its evidence
- S1: Given a pack whose dead end has no evidence or whose calibration figure has no source, when it loads, then loading fails naming the entry.

### Scenario: A pack never carries the source project's identity
- S2: Given a pack that contains a media file or a design token value of its source project, when it is validated, then it is rejected naming the file or the value.

### Scenario: Harvest proposes, with provenance
- S3: Given a finished project and a harvest manifest, when anvil harvest runs, then patterns/inbox/<id>/ holds the copied files with path, commit and sha256, the pack skeleton with open fields marked, and no model was called.

### Scenario: Quarantine holds
- S4: Given a proposal in patterns/inbox/ whose product type matches a project, when that project runs, then no pattern is selected and no packet changes.

### Scenario: Promotion needs evidence
- S5: Given a proposal with an open field, a copied file that no longer matches its hash, or no success evidence, when promote-pattern runs, then it refuses naming what is missing; given a complete proposal, then it is promoted and check-patterns passes.

### Scenario: Selection is deterministic and recorded
- S6: Given two promoted patterns that serve one product type, when a matching project runs twice, then the same pattern is selected both times and the run report records the pattern, its version and the rule.

### Scenario: Each station gets its slice
- S7: Given a project matching a promoted pattern, when its packets are built, then spec-writer and builder carry the structure and dead ends, reviewers carry the dead ends, and a project matching no pattern has unchanged packets.

### Scenario: A new project is born from a pattern
- S8: Given anvil init --pattern <id>, when the project is created, then it has the pattern's structure and its checks are wired into the project's checks.

### Scenario: No pattern, no change
- S9: Given a project with no matching pattern and an init without --pattern, when it is scaffolded and run, then the result is the same as before this change.
