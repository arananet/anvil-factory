# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.02 | runs/wo-gh-5/report.json | null |
| brief-writer | executed | 83963.308 | runs/wo-gh-5/brief-writer.output.md | null |
| researcher | executed | 139241.664 | runs/wo-gh-5/researcher.output.md | null |
| writer | executed | 418084.365 | runs/wo-gh-5/writer.output.md | null |
| media-producer | executed | 124507.124 | runs/wo-gh-5/media-producer.output.md | null |
| reviewer-facts | executed | 130199.358 | runs/wo-gh-5/reviewer-facts.output.md | null |
| reviewer-voice | executed | 177758.781 | runs/wo-gh-5/reviewer-voice.output.md | null |
| reviewer-platform | failed | 58366.703 | runs/wo-gh-5/reviewer-platform.packet.md | null |
| reviewer-brand | executed | 80556.897 | runs/wo-gh-5/reviewer-brand.output.md | null |
| reviewer-design | executed | 41126.617 | runs/wo-gh-5/reviewer-design.output.md | null |
| approver | completed | 0.041 | runs/wo-gh-5/report.json | null |
| triage-human | completed | 0.015 | - | null |
| publisher | failed | 47117.159 | runs/wo-gh-5/publisher.packet.md | null |
| observer | failed | 16638.689 | runs/wo-gh-5/observer.packet.md | null |

## Decision

- Approver: All counted reviews passed.
- Human gate: Verdict approved, but the work order carries the risk hint 'publishing', so a human is required.
