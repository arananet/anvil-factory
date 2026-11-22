# Live Progress Sinks: a Run Seen While It Runs, on GitHub First

Status: proposed
Slug: live-progress-sinks
Work order: wo-gh-47 (https://github.com/arananet/anvil-factory/issues/47)
Base ref: factory main 10168fa560af7284b23f99e4e639621cf47eacd2 (anvil.yaml carries max_run_tokens 15000000, max_runtime_turns 100, max_packet_tokens 48000 and the wo-gh-42 station partitions; anvil.json wires the checks command `python -m unittest discover -s tests -p 'test_*.py'`).

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

A run of the line cannot be watched. state.json is rewritten before every station and report.json is checkpointed after every station (wo-gh-41), but both stay on the disk of the machine that runs the line until the run ends. The five runs of wo-gh-41 on 2026-11-20 and the run of wo-gh-42 on 2026-11-21 each showed only "In progress" for 5 to 27 minutes, and nobody could tell from outside what the line was doing. The existing export (observability.events_url, observability.otlp_endpoint) needs a receiver someone must build and host. Owner direction of 2026-11-21: no dependence on one vendor, and a person who copies ANVIL sees their runs without standing anything up. Every work order is already a GitHub issue and every run already holds a token that can write to it. This order adds progress sinks: consumers of the run state record, called each time the state is rewritten. Two ship: github-issue (one live comment on the work order's issue, on by default) and github-project (a card on a GitHub Projects board, documented and off).

## Terms
- State record: the JSON object of schema anvil/run-state@1 that anvil/observe.py `RunRecorder.state` writes to runs/<wo>/state.json and that `mark_crashed` rewrites.
- State write: one rewrite of state.json by `RunRecorder.state` or by `mark_crashed`.
- Pipeline order: the flat list of station ids the runner executes for the run (the runner's `order`, parallel groups flattened in their listed order).
- Sink note: a string recorded for a sink, of the form `<type>: <reason>`.

## Requirements

### R1. Sinks receive the run state

- R1.1 Configuration. anvil.yaml accepts `observability.sinks`, an ordered list. Each entry is an object with a `type` key whose value is `github-issue` or `github-project`, plus only the keys R2.1 or R3.1 allow for that type. When the configuration for a run is loaded and `observability.sinks` is present, then: if it is not a list, loading raises ValueError whose message contains `observability.sinks`; if an entry is not an object, has a missing or unknown `type`, lacks a required key, carries a key its type does not allow, or has a value of the wrong type or outside the allowed set, loading raises ValueError whose message contains `observability.sinks[<index>]` (zero based) and the offending key or type. Validation lives in anvil/config.py. An absent `observability.sinks` or an empty list is valid and means no sink.
- R1.2 Call points. Every configured, active sink is called once per state write with that state record: the write at run start (run.started or run.resumed), the write before each station, the write after the last station, the `finished` write, and the `crashed` write made by `mark_crashed` (uncaught error or signal). Early stops (budget_exceeded, station_timeout, turn_limit, runtime_refused and any other exit status) reach the `finished` write and so call the sinks there.
- R1.3 Order of call and write. For each state write the recorder builds the record, calls the sinks in list order, then writes state.json with `export_errors` and `sinks` (R1.6) as they stand after those calls. Exactly one file write happens per state write, as today.
- R1.4 Additive state fields. The state record gains, and only gains, these fields (existing fields keep their names, types and meaning):
  - `stations`: the pipeline order (list of station id strings), present on every write.
  - in each element of `steps`: `total_tokens`, the value `summarize_steps([step])["total_tokens"]` from anvil/telemetry.py (an integer, or null when unmeasured).
  - `exit_status`: on the `finished` write, the report's `exit_status`; on the `crashed` write, the `exit_status` of runs/<wo>/report.json when that file holds one, otherwise absent.
  - `sinks`: a list with one object per configured sink, `{"type": <type>, "active": true|false, "reason": <string or null>}`, in list order.
- R1.5 Failures never decide a run. A sink call that raises, exceeds the timeout, or receives an HTTP status of 400 or higher is caught in the line process; one sink note is appended to `export_errors` when not already present, of the form `<type>: <ExceptionClassName>` or `<type>: HTTP <status>`. Exception messages, URLs and response bodies are never recorded. The verdict, report.json, events.jsonl, the webhook POSTs and the OTLP trace are byte for byte what they would be without the sink, apart from the `updated_at` and `ts` timestamps.
- R1.6 Inactive sinks. A sink that is inactive for a run (R2.2, R3.5) makes no network call and has `active: false` and a fixed reason string in its `sinks` element; the reason is not written to `export_errors`. The reason is set at its first call and not repeated or changed later.
- R1.7 Timeout. Every HTTP request a sink makes is given `observability.timeout_seconds` as its timeout (default 5, the value the recorder already uses).
- R1.8 No sinks, no calls. With `observability.sinks` absent or empty, the run makes no network call it did not make before this change, and state.json carries `sinks: []`.
- R1.9 Events unchanged. No event kind is added, removed or reordered; events.jsonl, the webhook payloads and the OTLP spans are unchanged.
- R1.10 Placement. Sink code lives in a new module beside anvil/observe.py (anvil/sinks.py). anvil/observe.py calls it. anvil/runner.py changes only at the `RunRecorder(...)` construction (to pass the pipeline order) and contains no new network code, no `urllib` import and the word "retry" nowhere. `mark_crashed` keeps its signature `mark_crashed(run_dir, error)`; it reads the observability configuration from `<run_dir>/../../anvil.yaml` and the pipeline order from the `stations` field of the record it rewrites.

### R2. The github-issue sink

- R2.1 Entry. `{"type": "github-issue"}`; optional `token_env` (non-empty string, default `GH_TOKEN`). No other key is allowed.
- R2.2 Activation. The sink is active only when all of: the work order id matches `^wo-gh-([0-9]+)$`; the environment variable `GITHUB_REPOSITORY` is set and of the form `<owner>/<repo>`; the variable named by `token_env` is set and non-empty. Otherwise it is inactive with exactly one of these reasons, checked in this order: `work order id is not wo-gh-<number>`, `GITHUB_REPOSITORY is not set`, `<token_env> is not set` (the variable name, never its value).
- R2.3 API base. The base URL is `GITHUB_API_URL` when set, otherwise `https://api.github.com`. Requests carry `Authorization: Bearer <token>`, `Accept: application/vnd.github+json` and a `User-Agent` of `anvil-progress`.
- R2.4 One comment per run id. The comment body begins with the line `<!-- anvil-progress run_id=<run_id> -->`. On its first call in a process the sink lists the issue's comments (`GET {base}/repos/{repo}/issues/{n}/comments?per_page=100`, following `Link: rel="next"`) and adopts the first comment whose body contains that marker. If none is found it creates one (`POST {base}/repos/{repo}/issues/{n}/comments`). Every later call edits that comment (`PATCH {base}/repos/{repo}/issues/comments/{id}`). A run, including a resumed run or the `crashed` write from a fresh process, never leaves more than one comment carrying its marker.
- R2.5 Content. After the marker the body is Markdown with:
  - a heading `ANVIL progress: <work_order_id>`;
  - lines `Pipeline: <pipeline>`, `State: <state>` (the record's `state` value verbatim: running, finished, crashed, stalled or any other), and once present `Verdict: <verdict>` and `Exit status: <exit_status>` (both verbatim; the sink holds no list of allowed values);
  - a table with header `| Station | Status | Attempt | Tokens |` and one row per station in `stations` order. Status per station: `running` when the record's state is running and the station equals `current_station`; otherwise taken from the latest step of that station whose status is not `loopback`: `executed` shows `done`, `not_run` shows `not run`, `failed` and `skipped` show as is, any other status shows verbatim; with no such step, `pending` while state is running, `not run` otherwise. Attempt is the highest `attempt` among that station's steps, or `-`. Tokens is the sum of that station's steps' `total_tokens`, or `-` when none is measured;
  - lines `Loopbacks: <loopbacks>`, `Tokens: <token_usage.total_tokens or "unmeasured">`, `Cost: $<cost to 4 decimals>` or `Cost: not priced` when `cost` is null, `Updated: <updated_at>`;
  - `Workflow run: <GITHUB_SERVER_URL or https://github.com>/<GITHUB_REPOSITORY>/actions/runs/<GITHUB_RUN_ID>` only when `GITHUB_RUN_ID` is set.
- R2.6 Scalar facts only. The body contains no prompt, no station output or detail text, no `error` text of a crashed record, no file system path, no environment variable value other than GITHUB_REPOSITORY, GITHUB_SERVER_URL and GITHUB_RUN_ID, and no token value.

### R3. The github-project sink

- R3.1 Entry. `{"type": "github-project", "owner": <non-empty string>, "number": <positive integer, not boolean>}`; optional `owner_type` (`user` or `organization`, default `user`), `status_field` (non-empty string, default `Status`), `token_env` (non-empty string, default `GH_TOKEN`), `columns` (object whose keys are phase names from R3.2 and whose values are non-empty strings). Any other key, or a `columns` key that is not a phase, fails loading per R1.1.
- R3.2 Phases and default option names: intake `Intake`, spec `Spec`, build `Build`, checks `Checks`, review `Review`, human `Needs human`, done `Done`, failed `Failed`. `columns` overrides the option name per phase.
- R3.3 Phase of a record. While state is running: the phase of `current_station`, or when it is null the phase of the station of the last step, or `intake` when there is no step. Station to phase: intake to intake; spec-writer to spec; test-writer and builder to build; checks-gate to checks; every station whose id starts with `reviewer-`, and approver, to review; triage-human to human; deployer and observer leave the phase unchanged; any other station to build. When state is not running: `failed` if state is crashed or stalled, or `exit_status` is present and not `completed`; else `human` if `human_required` is true; else `done` if verdict is `approved`; else `failed`.
- R3.4 Status changes. The sink sends a status change (GraphQL `updateProjectV2ItemFieldValue` with the option's id) only when the phase differs from the phase it last set in this process; the first active call always sets it. Before the first change it finds the issue's item in the project; when the issue is not in the project it adds it (`addProjectV2ItemById`). The GraphQL endpoint is `GITHUB_GRAPHQL_URL` when set, otherwise `<GITHUB_API_URL or https://api.github.com>/graphql`. The issue is resolved from GITHUB_REPOSITORY and the wo-gh number, with the same activation rules as R2.2.
- R3.5 Never alters the project's shape. The sink creates, renames or deletes no project, field or option. A project, status field or option it cannot find is recorded in `export_errors` as `github-project: project <owner>/<number> not found`, `github-project: field <status_field> not found` or `github-project: option <name> not found in <status_field>`, and the sink is inactive for the rest of the run (no further request), with that same text as its `sinks` reason.
- R3.6 Token. The default workflow token cannot reach Projects; `token_env` names a variable holding one that can. When that variable is unset or empty the sink is inactive with reason `<token_env> is not set`.

### R4. What ships enabled

- R4.1 The factory's own anvil.yaml carries `"observability": {"sinks": [{"type": "github-issue"}]}`, merged with any observability keys it already has.
- R4.2 The configuration the scaffold writes for a new project (`anvil init`, through `render_anvil_yaml`) carries the same github-issue entry.
- R4.3 The github-project sink is documented in docs/OPERATIONS.md (entry keys, phases, defaults, the token requirement and R5.3) and enabled nowhere.
- R4.4 The final "ANVIL line report" comment (tools/line_comment.py and the workflow step that posts it) is unchanged.
- R4.5 README.md gains one section of at most 15 lines titled "Watching a run" that names the live comment and links docs/OPERATIONS.md. docs/EXECUTION.md states where sinks are called in a run. CHANGELOG.md gains one entry. One decision record brain/decisions/0015-live-progress-sinks.md states the choice of state fed sinks over a new event, GitHub as the zero setup default, and what it makes harder (API rate use: about one request per state write).

### R5. Tokens stay where they are

- R5.1 Sinks run in the line process and read their token from its environment at call time. The token is held in no attribute that is serialized and is passed only as the Authorization header.
- R5.2 No token value appears in state.json, events.jsonl, report.json, any other file under runs/<wo>/, a comment body, a GraphQL request body, or an export error.
- R5.3 Loading fails (ValueError naming `observability.sinks[<index>]` and `token_env`) when a sink's `token_env` would reach a station: that is, when it is in `runtime.env_keep`, or is neither in `STATION_ENV_DENY` of anvil/executor.py nor in `runtime.env_deny`. GH_TOKEN, the default, is already denied. The station environment reduction itself is unchanged.

### R6. Regression tests

- R6.1 New test files under tests/ only (for example tests/test_live_progress_sinks.py and tests/test_live_progress_project_sink.py), using a local HTTP collector on 127.0.0.1 in the manner of tests/test_governed_delivery.py, with `GITHUB_API_URL` (and `GITHUB_GRAPHQL_URL` for the project sink) pointed at the collector, so no test reaches a real GitHub host. Each item (a) to (h) of S1 to S8 and S9 is covered by at least one test whose docstring names the scenario id.
- R6.2 Tests that assert facts about this order's own run (paths it changed, its builder report, a comparison against the base ref) skip unless `ANVIL_WORK_ORDER_ID` is `wo-gh-47`.
- R6.3 The full factory suite (`python -m unittest discover -s tests -p 'test_*.py'`) passes with no existing test file modified or deleted.

## Scenarios

- S1 (R1.2, R1.3, R2.4, R2.5; test a): Given a scripted run of wo-gh-901 on the sdlc-default pipeline with `observability.sinks: [{"type": "github-issue"}]`, GITHUB_REPOSITORY `acme/demo`, GH_TOKEN set and GITHUB_API_URL at the collector, when the run finishes with verdict approved, then the collector received exactly one POST to `/repos/acme/demo/issues/901/comments`, every later write was a PATCH to `/repos/acme/demo/issues/comments/<that id>`, the number of POST plus PATCH requests equals the number of state writes, and the last PATCH body starts with `<!-- anvil-progress run_id=<run_id> -->`, contains `Verdict: approved`, `State: finished` and a `done` row for every station that executed.
- S2 (R1.2, R1.4, R2.5; test b): Given the run of S1, the PATCH sent by the state write before the builder shows `| builder | running |`, shows intake, spec-writer and test-writer as `done`, and shows checks-gate, every reviewer and approver as `pending`; the state.json copied at that moment carries `stations` equal to the pipeline order and a `total_tokens` key on every step.
- S3 (R1.5, R1.7, R1.9, R6.1; test c): Given the S1 run with the collector answering HTTP 500 to every request, then the verdict and report.json (ignoring timestamps) equal those of the same run with no sink, events.jsonl has the same event kinds in the same order, and state.json `export_errors` equals `["github-issue: HTTP 500"]`. Given GITHUB_API_URL `http://127.0.0.1:9` (nothing listening), the same holds with exactly one `github-issue: ...` entry. Given a collector that accepts the connection and never answers, with `timeout_seconds: 1`, each sink request returns control within 2 seconds and `export_errors` holds exactly one `github-issue: ...` entry.
- S4 (R2.2, R1.6; test d): Given work order id `wo-s4` with the sink configured, the collector receives zero requests and state.json `sinks` equals `[{"type": "github-issue", "active": false, "reason": "work order id is not wo-gh-<number>"}]`, with `export_errors` unchanged. Given wo-gh-902 with GH_TOKEN unset, zero requests and reason `GH_TOKEN is not set`.
- S5 (R3.2, R3.3, R3.4; test e): Given a collector that serves a project with a Status field holding the eight default options and an issue not yet in the project, when a run moves intake, spec-writer, test-writer, builder, checks-gate, reviewers, approver and finishes with human_required true, then the collector receives one `addProjectV2ItemById` request, then `updateProjectV2ItemFieldValue` requests whose option ids correspond, in order, to Intake, Spec, Build, Checks, Review, Needs human, and no status request for the write before builder (phase still build).
- S6 (R3.5; test e): Given the project of S5 without the option `Review`, when the run reaches reviewer-spec, then `export_errors` contains `github-project: option Review not found in Status`, the collector receives no further request after that lookup, no request creates or edits a field or option, and the verdict equals that of S5.
- S7 (R1.8; test f): Given a scaffolded project whose anvil.yaml has `observability.sinks` removed, when a wo-gh-903 run finishes with GH_TOKEN and GITHUB_REPOSITORY set and GITHUB_API_URL at the collector, the collector receives zero requests and state.json carries `sinks: []`.
- S8 (R1.1, R3.1, R5.3; test g): Loading an anvil.yaml whose sinks are `[{"type": "github-issue"}, {"type": "github-project", "owner": "acme"}]` raises ValueError containing `observability.sinks[1]` and `number`; `[{"type": "slack"}]` raises naming `observability.sinks[0]` and `slack`; `{"type": "github-issue"}` (not a list) raises naming `observability.sinks`; a github-issue entry with `token_env: "MY_PROJECT_TOKEN"` not in any deny list raises naming `token_env`, and passes once `runtime.env_deny` lists it.
- S9 (R5.1, R5.2; test h): Given GH_TOKEN `ghs_SENTINEL_47_0123456789` and the S1 run, the sentinel appears in the Authorization header of the collector's requests and in no request body, and in no file under runs/wo-gh-901/ (state.json, events.jsonl, report.json and every other file).
- S10 (R1.2, R1.4, R2.5): Given a run whose runner stops with exit_status `runtime_refused`, the last PATCH shows `State: finished` and `Exit status: runtime_refused`, and stations after the stop show `not run`; given a record with exit_status `some_future_status`, the rendered body shows `Exit status: some_future_status`.
- S11 (R1.2, R1.10, R2.4): Given a run where a station raises an uncaught error, the `crashed` write from `mark_crashed` sends a PATCH (not a POST) to the same comment id, whose body shows `State: crashed` and does not contain the exception message.
- S12 (R4.1, R4.2, R4.3): The factory anvil.yaml parsed as JSON has an `observability.sinks` list containing `{"type": "github-issue"}` and no github-project entry; a project created by `anvil init` in a temp directory has the same; docs/OPERATIONS.md contains `github-project`, `status_field` and `Needs human`.
- S13 (R1.10, R4.4, R6.2, R6.3): anvil/runner.py at the end of the run contains no `urllib`, no `http.client` and no `retry`; `git diff 10168fa560af7284b23f99e4e639621cf47eacd2 -- tools/line_comment.py .github/workflows pipelines anvil.json anvil/executor.py` is empty, and no existing test file differs (this check skips unless ANVIL_WORK_ORDER_ID is wo-gh-47, per R6.2).
- S14 (R4.5): README.md has a "Watching a run" section of at most 15 lines; brain/decisions/0015-live-progress-sinks.md exists; CHANGELOG.md names live-progress-sinks; no produced file contains U+2014 or U+2013.

- S15 (R2.3, R2.6): In the S1 run with GITHUB_RUN_ID `4242` and GITHUB_SERVER_URL `https://github.example`, every request path starts with the collector base given as GITHUB_API_URL, carries `Accept: application/vnd.github+json` and `User-Agent: anvil-progress`, and the last body contains `Workflow run: https://github.example/acme/demo/actions/runs/4242`; no body contains the project's directory path, any station's `detail` text, or the text of any packet or station output.
- S16 (R3.6, R1.6): Given `{"type": "github-project", "owner": "acme", "number": 3, "token_env": "ANVIL_PROJECTS_TOKEN"}` listed in `runtime.env_deny` and ANVIL_PROJECTS_TOKEN unset, the collector receives zero GraphQL requests and the sink's `sinks` element has reason `ANVIL_PROJECTS_TOKEN is not set`.

## Out of scope
- Any sink other than github-issue and github-project; a plugin registry for sinks.
- Retrying failed sink calls, rate limit handling beyond recording the failure, batching or throttling writes.
- Changing the events contract, the webhook, the OTLP trace, the final line report comment, the station environment reduction, or any existing state field.
- Creating or reshaping GitHub Projects, fields or options; wiring a Projects token into the workflow.
- Merging, publishing or deploying anything; the run stops at the owner human gate.

## Allowed write set
- anvil/observe.py; anvil/sinks.py (new); anvil/config.py (validation of observability.sinks and the scaffold default in `build_default_config`/`render_anvil_yaml`); anvil/scaffold.py (only if the default cannot live in config.py); anvil.yaml (the sink entry only); anvil/runner.py (only the `RunRecorder(...)` construction, to pass the pipeline order).
- docs/OPERATIONS.md, docs/EXECUTION.md, README.md (one section), CHANGELOG.md, brain/decisions/0015-live-progress-sinks.md (new).
- New test files under tests/.
- Run artifacts under runs/wo-gh-47/ written by the line itself.

Not touched: .github/workflows/*, pipelines/*, anvil.json, anvil/executor.py, tools/line_comment.py, every test file present at the base ref. Python standard library only. No em dash or en dash character in any produced file.

## Builder report
The builder report contains in full: `10168fa560af7284b23f99e4e639621cf47eacd2`, `live-progress-sinks`, `github-issue`, `github-project`; the base ref it verified the tree against; the exact full factory test count from the suite run; and the names of the new test files.

## Reconciliation with active specs and existing tests
- governed-delivery owns state.json, events.jsonl, the webhook and the OTLP trace; this spec only adds state fields (R1.4) and consumers. tests/test_governed_delivery.py compares webhook events with events.jsonl and counts station.finished and loopback events against the report's steps: R1.9 keeps both true. Its export tests replace the whole `observability` object, so the scaffold default sink is absent there; and because inactive reasons go to `sinks`, not `export_errors` (R1.6), any scaffolded run without GitHub variables keeps `export_errors: []`.
- tests/test_review_producer.py: no "retry" in anvil/runner.py (R1.10).
- tests/test_continuous_run_accounting.py (wo-gh-41): report.json is not touched by sinks (R1.5).
- wo-gh-42 efficiency keys and these observability keys do not overlap.
- runtime_refused and any future exit status are shown verbatim (R2.5, S10).
