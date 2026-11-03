# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.01 | runs/wo-gh-24/report.json | null |
| spec-writer | executed | 78638.556 | runs/wo-gh-24/spec-writer.output.md | null |
| test-writer | executed | 199610.879 | runs/wo-gh-24/test-writer.output.md | null |
| builder | executed | 630705.244 | runs/wo-gh-24/builder.output.md | null |
| reviewer-spec | executed | 194592.619 | runs/wo-gh-24/reviewer-spec.output.md | null |
| reviewer-security | executed | 149132.045 | runs/wo-gh-24/reviewer-security.output.md | null |
| reviewer-tests | executed | 160806.349 | runs/wo-gh-24/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 190074.05 | runs/wo-gh-24/reviewer-architecture.output.md | null |
| reviewer-design | executed | 69006.676 | runs/wo-gh-24/reviewer-design.output.md | null |
| approver | completed | 0.041 | runs/wo-gh-24/report.json | null |
| triage-human | completed | 0.012 | - | null |
| deployer | packet_ready | 0.054 | runs/wo-gh-24/deployer.packet.md | null |
| observer | executed | 117072.749 | runs/wo-gh-24/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Counted 1 reviews, expected 5.)
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
