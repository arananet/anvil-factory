I've finished the attribution work and written the builder report to `runs/wo-gh-43/builder.output.md`. One thing needs your call: the gate's own suite command still exits 1 in this Actions runner. That's because of 5 approval tests, not this change.

**Why the suite is red here:** the runner sets `GITHUB_ACTIONS=true` and `GITHUB_ACTOR=arananet`, so approvals in `test_autonomous_line` and `test_governed_delivery` are refused with "does not match the authenticated GitHub actor arananet". The same 5 tests fail on an unmodified checkout of HEAD. With those variables unset, the full suite passes: `Ran 751 tests`, `OK (skipped=6)`, exit 0. Fixing this means changing those existing tests or the gate environment, and both are outside this order's allowed files.

**What this attempt added** (the gate code from attempt 1 is kept as it was):
- **Onboard:** a web project (one with an HTML page) gets an "ANVIL attribution" section in `ONBOARDING.md`. No existing file is changed.
- **Station guidance:** the builder and publisher prompts now carry the default line "Made with ANVIL, an open source software factory.", where to place it, the rule to keep a project's own ANVIL credit, and the owner approved exception path. The publisher treats a missing attribution as a defect.
- **Decision record:** `brain/decisions/0012-anvil-attribution-default.md`, in the same format as 0011.

The 15 new attribution tests pass. I also ran it by hand:
- A new static site gets the line in its seeded spec and project brain.
- Onboarding a web project records the requirement; onboarding a Python-only project doesn't.
- The gate fails a page with no credit and says why.

The report includes all the literals the gate looks for.

**Decisions for you:**
- **Cloudflare worker:** the worker blueprint doesn't get the requirement seeded, because its first spec is a worker, not a page. The gate still checks any worker project that ships HTML. If you want worker projects seeded too, it's a one-flag change in `blueprints/cloudflare-worker.json`.
- **What the check misses:** only the index page is checked, not other pages. A credit in unusual wording can be wrongly failed; rewording it or recording an exception fixes that.
- **Game placement:** "credits or footer outside the game canvas" is written into the guidance and seeded requirement, but nothing checks it automatically and no test covers it.

The new test file contains one em dash, but only as the constant the test uses to check that other files have none; nothing I wrote contains one. No existing tests were edited, and `anvil.json`, `pipelines/` and `anvil.yaml` are untouched.