The spec at `.openspec/specs/station-budgets-completeness/spec.md` already covered the whole work order. It needed one added line to the allowed write set; nothing else changed. I compared the order against the spec line by line and nothing in the order is missing.

**The one change:** I added the spec file itself to the allowed write set. Scenario S11 checks every path in `git diff 72a84126a600fafb99446946694b5de809e01e66..HEAD --name-only` against that set. The spec file is in that diff, so without this line S11 would have flagged the spec as an out-of-bounds edit.

**What the spec already had right:**
- **The 2026-11-21 correction:** the 14 partitions in R1 add up to exactly 15000000, and the base is pinned to `72a84126…`.
- **The 2026-11-22 owner ruling:** R4 (the completeness check) applies only when partitions are configured. R4 and scenarios S4, S5 and S8 say so, from commit eb22a19.
- **The reconciliation with the active specs:** each is written into the Guardrails and Out of scope sections: checks gate, artifact contract, token-efficiency, station-timeout, continuous run accounting (wo-gh-41), the existing top-level `station_budgets` key, and wo-gh-28.
- **The report literals, write set and frozen surfaces:** R8 has the required builder report literals, and the write set and frozen surfaces match the order's guardrails.

**Requirement ids:** R1 to R8 are unchanged. The only edit is the Allowed write set list.

**Which scenarios prove which requirements:**

| Requirement | Scenarios |
|---|---|
| R1 | S3 |
| R2 | S2, S7 |
| R3 | S1 |
| R4 | S4, S5, S8, S9 |
| R5 | S6 |
| R6 | S1 to S5 |
| R7, R8 | S10 |
| Write set and guardrails | S11 |

There are no em or en dashes in the spec.

**For the owner to decide:**
- **wo-gh-28:** which runs first, it or this order. The spec works either way.
- **Unconditional completeness check:** making it apply to every project would mean changing 22 protected tests. The ruling defers that to a separate order, which hasn't been filed yet.
- **Decision record number:** the previous attempt already wrote `brain/decisions/0014-station-budgets-completeness.md` on this branch. It isn't in the base ref and is the next free number after 0013, so it matches "one new decision record". The builder should revise that file rather than add a second one.
{"model": "claude-opus-5-5"}
