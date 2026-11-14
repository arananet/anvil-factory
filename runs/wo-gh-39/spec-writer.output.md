The spec for this order already exists at `.openspec/specs/station-timeout/spec.md` (Status: approved). I re-read the work order line by line against it and found no gap, so I made no changes to it.

## Coverage of the work order

| Work order item | Requirement | Scenario |
|---|---|---|
| S1 diagnosis with file and line | R1 | S1 |
| S2 configuration, resolution order, defaults, ceiling, executor coordination, job timeout | R2, R3, R4, R5, R6 | S2 to S6 |
| S3 honest timeout records | R7 | S7 |
| S4 regression evidence (scaled mechanism tests) | R9 | S9 |
| S5 decision record, changelog, docs | R10 | S10 |
| Builder report literals | R11 | S11 |
| Healthy behaviour unchanged (added guard) | R8 | S8 |

Every requirement has at least one scenario that names it. Out of scope and the allowed write set are stated, including the protected paths (anvil.json, pipelines/, existing tests) and the rule that new tests arrive as new files.

## Ids written or changed
None. R1 to R11 and S1 to S11 are unchanged.

## Left open for the owner
- Ceiling behaviour (R4): the order allows clamping a value above 7200 to 7200 or rejecting it with 7200 named. The spec accepts both. The builder picks one and records it in decision 0011.
- Per station override (R2): allowed "in addition" to the environment and anvil.yaml values, not required.
{"model": "claude-sonnet-5-5"}
