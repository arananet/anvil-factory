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

## Not done here

- The status page still lists finished runs only; `anvil runs` is where runs
  in progress and interrupted runs show.
- No alerts: point `events_url` at something that alerts on `run.crashed` and
  on `run.finished` with a verdict you care about.
- The sandbox does not restrict network egress.
