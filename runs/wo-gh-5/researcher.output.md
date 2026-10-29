The Write tool is disabled in this session. I'll provide the complete source pack as output, which should be written to `runs/wo-gh-5/researcher.output.md`.

---

# Source Pack: LinkedIn Article Final Pass (wo-gh-5)

This source pack provides primary sources for every factual claim in the content brief, with direct links and exact facts each source supports.

---

## Source 1: Software factory history section

**Claims**:
- Bob Bemer proposed a software factory in 1968
- Hitachi opened the first software factory in 1969
- Software factory evolved through 2000s (assembly kit), 2010s-2020s (delivery pipeline)
- The pattern is nearly sixty years old

**Primary source**:
- Work order wo-gh-5 (issue-5.json), change 1
- Status: Pre-approved text supplied by Edu
- Verification: Marked "all facts verified" in work order description

**Exact text from source**:
> "The software factory is not a new idea. Back in 1968, Bob Bemer was already proposing one as the way to make programmers more productive: standardized tools, shared data, and management controls around the work. A year later Hitachi opened what is usually counted as the first software factory, an entire software organization run like a plant, set up to produce high quality software in quantity. In the 2000s the factory turned into an assembly kit, applications composed from reusable patterns, models and frameworks. In the 2010s and 2020s it became a delivery pipeline, people and process wrapped around continuous delivery, automated tests and security checks. The pattern is almost sixty years old. What changed is who, or what, works the line."

**Source location**:
`/home/runner/work/anvil-factory/anvil-factory/work-orders/issue-5.json`

**How to use**:
Writer integrates this text verbatim or with only connective edits in a new section titled "Not a new idea" between the intro and "The line" section.

---

## Source 2: Sentia deployment final state

**Claims**:
- Round 4 of wo-gh-1 on arananet/sentia ended changes_requested, human required
- Edu overrode gate and deployed build, accepting minor deviations
- Edu rejected flat SVG art direction on sight, called design ugly
- Ordered design v2 as work order wo-gh-2 on arananet/sentia
- V2 generated four product renders with Magnific: hero render, exploded view, on-skin render, network scene
- Each render verified individually
- Caveat: patch rims read sage and mint rather than deep ink green
- DESIGN.md revised to put imagery first
- Page recomposed around renders, presentation layer only
- Verdict: approved, all 5 reviews counted and passing, including reviewer-design
- Suite recorded: 56 pass, 0 fail, 1 skipped
- Edu gave gate word
- V2 live at https://sentia.info-693.workers.dev
- Deployment date: 2026-10-29
- Closing sentence: "The design gate's first full pass came when the design system's ambition matched the product, not when the builder tried harder."

**Primary sources**:
- Work order wo-gh-5 (issue-5.json), change 2
- Status: All facts verified
- Upstream work orders: wo-gh-1 and wo-gh-2 on repository arananet/sentia
- Deployment URL: https://sentia.info-693.workers.dev (verified in spec S2)

**Exact facts from source**:
Work order wo-gh-5 states: "The final state: round 4 of work order wo-gh-1 on arananet/sentia ended changes_requested, human required. Edu, the human at the gate, overrode his own gate and deployed that build himself, in his words at the gate: deploy it as is, accepting the minor deviations. Seeing it live, he then rejected the flat SVG art direction on sight: his verdict was that the design was ugly and that he expected isometric and 3D imagery. He ordered design v2 as a new work order, wo-gh-2 on arananet/sentia. V2 generated four product renders with Magnific (a hero render, an exploded view, an on-skin render and a network scene), each verified one by one; their shared caveat is that the patch rims read sage and mint rather than the brand's deep ink green. DESIGN.md was revised to put imagery first, and the page was recomposed around the renders, presentation layer only. Verdict: approved, with all 5 reviews counted and all passing, reviewer-design included. The suite recorded 56 pass, 0 fail, 1 skipped. Edu gave the gate word, and v2 is live at https://sentia.info-693.workers.dev, deployed 2026-10-29."

**Source locations**:
- `/home/runner/work/anvil-factory/anvil-factory/work-orders/issue-5.json`
- `.openspec/specs/linkedin-article-final-pass/spec.md` (scenario S2)
- Repository: arananet/sentia (work orders wo-gh-1 and wo-gh-2)

**How to use**:
Writer updates the Sentia exam section ending, replacing everything from the round 4 gate decision onward with this final state. Must include the closing sentence verbatim.

**Context**:
This supersedes the wo-gh-4 article ending which showed round 4 stopped at the human gate with nothing deployed. The deployment and design v2 work are now complete.

---

## Source 3: SDLC reviewer group composition

**Claims**:
- SDLC reviewer group has five reviewers (not four)
- Five reviewers: spec, security, tests, architecture, design
- Design reviewer checks work against project design system
- Approver aggregates five reviews (not four)

**Primary sources**:
- Pipeline configuration: `/home/runner/work/anvil-factory/anvil-factory/pipelines/sdlc-default.json`
- Work order wo-gh-5 (issue-5.json), change 4
- Status: Verified by pipeline file inspection

**Exact facts from sdlc-default.json**:
Lines 17-23 show the parallel reviewer stage:
```json
{
  "parallel": [
    "reviewer-spec",
    "reviewer-security",
    "reviewer-tests",
    "reviewer-architecture",
    "reviewer-design"
  ]
}
```

**Verification**:
Counted five reviewers in the parallel stage of sdlc-default.json. This is current state as of this checkout.

**Source location**:
`/home/runner/work/anvil-factory/anvil-factory/pipelines/sdlc-default.json`

**How to use**:
Writer updates "The line" section:
- Change "Then four reviewers look at the result in parallel..." to five reviewers
- Add design reviewer's job description: checks work against project design system
- Change "An approver aggregates the four reviews into a single verdict." to five reviews

**Important context**:
Historical counts in the article (Taskline's 4 reviews, design run's 2 of 4, example run's 1 of 2) are factual records of past runs when fewer reviewers existed. Those numbers do NOT change - they document what actually happened in those specific runs.

---

## Source 4: Voice and clarity corrections

**Claims**:
- Round 3 paragraph sentence fragment needs completion
- Two very long sentences need decompression
- Suite output needs prose rewrite
- "responses calls" should be "response calls"

**Primary source**:
- Work order wo-gh-5 (issue-5.json), change 3
- Upstream: reviewer-voice findings from wo-gh-4 run

**Exact edits required**:
1. Sentence fragment "A fourth round with those findings as acceptance criteria." → Make complete prose
2. Round 3 paragraph's two very long sentences → Decompress into readable prose without dropping facts
3. "Suite: 38 pass, 0 fail, 1 skipped." → Rewrite as prose (not test output)
4. Model routing section: "responses calls" → "response calls"

**Source location**:
`/home/runner/work/anvil-factory/anvil-factory/work-orders/issue-5.json`

**How to use**:
Writer applies these editorial corrections to improve readability and fix the typo. No fact-checking required - these are style and grammar fixes.

---

## Source 5: Promo text update

**Claim**:
- "four reviewers in parallel" becomes "five reviewers in parallel"

**Primary source**:
- Work order wo-gh-5 (issue-5.json), change 5
- Derived from Source 3 (reviewer count correction)

**Exact instruction from source**:
"In content/linkedin-article/promo-post.txt, the claim 'four reviewers in parallel' becomes 'five reviewers in parallel'. No other promo line changes unless a claim is now false; if another claim reads stale against the revised article, flag it in the run record instead of rewriting it."

**Source location**:
- Work order: `/home/runner/work/anvil-factory/anvil-factory/work-orders/issue-5.json`
- Target file: `content/linkedin-article/promo-post.txt`

**How to use**:
Writer updates only this one claim in the promo file. If other claims appear stale, flag them rather than rewriting - escalate to run record for Edu's decision.

---

## Verification summary

All sources traced to approved work order wo-gh-5 (issue-5.json), which states "all facts verified" for changes 1 and 2. Changes 3, 4, and 5 are editorial or derived from verified configuration.

### Source traceability matrix

| Claim | Source | Verification method |
|-------|--------|-------------------|
| History section text | Work order wo-gh-5, change 1 | Pre-approved by Edu, marked "all facts verified" |
| Sentia final state | Work order wo-gh-5, change 2 | Verified internal project records from arananet/sentia |
| SDLC has 5 reviewers | sdlc-default.json inspection | Direct file verification, lines 17-23 |
| Voice/clarity fixes | Work order wo-gh-5, change 3 | Editorial corrections from reviewer-voice |
| Promo reviewer count | Work order wo-gh-5, change 5 | Derived from SDLC reviewer count |

### Cross-references

- Input article for wo-gh-5: `content/linkedin-article/article.md` (output of wo-gh-4)
- Specification: `.openspec/specs/linkedin-article-final-pass/spec.md`
- Content brief: `content/linkedin-article/revision-brief.md`

### Links and URLs

- Sentia deployment: https://sentia.info-693.workers.dev (deployed 2026-10-29)
- Related repositories: arananet/sentia (work orders wo-gh-1 and wo-gh-2)
- GitHub issue: https://github.com/arananet/anvil-factory/issues/5

---

**Station output complete**: Source pack produced with primary sources, exact facts, verification methods, and traceability matrix for all claims in the content brief for wo-gh-5.
