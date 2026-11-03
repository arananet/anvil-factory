# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.019 | runs/wo-gh-6/report.json | null |
| spec-writer | executed | 76046.596 | runs/wo-gh-6/spec-writer.output.md | null |
| test-writer | executed | 116170.182 | runs/wo-gh-6/test-writer.output.md | null |
| builder | executed | 156550.487 | runs/wo-gh-6/builder.output.md | null |
| checks-gate | passed | 7682.744 | runs/wo-gh-6/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 185573.361 | runs/wo-gh-6/reviewer-spec.output.md | null |
| reviewer-security | executed | 150210.81 | runs/wo-gh-6/reviewer-security.output.md | null |
| reviewer-tests | executed | 90696.925 | runs/wo-gh-6/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 119272.743 | runs/wo-gh-6/reviewer-architecture.output.md | null |
| reviewer-design | executed | 56277.328 | runs/wo-gh-6/reviewer-design.output.md | null |
| approver | completed | 0.051 | runs/wo-gh-6/report.json | null |
| triage-human | completed | 0.015 | - | null |
| deployer | packet_ready | 0.165 | runs/wo-gh-6/deployer.packet.md | null |
| observer | executed | 54043.233 | runs/wo-gh-6/observer.output.md | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved and no risk hints matched (scanned: auth, payments, data-deletion, production-deploy, secrets, publishing), so no human is required.
