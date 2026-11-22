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
- If the station is killed at its timeout (see Station timeout below), the
  step status is `timed_out` instead, with a `timeout` record and the
  dispatched model as `executed_model`.
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
{"runtime": {"kind": "command", "command": "my-agent --packet {packet} --out {output}", "timeout_seconds": 900}}
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
and runs it through `tools/claude_station.py` (Claude Code print mode). There
is one runtime: every station, the design stations included, runs an Anthropic
model (`claude-sonnet-5-5` or `claude-opus-5-5`); the OpenAI route and the
Codex wrapper were removed (decision 0008). Producing stations may write;
reviewing and observing stations run without edit tools. Any other model
fails the step; there is no fallback runtime.

Claude returns a JSON result. The wrapper extracts
the answer for the existing artifact contract and keep scalar token evidence
in `<station>.output.md.usage.json`. Raw runtime JSON, prompts and environment
variables are not exported to the public usage pages. Each invocation of a
station is an agent call; its runtime may perform several model/tool turns.

### Station timeout

Every station invocation runs under a wall clock timeout enforced by the
station wrapper (`tools/claude_station.py`). It is configuration, resolved in
this order (decision 0011, spec station-timeout):

1. the environment variable `ANVIL_STATION_TIMEOUT_SECONDS`;
2. `runtime.station_timeout_seconds` in the project `anvil.yaml`, which the
   command executor hands to the wrapper through that same variable, like
   `ANVIL_RUNTIME` and `ANVIL_MAX_RUNTIME_TURNS`;
3. the station class default: 3600 seconds for the producing stations
   (builder, test-writer, spec-writer, blueprint, brief-writer, researcher,
   writer, media-producer), 1500 seconds for every other station.

The hard ceiling is 7200 seconds. A configured value above it is clamped to
7200 and the wrapper says so on stderr, so a runaway station still dies. A
value that is not a positive whole number of seconds is rejected with the
value named: the command executor refuses to start, and the wrapper, when it
meets such a value, exits 10 so the step fails. The timeout bounds the
whole invocation, including a reviewer's one correction attempt.

The command executor timeout (`runtime.timeout_seconds`, default 300) is
raised automatically to the largest station timeout in effect plus 60
seconds, so the wrapper is always the binding cap and writes its record
before the executor would kill it. The factory `anvil.yaml` sets
`runtime.timeout_seconds` to 7200, and the anvil-line job allows 360 minutes.

A station killed at its timeout records what is knowable. The attempt in
`<station>.output.md.usage.json` has status `timed_out`, `station`,
`duration_ms` (the elapsed time measured around the call),
`timeout_seconds`, `reason` (the configured value and where it came from),
`configured_model`, and the partial usage the runtime printed before the
kill, or `usage_complete: false` with a `usage_reason` when it printed none.
The run record step has status `timed_out`, `executed_model` set to the
dispatched model, and a `timeout` object with the station, source, timeout
value, elapsed milliseconds and reason. A station that finishes within its
timeout records exactly what it did before.

The `efficiency` settings bound packet context for all agent stations and
stop new calls after run thresholds are reached. The final report records
`budget_exceeded` when further work is prevented; it does not grant approval.
Executed runs refresh `status/index.html`. Rerunning the same work order
archives its previous report under `runs/<id>/history/`, so earlier tokens
are still counted. The archive is taken before the new run writes anything,
so a killed run's record is never overwritten.

### Continuous run accounting

`runs/<id>/report.json` is written while the run goes, not only at its end
(spec continuous-run-accounting, decision 0013):

- After every station (completed, failed, timed out or skipped) the runner
  writes a checkpoint: the report in its final shape plus a `checkpoint`
  object with `last_completed_station`, `elapsed_ms` and `usage_so_far`
  (the measured usage summed over the steps so far). Every write goes to a
  sibling temporary file renamed over report.json, so a reader always sees a
  whole record. A write that fails leaves the previous record in place and
  says why on stderr. Checkpointing adds no station and no model call.
- Every exit path completes the record with `exit_status` and
  `termination_reason`. The exit statuses are `completed` (the line ran to its
  end), `budget_exceeded` (a run threshold, the run token cap crossed by a
  station, or a packet limit), `station_timeout`, `turn_limit` (the runtime's
  `error_max_turns`), `checks_stopped` (a failed pre-review gate with no
  attempt left, or a failed pre-deploy gate), `intake_stopped` (rejected,
  waiting_info, or a knowledge pack that does not load), `runtime_refused`
  (the model runtime answered a station with HTTP 401, 402 or 403: bad
  credentials, no billing balance or no access), `error` (an uncaught
  exception: its type and message) and `signal` (`SIGTERM` or `SIGINT`).
- A budget death, a station timeout, the turn limit, a runtime refusal and a
  checks gate stop end the line at that station: no later station runs. Every pipeline station is
  named once in `steps`; one that never ran has status `not_run`, and one in
  flight when an error or signal ended the run is recorded with
  `in_flight: true`.
- A budget death carries `budget_death`: the `limit` that stopped the run,
  `measured_tokens` (the run's measured consumption), `max_run_tokens`,
  `station_in_flight` and that station's `station_usage` (or
  `station_usage_reason` when the runtime exposed none).
- The cost section keeps cost-measurement semantics: the total is the sum of
  measured steps.

A killed run needs no second run for its paperwork: `tools/line_comment.py`
and `anvil.runner.render_swimlane(report)` render it from report.json alone,
and `anvil resume` names its exit status instead of resuming. For SIGKILL or a
lost host the last checkpoint is the record. Reports written before this
change carry none of these keys and render as before.

### Live progress sinks

The sinks in `observability.sinks` (spec live-progress-sinks, decision 0015,
configuration in [OPERATIONS.md](OPERATIONS.md)) are called by the recorder
in `anvil/observe.py` at every state write, with the state record, before
`state.json` is written:

- at run start (`run.started`; a resumed run writes its first state before
  its first station, a moment later);
- before each station, with that station as `current_station`;
- after the last station, and at the `finished` write, which carries the
  report's `exit_status` for every exit path that reaches it (budget,
  timeout, turn limit, runtime refusal, checks or intake stop, completed);
- at the `crashed` write of `mark_crashed` (an uncaught error or a signal),
  which reads the configuration from the project's `anvil.yaml`.

The state record gains `stations` (the pipeline order), `total_tokens` per
step, `exit_status` and `sinks`. No event is added: events.jsonl, the
webhook and the OTLP trace are unchanged, and a sink failure is an
`export_errors` entry, never a verdict. The sink code is `anvil/sinks.py`;
the runner only hands the recorder its pipeline order.

### Per-station token budgets and the completeness gate

The run cap `efficiency.max_run_tokens` is one shared pool. Per-station
partitions divide it so one station cannot use it all up (spec
station-budgets-completeness, decision 0014). There are two keys in the
`efficiency` section of `anvil.yaml`:

- `efficiency.station_budgets`: a map from station id to the tokens that
  station may consume across one run, summed over all of its dispatches.
- `efficiency.default_station_budget`: the partition for a model station the
  map does not name. When it is absent, an unnamed station has no partition
  and is bounded only by `max_run_tokens`. Deterministic stages such as
  `checks-gate` make no model call and take no partition.

These keys are a different quantity from the top level `station_budgets` key
(astra-consumption, read by `anvil.config.get_station_budget`). The top level
`station_budgets` caps the packet tokens a station is sent in one packet. The
efficiency keys `efficiency.station_budgets` and
`efficiency.default_station_budget` cap what a station consumes over the run.
Each keeps its own place and behaviour.

Load time validation: before any station runs, the runner computes each
pipeline's worst case. That is the sum of the named partitions of its
stations, plus the default for each unnamed model station. A worst case above
`max_run_tokens` fails to load, naming the pipeline and the excess. A worst
case equal to the cap loads. `anvil.config.validate_station_budgets(config,
pipelines, registry)` runs the same check for any set of pipelines. The
factory's own `anvil.yaml` ships sdlc-default partitions that sum to exactly
15000000, the run cap, so no default partition is set:

| station | partition |
|---|---|
| intake | 200000 |
| spec-writer | 1200000 |
| test-writer | 3200000 |
| builder | 5800000 |
| reviewer-spec, reviewer-security, reviewer-tests, reviewer-architecture, reviewer-design, reviewer-ux | 600000 each |
| approver | 200000 |
| triage-human | 100000 |
| deployer | 300000 |
| observer | 400000 |

The pre-call check: the spine checks every dispatch of a partitioned station
before it is made. That covers the first attempt and a loopback re-dispatch
in the runner, and a reviewer's in-session correction re-dispatch in the
wrapper. The check sums the station's consumption for this run from the
per-attempt usage records the token-efficiency capability writes. A station
whose measured consumption has reached its partition is refused. Usage that
was never measured is not counted as zero. With `require_usage` set, a
station with an unmeasured earlier call counts as exhausted until it is
measured. Without it, the dispatch proceeds and the check records
`proceeded_unmeasured`. A refusal makes no model call. It is recorded as a
budget outcome (station, partition, consumed, `refused_at`) and ends the run
through the continuous run accounting exit path: `exit_status`
`budget_exceeded`, a `termination_reason` naming the station and its
partition, and unreached stations recorded as `not_run`.

The in-flight ceiling: the runner hands the wrapper what is left of the
station's partition (`ANVIL_STATION_BUDGET_TOKENS`, with the partition itself
in `ANVIL_STATION_PARTITION`). With a ceiling set, the wrapper runs Claude
Code with `--output-format stream-json --verbose`. It sums the usage each
model call reports while the session runs, and kills the session once that
reaches the ceiling, in the same way it kills a session at its station
timeout. The attempt in `<station>.output.md.usage.json` has status
`budget_exceeded`, `station`, `duration_ms`, `partition`, `reason` (the limit
reached), `configured_model` and the partial usage. The run record step has
status `budget_exceeded`, the dispatched model as `executed_model` and a
`budget_ceiling` object. The undone work is not resumed in that dispatch, and
the run ends through the same exit path. The copilot runtime reports usage
only when a session ends, so it gets the pre-call check but no in-flight
ceiling, and the wrapper says so on stderr. The station timeout keys are
unchanged: timeouts partition wall clock time, these keys partition tokens.

The run report carries `budgets`: `stations` (each partitioned station with
`partition`, `consumed` (null when unmeasured), `measured_tokens` and `calls`)
and `outcomes` (`refused`, `budget_exceeded`, `proceeded_unmeasured`). Its
cost section gains `cost.stations`, which gives each partitioned station's
`partition`, `consumed`, `amount`, `priced` and `source`. A station is priced
only when the recorded price table covers every measured call. The amount is
labelled as priced from that table, an estimate and never an invoice. Any
other station shows tokens only and stays unmeasured in money. The cost total
keeps cost-measurement semantics.

The completeness precondition: in a project that configures partitions, the
runner evaluates a deterministic completeness precondition after the builder
and the pre-review checks gate, before any reviewer is dispatched. It needs
all of the following:

- the builder report `runs/<id>/builder.output.md` exists and is non-empty;
- the test-writer's test files (the files its dispatch changed) exist and are
  non-empty;
- the attempt's delta file list is not empty;
- the checks gate verdict for the attempt is `pass` (the verdict as the gate
  decided it, artifact validation included);
- no station the pipeline runs before the gate is recorded failed, timed out
  or budget exceeded without its artifact.

A failed precondition sends the named gaps back to the builder as a gate
loopback. That loopback counts against `max_loopbacks` exactly as a checks
failure does, and no reviewer is dispatched for the attempt. With no loopback
left, the run stops with `checks_stopped` and a reason naming the gaps. Each
evaluation is recorded in the report's own `completeness` list (`attempt`,
`passed`, `gaps`, `gate_verdict`), never in the gate's step. The precondition
reads verdicts and artifacts that already exist. It runs no command, does not
re-run the project suite, does not repeat the artifact contract's literal
validation and does not change the gate. A project without partitions keeps
the review flow it had (decision 0014).

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

## Choosing the runtime: the gateway or GitHub Copilot

Spec: `.openspec/specs/runtime-selection/spec.md`. Tests: `tests/test_runtime_selection.py`.

One variable, `ANVIL_RUNTIME`, chooses how the stations reach their models:

| Value | Runtime | Credential |
|---|---|---|
| `claude-gateway` (default) | Claude Code print mode through the Cloudflare AI Gateway | `CF_AIG_TOKEN`, as before |
| `copilot` | GitHub Copilot CLI with the Anthropic models of a GitHub account | `COPILOT_GITHUB_TOKEN` |

```bash
ANVIL_RUNTIME=copilot python3 -m anvil.cli run . --pipeline pipelines/sdlc-default.json --work-order work-order.json --execute
```

- In the workflow, set the repository variable `ANVIL_RUNTIME`. For `copilot`
  add the secret `COPILOT_GITHUB_TOKEN`: a fine-grained personal access token
  of an account with a Copilot plan, with the Copilot Requests permission and
  nothing else. On a workstation a stored `copilot login` works without it.
- A project can set its default in `anvil.yaml` with `"provider": "copilot"`
  inside `runtime`; the variable wins over it.
- The models are the same Anthropic models. Copilot writes versions with a
  dot, so `claude-opus-5-5` is requested as `claude-opus-5.5`. If your plan
  lists a model under another name, state it:
  `"copilot_models": {"claude-opus-5-5": "<name in copilot /model>"}` inside
  `runtime`, or the variable `ANVIL_COPILOT_MODELS` with the same JSON.
- The station contract does not change: producing stations may use every
  tool; reviewers and observers may read, run commands and write only inside
  their run directory; the review file is checked and corrected once; a
  missing CLI or a failing run fails the station.
- Token usage comes from the statistics file Copilot writes
  (`--usage-output-file`), kept beside the station output as
  `<station>.output.md.copilot-usage.json`. If that file is missing or not in
  a shape the wrapper recognizes, usage is recorded as unknown.
- `max_runtime_turns` has no Copilot equivalent. Set
  `ANVIL_COPILOT_MAX_AI_CREDITS` to cap a station's session in AI credits.

What was verified and what was not: the command line was checked against
the real Copilot CLI (version 1.0.109), which accepted every flag and stopped
at authentication. No authenticated run was made, so two things wait for your
first run: that your plan serves the two models under the dotted names, and
that the usage file has the per model shape the wrapper reads.

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

Reviewers still run one after another. With a single runtime nothing in the
wrappers prevents concurrent reviewers any more; what remains is in the
runner, which checks the run thresholds between calls and hands per call
limits through shared executor state.
