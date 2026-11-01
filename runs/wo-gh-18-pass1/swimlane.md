# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.01 | runs/wo-gh-18/report.json | null |
| brief-writer | executed | 13692.687 | runs/wo-gh-18/brief-writer.output.md | null |
| researcher | executed | 15954.062 | runs/wo-gh-18/researcher.output.md | null |
| writer | executed | 31446.037 | runs/wo-gh-18/writer.output.md | null |
| media-producer | executed | 63389.659 | runs/wo-gh-18/media-producer.output.md | null |
| reviewer-facts | executed | 24488.038 | runs/wo-gh-18/reviewer-facts.output.md | null |
| reviewer-voice | executed | 13179.542 | runs/wo-gh-18/reviewer-voice.output.md | null |
| reviewer-brand | executed | 14243.535 | runs/wo-gh-18/reviewer-brand.output.md | null |
| reviewer-design | executed | 12813.387 | runs/wo-gh-18/reviewer-design.output.md | null |
| approver | completed | 0.031 | runs/wo-gh-18/report.json | null |
| triage-human | completed | 0.015 | - | null |
| publisher | executed | 19637.62 | runs/wo-gh-18/publisher.output.md | null |
| observer | executed | 77889.369 | runs/wo-gh-18/observer.output.md | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved, but the work order carries the risk hint 'publishing', so a human is required.
