# Builder report: wo-gh-43, ANVIL attribution by default

Spec: .openspec/specs/attribution-default/spec.md
Attempt: 2 of 3 (loopback from checks-gate). Kept the attempt 1 work (anvil/attribution.py, gates, scaffold, blueprints, spec refinements) and finished what it left undone: onboard, the two station prompts, decision record 0012, and this report.

Default line, exact: "Made with ANVIL, an open source software factory." linked to https://anvil-landing-7x1.pages.dev.

## What changed, by scenario

| File | Change | Scenario |
|---|---|---|
| anvil/attribution.py (new) | The one place for the default line, landing URL, requirement text, exception form, visible text extraction (comments, attributes, script, style, template, noscript ignored), bespoke credit test, deliverable lookup (public/, dist/, root index.html) and `check_attribution`, which returns None when there is no HTML deliverable | S2, S3, S4, S5, S8 (placement text) |
| anvil/gates.py | `checks_gate` runs `check_attribution(project_dir, config)`; a fail fails the gate; an `# ANVIL Attribution` section goes into the output only when the check applies; adds `attribution_verdict` to the result | S2, S3, S4, S5 |
| anvil/scaffold.py | `new_project` appends the requirement section to the first seeded spec (site-shell) and to brain/project.md for blueprints with `"ships_pages": true` | S1 |
| blueprints/static-site.json | `"ships_pages": true` | S1 |
| blueprints/cloudflare-worker.json | `"ships_pages": false` (its first spec is a worker entry, not a page) | S1 |
| anvil/onboard.py | When the project has an HTML deliverable, ONBOARDING.md gets the requirement section. No other file is written; existing files stay byte-identical | S1 |
| stations/builder/PROMPT.md | Rule: default line, footer or credits placement (outside canvas and input region on games), keep bespoke credit, owner approved exception form, the gate fails when it's missing | S6, S8 |
| stations/publisher/PROMPT.md | The same rule; a missing attribution is a defect, so do not publish | S6 |
| brain/decisions/0012-anvil-attribution-default.md (new) | Context (the 2026-11-15 audit), Decision, Consequences, in the format of 0011 | S7 |
| .openspec/specs/attribution-default/spec.md | Spec-writer refinements carried from attempt 1 (out of scope, exception record form, compliance test, scenarios S1 to S8) | all |

Exception form honoured (S4): a spec line `Attribution exception: approved by <owner> on <YYYY-MM-DD>: <reason>`, or the same form in anvil.json `attribution_exception`. The gate quotes the line.

## Verification

- `python -m unittest tests.test_attribution_default` gives `Ran 15 tests in 0.072s` and `OK` (covers S1, S2, S3, S4, S5, S6, S7).
- Full suite, as the gate runs it in this Actions environment: `python -m unittest discover -s tests -p 'test_*.py'` gives `Ran 751 tests in 80.148s` and `FAILED (failures=5, skipped=6)`. The 5 failures are test_autonomous_line.TestHumanGate (test_approval_rules_s4, test_approve_and_resume_deploys_s4, test_publisher_held_until_approved_s5) and test_governed_delivery.TestApprovalPolicy (test_identity_and_policy_s5, test_policy_comes_from_the_operator_checkout_s5). They come from the environment, not from this change: the runner sets GITHUB_ACTIONS=true and GITHUB_ACTOR=arananet, so approvals are refused with "does not match the authenticated GitHub actor arananet". The same 5 tests fail on an unmodified `git archive HEAD` checkout (`python -m unittest tests.test_autonomous_line tests.test_governed_delivery` gives `FAILED (failures=5)`).
- Full suite without those runner variables: `env -u GITHUB_ACTIONS -u GITHUB_ACTOR -u CI python -m unittest discover -s tests -p 'test_*.py'` gives `Ran 751 tests in 80.599s` and `OK (skipped=6)`, exit 0.
- Ran by hand: a scaffolded static-site has the line in its site-shell spec; a scaffolded cloudflare-worker does not; onboarding a project with public/index.html adds the "## ANVIL attribution" section to ONBOARDING.md, and onboarding a Python-only project does not; `checks_gate` on the onboarded page with no credit returns `fail` with "Attribution check failed: missing ANVIL attribution in public/index.html."
- Em dash check (S7): grep for U+2014 over every file this order changed matches only tests/test_attribution_default.py. That file is the test-writer's, and the match is its `EM_DASH` constant used for the assertion. No builder-written file contains one.
- No existing test was edited; tests/ holds only the new test-writer file. anvil.json, pipelines/ and anvil.yaml are untouched.

## Open items and gaps

- Gate environment: as long as checks-gate runs inside GitHub Actions with GITHUB_ACTOR set, the full suite will show those 5 failures, with or without this change. Fixing that means changing those tests or the gate environment, which is outside this order's authorised surface. The operator needs to decide.
- cloudflare-worker is `ships_pages: false`. If the owner wants worker projects seeded too, flip the flag; the gate already checks any worker project that ships an HTML deliverable.
- When an index page exists, only it is checked; secondary pages are not.
- The bespoke credit test is a pattern: a build verb with by, with or using ANVIL, or ANVIL followed by a build verb. An unusual wording can false fail. The fix is to reword the credit or record an exception.
- S8 (game placement) is covered by station guidance and the seeded requirement text. No deterministic DOM placement check is implemented, and no test covers it.
- Nothing visual was rendered: this order changes the factory only and ships no page.
{"model": "claude-opus-5-5"}
