# ANVIL landing page

`site/index.html` is the complete English landing page. It has inline CSS and SVG,
no JavaScript, no external assets and no build step. This order deploys nothing.

## Local preview

From the repository root:

```bash
python3 -m http.server 8000 --directory site
```

Open http://localhost:8000/ and stop the server with Ctrl+C. The page also opens
as a local file. Check at desktop, tablet and 360 px phone widths with scripts
disabled. Run the page checks with:

```bash
python3 -m unittest discover -s tests -p 'test_landing_page.py' -v
```

## Cloudflare Pages (recommended)

Use a separate Pages project for the landing page so the existing status page
remains available at its linked URL. This is the same static hosting route used
by the run status page.

After the owner's human gate approval, the operator:

1. Retrieves the Cloudflare vault credential in process as
   `CLOUDFLARE_API_TOKEN` and selects the account via `CLOUDFLARE_ACCOUNT_ID`.
   Never print or commit credential values. See
   [OPERATOR-REQUIREMENTS.md](OPERATOR-REQUIREMENTS.md).
2. Creates a dedicated project if needed:
   `wrangler pages project create anvil-landing --production-branch main`.
3. From the approved checkout, runs
   `wrangler pages deploy site/ --project-name anvil-landing --branch main`.
   There is no build command; `site/` is the output directory.
4. Opens the returned deployment URL, checks the page and links, and confirms
   desktop and phone layouts before recording that URL as the canonical page.

Wrangler is operator tooling, not a dependency of this page or its tests.
The vault credential supports this route; no deployment was attempted here.

## GitHub Pages (alternative)

The owner must enable GitHub Pages in repository Settings. The vault GitHub
token cannot enable Pages; this is a documented permission limit in
[OPERATOR-REQUIREMENTS.md](OPERATOR-REQUIREMENTS.md).

GitHub's branch publishing source accepts the root or `/docs`, not `site/`.
To retain the current file layout, after approval:

1. The owner opens Settings > Pages > Build and deployment and chooses
   GitHub Actions as the source.
2. In a separate authorized hosting change, the operator adds a Pages workflow
   on pushes to main and manual dispatch. It checks out the repo, uses
   `actions/configure-pages`, uploads `site/` with `actions/upload-pages-artifact`,
   and deploys with `actions/deploy-pages` in the `github-pages` environment.
   Grant `contents: read`, `pages: write` and `id-token: write`; use a Pages
   concurrency group. There is no generator or build command.
3. The owner/operator runs that workflow and verifies the deployment URL from
   Settings > Pages, including the repository path prefix and anchor links.

This order adds no workflow and enables no hosting. The recommended Cloudflare
route avoids requiring a new workflow or owner Pages enablement.

## Operator follow up

After the owner's gate approval, the operator deploys the approved page using
the chosen route and updates the repository homepage to the verified landing
page URL. This retires the status URL as the homepage; the status page remains
available through the footer link. No homepage metadata was changed by this
order, and nothing was published.

## Build facts and spec reconciliation

Verified on 2026-11-07 against the checkout and freshly fetched main at
`30f8bb1035a4075d61918d3a6ba53edd7cc96f8a`:

- There are 27 directories with `stations/*/station.json` and 8
  `pipelines/*.json` files.
- `pipelines/sdlc-default.json` has 6 parallel reviewers, including UX.
  The page follows that current pipeline rather than the spec's older five.
- The checks gate is after the builder and before the model reviewers. It does
  not run before all model stations. The page describes the shipped behavior
  in `docs/CHECKS-GATE.md`, not the staged preflight capability of issue 28.
- The page describes existing verified memory, not the staged memory work of
  issue 33. Neither staged capability is advertised as shipped. Fetched main
  contains neither a preflight nor a memory consolidation spec; no merge
  evidence was found to justify including either.
- Release tag `v0.1.0` exists in the fetched tags. Product URLs and claims come
  from the README showcase. Quickstart commands match its `## Quickstart`
  section exactly. No suite size or example timing is printed on the page.
- Supporting merged documentation on main: `docs/MEMORY-GATE.md`,
  `docs/CHECKS-GATE.md`, `docs/RENDERED-DESIGN-REVIEW.md`,
  `docs/EXECUTION.md`, and `docs/COST-MEASUREMENT.md`. Cost coverage and
  configured health checks are qualified rather than promised unconditionally.

## Rendered evidence

Desktop and phone captures of the actual page, with browser scripting disabled,
are stored in `runs/wo-gh-35/evidence/` as `landing-desktop.png` and
`landing-mobile.png`. Their companion `.comparison.json` files record the
charter comparison for reviewer-design, with no reference anchors supplied.
The physical-product charter has no applicable material, lighting, contact or
anatomical scale subject in this typographic interface; those criteria are
recorded as inapplicable rather than treated as a physical rendering verdict.
Approval belongs to the independent reviewers and owner.

## Validation results

- Landing checks: 19 run, 18 passed, 1 skipped. The run-delta test could not
  compare `origin/main...HEAD` because this shallow checkout has no merge base.
  Manual status inspection shows only the new page and this document from the
  builder, in addition to the upstream new test and work-order files.
- Browser: scripts disabled, no external asset requests, no horizontal overflow
  at 360, 768 and 1440 px; visible links have at least 44 px target height.
  Text color pairings were checked at 4.5:1 minimum contrast.
- Full discovery was stopped because the existing
  `test_test_suite_count_measured_r3` recursively launches full discovery.
  With that one method excluded in an external temporary runner, 604 tests ran:
  596 passed, 6 skipped, 1 failed, 1 errored. Both failures concern missing
  `render-stats.json` in the existing render-crash S1 and S5 tests, outside this
  page's scope. Existing test files were not modified.
- Build facts, browser measurements, contrast ratios and charter comparisons
  are recorded alongside the captures. These results are evidence for review,
  not approval of this work.
