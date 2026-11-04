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

- id: wo-gh-12
- kind: feature
- title: A dedicated UX reviewer station (reviewer-ux), separate from reviewer-design
- source: github-issue
- description: Implement the spec in .openspec/specs/reviewer-ux/spec.md in the factory. It builds on the routing capability and the design knowledge capability, both landed earlier in this program's sequence, and on the rendered evidence capability where screenshots exist.

Build, per the spec scenarios:

S1: stations/reviewer-ux/ in the catalog (agent kind, standard review format) whose contract judges the experience: user flows and task completion, usability heuristics, accessibility basics, and clarity of the interface copy; the contract explicitly excludes visual system compliance (tokens, type scale, palette) as reviewer-design's lens, and the catalog entry carries the guided design station designation naming the design model from the recorded routing policy.

S2: reviewer-ux joins the reviewer group of sdlc-default, content-default and content-short (the pipelines reviewer-design serves). The routing step activates it when the work order carries a ui surface; its packet then carries the design knowledge guidelines slice for the project's product type and, where the run produced rendered screenshots, the rendered evidence.

S3: on work with no ui surface the router routes reviewer-ux out before execution, records it as routed out with the surface rule named, and the approver's expected review count excludes it; no reviewer-ux step executes and non-UI work pays nothing for the lens.

S4: the run report and swimlane list reviewer-design and reviewer-ux as separate entries with independent verdicts and findings.

S5: when a ui surface run has no rendered screenshots, reviewer-ux's recorded review states it judged from source and the knowledge slice without rendered evidence.

Tests covering S1 to S5 in the factory suite style, including the ui-surface selection and the non-ui skip, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/12

Operator standing note for every round of this order: the builder must not create or modify anything under .github/workflows/ (the Actions token cannot push workflow changes; a run that touches them loses its commit-back). Tooling the run needs is staged by the operator in the workflow before the line step. Test changes are written by the test-writer station; the builder must not modify tests/, anvil.json or pipelines/. Tests must be real: every test calls the implementation it names and asserts behavior, never the mere existence of data structures.
- risk_hints: 
- status: new

## Upstream steps

- (none)
