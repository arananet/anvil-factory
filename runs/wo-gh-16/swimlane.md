# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.007 | runs/wo-gh-16/report.json | null |
| spec-writer | executed | 59253.429 | runs/wo-gh-16/spec-writer.output.md | null |
| test-writer | executed | 286896.549 | runs/wo-gh-16/test-writer.output.md | null |
| builder | executed | 277545.572 | runs/wo-gh-16/builder.output.md | null |
| reviewer-spec | executed | 204580.871 | runs/wo-gh-16/reviewer-spec.output.md | null |
| reviewer-security | executed | 106765.305 | runs/wo-gh-16/reviewer-security.output.md | null |
| reviewer-tests | executed | 77771.938 | runs/wo-gh-16/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 93239.977 | runs/wo-gh-16/reviewer-architecture.output.md | null |
| reviewer-design | executed | 75736.796 | runs/wo-gh-16/reviewer-design.output.md | null |
| approver | completed | 0.028 | runs/wo-gh-16/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.005 | - | null |
| deployer | packet_ready | 0.048 | runs/wo-gh-16/deployer.packet.md | null |
| observer | executed | 204044.841 | runs/wo-gh-16/observer.output.md | null |

## Decision

- Approver: Reviewers reviewer-spec, reviewer-architecture requested changes.
- Human gate: Verdict is changes_requested, not approved, so a human is required.
