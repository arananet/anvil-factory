# Swimlane

Routing: 5 reviewers (full panel)

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 37712.6 | runs/wo-gh-9/intake.output.md | null |
| spec-writer | executed | 98999.873 | runs/wo-gh-9/spec-writer.output.md | null |
| test-writer | executed | 182649.418 | runs/wo-gh-9/test-writer.output.md | null |
| builder | executed | 408912.672 | runs/wo-gh-9/builder.output.md | null |
| checks-gate | passed | 15912.886 | runs/wo-gh-9/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 99743.941 | runs/wo-gh-9/reviewer-spec.output.md | null |
| reviewer-security | executed | 100544.817 | runs/wo-gh-9/reviewer-security.output.md | null |
| reviewer-tests | executed | 95398.898 | runs/wo-gh-9/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 94799.728 | runs/wo-gh-9/reviewer-architecture.output.md | null |
| reviewer-design | executed | 99335.615 | runs/wo-gh-9/reviewer-design.output.md | null |
| approver | completed | 0.04 | runs/wo-gh-9/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.093 | runs/wo-gh-9/deployer.packet.md | null |
| observer | executed | 123537.874 | runs/wo-gh-9/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-tests returned fail.
- Human gate: Verdict is rejected, not approved, so a human is required.
