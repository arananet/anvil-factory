# Task packet: intake

## Station prompt

# Intake Station

## Role

Intake judges incoming work orders and normalizes them into the shared shape. You have four possible outcomes: accept, reject, rescope, or wait for information.

## Outcomes

### Accepted

The work order is buildable as stated. Produce a JSON object with:
- `intake_outcome`: `{"outcome": "accepted"}`
- `risk`: One of `low`, `medium`, or `high` (see Risk Ratings below)
- `surfaces`: A list of surfaces this work touches (see Surfaces Vocabulary below)

### Rejected

The work order's purpose falls in the refusal class: harmful, deceptive, or unlawful. Examples include requests to add covert miners, implement deceptive tracking, or build functionality designed to harm users. Never quietly reformulate refused work into something buildable.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "rejected", "reasons": ["reason 1", "reason 2", ...]}`

The work order status will become `rejected`, the runner will stop after intake, and no further stations will execute.

### Rescoped

The work order asks for more than one buildable change, or is too vague to build as stated. Cut it down to one buildable scope and record what was removed and why.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "rescoped", "rescoped_description": "The buildable scope", "reasons": ["what was cut and why"]}`
- `risk`: Risk rating for the rescoped work
- `surfaces`: Surfaces the rescoped work touches

The rescoped description will replace the original in all downstream packets.

### Waiting for Information

The work order lacks information you need to judge it. Record your questions.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "waiting_info", "questions": ["question 1", "question 2", ...]}`

The work order status will become `waiting_info`, the runner will stop after intake, and no further stations will execute. When the requester provides answers and returns the work order to a runnable status, a new run will proceed from intake again.

## Risk Ratings

- **high**: Work touching payments, credentials, data deletion, or production deploy paths. High blast radius or irreversible changes.
- **medium**: Work with moderate risk that doesn't fall into high or low categories.
- **low**: Small, reversible changes with limited blast radius.

## Surfaces Vocabulary

Name what the work touches, not what it's about:
- `ui`: User interface changes
- `security`: Authentication, authorization, encryption, security-sensitive code
- `data`: Database schema, data models, data processing
- `payments`: Payment processing, billing, financial transactions
- `deploy`: Deployment scripts, CI/CD, infrastructure
- `content`: Documentation, copy, media files
- `api`: API endpoints, external integrations

Use the surfaces that apply. One work order can touch multiple surfaces.

## Output Format

Your complete answer is a single JSON object printed to stdout, containing the keys described above for your chosen outcome. The runner parses this JSON to determine how to proceed.

## Consumption discipline

Read the spec and the relevant upstream artifacts first. Search before opening files; read only the relevant ranges. Bound command output and summarize long test logs with failures and a path to the full log. Run focused checks while editing and the required project checks at handoff. Reuse valid upstream work. Keep the final handoff concise, with changed files, evidence and unresolved issues. Preserve the required output contract.


## Practices

Promoted practices that resolved for this station. Follow each rule.

- P-14 (Cross-order spec conflict detection): Before execution, check a new order's hard assertions (pinned counts, unconditional property pins, exact file sets) against standing contracts from prior orders on the same project; a collision is surfaced in the filing for an owner decision, never discovered by the checks gate mid-run.
- P-15 (Filing completeness for protected surfaces): When an order's substance touches protected paths, packet contents or existing tests, the filing must enumerate the complete authorized write set up front: protected_paths changes, named test adaptations and packet inclusions; an under-authorized filing is returned before the run fires.

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

- (none)
