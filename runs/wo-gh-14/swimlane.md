# Swimlane

Routing: 5 reviewers (reduced panel, 1 routed out)

**Cost**: No measured steps (10 executed steps)

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | executed | 49783.807 | runs/wo-gh-14/intake.output.md | null |
| spec-writer | executed | 40742.728 | runs/wo-gh-14/spec-writer.output.md | null |
| test-writer | executed | 193898.449 | runs/wo-gh-14/test-writer.output.md | null |
| builder | executed | 424834.269 | runs/wo-gh-14/builder.output.md | null |
| checks-gate | passed | 31888.686 | runs/wo-gh-14/checks-gate.pre-review.output.md | null |
| reviewer-spec | executed | 150858.581 | runs/wo-gh-14/reviewer-spec.output.md | null |
| reviewer-security | executed | 105879.267 | runs/wo-gh-14/reviewer-security.output.md | null |
| reviewer-tests | executed | 50721.195 | runs/wo-gh-14/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 111740.363 | runs/wo-gh-14/reviewer-architecture.output.md | null |
| reviewer-design | executed | 167510.842 | runs/wo-gh-14/reviewer-design.output.md | null |
| reviewer-ux | routed_out | 0.841 | runs/wo-gh-14/reviewer-ux.packet.md | null |
| approver | completed | 0.033 | runs/wo-gh-14/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.006 | - | null |
| deployer | packet_ready | 0.041 | runs/wo-gh-14/deployer.packet.md | null |
| observer | executed | 52574.038 | runs/wo-gh-14/observer.output.md | null |

## Decision

- Approver: Reviewer reviewer-spec returned fail. (Expected 5 reviews after routing.)
- Human gate: Verdict is rejected, not approved, so a human is required.
