# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.016 | runs/wo-gh-18/report.json | null |
| brief-writer | executed | 16257.353 | runs/wo-gh-18/brief-writer.output.md | null |
| researcher | executed | 24843.713 | runs/wo-gh-18/researcher.output.md | null |
| writer | executed | 21849.64 | runs/wo-gh-18/writer.output.md | null |
| media-producer | executed | 33145.512 | runs/wo-gh-18/media-producer.output.md | null |
| reviewer-facts | executed | 21050.588 | runs/wo-gh-18/reviewer-facts.output.md | null |
| reviewer-voice | executed | 15434.649 | runs/wo-gh-18/reviewer-voice.output.md | null |
| reviewer-brand | executed | 14308.899 | runs/wo-gh-18/reviewer-brand.output.md | null |
| reviewer-design | executed | 19142.656 | runs/wo-gh-18/reviewer-design.output.md | null |
| approver | completed | 0.044 | runs/wo-gh-18/report.json | null |
| triage-human | completed | 0.017 | - | null |
| publisher | executed | 26573.104 | runs/wo-gh-18/publisher.output.md | null |
| observer | executed | 33822.99 | runs/wo-gh-18/observer.output.md | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved, but the work order carries the risk hint 'publishing', so a human is required.
