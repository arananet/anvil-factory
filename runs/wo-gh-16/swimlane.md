# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.02 | runs/wo-gh-16/report.json | null |
| spec-writer | executed | 101648.477 | runs/wo-gh-16/spec-writer.output.md | null |
| test-writer | executed | 232398.687 | runs/wo-gh-16/test-writer.output.md | null |
| builder | executed | 313117.457 | runs/wo-gh-16/builder.output.md | null |
| reviewer-spec | executed | 148994.868 | runs/wo-gh-16/reviewer-spec.output.md | null |
| reviewer-security | executed | 114642.591 | runs/wo-gh-16/reviewer-security.output.md | null |
| reviewer-tests | executed | 88345.1 | runs/wo-gh-16/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 120502.15 | runs/wo-gh-16/reviewer-architecture.output.md | null |
| reviewer-design | executed | 64587.547 | runs/wo-gh-16/reviewer-design.output.md | null |
| approver | completed | 0.046 | runs/wo-gh-16/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.197 | runs/wo-gh-16/deployer.packet.md | null |
| observer | executed | 110182.218 | runs/wo-gh-16/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-security requested changes. (Counted 1 reviews, expected 5.)
- Human gate: Verdict is changes_requested, not approved, so a human is required.
