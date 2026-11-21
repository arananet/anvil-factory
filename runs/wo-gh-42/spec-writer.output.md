I revised the spec for wo-gh-42 at `.openspec/specs/station-budgets-completeness/spec.md`. The staged version already had the 2026-11-21 correction: the new partition table, which sums to exactly 15000000, and the wo-gh-41 and packet-budget reconciliation. I added the parts of the work order that were still missing. I checked it line by line against the order, there are no em or en dashes in the file, and I have not committed anything.

**Added**
- **Header:** the work order id, the issue link, and the base ref `72a84126a600fafb99446946694b5de809e01e66`, which I confirmed is HEAD~1. It also states that the partitions divide the existing 15000000 pool and do not raise it.
- **R7 (documentation):** `docs/EXECUTION.md` must name both `efficiency.station_budgets`/`default_station_budget` and the top-level `station_budgets` packet cap, and state the difference. It also requires a CHANGELOG entry and one new decision record.
- **R8 (builder report evidence):** the four required literals, the verified base ref, the partition table with its sum, the full suite test count and the names of the new test files.
- **Allowed write set:** lists every path the order authorizes, per P-15. It names the protected paths (`pipelines/`, `anvil.json`, existing tests) and says which `anvil.yaml` keys may change.
- **Out of scope:** a new section.
- **New scenarios:**
  - S7 (R2): unmeasured usage, with `require_usage` on and off.
  - S8 (R4): part (c), a station recorded failed without its artifact, an empty delta list, and the max-loopbacks limit.
  - S9 (R4): completeness does not re-run the suite or repeat the literal checks.
  - S10 (R7, R8): the docs and the builder report evidence.
  - S11: write set, protected paths and the dash rule, checked by diff against the base ref.

**Changed**
- **Guardrails:** the full suite must pass at handoff, with the two protected tests unmodified.
- **S1 to S6:** each now names its requirement (S1 R3/R6a, S2 R2/R6b, S3 R1/R6c, S4 and S5 R4/R6d, S6 R5).
- **S1 and S2:** now require the run to end through the wo-gh-41 exit path (`budget_exceeded`, a `termination_reason` naming the station, `not_run`).
- **S3:** now has a concrete over-cap example: a 1000000 cap against 900000 plus 200000.

R1 to R6 are unchanged.

**For the owner to decide**
- **Order against wo-gh-28:** the order leaves which of this and the staged preflight order runs first to you.
- **Default budget value:** neither the order nor the base `anvil.yaml` sets a `default_station_budget` value. With all 14 sdlc-default stations named and summing to the full 15000000 cap, any default above 0 would fail load validation for a pipeline that has unnamed model stations. The builder needs to know the value (0 or absent) or how an unset default is handled.
- **Other pipelines:** they get no named partitions, so they depend on that default too.
{"model": "claude-opus-5-5"}
