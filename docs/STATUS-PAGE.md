# Run status page

Every ANVIL run leaves a `report.json` behind. The status page turns all of
them into one page anyone can open: each run with its work order, verdict,
human gate flag, deployment status, and a per station table showing exactly
what each step did (completed, packet_ready, executed, failed), how long it
took, and which artifacts it produced.

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

## Publish to Cloudflare Pages

The output directory is the whole site:

```bash
wrangler pages deploy status --project-name anvil-status
```

Or drag and drop the output directory in the Cloudflare Pages dashboard.
The Taskline example is live this way (see its status/ folder).

## Publish to GitHub Pages

The same file works unchanged. Either commit the output under `docs/` in
the repository and enable Pages from that folder in the repository settings,
or push the output to a `gh-pages` branch and serve from the branch root.

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
