I've built the practices base, but one of the 28 new tests still fails. That's `test_no_base_changes_nothing_but_the_report_field_s8`, and the cause is in the test rather than the code. The full suite has 649 tests with that one failure. At the base ref there was 1 error, the new test file failing to import, so nothing that used to pass broke.

**The failing test:** it expects the run's verdict to be `approved`, but the run gives `no_reviews`. The test's fake reviewer prints its review to stdout. The runner never turns printed output into a review file; that rule comes from work order wo-gh-24. I ran the same pipeline on the base code without my change and got `no_reviews` there too. I left the review handling alone, since changing it would break that rule. The rest of that test passes. The fix belongs to the test-writer: have the fake executor write `runs/<id>/<station>.review.json`, or compare the verdict against the base code's.

**What's in place:**
- **Brain module (`anvil/brain.py`):**
  - `propose_practice` writes a proposal to `brain/inbox/` and nowhere else.
  - `promote_practice` is the only thing that writes `brain/practices.md`. When it refuses, it says why and changes nothing on disk. The checks are bad provenance, a conflicting active practice (named by id), a bad Supersedes, or a malformed entry.
  - `resolve_practices` decides which stations get which practices, in plain code with no model.
  - `check_brain` now also fails on a malformed practices file or two active practices that conflict. With no practices file it passes.
- **Runner (`anvil/runner.py`):**
  - Practices are resolved at run start, and again if intake changes the work order's surfaces.
  - Prompt practices go into a `## Practices` section of the packets for the stations they resolved for.
  - Gate practices are listed by id and topic in the checks gate pre-review output, never as prompt text.
  - `report.json` and `routing.json` both record the same resolution.
- **CLI (`anvil/cli.py`):** new `propose-practice` and `promote-practice` commands, and `check-brain` now shows the active practice count.
- **Empty base:** no `brain/practices.md` ships. `anvil check-brain .` on the factory passes with 0 active practices.
- **No practices file:** a full run's packets are byte-identical to the base code's. I checked by comparing hashes of every packet. The only difference is the new empty `practices` field in the report.
- **Issue 33:** scoped learnings hasn't merged, so I wrote the scope matching in the brain module. That means two parallel matchers until it lands, which the builder report records.

No dependencies were added, no existing test files were touched, and none of the changed files contain an em or en dash. The full report is at `runs/wo-gh-36/builder.output.md`.
