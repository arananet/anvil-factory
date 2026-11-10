# ANVIL landing page

## Consumption update

The token-efficiency change adds a consumption section and a direct link to
the status board. It describes project/run/attempt breakdowns, measurement
coverage, context limits and execution thresholds without claiming a measured
percentage saving. Thresholds are checked between calls; an in-flight call
may exceed them. Historical consumption without runtime evidence stays unknown.
The source remains static HTML/CSS with no external assets or JavaScript.

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

Re-verified on 2026-11-07 against this checkout. A read-only
`git ls-remote origin refs/heads/main refs/tags/v0.1.0` confirms main remains
`30f8bb1035a4075d61918d3a6ba53edd7cc96f8a` and the release tag resolves to
`7e71fc2b3d5bb00af26fcb11f728442a47a6c365`. The local checkout has neither
that tag nor an origin/main tracking ref; tests requiring those refs skip.

- There are 27 directories with `stations/*/station.json` and 8
  `pipelines/*.json` files.
- `pipelines/sdlc-default.json` has 6 parallel reviewers, including UX.
  The page follows that current pipeline rather than the spec's older five.
- The checks gate is after the builder and before the model reviewers. It does
  not run before all model stations. The page describes the shipped behavior
  in `docs/CHECKS-GATE.md`, not the staged preflight capability of issue 28.
- The page describes existing verified memory, not the staged memory work of
  issue 33. Neither staged capability is advertised as shipped. The previously inspected main tree
  contains neither a preflight nor a memory consolidation spec; no merge
  evidence was found to justify including either.
- Release tag `v0.1.0` exists on origin (verified by the read-only query). Product URLs and claims come
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

- Landing checks re-run: 19 tests, 17 passed, 2 skipped. The release-tag check
  lacks a local tag; the run-delta check lacks origin/main. The release was
  independently verified on origin as recorded above. Existing tests were
  not modified.
- The builder retained the existing implementation, added a keyboard skip
  link, and switches the SVG to its legible vertical layout through tablet
  widths rather than shrinking desktop labels below readable size.
- Desktop and mobile captures and browser measurements are regenerated for
  this attempt. Scripts are disabled during capture. Measurements cover
  360, 768 and 1440 px viewports, external requests and visible link targets.
- The broader suite was not re-run for these isolated HTML/CSS changes.
  Earlier suite results are not presented as validation of this attempt.
- Build facts, browser measurements, contrast ratios and charter comparisons
  accompany the captures. They are evidence for independent review.
