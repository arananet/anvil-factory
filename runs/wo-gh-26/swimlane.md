# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.01 | runs/wo-gh-26/report.json | null |
| spec-writer | executed | 93298.199 | runs/wo-gh-26/spec-writer.output.md | null |
| test-writer | executed | 126572.416 | runs/wo-gh-26/test-writer.output.md | null |
| builder | executed | 156605.461 | runs/wo-gh-26/builder.output.md | null |
| reviewer-spec | executed | 119527.549 | runs/wo-gh-26/reviewer-spec.output.md | null |
| reviewer-security | executed | 120802.013 | runs/wo-gh-26/reviewer-security.output.md | null |
| reviewer-tests | executed | 84841.366 | runs/wo-gh-26/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 136183.745 | runs/wo-gh-26/reviewer-architecture.output.md | null |
| reviewer-design | executed | 46167.69 | runs/wo-gh-26/reviewer-design.output.md | null |
| approver | completed | 0.037 | runs/wo-gh-26/report.json | null |
| triage-human | completed | 0.014 | - | null |
| deployer | packet_ready | 61.347 | runs/wo-gh-26/deployer.packet.md | null |
| observer | executed | 152629.034 | runs/wo-gh-26/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Counted 4 reviews, expected 5.)
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
