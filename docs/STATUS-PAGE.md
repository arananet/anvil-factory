# Run status page

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

## Generate

```bash
python3 -m anvil.cli status-page path/to/project
python3 -m anvil.cli status-page path/to/project --out path/to/output-dir
```

Without `--out`, the page lands in `<project>/status/index.html`. The output
is a single self contained HTML file: inline CSS in the Arananet palette, no
external assets, no JavaScript, no build step. Runs whose report.json is
missing or corrupt are skipped and the skip is noted in the page footer.
Missing fields render as a dash and cost stays null: the page shows what the
reports say, nothing more.

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

Efficiency, measured on the Taskline example: the whole dashboard is one
self contained HTML file of 8,857 bytes (two runs, decision blocks
included). Generation is a local read of the run reports on disk, no
network, no build step. Hosting is static and free on both GitHub Pages and
Cloudflare Pages. The only recurring cost is one small commit per
regeneration on the GitHub Pages route, or one small deploy on the
Cloudflare route. Regenerating in CI after each run (see the honest note
below) keeps it current for that same small cost.

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
