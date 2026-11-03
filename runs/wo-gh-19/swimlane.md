# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.02 | runs/wo-gh-19/report.json | null |
| builder | executed | 43212.517 | runs/wo-gh-19/builder.output.md | null |
| reviewer-spec | executed | 72019.739 | runs/wo-gh-19/reviewer-spec.output.md | null |
| approver | completed | 0.039 | runs/wo-gh-19/report.json | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
