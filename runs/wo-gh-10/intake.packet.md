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

- id: wo-gh-10
- kind: feature
- title: Per job cost measurement in run reports
- source: github-issue
- description: Implement the spec in .openspec/specs/cost-measurement/spec.md in the factory.

Build, per the spec scenarios:

S1: each run step gains a cost record (measured flag, input and output token usage when reported, the model priced from, the amount when measured). For stations executed by a runtime that leaves session transcripts with token usage, the executor sums the usage attributable to the step's execution window; usage that cannot be attributed to a step is not spread across steps.

S2: for HTTP gateway executions, the executor reads the usage object from the gateway response when present and attaches it the same way; a response with no usage object leaves the step unmeasured.

S3: a step with no usage source, or an executed model with no price table entry, records measured false, a null amount, and the stated reason. Nothing is estimated.

S4: the run report gains a cost section whose total is the sum of measured steps only, with measured and unmeasured step counts; the swimlane shows the total with its coverage counts.

S5: prices live in configuration as a price table mapping model names to input and output prices per million tokens, every entry labelled with its source and the date recorded; the loader rejects an entry missing either label.

Cost measurement changes no verdict: the approver, the gates and the human gate read nothing from the cost section. Tests covering S1 to S5 in the factory suite style, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/10

Operator standing note for every round of this order: the builder must not create or modify anything under .github/workflows/ (the Actions token cannot push workflow changes; a run that touches them loses its commit-back). Tooling the run needs is staged by the operator in the workflow before the line step. Test changes are written by the test-writer station; the builder must not modify tests/, anvil.json or pipelines/. Tests must be real: every test calls the implementation it names and asserts behavior, never the mere existence of data structures.

GATE LOOPBACK 1 (after run 41761646614, verdict changes_requested, reviews counted 5 of 5; reviewer-architecture is the only requesting reviewer). Fix exactly these counted findings:

1. Process violation: the builder created tests/test_cost_measurement.py and tests/test_cost_measurement_README.md, which the work order forbids. In this round the builder removes both files from its change and does not recreate them. The cost measurement tests are authored by the test-writer station in its own step; if the suite needs them, the test-writer writes them.

2. Out of scope changes: the intake station changes (anvil/config.py DEFAULT_MODELS and the stations/intake/station.json model field) are unrelated to the cost measurement spec. The builder reverts them; this order changes nothing about the intake station's model configuration.

3. Legacy cost override: anvil/runner.py (around lines 864-866) lets usage.cost override the calculated cost, and the spec does not document that behavior. Either remove the legacy path, or document it in the cost measurement spec and docs as intentional backwards compatibility. State which option was taken in the builder output. The suite stays green either way.

Everything else from round 1 stands (reviewer-spec, reviewer-security, reviewer-tests and reviewer-design passed; the architecture review confirms anvil/cost.py separates concerns correctly and cost does not affect verdicts). Standing discipline unchanged: the builder must not modify tests/, anvil.json, pipelines/ or .github/workflows/. Keep the whole suite green and every pipeline valid. Update CHANGELOG Unreleased if the change set changes.
- risk_hints: 
- status: new

## Upstream steps

- (none)
