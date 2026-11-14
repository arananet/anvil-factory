The spec for this order already exists at `.openspec/specs/station-timeout/spec.md`, marked approved, so I did not change it. I re-read the work order line by line against it and found no gap.

- **Coverage:** work order S1 to S5 map to spec R1 to R10 and S1 to S10. The order's builder-report literals map to R11/S11. R8/S8 (healthy stations record exactly what they did before) is an extra guard. Each requirement has a scenario that names it. Out of scope and the allowed write set are stated, including the protected paths.
- **Ids changed:** none. R1 to R11 and S1 to S11 are as they were.
- **Handoff file:** I wrote `runs/wo-gh-39/spec-writer.output.md`, which was showing as deleted in git status.

Two points are left for the owner to decide:
- **Ceiling (R4):** a value above 7200 can be clamped to 7200 or rejected with 7200 named. The spec accepts either, and the builder picks one and records it in decision 0011.
- **Per-station override (R2):** one is allowed on top of the environment and `anvil.yaml` values but not required.

I did not run any checks or tests. This station only checked the spec against the order.