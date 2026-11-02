# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.023 | runs/wo-gh-6/report.json | null |
| spec-writer | failed | 108110.292 | runs/wo-gh-6/spec-writer.packet.md | null |
| test-writer | failed | 10845.256 | runs/wo-gh-6/test-writer.packet.md | null |
| builder | failed | 692.458 | runs/wo-gh-6/builder.packet.md | null |
| checks-gate | passed | 6234.512 | runs/wo-gh-6/checks-gate.pre-review.output.md | null |
| reviewer-spec | failed | 16740.52 | runs/wo-gh-6/reviewer-spec.packet.md | null |
| reviewer-security | failed | 21695.875 | runs/wo-gh-6/reviewer-security.packet.md | null |
| reviewer-tests | failed | 9836.196 | runs/wo-gh-6/reviewer-tests.packet.md | null |
| reviewer-architecture | failed | 12032.435 | runs/wo-gh-6/reviewer-architecture.packet.md | null |
| reviewer-design | failed | 651.604 | runs/wo-gh-6/reviewer-design.packet.md | null |
| approver | completed | 0.039 | runs/wo-gh-6/report.json | null |
| triage-human | completed | 0.007 | - | null |
| deployer | packet_ready | 0.191 | runs/wo-gh-6/deployer.packet.md | null |
| observer | failed | 876.358 | runs/wo-gh-6/observer.packet.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
