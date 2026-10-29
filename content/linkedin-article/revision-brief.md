# Content Brief: LinkedIn Article Final Pass (wo-gh-5)

## Audience

Technical professionals and engineering leaders interested in agentic systems, software factories, and AI-assisted development workflows. Reader profile: experienced enough to evaluate factory patterns, skeptical of hype, values evidence over claims.

## Angle

Personal account of building and testing ANVIL in production, written in first person with technical honesty. The revision completes the narrative arc by adding historical context upfront and closing the Sentia deployment story with the actual verdict.

## Input

The wo-gh-4 revision of the article, committed at `content/linkedin-article/article.md`. All changes are additions or corrections to that baseline, not rewrites.

## Claims and Required Sources

### 1. Software factory concept has deep history (NEW SECTION)

**Section title**: "Not a new idea"  
**Placement**: Between intro and "The line" section

**Claims**:
- The software factory concept dates to 1968
- Bob Bemer proposed it as a productivity approach: standardized tools, shared data, management controls
- Hitachi opened the first actual software factory in 1969, run like a plant for quality and quantity
- 2000s variant: assembly kit pattern (reusable patterns, models, frameworks)
- 2010s-2020s variant: delivery pipeline (continuous delivery, automated tests, security checks)
- The pattern is nearly sixty years old
- What changed is who (or what) works the line

**Source**: Pre-approved text supplied by Edu in work order wo-gh-5, to be integrated verbatim or with only connective edits.

### 2. Sentia deployment reached production with design verdict (REVISION)

**Section**: "The Sentia exam"  
**Scope**: Replace ending from round 4 gate onward

**Claims**:
- Round 4 of wo-gh-1 on arananet/sentia ended changes_requested, human required
- Edu (human at gate) overrode his own gate and deployed the build anyway, accepting minor deviations
- His decision quote: "deploy it as is, accepting the minor deviations"
- Seeing it live, Edu rejected the flat SVG art direction on sight: verdict was design was ugly, expected isometric and 3D imagery
- Design v2 ordered as new work order wo-gh-2 on arananet/sentia
- V2 generated four product renders with Magnific:
  - Hero render
  - Exploded view
  - On-skin render
  - Network scene
- Each render verified individually
- Shared caveat: patch rims read sage/mint rather than brand's deep ink green
- DESIGN.md revised to put imagery first
- Page recomposed around renders, presentation layer only
- Verdict: approved
- All 5 reviews counted, all passing, including reviewer-design
- Suite result: 56 pass, 0 fail, 1 skipped
- Edu gave gate word, v2 is live at https://sentia.info-693.workers.dev
- Deployment date: 2026-10-29
- Closing sentence (verbatim): "The design gate's first full pass came when the design system's ambition matched the product, not when the builder tried harder."

**Source**: Work order wo-gh-5 facts section, change 2. All details verified and approved for publication.

### 3. SDLC reviewer group is five reviewers, not four (CORRECTION)

**Section**: "The line"  
**Scope**: Reviewer walkthrough paragraph

**Claims**:
- Five reviewers work in parallel (was: four)
- Reviewer jobs: spec compliance, security, tests, architecture, design
- Design reviewer checks work against project design system (NEW detail)
- Approver aggregates five reviews into single verdict (was: four)

**Source**: Current ANVIL design state. Historical counts in other sections (Taskline's 4 reviews, design run's 2 of 4, example run's 1 of 2) are factual records of those specific runs and remain unchanged.

### 4. Voice and clarity corrections (FIXES)

**Claims**:
- Round 3 paragraph in Sentia section: sentence fragment made complete prose
- Round 3 paragraph: two very long sentences decompressed without losing facts
- Suite output "Suite: 38 pass, 0 fail, 1 skipped." rewritten as prose
- "Model routing" section: "responses calls" corrected to "response calls"

**Source**: Reviewer-voice findings from wo-gh-4, provided in work order wo-gh-5 change 3.

### 5. Promo text updated for reviewer count (REVISION)

**File**: `content/linkedin-article/promo-post.txt`

**Claim**:
- "four reviewers in parallel" becomes "five reviewers in parallel"

**Source**: Alignment with revised article claims. No other promo changes unless claims are now false; if other claims read stale, flag for review rather than rewrite.

## Presentation constraints

- Preserve input article structure, section order, first-person voice
- Single insertion: history section after intro
- Image markers stay in place
- No em dash (—) or en dash (–) characters
- Never mention author's employer
- Title, credit section, signature stay byte-identical to input
- Final line preserved verbatim: "That's where I stand today. I reserve the right to change my mind tomorrow. In AI, that's not flip-flopping, it's keeping up."
- Publishing hold: output is draft for author review
- Must not state or imply publication has occurred

## Risk notes

- risk_hints: publishing
- This is pre-publication draft requiring author approval before any external distribution
