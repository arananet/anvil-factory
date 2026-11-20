# Verification first: draft orders

Drafted 2026-11-19 outside the line, at the owner's request. Nothing here is filed: no GitHub issue, no work order id, no branch, no run. These files are untracked and sit outside work_orders/, work-orders/ and .openspec/ on purpose, so no gate or loader reads them.

Basis: factory main 65aae7cc4d5c934cbf1e5a3186b81070e81cc8c1 (2026-11-17), read through git without checking it out. The working tree was on quality/curated-skills at the time.

## Contents

| Order | Spec | What it adds | Depends on |
|---|---|---|---|
| 03-line-yield-metrics | spec.md | First pass yield, survival, verification share, cost per accepted change | none (better after wo-gh-41) |
| 01-runtime-verification | spec.md | Feature map, driver, verify stage before review | none |
| 02-practice-enforcement-ladder | spec.md | Gate by default, named check per gate practice, P-9/P-10/P-11 as checks | 01 for R3 |
| 04-blueprint-guardrails | spec.md | Check packs installed at scaffolding | 02 for R3 |

Each folder holds spec.md (factory spec format) and work-order.draft.json (factory work order fields, id wo-gh-TBD, status draft).

decision-draft-verification-first.md proposes the order of adoption, what is deferred and why, and what is not adopted.

## Suggested order

1. Merge or run the staged accounting orders (wo-gh-41, wo-gh-42).
2. 03 metrics, 3. 01 runtime verification, 4. 02 ladder, 5. 04 guardrails.

## To file one

1. Open the GitHub issue; take its number as the id.
2. Copy spec.md to .openspec/specs/<slug>/spec.md and set Status: proposed.
3. Turn work-order.draft.json into the filed record: id, issue link, base ref pinned again, status new.
4. Check the authorized write set against anvil.json protected paths. Order 01 changes pipelines/sdlc-default.json, a protected path.

## Open points for the owner

- 01: verify is specified as a deterministic stage driven by the feature map. The alternative is an agent station that explores the app freely; it finds more and costs more.
- 03: station_roles puts test-writer under verify. If you count it as produce, the verification share drops.
- 04: needs your choice of first rules per blueprint; with none it ships empty packs.
- Module names in the authorized write sets were taken from main and from staged specs; confirm them at filing.
