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

- id: wo-gh-14
- kind: feature
- title: Application metrics and post-deploy health verification
- source: github-issue
- description: Implement the spec in .openspec/specs/post-deploy-health/spec.md in the factory. It is the ninth and final work order of the capability program and runs after the status dashboard work in the same sequence.

Build, per the spec scenarios:

S1: post-deploy health verification as a deterministic step after the deploy step: a project declares a health target in its configuration (deployed base URL, key routes with expected statuses, optional platform signal source). Route checks are plain HTTP requests recording route, expected and observed status or transport error, and latency. Where the project declares a Cloudflare Workers source, the verification reads the Worker's request and error signals through the Cloudflare API for the window since the deploy, through the operator's existing credential path. All checks passing and no platform errors reads healthy, recorded in a health section in the run report, reflected in the deployment status as deployed and healthy, and shown as a health step in the swimlane.

S2: any failing route or platform errors above the configured acceptable level reads unhealthy, with the failing signals quoted in the record (route and observed status, or error counts), the deployment status reading deployed and unhealthy, and the human gate forced with the health reason in the decision record even when the approver verdict was approved.

S3: no health target, or every signal source failing to read, reads unknown with the reason named and a warning that health could not be verified; unknown is never rendered or aggregated as healthy anywhere.

S4: the application metrics slot: anvil init, anvil new-project and anvil onboard configurations gain an opt-in metrics section (empty endpoint and provider key placeholder fields, an explanatory comment, no vendor name or endpoint shape anywhere in the factory core or the generated config); onboard still never overwrites an existing configuration.

S5: demonstrate on a factory owned target (the published status page or the intake Worker; choose whichever is deployable and checkable from the executed-run environment and record the choice and reason), with the demonstration run's report carrying the health section and its evidence.

Health verification is deterministic, never a model station, and never blocks a run whose project declares no target. Tests from fixtures covering S1 to S5 in the factory suite style, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/14
- risk_hints: production-deploy
- status: new

## Upstream steps

- (none)
