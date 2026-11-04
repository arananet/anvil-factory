# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.011 | runs/wo-gh-26/report.json | null |
| spec-writer | executed | 72595.795 | runs/wo-gh-26/spec-writer.output.md | null |
| test-writer | executed | 126974.997 | runs/wo-gh-26/test-writer.output.md | null |
| builder | executed | 208128.925 | runs/wo-gh-26/builder.output.md | null |
| reviewer-spec | executed | 115293.347 | runs/wo-gh-26/reviewer-spec.output.md | null |
| reviewer-security | executed | 213919.763 | runs/wo-gh-26/reviewer-security.output.md | null |
| reviewer-tests | executed | 206093.862 | runs/wo-gh-26/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 179038.811 | runs/wo-gh-26/reviewer-architecture.output.md | null |
| reviewer-design | executed | 42381.598 | runs/wo-gh-26/reviewer-design.output.md | null |
| approver | completed | 0.038 | runs/wo-gh-26/report.json | null |
| triage-human | completed | 0.011 | - | null |
| deployer | packet_ready | 0.234 | runs/wo-gh-26/deployer.packet.md | null |
| observer | executed | 138445.224 | runs/wo-gh-26/observer.output.md | null |

## Decision

- Approver: All counted reviews passed. (Counted 4 reviews, expected 5.)
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
