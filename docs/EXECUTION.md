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
- For reviewer stations, the reviewer itself writes its review to
  `runs/<id>/<station>.review.json`, which is the authoritative review channel.
  The runner removes any pre-existing review file before the reviewer executes,
  so the file's presence at step exit means it was produced during this run.
  The runner parses reviews only from this file, never from the free output
  transcript (which stays as provenance only).
- The step status becomes `executed`, and the envelope records status
  `executed` plus the executor object `{kind, detail}` (see Model
  provenance below).
- If the executor fails or the kind is unknown, the step status is `failed`
  with the error recorded in the step and the envelope. A failed step is never
  quietly reported as `packet_ready`.
- Reviewer stations are expected to write exactly one review JSON object to
  their review file: `{"station": "<station-id>", "verdict": "pass | fail |
  changes_requested", "findings": ["..."]}`. The review file must parse as
  exactly one JSON object (surrounding whitespace and one surrounding markdown
  code fence allowed) with the station field equal to the step station id,
  verdict one of pass, fail, or changes_requested, and findings a list of
  strings. A parsed review feeds the approver of that same run. If the review
  file is missing when the station exits, the envelope records
  `review_file_missing` and the station contributes no review. If the file
  exists but is empty, malformed, or does not match the expected shape, the
  envelope records `review_parse_failed` and the station contributes no review.
  The wrapper validates the review file at station exit and allows one
  in-session correction attempt when the file is missing or malformed; a second
  failure stands as recorded.
- Usage and cost are separate. The supplied wrappers capture runtime usage
  for every attempt, including failed calls and review corrections. The
  command executor hands them `ANVIL_USAGE_PATH` and reads the versioned
  usage artifact even when the command fails. Token counts remain available
  without a price table; cost requires recorded prices. Claude's own dollar
  figure is labeled a runtime estimate. See [COST-MEASUREMENT.md](COST-MEASUREMENT.md).

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

The executor resolves packet/output paths before changing directories and
hands off `ANVIL_PROJECT_ROOT` explicitly. Both wrappers use that target as
their working tree, including review-file checks, even when the factory code
lives in a separate checkout. A project run does not write reviews into the
factory's own run folder.

The factory itself wires `python3 tools/dispatch_station.py {packet} {output}`.
The dispatcher reads the step's effective model from `ANVIL_CONFIGURED_MODEL`
and runs Anthropic models through `tools/claude_station.py` (Claude Code
print mode) and `openai/gpt-6.1-sol` through `tools/codex_station.py`, which
runs the Codex CLI headlessly (`codex exec`) in the repo tree with the packet
as the task, against the gateway OpenAI route with the bare id `gpt-6.1-sol`.
The gateway credential reaches Codex only through its child environment.
Producing stations may write; reviewing and observing stations get no-edit instructions,
and a reviewer that changes anything besides its own review file fails. Any
other model, a missing `codex` CLI, or a missing gateway environment fails
the step; there is no fallback runtime.

Claude uses JSON result output; Codex uses JSONL events. The wrappers extract
the answer for the existing artifact contract and keep scalar token evidence
in `<station>.output.md.usage.json`. Raw runtime JSON, prompts and environment
variables are not exported to the public usage pages. Each invocation of a
station is an agent call; its runtime may perform several model/tool turns.

The `efficiency` settings bound packet context for all agent stations and
stop new calls after run thresholds are reached. The final report records
`budget_exceeded` when further work is prevented; it does not grant approval.
Executed runs refresh `status/index.html`. Rerunning the same work order
archives its previous report under `runs/<id>/history/`, so earlier tokens
are still counted.

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

## Health verification

After the deploy step completes, the factory can verify the deployed
application's health from live signals. Health verification is configured in
the project `anvil.json`:

```json
{
  "health": {
    "base_url": "https://your-deployed-app.example",
    "routes": [
      {"path": "/", "expected_status": 200},
      {"path": "/health", "expected_status": 200},
      {"path": "/api/status", "expected_status": 200}
    ],
    "platform": {
      "source": "cloudflare_workers",
      "account_id": "your-account-id",
      "worker_name": "your-worker",
      "acceptable_error_rate": 0.01
    }
  }
}
```

Health verification runs only when a health target is declared. It performs:

- **Route checks**: HTTP requests to each declared route, recording expected
  status, observed status (or transport error), and latency.
- **Platform signals** (optional): For Cloudflare Workers, reads request and
  error counts from the analytics API for the window since deploy. Requires
  `CLOUDFLARE_API_TOKEN` in the environment. Other platforms can be added as
  sources later.

**Security Warning**: Never put provider credentials (API tokens, secrets, or
keys) directly in configuration files (anvil.json or anvil.yaml). Instead, use
environment variables (like `CLOUDFLARE_API_TOKEN`) or a secrets management
system. Configuration files are often committed to version control and may be
shared, exposing credentials. Health verification is designed to read
credentials from the environment, not from project configuration files.

The outcome is one of three values, recorded in the run report's health
section:

- **healthy**: All route checks observed their expected status and platform
  error signals (if present) show no errors above the acceptable level.
- **unhealthy**: At least one route check failed or platform signals show
  errors above acceptable. The failing signals are quoted in the record with
  specific routes and observed statuses or error counts. An unhealthy outcome
  forces the human gate even when the approver verdict was approved, with the
  health reason recorded in the decision.
- **unknown**: No health target configured, or all signal sources failed to
  read (network failure, missing credential, API error). Unknown states the
  reason and warns that health could not be verified. Unknown is never
  rendered or aggregated as healthy anywhere.

The deployment status in the run report reflects health: deployed and healthy,
deployed and unhealthy, or deployed with health unknown. The swimlane shows
health verification as a step after deploy with its outcome.

Health verification never blocks a run with no health target configured. The
unknown outcome is recorded with the reason, and the run proceeds.

### Application metrics slot

Projects can optionally declare an application metrics endpoint in `anvil.json`:

```json
{
  "metrics": {
    "endpoint": "",
    "provider_key": ""
  }
}
```

This slot is provider-agnostic: no vendor name or endpoint shape is written
into the factory core or generated configurations. Projects fill the endpoint
and provider_key fields to connect their own metrics provider. The factory
scaffolds this slot in all new projects (`anvil init`, `anvil new-project`,
`anvil onboard`) but never overwrites an existing configuration.

## Model provenance

Every step in `report.json`, and every envelope, records `configured_model`:
the station's model label resolved through the Core Four (the project
`anvil.yaml` override when present, else the station manifest, else the
built in default). It is recorded in packet mode too, because configuration
is a fact about the run, not a result of it. Spine generated steps that are
not catalog stations (the verifier, a loopback marker) record null.

Executed steps additionally record `executed_model` and an `executor`
object `{kind, detail}`:

- For the http executor, the model that ran is the model named in its
  config, so `executed_model` is that model and `detail` is the endpoint
  host.
- For the command executor, the runtime is an opaque local process. The
  detail is the command template's first token, and `executed_model`
  stays null unless the runtime's own output reports a model (a `model`
  field in its JSON output). ANVIL never guesses which model a command
  runtime used: a packet that says `claude` might have run any model the
  operator's CLI is configured with, and the record refuses to pretend
  otherwise.

In packet mode `executed_model` and `executor` stay null. The status page
shows the provenance under each station name: `model: X` when a model
actually ran, otherwise `configured: X`.

## The honest boundary

ANVIL ships the contract and the plumbing: packet rendering, execution
recording, run scoped review aggregation, deploy and verification gating.
The model runtime is the operator's choice and the operator's credentials:
a local agent CLI, an HTTP model endpoint, or a human following the packet by
hand all satisfy the same contract. If no runtime is configured, ANVIL says
so by producing packets, and it never claims a model ran when one did not.

## The autonomous line

Spec: `.openspec/specs/autonomous-line/spec.md`. Tests: `tests/test_autonomous_line.py`, `intake-worker/dispatch.test.js`.

### Loopbacks are real

In execute mode a loopback sends the work back. When the approver verdict is
rejected or changes_requested, or the pre-review checks gate fails, the runner
re-enters the line at the return station (the builder, or the spec-writer for
a missing spec) and runs every station from there again, up to `max_loopbacks`
times (2).

- The stations of the new attempt get a `Loopback feedback` section in their
  packet: who sent the work back, why, and the findings. Reviewers are told it
  is a re-review.
- Reviews of the replaced attempt never count. Its outputs and review files
  are archived under `runs/<id>/attempts/<n>/`.
- Re-executed steps carry `attempt`; the return station's step carries
  `feedback`.
- A new attempt starts only when the run thresholds leave room for all of it.
  Otherwise the verdict stands and the loopback step records `not_reexecuted`
  with the reason. The default `max_agent_calls` is 32 so the default line can
  afford one full correction; the token threshold is unchanged.
- Packet mode (no `--execute`) records the loopback and re-executes nothing,
  as before: there is no runtime to run again.

### Exit codes

`anvil run` and `anvil resume` exit with the outcome:

| Code | Meaning |
|---|---|
| 0 | Approved with the human gate open, or a packet-only run (which judges nothing) |
| 1 | Not approved, a failed step, a failed or unverified deploy |
| 2 | Usage error, or a resume that has nothing to resume |
| 3 | A human must act: approve, then resume |
| 4 | Intake stopped the order (rejected or waiting for information) |

### The human gate: approve and resume

```bash
python3 -m anvil.cli approve . wo-gh-12 --by "Ana" --note "ok to ship"
python3 -m anvil.cli resume . wo-gh-12 --execute
```

`approve` writes `runs/<id>/human-approval.json`, bound to the `run_id` it
approves: running the line again voids it. A verdict the line did not approve
(rejected, changes_requested, no_reviews) needs `--override`, which is
recorded, and the report keeps the line's own verdict. A run that did not
finish (failed, budget_exceeded, gate_failed) cannot be approved.

`resume` re-enters the line after the gate. The steps up to the gate are kept
from the previous report and no earlier station runs again; the deployer runs
its pre-deploy gate, deploy and verification, and the publisher publishes.
The decision record gains `human_gate.approval` and `resumed`.

In execute mode the publisher is held exactly like the deployer: it never runs
on an unapproved run or behind a closed human gate.

### One workflow for every order

`.github/workflows/anvil-line.yml` replaces the per order workflows.

| Trigger | Effect |
|---|---|
| An issue is labeled `anvil` | The issue becomes work order `wo-gh-<number>` and the line runs |
| `repository_dispatch`, type `anvil-work-order` | The work order in `client_payload.work_order` runs (sent by the intake worker) |
| A comment `/anvil approve` by an owner, member or collaborator | The approval is recorded and the line resumes (`/anvil approve --override` for a verdict the line did not approve) |
| `workflow_dispatch` with an issue number | Manual run or resume |

Labels on the issue carry the structured part: a kind (`bug`, `feature`,
`task`, `incident`, `idea`, `content`; default feature), risk hints (`auth`
or `risk:auth`, and so on) and `pipeline:<name>` (default: the project's
`anvil.json` pipeline).

The job pushes branch `anvil/<work-order-id>`, opens a draft pull request,
marks it ready when the line approves, comments the report on the issue, and
fails when the line did not approve. Setup, once per repository:

- Create the `anvil` label.
- Secret `CF_AIG_TOKEN` (the gateway credential), as before.
- Settings, Actions, General: allow GitHub Actions to create pull requests.
  Or set secret `ANVIL_PAT` (contents and pull requests write): GitHub does
  not start workflows for what `GITHUB_TOKEN` pushes, so only with the PAT
  does the repository CI run on the line's pull request.
- Optional variable `ANVIL_AUTO_MERGE=true` to squash merge an approved pull
  request. Off by default: merging stays the owner's act.

Applying the `anvil` label needs triage rights, and that is the access
control: the text of an arbitrary issue never starts a run. Issue text is read
from the event file and reaches stations through the sanitized packet, never
through a shell.

### Isolation

`--isolate` (on `run`, `approve` and `resume`) gives the order branch
`anvil/<work-order-id>` in a git worktree beside the project
(`../.anvil-worktrees/<project>/<id>`) and commits the result there with the
run evidence. The checkout you work in is not edited, and uncommitted changes
in it are not carried over. This is a branch and a worktree, not a sandbox:
the station runtimes still run with their permission prompts bypassed, so run
executed lines on a machine you can throw away, as the workflow does.

### Red before green

With project `checks` configured, the checks run once after the test-writer
and before the builder. The result is recorded on the test-writer step as
`red_check`. When the checks pass there, the new tests did not fail first: the
report warns and reviewer-tests is told to verify they exercise the new
behavior.

### Not done here

Reviewers still run one after another. The reviewer tree guard compares the
whole working tree, so concurrent reviewers in one tree would fail each other;
parallel execution needs a tree per reviewer first.
