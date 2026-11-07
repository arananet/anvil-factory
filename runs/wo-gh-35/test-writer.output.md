I wrote `tests/test_landing_page.py` with 19 tests. They fail right now, because `site/index.html` and `docs/LANDING-PAGE.md` don't exist yet. The run gives 16 failures, 1 error and 2 skips. That's the intended pre-implementation state.

Every test opens the real page, the `stations/` and `pipelines/` trees, the README or the docs file. Nothing asserts against a copy of the content. It is a new file, so no base-ref test file is touched, and it holds no em or en dash characters.

The tests cover the spec like this:

- **S1 (stands alone):** One HTML document with a viewport meta. The title and meta description name ANVIL and its expansion. The page is in English with inline CSS. There are no script, stylesheet, iframe or inline-handler elements. Every `url()` must be a `data:` or `#` reference, and `<img>` sources must be empty or `data:`. There are also checks for `@media` rules and the FF5C00 accent.
- **S2 (story in order):**
  - The eight anchors appear in order. The builder must use the ids `hero`, `problem`, `how-it-works`, `different`, `proof`, `quickstart`, `not` and `footer`. The spec leaves the ids open, so I fixed them and put them in the file's docstring.
  - Both calls to action are checked. They are the repo link and `#quickstart`.
  - Hero and footer text is checked: the expansion, the no-self-approval promise, the Apache 2.0 line, the copyright and developer lines, and `v0.1.0`.
  - The inline SVG must carry the line labels.
  - The page must not mention "preflight" or "consolidation", which stand in for the unmerged issues 28 and 33.
- **S3 (counts):** The "N stations" and "N pipelines" figures on the page must equal the counts computed from the trees at test time. Reviewer counts are checked the same way against `sdlc-default.json`.
- **S4 (quickstart):** Every command in the page's `<pre>` block inside `#quickstart` must appear in the README Quickstart code blocks. The two sets must also be equal.
- **S6 and S7:** A dash check on the page, the hosting doc and the test file. The hosting doc must name both routes, recommend one, say nothing is deployed, mention the homepage follow-up and reference `OPERATOR-REQUIREMENTS`. A fence test checks that the diff against `origin/main` stays inside the allowed paths. It skips if `origin/main` isn't available.

Things to know:

- **Reviewer count conflict:** The spec says "five reviewers in parallel", but `pipelines/sdlc-default.json` lists six in its parallel stage (the sixth is `reviewer-ux`). My test checks the page against the tree, as R3 requires, so a page saying "five" will fail. The spec text needs correcting, or the page should say six and the diagram should show all six.
- **Not covered:** I didn't write tests for S5. It needs the desktop and mobile captures and `reviewer-design` citing them, and that is run evidence rather than a unit test. WCAG contrast and the 44 px target size need a rendered check, so they stay with `reviewer-design` and the captures.

I haven't committed anything.
{"model": "claude-sonnet-5-5"}
