# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.012 | runs/wo-gh-21/report.json | null |
| spec-writer | executed | 629445.678 | runs/wo-gh-21/spec-writer.output.md | null |
| test-writer | executed | 221077.287 | runs/wo-gh-21/test-writer.output.md | null |
| builder | executed | 231487.561 | runs/wo-gh-21/builder.output.md | null |
| reviewer-spec | executed | 332574.348 | runs/wo-gh-21/reviewer-spec.output.md | null |
| reviewer-security | executed | 216822.993 | runs/wo-gh-21/reviewer-security.output.md | null |
| reviewer-tests | executed | 121931.93 | runs/wo-gh-21/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 125810.25 | runs/wo-gh-21/reviewer-architecture.output.md | null |
| reviewer-design | executed | 49362.653 | runs/wo-gh-21/reviewer-design.output.md | null |
| approver | completed | 0.04 | runs/wo-gh-21/report.json | null |
| triage-human | completed | 0.01 | - | null |
| deployer | packet_ready | 0.23 | runs/wo-gh-21/deployer.packet.md | null |
| observer | executed | 81604.672 | runs/wo-gh-21/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Counted 4 reviews, expected 5.)
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
