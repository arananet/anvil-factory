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

- id: wo-gh-8
- kind: feature
- title: Risk and surface routing of reviewer sets and station models
- source: github-issue
- description: Implement the spec in .openspec/specs/risk-routing/spec.md in the factory. It consumes the risk and surfaces the intake outcomes capability stamps on the work order; that capability lands before this one in the same program, so build against its model fields.

Build, per the spec scenarios:

S1: a deterministic routing step after intake and before the reviewer stage; low risk with no ui and no security surface selects the reduced reviewer set (reviewer-spec and reviewer-tests) at the cheaper configured reviewer model, with the rule named as the reason.

S2: a security surface at any risk level always keeps reviewer-security in the set at the strong configured reviewer model.

S3: a null risk rating defaults to the full panel at the policy models, with the routing record stating the default applied because the work was unrated. A ui surface keeps reviewer-design in the set whenever the pipeline has it. Medium risk is the full panel at policy models; high risk the same with no reduction recorded.

S4: the recorded model routing policy is a ceiling: routing may reduce, never exceed it, and a project routing configuration that assigns a model above the policy for a station kind fails at config load naming the violation.

S5: a routed out reviewer is recorded as routed out with its rule; the approver treats it as not expected, and its review count names the expected count after routing.

S6: the routing record lands in the run report as its own section (selected set, selected models, reason per decision) and the swimlane shows a one line summary.

Routing rules live in project configuration with a factory shipped default table. Routing never changes the checks gate or the scenario-to-test gates. Tests covering S1 to S6 in the factory suite style, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/8
- risk_hints: 
- status: new

## Upstream steps

- (none)
