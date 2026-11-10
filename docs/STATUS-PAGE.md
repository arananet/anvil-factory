# Run status page

## Token consumption

Each project page leads with input, output, cached input, cache creation,
reasoning and total tokens. It states measurement coverage beside the totals.
Unknown usage stays unknown; a partial subtotal is labeled partial. Cached
input is already part of input and reasoning is already part of output.

Expand a station row to see each runtime attempt, its success or failure,
reported tokens, runtime turns and any separately labeled cost estimate.
Corrections and failed calls contribute to consumption. An agent call is a
station runtime invocation, which can contain multiple model/tool turns.
The initial packet estimate is shown separately from actual runtime usage.
The page also groups usage by station and executed model.

New projects receive `status/index.html` automatically. Executed runs refresh
it. Rerunning a work order archives the previous report under
`runs/<id>/history/`; earlier attempts stay in the project total while the
lifecycle board shows the latest run. `usage.json` exports the same totals
and per-run/attempt data without raw prompts, environment values or local paths.

## Factory and project pages

```bash
python3 -m anvil.cli status-page . --include-project ../project-one --include-project ../project-two
python3 tools/sync_project_usage.py
```

The first command writes the factory page and a linked page per project
under `status/projects/`. Project paths can also be configured as
`status_projects` in the factory's `anvil.yaml`. Included projects are read;
their working trees are not modified by portfolio generation.

The refresh tool reads `project-reports/catalog.json`, imports sanitized
public GitHub reports for Sentia, Platform25 and Taskline, and regenerates
their pages. Snapshot metadata records the source tree and import time.
Private repositories are refused. The tool requires `gh` access, makes no
model calls and does not alter the source repositories. Historical reports
that never captured tokens cannot be backfilled accurately and show unknown.

Every ANVIL run leaves a `report.json` behind. The status page turns all of
them into one page anyone can open: each run with its work order, verdict,
human gate flag, deployment status, and a per station table showing exactly
what each step did (completed, packet_ready, executed, failed), how long it
took, and which artifacts it produced.

Each run also shows why it ended as it did. Newer reports carry a decision
object recorded by the runner at the moment it decided: the approver rule
sentence (which aggregation branch produced the verdict, naming the reviewer
that failed or asked for changes) and the human gate rule sentence (verdict
not approved, an approved verdict with a matched risk hint, or an approved
verdict with no matched hints). Older reports predate that object, so the
page derives a minimal explanation from the recorded verdict, the
human_required flag and the executed reviewer steps, and labels it
"derived from the run record" so nobody mistakes it for the runner's own
words.

## Lifecycle board

The page leads with a lifecycle board: one row per work order showing its
stage progression at a glance. The stages are fixed vocabulary (SPEC, BUILD,
REVIEW, APPROVED, MERGED) derived from evidence in each run's report:

- **SPEC**: spec-writer step executed
- **BUILD**: builder step executed
- **REVIEW**: at least one reviewer step executed
- **APPROVED**: verdict is approved
- **MERGED**: a merge record exists in `merge_records/<work-order-id>.json` with `merged: true`

Each row shows the work order ID (as a real anchor link to that job's detailed
run section), title, and stage sequence with reached stages marked and the
current stage (the furthest reached) highlighted. When a work order's latest
run requires human review, a NEEDS HUMAN badge appears next to the stages.
Intake states (PARKED from a `waiting_info` verdict, REJECTED from a
`rejected` verdict) replace the stage progression when the run ended in that
state.

The board is regenerated from run reports and merge records on disk each time
the page is generated, with no network calls and no inference from branch
names or commit messages. Regenerating from the same data produces the same
board.

The board styling uses a consistent spacing scale (CSS custom properties),
adapts to narrow viewports without horizontal scrolling, and all text meets
WCAG 4.5:1 contrast minimums for accessibility.

## Generate

```bash
python3 -m anvil.cli status-page path/to/project
python3 -m anvil.cli status-page path/to/project --out path/to/output-dir
```

Without `--out`, the page lands in `<project>/status/index.html`. The output
uses self contained HTML files: inline CSS in the Arananet palette, no
external assets, no JavaScript, no build step. Runs whose report.json is
missing or corrupt are skipped and the skip is noted in the page footer.
Missing fields render as a dash or Unknown. Cost remains null without usage
and sourced prices: the page shows the recorded evidence.

## Host it in the project itself (recommended default)

The cheapest home for the page is the repository it describes. Generate it
into `docs/` at the repo root, commit the file, and let GitHub Pages serve
it (repository Settings, Pages, Build and deployment: deploy from a branch,
`main` plus `/docs`). GitHub Pages only serves from the root or from
`/docs`, which is why the output goes there.

```bash
python3 -m anvil.cli status-page path/to/project --out path/to/project/docs
```

The Taskline example does exactly this; its page is the `docs/` folder of
`anvil-example-taskline`. The same repository also keeps a `status/` copy
for its Cloudflare Pages deployment, regenerated from the same reports so
the content matches.

Generation reads local reports and snapshots without model calls, network
requests or a build step. Refreshing imported GitHub snapshots is a separate
read-only command. The factory overview includes its own consumption and
the included projects, with individual totals on each project card. Hosting
serves static HTML and JSON. Regenerate and publish after runs to keep the
public snapshot current.

## Publish to Cloudflare Pages (alternative)

When you do not want the extra commits in the project history, serve the
same file from Cloudflare Pages instead. The output directory is the whole
site:

```bash
wrangler pages deploy status --project-name anvil-status
```

Or drag and drop the output directory in the Cloudflare Pages dashboard.
The Taskline example is live this way too, from its `status/` folder.

## Honest note: it is a snapshot

The page states its generation time on its face because it is a snapshot of
the run reports on disk at that moment, not a live feed. It only moves when
someone regenerates it. If you want it current after every run, regenerate
it in CI as a step after the run, for example in a workflow like the
Taskline issue workflow:

```yaml
- name: Regenerate the status page
  run: PYTHONPATH=.anvil-factory python3 -m anvil.cli status-page . --out status
```

and publish the `status/` output with your usual Pages step.
