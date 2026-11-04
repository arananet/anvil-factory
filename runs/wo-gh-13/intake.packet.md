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


## Work order

- id: wo-gh-13
- kind: feature
- title: Status dashboard shows the lifecycle stage per work order
- source: github-issue
- description: Implement the spec in .openspec/specs/status-lifecycle-stages/spec.md in the factory's status page generation.

Build, per the spec scenarios:

S1: stage derivation as a pure function of the job's latest run data: SPEC from the recorded spec stage, BUILD from the builder step, REVIEW from reviewer steps, APPROVED from the decision's approver verdict, the current stage being the furthest the evidence supports, and a job with no runs showing nothing reached.

S2: MERGED comes only from an actual merge record (merged pull request or merged run branch) in the merge data the generator consumes; an approved job with no merge record shows APPROVED and MERGED stays unmarked; with a merge record it shows MERGED. Derivation never infers merges from branch names or commit messages and never calls the network.

S3: NEEDS HUMAN derives from the decision's human_required flag for any reason it was set, rendered with a visually prominent badge treatment alongside the current stage; absent when the flag is false.

S4: intake states compose: a latest run that ended parked (waiting_info) shows PARKED and one that ended rejected shows REJECTED, instead of a stage progression.

S5: the generated page is one board: one row per work order carrying its id, title, the stage sequence with reached stages marked and the current stage highlighted, the NEEDS HUMAN badge when it applies, and a link from each row to that job's swimlane or run detail. Regenerating from the same data produces the same board. The derivation and rendering live in the factory's status page generator so every surface it generates (the factory status page and the example project's page) renders the board the same way.

Tests covering S1 to S5 from report fixtures in the factory suite style, including the approved-but-unmerged case and the human_required case, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/13

Operator standing note for every round of this order: the builder must not create or modify anything under .github/workflows/ (the Actions token cannot push workflow changes; a run that touches them loses its commit-back). Tooling the run needs is staged by the operator in the workflow before the line step. Test changes are written by the test-writer station; the builder must not modify tests/, anvil.json or pipelines/. Tests must be real: every test calls the implementation it names and asserts behavior, never the mere existence of data structures.
- risk_hints: 
- status: new

## Upstream steps

- (none)
