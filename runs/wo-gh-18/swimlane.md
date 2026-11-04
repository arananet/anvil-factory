# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.015 | runs/wo-gh-18/report.json | null |
| brief-writer | executed | 14583.094 | runs/wo-gh-18/brief-writer.output.md | null |
| researcher | executed | 20346.404 | runs/wo-gh-18/researcher.output.md | null |
| writer | executed | 23146.632 | runs/wo-gh-18/writer.output.md | null |
| media-producer | executed | 30037.004 | runs/wo-gh-18/media-producer.output.md | null |
| reviewer-facts | executed | 23020.888 | runs/wo-gh-18/reviewer-facts.output.md | null |
| reviewer-voice | executed | 27445.914 | runs/wo-gh-18/reviewer-voice.output.md | null |
| reviewer-brand | executed | 28908.099 | runs/wo-gh-18/reviewer-brand.output.md | null |
| reviewer-design | executed | 24966.491 | runs/wo-gh-18/reviewer-design.output.md | null |
| approver | completed | 0.063 | runs/wo-gh-18/report.json | null |
| triage-human | completed | 0.017 | - | null |
| publisher | executed | 29364.357 | runs/wo-gh-18/publisher.output.md | null |
| observer | executed | 329276.11 | runs/wo-gh-18/observer.output.md | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved, but the work order carries the risk hint 'publishing', so a human is required.
