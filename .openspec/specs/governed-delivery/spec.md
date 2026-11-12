# Governed Delivery: live run state, events, verified approvals, contained stations, previews

Status: implemented
Slug: governed-delivery

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
ANVIL's record of a run was forensic: complete, but written once at the end, in files only a person opening the repository would read. A run that died halfway left no state, nothing could be asked across runs, nothing left the project for the tools a team already watches, an approval was a typed name, and a station ran model written commands holding every token of the job. This spec makes the line operable and governable on the two platforms it deploys to today, Cloudflare and GitHub: what is running is visible while it runs, every station emits a structured event, approvals carry a verified identity and obey a policy, stations and checks never hold deploy or repository credentials, and every work order gets its own preview deployment before review.

Provenance: owner-authored work outside the line (decision 0006, record 0009).

## Requirements

- R1, live state. runs/<id>/state.json is rewritten atomically before every station with state running, the current station, the steps so far, token usage and cost. It ends finished. A run that raises ends crashed with the error class, and the exception still propagates. A state left running and untouched for three hours is reported as stalled.
- R2, events. runs/<id>/events.jsonl gets one JSON line per run boundary (run.started or run.resumed, run.finished, run.crashed), per step (station.finished) and per loopback. Events carry scalar facts only: ids, project, pipeline, station, status, attempt, models, duration, token usage, cost, verdict. No prompt, station output, finding text or file path is in an event.
- R3, export. With observability.events_url in anvil.yaml every event is POSTed as JSON, with a bearer token from the environment variable named by events_token_env. With observability.otlp_endpoint the finished run is POSTed as one OTLP/HTTP JSON trace: a root span for the run and a span per step, with headers from the variable named by otlp_headers_env. A failed export never changes a run; it is recorded in state.json as export_errors.
- R4, fleet view. `anvil runs <project>` lists every run with its state, and summarizes approval rate and loopbacks per pipeline, reviews not passed per reviewer, runs in progress, runs interrupted, tokens and cost. `--json` prints the same as data.
- R5, verified approvals under policy. An approval records an identity: inside GitHub Actions the authenticated actor (verified, and --by must name it), elsewhere the typed name (unverified). The approvals object in anvil.yaml can require a verified identity, list approvers, narrow approvers per risk hint, and list who may override. The policy is read from the operator's checkout, never from the run's worktree. A refused approval records nothing.
- R6, stations and checks hold no deploy credentials. The environment of every station command and every project check has repository, deploy, registry and workflow identity tokens removed (a fixed deny list, extended by runtime.env_deny, relaxed only by runtime.env_keep). Deploy, preview and verify commands, run by the spine, keep the full environment. With runtime.sandbox of kind docker, a station command runs in a container that mounts only the project tree, drops all capabilities, runs as the calling user and receives only the ANVIL hand-offs and the variables named in env_pass.
- R7, a preview per work order. With deploy.preview configured, in execute mode the preview command runs once per attempt after the builder and before the first reviewer, with ANVIL_PREVIEW_NAME (the work order id as lowercase letters, digits and hyphens, at most 28 characters) and ANVIL_PREVIEW_URL (from the url template). Reviewers get the URL in their packet and the report records it. A failed preview warns and does not block review. `anvil preview-cleanup <project> <id>` runs the cleanup command. `anvil provision <project>` runs the one time deploy.provision commands, stopping at the first failure.
- R8, deploy targets in the blueprints. `anvil new-project --deploy-target cloudflare|github` writes the blueprint's deploy, preview, provision and health config into the new project's anvil.yaml with the project's slug filled in. A blueprint without that target is refused.
- R9, GitHub Pages without a build service. tools/deploy_github_pages.py commits a directory to the pages branch: production at the root, previews under previews/<name>/, each kept apart from the other, and cleanup removes one preview. A token is handed to git through its environment, never in a URL or an argument.
- R10, the workflow keeps tokens away from stations. anvil-line.yml persists no credentials in the checkout, sets no repository or deploy token at job level, and removes a closed order's preview.

Guardrails: Python standard library only. The container sandbox confines the filesystem and the credentials, not the network: a station can still reach any host. Prices are not part of this change: cost stays unmeasured until the owner records sourced prices in anvil.yaml.

## Scenarios

### Scenario: A run can be seen while it runs
- S1: Given a run in execute mode, when a station is running, then state.json says running and names that station; when the run ends it says finished; when the run raises it says crashed and the exception propagates; and a running state untouched for three hours is listed as stalled.
- S2: Given a run with a loopback, when it ends, then events.jsonl holds the run boundaries, one event per step and the loopback, and no event carries free text.
- S3: Given an events URL and an OTLP endpoint, when a run ends, then the endpoint received every event with the bearer token and one trace with a span per step; and given an unreachable endpoint, then the run's verdict is unchanged and the failure is in state.json.
- S4: Given finished, crashed and approved runs, when `anvil runs --json` runs, then the summary holds the approval rate per pipeline and names the interrupted run.

### Scenario: Approvals are governed
- S5: Given an approvals policy, when an approval is recorded inside GitHub Actions, then the identity is the verified actor and a --by naming someone else is refused; an actor outside the approvers list, or outside the list of a matched risk hint, is refused; an unverified approval is refused when the policy requires verification; and the policy of the operator's checkout applies even when the worktree's copy was edited.

### Scenario: Stations cannot deploy or push
- S6: Given deploy and repository tokens in the environment, when the line runs, then no station and no project check sees them and the deploy command does; and given a docker sandbox, then the station command is wrapped in a container that mounts only the project and passes only the allowed variables.

### Scenario: Every order has its own preview
- S7: Given a preview configuration, when the line runs with one loopback, then the preview deploys once per attempt before the reviewers under the order's preview name, the reviewers' packets and the report carry the URL, a failing preview only warns, and the cleanup command runs on request.
- S8: Given the static-site blueprint, when a project is created with a deploy target, then anvil.yaml holds that platform's deploy, preview and provision commands with the project slug, and `anvil provision` runs them in order.
- S9: Given a git remote, when the GitHub Pages tool deploys production, a preview, production again and then cleans up, then each lands where R9 says and the others are untouched.
- S10: Given the workflow, then the checkout persists no credentials, no token is set at job level, and a cleanup job removes the preview of a closed anvil pull request.
