# Agent Execution

Status: approved
Slug: agent-execution

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
Let an operator plug a real agent runtime into the line. In execute mode a configured executor runs each agent station packet and returns output; the runner records what actually ran, feeds reviewer output back to the approver, and can deploy and verify a change automatically when the run earned it.

## Requirements
- Execution is opt in: `anvil run --execute` with a `runtime` object in anvil.yaml. Without the flag, runs behave exactly as before and agent stations produce packets.
- Two executor kinds: `command` (a shell command template with {packet} and {output} placeholders) and `http` (an OpenAI style chat endpoint). The HTTP executor reads its API key from the environment variable named by `api_key_env`; a key never comes from the config file and is never logged.
- Cost stays null unless the executor reports usage. When usage is reported, its token counts are recorded on the step and the envelope.
- The deployer station is special: it never runs through a generic executor. It runs only from a `deploy` object in anvil.yaml, only in execute mode, only when the approver verdict is approved and no human gate blocks. Secrets for deploy and verify commands stay in the operator environment, never in config.

## Scenarios

### Scenario: Executed packet produces an output artifact and an executed step
- S1: Given a configured command executor, when a run executes an agent station packet, then the executor output is written to runs/<id>/<station>.output.md, the step status is executed, and the envelope records status executed with the executor name.

### Scenario: Unknown or failing executor fails the step openly
- S2: Given an executor kind that does not exist, or a command executor that exits non zero, when a run tries to execute a station, then the step status is failed with the error recorded in the step and the envelope, and the step is never reported as packet_ready.

### Scenario: Reviewer executor output feeds the run scoped approver
- S3: Given a reviewer station executed by an executor whose output contains a review JSON with verdict pass, when the approver step runs, then the verdict is approved from that run produced review; if the review JSON cannot be parsed, the envelope records review_parse_failed and the run counts no review from that station.

### Scenario: HTTP executor records reported usage
- S4: Given an http executor whose endpoint returns an OpenAI style response with a usage object, when a station executes, then the token counts from usage are recorded on the step and envelope, and cost stays null because no cost was reported.

### Scenario: Approved run deploys automatically
- S5: Given execute mode, a deploy config, an approver verdict of approved and no human gate blocking, when the line reaches the deployer station, then the configured deploy command runs in the project root with ANVIL_WORK_ORDER_ID in its environment, its output is captured to runs/<id>/deployer.output.md, and the deployer step status is executed.

### Scenario: Verification is a gate after deploy
- S6: Given a successful deploy, when the configured verify commands run, then each result is recorded in the report; if all pass the run deployment status is deployed_verified, and if any fails the verify step is failed, the run deployment status is deployed_unverified, the failing output is recorded, and runs/<id>/verify-findings.md summarizes the failure. A failed deploy command sets the deployment status to deploy_failed and no verify commands run. A run is never reported as a successful deploy unless verification passed.

### Scenario: No deploy without the full set of conditions
- S7: Given any of: no --execute flag, no deploy config, an approver verdict other than approved, or a human gate that blocks, when the line reaches the deployer station, then no deploy command runs and the deployer stays a packet, exactly as a non executed run behaves today.
