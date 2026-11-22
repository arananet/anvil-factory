# Operations: watching, governing and deploying the line

Spec: `.openspec/specs/governed-delivery/spec.md`. Tests: `tests/test_governed_delivery.py`.

This is the operator's page: how to see what the line is doing, who may
approve what, what a station can and cannot reach, and how each work order
gets its own preview on Cloudflare or GitHub Pages.

## Seeing a run while it runs

Every run writes two files next to its report:

- `runs/<id>/state.json` is rewritten before every station. It says
  `running` and names the station in progress, with the steps so far, token
  usage and cost. It ends `finished`. A run that raises ends `crashed` with
  the error class. A state left `running` and untouched for three hours is
  reported as `stalled`: the process was killed without a chance to say so.
- `runs/<id>/events.jsonl` gets one JSON line per run boundary, per step and
  per loopback. Events carry scalar facts only (ids, project, pipeline,
  station, status, attempt, models, duration, tokens, cost, verdict). No
  prompt, station output, finding text or file path is ever in an event, so
  the stream can leave the repository.

```bash
python3 -m anvil.cli runs .          # one line per run, then per pipeline totals
python3 -m anvil.cli runs . --json   # the same as data
```

`runs` answers what is in progress, what was interrupted and where, the
approval rate and loopbacks per pipeline, which reviewer rejects most, and
tokens and cost across runs.

## Watching a run on GitHub: progress sinks

Spec: `.openspec/specs/live-progress-sinks/spec.md`. Decision 0015. Tests:
`tests/test_live_progress_sinks.py`, `tests/test_live_progress_project_sink.py`.

A progress sink receives the state record every time `state.json` is
rewritten: at run start, before each station, after the last station, when
the run finishes (whatever its exit status, `runtime_refused` included) and
when it crashes. Sinks are listed in `anvil.yaml`:

```json
{
  "observability": {
    "sinks": [
      {"type": "github-issue"},
      {"type": "github-project", "owner": "acme", "number": 3, "token_env": "ANVIL_PROJECTS_TOKEN"}
    ],
    "timeout_seconds": 5
  },
  "runtime": {"env_deny": ["ANVIL_PROJECTS_TOKEN"]}
}
```

The list is validated when the configuration loads: an unknown `type`, a
missing required key, a key the type does not allow or a value of the wrong
type fails loading with a message naming `observability.sinks[<index>]` and
the key. No sinks (absent or `[]`) means no extra network call. Every request
is bounded by `timeout_seconds`. A sink that fails (an exception, a timeout,
an HTTP status of 400 or more) is recorded in `state.json` under
`export_errors` as `<type>: HTTP <status>` or `<type>: <ExceptionClass>` and
the line goes on: a sink never decides a run and never changes the report or
the events. `state.json` says per sink whether it is active, and why not,
under `sinks`.

### github-issue (on by default)

`{"type": "github-issue"}`, optional `token_env` (default `GH_TOKEN`). The
factory's `anvil.yaml` and every project made by `anvil init` enable it.

- Active only when the work order id is `wo-gh-<number>`, `GITHUB_REPOSITORY`
  is set and the token variable is set. Otherwise it makes no request and
  `state.json` records the reason once (`work order id is not
  wo-gh-<number>`, `GITHUB_REPOSITORY is not set`, `GH_TOKEN is not set`).
- It creates one comment on the issue at its first call and edits that same
  comment afterwards. The comment starts with a hidden marker carrying the
  run id, so a resumed run or the crash write from a fresh process finds it
  again instead of posting a second one.
- The comment shows the work order, the pipeline, the run state, the verdict
  and exit status once known, a row per station in pipeline order (done,
  running, pending, failed, skipped, not run) with attempt and measured
  tokens, loopbacks, tokens and priced cost so far, the time of the last
  update and, when `GITHUB_RUN_ID` is set, the workflow run link. Scalar
  facts only: no prompt, no station output, no error text, no path, no token.
- The API base is `GITHUB_API_URL` when set (GitHub Enterprise), otherwise
  `https://api.github.com`. Cost in rate limit: about one request per state
  write, plus one listing at the first call.

The final "ANVIL line report" comment of the workflow is unchanged; the
progress comment is a separate one.

### github-project (documented, off)

`{"type": "github-project", "owner": ..., "number": ...}` with optional
`owner_type` (`user` or `organization`, default `user`), `status_field`
(default `Status`), `token_env` (default `GH_TOKEN`) and `columns`.

It sets the status of the issue's item on a GitHub Projects (v2) board when
the run's phase changes, and adds the issue to the project when it is not on
it yet. Phases and the default option names:

| Phase | Stations | Default option |
|---|---|---|
| intake | intake | Intake |
| spec | spec-writer | Spec |
| build | test-writer, builder | Build |
| checks | checks-gate | Checks |
| review | reviewers, approver | Review |
| human | triage-human, or a finished run that needs a human | Needs human |
| done | a finished, approved run | Done |
| failed | a crashed run or any exit status other than completed | Failed |

`columns` renames the option per phase, for example
`{"human": "Waiting on owner", "done": "Shipped"}`.

It never changes the board's shape. A project, status field or option it
cannot find is recorded by name (`github-project: option Review not found in
Status`) and the sink makes no further request for the run. Create the field
and its options yourself.

The workflow's own token cannot reach Projects. `token_env` names a variable
holding a token that can (a fine grained token with Projects read and write,
or a classic one with `project`); the workflow does not wire one in, so
exposing it to the line step is your change. With the variable unset the
sink is inactive and says so once.

### Tokens stay with the line

Sinks run in the line process and read their token from its environment at
call time. The token goes into the `Authorization` header and nowhere else:
not into `state.json`, `events.jsonl`, `report.json`, a comment or an export
error. A sink's `token_env` must not reach a station: loading fails, naming
`observability.sinks[<index>]` and `token_env`, when the variable is in
`runtime.env_keep` or is neither in the engine's denied list (which holds
`GH_TOKEN`) nor in `runtime.env_deny`.

## Sending it to the tools you already watch

In the project `anvil.yaml`:

```json
{
  "observability": {
    "events_url": "https://example.com/hooks/anvil",
    "events_token_env": "ANVIL_EVENTS_TOKEN",
    "otlp_endpoint": "https://otlp.example.com/v1/traces",
    "otlp_headers_env": "ANVIL_OTLP_HEADERS",
    "timeout_seconds": 5
  }
}
```

- `events_url`: every event is POSTed as JSON as it happens, with
  `Authorization: Bearer <token>` when the named variable is set.
- `otlp_endpoint`: when the run ends it is POSTed as one OpenTelemetry trace
  (OTLP over HTTP, JSON encoding): a root span for the run and a span per
  step, with `gen_ai.*` and `anvil.*` attributes. `otlp_headers_env` names a
  variable shaped `name=value,name2=value2`, the same shape as
  `OTEL_EXPORTER_OTLP_HEADERS`.

Secrets come from the environment, never from the file. Export never decides
a run: a failed POST is recorded in `state.json` under `export_errors` and
the line goes on. Stations never receive these two variables.

## Cost

Token counts are always recorded. Cost in money appears only for models with
a price in `anvil.yaml`, and a price needs a source (see
[COST-MEASUREMENT.md](COST-MEASUREMENT.md)). No price ships with the factory:
add the two models you run with the provider page you took them from, and
`runs`, the events and the traces carry cost from the next run on.

## Who may approve

```json
{
  "approvals": {
    "require_verified_identity": true,
    "approvers": ["ana", "bo"],
    "by_risk_hint": {"production-deploy": ["bo"], "payments": ["bo"]},
    "override": ["bo"]
  }
}
```

- An approval records an identity. Inside GitHub Actions it is the actor
  GitHub authenticated for the event (`/anvil approve` on the issue), marked
  verified, and `--by` must name that same login. From a shell it is the
  typed name, marked unverified.
- `require_verified_identity` refuses shell approvals.
- `approvers` lists who may approve at all; `by_risk_hint` narrows the list
  for work carrying that hint; `override` lists who may approve what the
  line did not approve.
- The policy is read from the checkout the operator controls (the default
  branch in the workflow), never from the run's worktree, which the builder
  can edit. A refused approval records nothing.

With no `approvals` object, behavior is as before: any maintainer who can
comment `/anvil approve` approves.

## What a station can reach

A station runs model written commands with its permission prompts bypassed.
Two layers keep that from reaching your deploys and your repository:

1. Credentials. The engine removes repository, deploy, registry and workflow
   identity tokens (`GH_TOKEN`, `GITHUB_TOKEN`, `ANVIL_PAT`,
   `CLOUDFLARE_API_TOKEN`, the Actions OIDC variables and others) from the
   environment of every station command and every project check. Deploy,
   preview and verify commands, which the spine runs, keep them.
   `runtime.env_deny` adds names; `runtime.env_keep` hands one through on
   purpose. The workflow also persists no credentials in the checkout and
   sets no token at job level.
2. A container, optional:

```json
{
  "runtime": {
    "kind": "command",
    "command": "python3 tools/dispatch_station.py {packet} {output}",
    "sandbox": {"kind": "docker", "image": "anvil-station:latest"}
  }
}
```

   Build the image with `docker build -t anvil-station:latest tools/sandbox`.
   The station then runs in a container that mounts only the project tree
   (and, for an isolated run, the repository's git data), drops every
   capability, runs as the calling user, and receives only the `ANVIL_*`
   hand-offs and the model gateway variables (`env_pass` changes the list).

Limits, stated plainly: the container confines the filesystem and the
credentials, not the network; a station can still reach any host. And the
container path is covered by tests of the wrapping and of the wiring with a
stand-in `docker`; it has not yet run against a real Docker daemon.

A preview deploys code no reviewer has seen yet. Give the preview a token
that can only deploy previews, and prefer preview commands that publish
files over ones that run the project's own build scripts with that token.

## A preview for every work order

```json
{
  "deploy": {
    "command": "npx wrangler pages deploy public --project-name my-shop --branch main",
    "verify": ["curl -fsS https://my-shop.pages.dev/"],
    "preview": {
      "command": "npx wrangler pages deploy public --project-name my-shop --branch \"$ANVIL_PREVIEW_NAME\"",
      "url": "https://{preview_name}.my-shop.pages.dev",
      "verify": ["curl -fsS \"$ANVIL_PREVIEW_URL\""],
      "cleanup": ""
    },
    "provision": ["npx wrangler pages project create my-shop --production-branch main"]
  }
}
```

- In execute mode the preview command runs once per attempt, after the
  builder and before the first reviewer. It gets `ANVIL_PREVIEW_NAME` (the
  work order id as lowercase letters, digits and hyphens, at most 28
  characters: `wo-gh-12`) and `ANVIL_PREVIEW_URL`.
- Reviewers get the URL in their packet; the report and the issue comment
  carry it; a loopback redeploys the same preview.
- A preview that fails to deploy is a warning. Review goes on without it.
- Production stays behind the approver and the human gate, as before.
- `python3 -m anvil.cli preview-cleanup . wo-gh-12` runs the cleanup command.
  The workflow runs it when the order's pull request closes.
- `python3 -m anvil.cli provision .` runs the one time `provision` commands.
  Run it yourself with a token that can create projects; the line never does.

### Starting a project with a target

```bash
python3 -m anvil.cli new-project ../my-shop --name "My Shop" --blueprint static-site --deploy-target cloudflare
python3 -m anvil.cli new-project ../docs --name Docs --blueprint static-site --deploy-target github
python3 -m anvil.cli new-project ../api --name Api --blueprint cloudflare-worker --deploy-target cloudflare
```

| Blueprint and target | Production | Preview per order | Cleanup |
|---|---|---|---|
| static-site, cloudflare | Pages, branch main | Pages branch alias `<order>.<project>.pages.dev` | none needed |
| static-site, github | pages branch root | `previews/<order>/` on the same site | removes the folder |
| cloudflare-worker, cloudflare | `wrangler deploy` | a Worker named `<project>-<order>` | `wrangler delete` |

The Cloudflare commands follow Wrangler's documented interface and have not
been run against a Cloudflare account from this repository yet: run
`provision` and one preview by hand before trusting the line with them. Two
placeholders need your values: `SUBDOMAIN` in the Worker preview URL and
`OWNER`/`REPO` in the GitHub Pages preview URL.

### Cloudflare setup

- Secret `CLOUDFLARE_API_TOKEN`: a token scoped to this account with Pages
  Edit (or Workers Scripts Edit) and nothing else. Variable
  `CLOUDFLARE_ACCOUNT_ID`.
- If the project is connected to Cloudflare's own Git integration, Cloudflare
  already builds a preview for the `anvil/<order>` branch the line pushes.
  Then leave `preview.command` out and keep only what the line should verify.

### GitHub Pages setup

- Settings, Pages: deploy from branch `gh-pages`, root.
- No extra secret: `tools/deploy_github_pages.py` pushes with the workflow's
  token, handed to git through its environment.

## Which runtime runs the stations

`ANVIL_RUNTIME` chooses between Claude Code through the Cloudflare AI Gateway
(the default) and GitHub Copilot CLI with the GitHub account. See
[EXECUTION.md](EXECUTION.md), Choosing the runtime.

## Not done here

- The status page still lists finished runs only; `anvil runs` is where runs
  in progress and interrupted runs show.
- No alerts: point `events_url` at something that alerts on `run.crashed` and
  on `run.finished` with a verdict you care about.
- The sandbox does not restrict network egress.
