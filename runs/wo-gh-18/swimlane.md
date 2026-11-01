# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.013 | runs/wo-gh-18/report.json | null |
| brief-writer | executed | 34529.614 | runs/wo-gh-18/brief-writer.output.md | null |
| researcher | executed | 72166.449 | runs/wo-gh-18/researcher.output.md | null |
| writer | executed | 113539.388 | runs/wo-gh-18/writer.output.md | null |
| media-producer | failed | 1500184.037 | runs/wo-gh-18/media-producer.packet.md | null |
| reviewer-facts | executed | 25272.079 | runs/wo-gh-18/reviewer-facts.output.md | null |
| reviewer-voice | executed | 21805.812 | runs/wo-gh-18/reviewer-voice.output.md | null |
| reviewer-brand | executed | 25882.664 | runs/wo-gh-18/reviewer-brand.output.md | null |
| reviewer-design | executed | 13176.836 | runs/wo-gh-18/reviewer-design.output.md | null |
| approver | completed | 0.042 | runs/wo-gh-18/report.json | null |
| approver | loopback | 0.0 | - | null |
| triage-human | completed | 0.007 | - | null |
| publisher | executed | 28631.261 | runs/wo-gh-18/publisher.output.md | null |
| observer | executed | 115801.901 | runs/wo-gh-18/observer.output.md | null |

## Decision

- Approver: Reviewers reviewer-facts, reviewer-design requested changes.
- Human gate: Verdict is changes_requested, not approved, so a human is required.
