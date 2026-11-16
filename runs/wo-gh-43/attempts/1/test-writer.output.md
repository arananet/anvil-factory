I wrote `tests/test_attribution_default.py`, with 15 tests. 11 of them fail now, for the right reason: the behaviour isn't built yet. The other 4 pass before the build, as expected (see S5 below). The full suite fails, but only on 5 tests that aren't mine.

**Suite count**
- Baseline: 736 tests (751 total minus my 15), with 6 skipped.
- Added: 15 tests. I edited no existing tests.
- Full suite last run: `Ran 751 tests`, `FAILED (failures=16, skipped=6)`. That is 11 new failures plus 5 old ones.
- The 5 old failures are in `test_autonomous_line.TestHumanGate` (`test_approval_rules_s4`, `test_approve_and_resume_deploys_s4`, `test_publisher_held_until_approved_s5`) and `test_governed_delivery.TestApprovalPolicy` (`test_identity_and_policy_s5`, `test_policy_comes_from_the_operator_checkout_s5`).
- They also fail with my test file and the spec edit stashed away: 5 failures in those two modules. The error shows the approval check rejecting `--by bo` because the authenticated GitHub actor is `arananet`.
- That is an environment issue unrelated to this order. The suite can't go fully green on this runner whatever the builder does.

**Scenario to test**
- **S1:** the static-site scaffold must put the line, the landing URL, "footer" and "bespoke" in the `site-shell` spec and in `brain/project.md` (fails now). Onboarding a web project must write the same into `ONBOARDING.md` and leave every existing file byte-identical (fails now). A `python-service` scaffold must not get the footer requirement (passes now, as a guard).
- **S2:** the default line linked to the landing passes, and the Sentia credit passes (both pass now, because the gate has no attribution check yet). Under `dist/` and at the project root, a page with no attribution must fail (fails now).
- **S3:** no attribution fails with the reason named in the output (fails now). ANVIL only in a comment, a script or an attribute fails. A page that mentions ANVIL without saying it built the project fails.
- **S4:** the exact exception line in a spec passes and appears in the output (fails now). A loosely worded "waiver" line is not honoured (fails now).
- **S5:** a project with no HTML deliverable passes with no "attribution" text in the output (passes now, and must stay that way).
- **S6:** both station prompts contain the line, "footer", "bespoke" and "owner approved exception", and the publisher prompt contains "defect" (fails now).
- **S7:** `0012-anvil-attribution-default.md` exists, has the sections `0011` has, mentions 2026-11-15 and the line, and has no em dash (fails now).

**Gaps and assumptions the builder should know**
- **S8 (game placement):** not covered. The spec says it is a deliverable check with no named code path, so a test would be a facade.
- **Gate interface:** the spec leaves it open, so the tests go through `checks_gate` itself with a configured `exit 0` check. The gate returns early when no checks are configured, so the attribution check needs to run only when checks exist, or the builder should say otherwise. I read the deliverable as `public/index.html`, `dist/index.html` or `./index.html`, and the exception from `.openspec/specs/*/spec.md`.
- **Cloudflare worker blueprint:** it ships no pages today, so I didn't test it.
- **Onboard detection:** a project counts as web when it has an HTML file under `public/`. The builder may widen that.
{"model": "claude-sonnet-5-5"}
