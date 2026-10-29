# Application Metrics and Post-Deploy Health

Status: approved
Slug: post-deploy-health

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
A run today can end at deployed_verified having proved only that a deploy command exited well. Nothing checks that the shipped product is actually alive: the page can 500, the Worker can be throwing on every request, and the run record still reads like success. This spec closes the loop between shipping and knowing: after the deploy step, the factory verifies the product's health from live signals and records what it found with the same honesty rules as every other verdict in the system, including saying "unknown" when there is nothing it can truthfully read. It also gives projects a standing, opt-in place to point the factory at their own application metrics, without the factory core marrying any one vendor.

## Requirements

### Post-deploy health verification
- Health verification runs after a run's deploy step completes, for any run whose project declares a health target. It is a deterministic step, not a model station: it performs checks, reads signals, and records results; no model judges health.
- A project declares its health target in project configuration: the deployed base URL, the key routes to check (paths appended to the base URL, each with its expected HTTP status, defaulting to 200), and optionally a platform signal source. Route checks are plain HTTP requests from the runner or the executed-run workflow environment; each check records the route, the expected status, the observed status (or the transport error), and the latency.
- Platform error signals are read where the platform exposes them and the project declares the source. The first supported source is Cloudflare Workers: for a project whose deploy target is a Worker, the verification reads the Worker's request and error signals through the Cloudflare API (requests served, errors observed in the window since the deploy) using the project's configured account and Worker identifiers and the operator's existing Cloudflare credential path. Other platforms are added as sources later; the contract is the shape of the recorded signal (source, window, requests, errors, read success or failure), not any one vendor's API.
- The health outcome has exactly three values:
  - healthy: every route check observed its expected status and, where a platform source was read, its error signals show no errors in the window (or an error level the project config declares acceptable).
  - unhealthy: at least one route check failed or the platform signals show errors above the declared acceptable level. The failing signals are quoted in the record: the route and observed status, or the platform error counts, never summarized away.
  - unknown: the project has no live target declared, or every signal source failed to read (network failure, missing credential, platform API error). Unknown names which case it is. Unknown is a stated gap in the run record; nothing anywhere in the factory renders or aggregates unknown as healthy.
- The outcome lands in the run report as a health section (outcome, per route results, platform signals with their source and window, and the reason when unknown) and modifies the deployment status the report carries: the deploy verdict reads as deployed and healthy, deployed and unhealthy, or deployed with health unknown, alongside the existing deployment status vocabulary, so the two facts (the deploy ran; the product is alive) are never collapsed into one ambiguous word. The swimlane shows the health outcome as its own step after the deploy step.
- An unhealthy outcome feeds the human gate exactly as other risk outcomes do: a run whose health is unhealthy requires a human at the gate (human_required set with the health reason in the decision record), even when the approver's verdict was approved. A healthy outcome changes nothing at the gate. An unknown outcome is recorded and warned in the report's warnings, and does not by itself force the gate beyond what the decision already required; the warning states plainly that health could not be verified.
- Verification never blocks on missing configuration: a project with no health target gets the unknown outcome recorded with the no-target reason and the run otherwise proceeds as today.

### Application metrics slot
- Project scaffolding (anvil init, anvil new-project) and anvil onboard add an opt-in application metrics slot to the project configuration they create: a metrics section with an endpoint field and a provider key placeholder field, both empty by default, plus a comment in the generated configuration explaining that the project fills them to connect its own metrics provider. The slot is provider agnostic: no vendor name, SDK or endpoint shape is written into the factory core or the generated configuration; the factory reads the slot only as an endpoint and an optional key reference.
- Onboard never overwrites: a project whose configuration already exists keeps it byte for byte, as with every other onboard discipline; the slot appears only in configurations the factory creates.
- The health verification may use the metrics endpoint as an additional signal source when a project has filled it (a reachable endpoint answering as configured counts toward the signal record), but health verification works fully from route checks and platform signals when the slot is empty.

### Demonstration
- The capability is demonstrated on a target the factory itself owns: the factory's published status page or its intake Worker, declared as that project's health target, with the demonstration run's report carrying the health section and its evidence. The demonstration target is chosen by which of the two is deployable and checkable from the executed-run environment at build time, and the choice and its reason are recorded in the run.

## Scenarios

### Scenario: A healthy deploy reads as deployed and healthy
- S1: Given a fixture project whose route checks all observe their expected status and whose platform signals show no errors in the window, when health verification runs after the deploy step, then the health section records healthy with the per route results and the platform signals, the deployment status reads deployed and healthy, and the swimlane shows the health step.

### Scenario: An unhealthy deploy quotes its failing signals and forces the gate
- S2: Given a fixture project with one route observing a 500 against an expected 200 (or platform error counts above the acceptable level), when health verification runs, then the health section records unhealthy quoting the failing route and observed status (or the error counts), the deployment status reads deployed and unhealthy, and the run's decision requires a human with the health reason recorded, even if the approver verdict was approved.

### Scenario: No target or unreadable signals reads as unknown, never as healthy
- S3: Given a fixture project with no health target declared, when health verification runs, then the health section records unknown with the no-target reason and a warning states health could not be verified; and given a fixture project whose signal sources all fail to read, then the outcome is likewise unknown naming the read failure, and no part of the report or swimlane renders the job as healthy.

### Scenario: The metrics slot is scaffolded opt-in and provider agnostic
- S4: Given anvil init, anvil new-project and anvil onboard creating a project configuration, when the generated configuration is read, then it contains a metrics section with empty endpoint and provider key placeholder fields and the explanatory comment, containing no vendor name or vendor endpoint shape; and given a project with an existing configuration, when onboard runs, then the configuration is byte for byte unchanged.

### Scenario: The demonstration run carries health evidence on a factory owned target
- S5: Given the demonstration target (the factory status page or the intake Worker) declared as a health target, when its demonstration run completes its deploy step, then the run report contains a health section for that target with route results and, where readable, platform signals, and the swimlane shows the health step with its outcome.
