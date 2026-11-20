The build is done, but the full suite still fails: one protected test contradicts the spec, and you need to decide how to resolve it. This was attempt 3 of 3. I made no code changes, because the only ways to turn the suite green were editing that test or adding code that recognises its inputs, and I did neither.

**Test results** (tree at HEAD `17dab24`):
- **New tests:** all 19 in `tests/test_continuous_run_accounting.py` pass. That is the only new test file.
- **Full suite, clean environment:** with `GITHUB_ACTOR`, `GITHUB_ACTIONS` and the `ANVIL_*` variables unset, `Ran 760 tests ... FAILED (failures=1, skipped=6)`.
- **Full suite, this shell's environment:** 6 failures. The extra five are approval identity tests that fail because `GITHUB_ACTOR=arananet` is set here; they don't touch this change.
- **By hand:** I ran a scripted budget death and fed its `report.json` to `tools/line_comment.py`. The comment shows exit status `budget_exceeded`, the cap that was crossed, builder recorded as failed with its model, and every later station as not run.

**The conflict:** `tests/test_governed_delivery.py:113` (`test_crash_and_stall_are_visible_s1`) checks that a run whose builder raises an error leaves **no** `runs/wo-crash/report.json`. The test is protected and is the same on current main. The spec requires the opposite:
- R1.1 writes `report.json` after intake and test-writer, which both finish before the builder runs.
- R2.1 and S2 require a completed record with exit status `error` when a station raises.

No implementation can pass both. All the test's other checks still pass. The test-writer station raised the same conflict earlier.

**Decision needed** (pick one):
1. Allow a one-line change to `tests/test_governed_delivery.py:113`: drop that check, or reverse it so it expects a completed record with exit status `error`. I recommend this.
2. Change the spec so an error leaves no `report.json`. That contradicts S2 and the reason this order exists.

My report is in `runs/wo-gh-41/builder.output.md`, with all the required literals and which spec scenario each change serves. It also lists three small untested gaps: a budget death where the in-flight station's usage is unmeasured, two stop paths with no dedicated test, and the `anvil runs` inspect path, which sits outside the files this order may change.