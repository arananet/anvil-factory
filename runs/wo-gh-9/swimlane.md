# Swimlane

Routing: 3 reviewers (reduced panel, 2 routed out)

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 34608.819 | runs/wo-gh-9/intake.output.md | null |
| spec-writer | executed | 183755.153 | runs/wo-gh-9/spec-writer.output.md | null |
| test-writer | executed | 211934.263 | runs/wo-gh-9/test-writer.output.md | null |
| builder | executed | 336863.058 | runs/wo-gh-9/builder.output.md | null |
| checks-gate | passed | 27120.936 | runs/wo-gh-9/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 167237.01 | runs/wo-gh-9/reviewer-spec.output.md | null |
| reviewer-security | executed | 55854.727 | runs/wo-gh-9/reviewer-security.output.md | null |
| reviewer-tests | executed | 121098.334 | runs/wo-gh-9/reviewer-tests.output.md | null |
| reviewer-architecture | routed_out | 0.258 | runs/wo-gh-9/reviewer-architecture.packet.md | null |
| reviewer-design | routed_out | 0.836 | runs/wo-gh-9/reviewer-design.packet.md | null |
| approver | completed | 0.034 | runs/wo-gh-9/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.216 | runs/wo-gh-9/deployer.packet.md | null |
| observer | executed | 87087.439 | runs/wo-gh-9/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-tests returned fail. (Expected 3 reviews after routing.)
- Human gate: Verdict is rejected, not approved, so a human is required.
