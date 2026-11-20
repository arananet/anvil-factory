Nothing was released for wo-gh-41, so there was no release record to observe. The deployer only got as far as preparing its packet and never wrote a release record. Nothing was merged, published or deployed. I wrote the observation report from the run's own state and event logs instead: `runs/wo-gh-41/observer.output.md`.

**What happened:**
- **Checks gate:** the gate failed on all three builder attempts. Each time the factory suite ran 760 tests with one failure.
- **Reviews and verdict:** all six reviewers were skipped, and the run reached your human gate with verdict `no_reviews`.

**Why it failed every time:** an existing test conflicts with this order's spec. `tests/test_governed_delivery.py:113` asserts that a crashed run leaves no `report.json`. The spec requires the opposite: the record is saved after every station, and a crash must leave a completed record with exit status `error`. That test file is protected, so the builder couldn't change it, and the two retries spent tokens without any chance of fixing it. The work order said no active spec conflicted, which was wrong. The builder and the test-writer had both flagged this.

**Decision needed from you:** either allow a one-line change at `tests/test_governed_delivery.py:113`, or change the spec so a crash leaves no record. I recommend the first. The test's other checks still pass, and the spec that test belongs to doesn't require the record to be absent. The second option would undo the point of this order. Either way, the gate and the reviewers need to run again afterwards.

**Other things in the report:**
- `runs/wo-gh-41/report.json` is left over from the earlier run (verdict `budget_exceeded`). This run never wrote its own, which is the exact gap this order is meant to close, happening on the factory itself.
- There are uncommitted edits to `.openspec/specs/continuous-run-accounting/spec.md`, which the builder wasn't authorized to touch. Check them before any merge.
- The code on the branch has not been reviewed. The builder reports its 19 new tests pass, and that a simulated budget-cap death leaves a readable record. I did not re-run either.