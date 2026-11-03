# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.011 | runs/wo-gh-21/report.json | null |
| spec-writer | executed | 174267.914 | runs/wo-gh-21/spec-writer.output.md | null |
| test-writer | executed | 234928.645 | runs/wo-gh-21/test-writer.output.md | null |
| builder | executed | 365502.648 | runs/wo-gh-21/builder.output.md | null |
| reviewer-spec | executed | 169974.546 | runs/wo-gh-21/reviewer-spec.output.md | null |
| reviewer-security | executed | 159732.248 | runs/wo-gh-21/reviewer-security.output.md | null |
| reviewer-tests | executed | 81685.113 | runs/wo-gh-21/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 96568.359 | runs/wo-gh-21/reviewer-architecture.output.md | null |
| reviewer-design | executed | 38144.627 | runs/wo-gh-21/reviewer-design.output.md | null |
| approver | completed | 0.025 | runs/wo-gh-21/report.json | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.229 | runs/wo-gh-21/deployer.packet.md | null |
| observer | executed | 52281.109 | runs/wo-gh-21/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
