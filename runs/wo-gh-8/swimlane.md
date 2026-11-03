# Swimlane

Routing: 5 reviewers (full panel)

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 35994.871 | runs/wo-gh-8/intake.output.md | null |
| spec-writer | executed | 102760.021 | runs/wo-gh-8/spec-writer.output.md | null |
| test-writer | executed | 96521.445 | runs/wo-gh-8/test-writer.output.md | null |
| builder | executed | 185813.635 | runs/wo-gh-8/builder.output.md | null |
| checks-gate | passed | 15099.719 | runs/wo-gh-8/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 131542.796 | runs/wo-gh-8/reviewer-spec.output.md | null |
| reviewer-security | executed | 125006.209 | runs/wo-gh-8/reviewer-security.output.md | null |
| reviewer-tests | executed | 86689.451 | runs/wo-gh-8/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 130303.573 | runs/wo-gh-8/reviewer-architecture.output.md | null |
| reviewer-design | executed | 130574.671 | runs/wo-gh-8/reviewer-design.output.md | null |
| approver | completed | 0.046 | runs/wo-gh-8/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.22 | runs/wo-gh-8/deployer.packet.md | null |
| observer | executed | 59753.195 | runs/wo-gh-8/observer.output.md | null |

## Decision

- Approver: Reviewers reviewer-spec, reviewer-security, reviewer-tests, reviewer-architecture requested changes.
- Human gate: Verdict is changes_requested, not approved, so a human is required.
