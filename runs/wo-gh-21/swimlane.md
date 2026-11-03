# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.009 | runs/wo-gh-21/report.json | null |
| spec-writer | executed | 96690.765 | runs/wo-gh-21/spec-writer.output.md | null |
| test-writer | executed | 199307.783 | runs/wo-gh-21/test-writer.output.md | null |
| builder | executed | 368076.076 | runs/wo-gh-21/builder.output.md | null |
| reviewer-spec | executed | 102137.978 | runs/wo-gh-21/reviewer-spec.output.md | null |
| reviewer-security | executed | 68379.39 | runs/wo-gh-21/reviewer-security.output.md | null |
| reviewer-tests | executed | 48731.963 | runs/wo-gh-21/reviewer-tests.output.md | null |
| reviewer-architecture | executed | 137285.174 | runs/wo-gh-21/reviewer-architecture.output.md | null |
| reviewer-design | executed | 66775.086 | runs/wo-gh-21/reviewer-design.output.md | null |
| approver | completed | 0.019 | runs/wo-gh-21/report.json | null |
| triage-human | completed | 0.005 | - | null |
| deployer | packet_ready | 0.05 | runs/wo-gh-21/deployer.packet.md | null |
| observer | executed | 41437.492 | runs/wo-gh-21/observer.output.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted. (Counted 0 reviews, expected 5.)
- Human gate: Verdict is no_reviews, not approved, so a human is required.
