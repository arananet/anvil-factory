# Execution: agent runtimes, deploy and verification

In a normal run the deterministic spine executes and every agent station
produces a task packet. Packets are the contract. This document describes how
an operator plugs a real agent runtime into that contract, and how a run can
deploy and verify its own change once it has earned approval.

## The runtime contract

A runtime config lives in the project `anvil.yaml` under `runtime`:

```json
{
  "runtime": {"kind": "command", "command": "my-agent --packet {packet}", "timeout_seconds": 300}
}
```

Run the line with execution enabled:

```bash
python3 -m anvil.cli run . --pipeline pipelines/sdlc-default.json --work-order work-order.json --execute
```

Without `--execute`, nothing changes: packets only. With `--execute` and a
configured runtime, each agent station packet is rendered as today (station
prompt, work order, upstream step summary) and sent to the executor:

- The executor output is written to `runs/<id>/<station>.output.md`.
- The step status becomes `executed`, and the envelope records status
  `executed` plus the executor name.
- If the executor fails or the kind is unknown, the step status is `failed`
  with the error recorded in the step and the envelope. A failed step is never
  quietly reported as `packet_ready`.
- Reviewer stations are expected to answer with a review JSON (their prompts
  ask for it). A parsed review feeds the approver of that same run. If the
  output does not parse, the envelope records `review_parse_failed` and the
  station contributes no review.
- Cost stays null unless the executor reports usage. When usage is reported,
  token counts are recorded on the step and the envelope; a numeric cost in
  the usage object is the only way a step cost becomes non null.

The approver only ever aggregates reviews produced during the same run.
Standing reviews under `reviews/<slug>/` are the project record that
`anvil check` reads; they are not run inputs.

## Executor kinds

### command

```json
{"runtime": {"kind": "command", "command": "claude -p \"$(cat {packet})\"", "timeout_seconds": 900}}
{"runtime": {"kind": "command", "command": "codex exec --packet {packet} --out {output}", "timeout_seconds": 900}}
```

The template supports two placeholders: `{packet}` (path of the rendered
packet file) and `{output}` (path the runtime may write its answer to). The
command runs through the shell in the project root. Standard output is the
station output; if the command writes a non empty `{output}` file, that file
wins. These two examples are shapes, not endorsements: wire the CLI you
already operate, with the flags that CLI actually accepts.

### http

```json
{"runtime": {"kind": "http", "endpoint": "https://api.example.com/v1/chat/completions", "model": "your-model", "api_key_env": "MY_RUNTIME_API_KEY", "timeout_seconds": 300}}
```

ANVIL POSTs an OpenAI style chat payload (`model`, `station`, `messages`
with the packet as the user message) and reads `choices[0].message.content`
plus the optional `usage` object. The API key is read from the environment
variable named by `api_key_env` at call time and sent as a bearer token. The
key never comes from the config file and is never logged.

## Automatic deploy and post deploy verification

The deployer station never runs through a generic executor. Deploying is a
different kind of act, so it has its own config in `anvil.yaml`:

```json
{
  "deploy": {
    "command": "wrangler deploy",
    "verify": ["curl -fsS https://your-service.example/health", "python3 -m unittest discover -s tests"],
    "timeout_seconds": 600
  }
}
```

The deploy command runs automatically only when all of these hold:

- the run used `--execute`,
- a deploy config with a command exists,
- the approver verdict is `approved` from reviews produced in that run,
- no human gate blocks the run.

Otherwise the deployer stays a packet, exactly as in a non executed run.

When the deploy command runs:

- It runs in the project root with `ANVIL_WORK_ORDER_ID` in the environment.
- Its combined output is captured to `runs/<id>/deployer.output.md`.
- Right after a successful deploy, and before any later station such as the
  observer is emitted, the spine runs each verify command as a deterministic
  gate and records every result in `report.json` and `swimlane.md`.
- The run ends with a deployment status:
  - `deployed_verified`: deploy ran and every verify command passed.
  - `deployed_unverified`: deploy ran but at least one verify command
    failed. The verify step is marked failed and
    `runs/<id>/verify-findings.md` summarizes the failure for a follow up
    work order. A deploy in this state is never reported as a success.
  - `deploy_failed`: the deploy command itself failed; no verify commands
    run.

The deploy target is whatever the operator's command does: a directory copy
in the Taskline demonstration, `wrangler deploy` or a release script in real
use. ANVIL runs the command and the verification; it does not invent a
hosting target, and it does not hold credentials. Secrets for deploy and
verify commands stay in the operator environment, never in the config file.

## The honest boundary

ANVIL ships the contract and the plumbing: packet rendering, execution
recording, run scoped review aggregation, deploy and verification gating.
The model runtime is the operator's choice and the operator's credentials:
a local agent CLI, an HTTP model endpoint, or a human following the packet by
hand all satisfy the same contract. If no runtime is configured, ANVIL says
so by producing packets, and it never claims a model ran when one did not.
