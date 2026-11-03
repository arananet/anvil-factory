# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.01 | runs/wo-gh-7/report.json | null |
| spec-writer | executed | 108822.004 | runs/wo-gh-7/spec-writer.output.md | null |
| test-writer | executed | 152601.986 | runs/wo-gh-7/test-writer.output.md | null |
| builder | executed | 363205.91 | runs/wo-gh-7/builder.output.md | null |
| checks-gate | passed | 8560.967 | runs/wo-gh-7/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 143723.643 | runs/wo-gh-7/reviewer-spec.output.md | null |
| reviewer-security | executed | 89882.282 | runs/wo-gh-7/reviewer-security.output.md | null |
| reviewer-tests | executed | 43454.549 | runs/wo-gh-7/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 132091.642 | runs/wo-gh-7/reviewer-architecture.output.md | null |
| reviewer-design | executed | 86119.216 | runs/wo-gh-7/reviewer-design.output.md | null |
| approver | completed | 0.026 | runs/wo-gh-7/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.005 | - | null |
| deployer | packet_ready | 0.048 | runs/wo-gh-7/deployer.packet.md | null |
| observer | executed | 64258.67 | runs/wo-gh-7/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-security requested changes.
- Human gate: Verdict is changes_requested, not approved, so a human is required.
