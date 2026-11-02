# Swimlane

Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.

| Station | Status | Duration ms | Artifacts | Cost |
|---|---|---|---|---|
| intake | completed | 0.012 | runs/wo-gh-18/report.json | null |
| brief-writer | executed | 15483.972 | runs/wo-gh-18/brief-writer.output.md | null |
| researcher | executed | 22483.365 | runs/wo-gh-18/researcher.output.md | null |
| writer | failed | 11863.261 | runs/wo-gh-18/writer.packet.md | null |
| media-producer | failed | 206427.004 | runs/wo-gh-18/media-producer.packet.md | null |
| reviewer-facts | failed | 3581.936 | runs/wo-gh-18/reviewer-facts.packet.md | null |
| reviewer-voice | failed | 1118.029 | runs/wo-gh-18/reviewer-voice.packet.md | null |
| reviewer-brand | failed | 683.989 | runs/wo-gh-18/reviewer-brand.packet.md | null |
| reviewer-design | failed | 689.113 | runs/wo-gh-18/reviewer-design.packet.md | null |
| approver | completed | 0.028 | runs/wo-gh-18/report.json | null |
| triage-human | completed | 0.006 | - | null |
| publisher | failed | 669.233 | runs/wo-gh-18/publisher.packet.md | null |
| observer | failed | 16110.104 | runs/wo-gh-18/observer.packet.md | null |

## Decision

- Approver: No reviews were produced in this run, so the verdict is no_reviews; standing project reviews are never counted.
- Human gate: Verdict is no_reviews, not approved, so a human is required.
