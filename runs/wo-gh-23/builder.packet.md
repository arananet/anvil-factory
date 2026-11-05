# Task packet: builder

## Station prompt

# Builder

## Role
Implement the spec so the scenario tests pass.

## Inputs
- spec
- tests

## Outputs
- code change

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.
- **Design citation**: When authoring or revising design/DESIGN.md, include a "Design knowledge sources" note citing the knowledge entries you drew from by data kind and entry name (e.g., "Style: modern-minimal", "Palette: metrics-blue", "Guideline: accessibility - contrast ratio"). If the knowledge came from an operator-supplied pack, cite it as "operator-supplied pack entry" without naming the pack's origin.

### Visual Output Quality Verification

When your packet includes a Quality Charter section (visual runs only), you must verify each produced output against the run's reference anchors and charter criteria before the review step:

1. **Read the output**: Examine each visual deliverable you produce (images, UI components, rendered interfaces).

2. **Compare against anchors**: If reference anchors are provided, compare your output against them. Check how your output measures up to the anchor's quality bar across the charter criteria.

3. **Check charter criteria**: Evaluate your output against the observable criteria from the Quality Charter:
   - For physical products: materials, light, contact, scale
   - For games/illustrations: the stated standard from the project design system

4. **Record the comparison**: Document your findings in the run evidence directory (runs/{work_order_id}/evidence/) as a JSON file named `{output_filename}.comparison.json` with this structure:

```json
{
  "output": "path/to/generated/output.png",
  "anchor_cited": "path/to/reference/anchor.png or null if none",
  "criteria_checked": ["materials", "light", "contact", "scale"],
  "gaps": [
    {
      "criterion": "materials",
      "description": "Surfaces read as plastic rather than the metal shown in anchor"
    }
  ],
  "statement": "Explicit statement: 'No gaps found at charter bar' or description of gaps identified"
}
```

5. **Evidence, not verdict**: Your comparison is evidence for reviewers, not a final verdict. Record what you observe; reviewers are not bound by your self-assessment.

This verification step only applies when the Quality Charter section is present in your packet. For non-visual work, this step does not apply.


## Project design

### Design tokens

```json
{
  "colors": {
    "primary": "TODO",
    "secondary": "TODO",
    "accent": "TODO",
    "background": "TODO",
    "surface": "TODO",
    "text": "TODO",
    "text-secondary": "TODO",
    "error": "TODO",
    "warning": "TODO",
    "success": "TODO",
    "info": "TODO"
  },
  "typography": {
    "font-family-base": "TODO",
    "font-family-heading": "TODO",
    "font-family-mono": "TODO",
    "font-size-base": "TODO",
    "font-size-scale": "TODO",
    "line-height-base": "TODO",
    "line-height-heading": "TODO"
  },
  "spacing": {
    "unit": "TODO",
    "scale": [
      "TODO"
    ]
  },
  "layout": {
    "max-width": "TODO",
    "breakpoint-mobile": "TODO",
    "breakpoint-tablet": "TODO",
    "breakpoint-desktop": "TODO"
  },
  "motion": {
    "duration-fast": "TODO",
    "duration-base": "TODO",
    "duration-slow": "TODO",
    "easing-standard": "TODO",
    "easing-enter": "TODO",
    "easing-exit": "TODO"
  }
}
```

### Quality bars

for Product Pages

These bars apply to every product page or interface this project ships.

### Visual Hierarchy
- [ ] Clear content hierarchy with size, weight, and spacing
- [ ] Important actions are visually prominent
- [ ] Related elements are grouped

### Scale Contrast
- [ ] Minimum 4.5:1 contrast ratio for normal text
- [ ] Minimum 3:1 contrast ratio for large text (18pt+)
- [ ] Interactive elements have sufficient contrast

### Spacing Rhythm
- [ ] Consistent spacing scale used throughout
- [ ] Whitespace creates clear content boundaries
- [ ] Spacing adapts appropriately to different screen sizes

### Responsive Behavior
- [ ] Layout works on mobile, tablet, and desktop
- [ ] Touch targets are at least 44x44px on mobile
- [ ] Text is readable without zooming on any device
- [ ] No horizontal scrolling on standard viewports


## Design knowledge

**Authority**: The project's own design system (design/DESIGN.md, design/tokens.json) is the authority for this project. The knowledge base below is reference material that the design system may draw from. On any conflict, the project's design system wins. A deviation from the knowledge base alone is not a finding; a deviation from the project's design system is.

**Note**: No product type slice matched. General guidelines only.

### Product Type: Undeclared

No specific product type declared. Using general guidelines only.

### UX Guidelines

**Accessibility:**
- Maintain minimum 4.5:1 contrast ratio for normal text, 3:1 for large text (18pt+)
- Touch targets must be at least 44x44px on mobile devices

**Feedback:**
- Loading states should appear after 300ms delay to avoid flashing
- Provide immediate visual feedback for user actions

**Forms:**
- Form fields should have clear labels and validation feedback
- Error messages should explain what went wrong and how to fix it

**Hierarchy:**
- Establish clear visual hierarchy using size, weight, and color
- Important actions should be visually prominent and easy to locate

**Motion:**
- Keep animation durations between 200-400ms for most transitions
- Provide reduced motion alternatives for users with vestibular sensitivity

**Responsive:**
- Test layouts at mobile (320-768px), tablet (768-1024px), and desktop (1024px+) breakpoints
- Avoid horizontal scrolling on standard viewports

**Spacing:**
- Use consistent spacing scale throughout (e.g., 4px, 8px, 16px, 24px, 32px)
- Group related elements together with whitespace separating distinct sections


## Work order

- id: wo-gh-23
- kind: task
- title: Showcase README: first screen demo, Built by ANVIL, quickstart, trust section
- source: github-issue
- description: Implement the spec in .openspec/specs/readme-showcase/spec.md: rewrite README.md of this repository into the launch showcase, keeping the existing documentation below the fold. Pipeline for this order is sdlc-default (software domain, full reviewer set), selected by the run workflow. The run touches README.md, README assets under docs/ or assets/ as the builder judges cleanest, and run evidence only. No factory code changes.

SEQUENCING GATE: execute this order only from a main that already carries the capability minimum, issues 6 to 10 (wo-gh-6 checks gate with the S4 base ref fix, wo-gh-7 intake outcomes, wo-gh-8 risk and surface routing, wo-gh-9 rendered design review, wo-gh-10 per job cost) merged. Verify their presence in the branch history before building (the checks gate code and docs, the intake outcomes, the routing, the rendered review and the cost fields in run reports). If the minimum is not in the history, stop and report instead of running.

Build, per the spec requirements:

R1, first screen: house template header (title, stack badges plus OpenSpec and Apache 2.0 badges, the quoted one line description), then in order: (1) the animated demo of one real run cycle (work order, spec, tests, build, reviews, human gate, merged), GIF or embedded MP4 under 90 seconds, produced from a real run's own evidence (captures and report data of runs already on record in this repo, for example a capability run or wo-gh-20), never a mockup or a staged animation of events that did not happen; if a truthful animated demo cannot be produced inside the line, say so plainly in the run output and ship the README with the strongest truthful static evidence instead; (2) the Built by ANVIL block with live links to Sentia (https://sentia.info-693.workers.dev), Platform25 (https://platform25.pages.dev) and the status board (https://anvil-status.pages.dev), one line each on what it proves; (3) the quickstart against arananet/anvil-example-taskline, under 5 minutes, which the line EXECUTES from a clean clone during the run and records (commands, duration, output tail) as evidence.

R2, trust section: the three mechanisms (no station approves its own work, with verdicts read from authoritative review files and parsing that fails closed; memory promoted only with run report provenance, the CONTAM-Bench answer; a human gate before publishing or production deploys), each claim linked to the repo file, test or report that backs it.

R3, claim hygiene: verify every number against the tree at run time (station count, pipeline count, factory suite size measured fresh, reviewer counts corrected to five wherever the current README says four, including the approver line in the station table). Cite S4 and the capability items only as merged fact, because the gate above guarantees they are in main; anything not in main goes to a roadmap section labelled as roadmap or stays out.

R4, metadata is an OPERATOR step after the merge, not the line's: the line's part is only to produce the social preview image (1280 by 640, ANVIL wordmark, simplified station line, the one line quote, production quality, any generated text verified letter by letter) as a run evidence file named social-preview.png, and to record in its output that the homepage, topics and image upload are operator steps. The line does not call the GitHub settings API and does not change the repo description.

R5, closing: the house template sections (Contributing pointing at OpenSpec, Documentation, License Apache 2.0 with Copyright Eduardo Arana, Developer Eduardo Arana, the ko-fi block), and exactly one star call to action, worded exactly as the spec states, at the end of the first screen and repeated at the close.

Tests and evidence, per the spec: a link and claim check over the produced README recorded in the run evidence (relative links resolve in the tree, the three showcase links answer live during the run, the R3 claim list item by item against the tree); a capture of the rendered README from the real GitHub view of the run branch at desktop width; the quickstart execution record. The factory suite must stay green; any suite change is reported, not fixed inside this order.

Guardrails: no em dash or en dash character in any produced file (project style rule). The reviewer writes its review to the authoritative review file named in its packet; prose outside that file is not a review. Nothing in this order publishes anything: no posts, no release, no metadata changes by the line.

GitHub issue: https://github.com/arananet/anvil-factory/issues/23

GATE LOOPBACK BRIEF (operator, after run 41944293495):

The first run's verdict was no_reviews: the checks gate failed (suite exit 1, 502 tests, 3 failures; protected paths verdict PASS) and every reviewer was skipped by design, so the README product is unjudged, not rejected. The operator reproduced all three failures locally against the run branch tree (the showcase module alone: 22 tests, the same 3 failures). All three are defects in tests/test_readme_showcase.py, the test-writer station's output, not in the builder's README:

1. test_showcase_external_links_valid asserts live answers through urllib with its default user agent. The operator verified from two separate networks: all three showcase links (Sentia, Platform25, the status board) answer 200 to a browser user agent and 403 to the Python urllib agent, which is Cloudflare bot filtering, not an outage. A deterministic gate test must not assert live network behavior through a bot-filtered agent. Fix: the test skips unless the environment sets ANVIL_LIVE_TESTS=1, and when enabled it sends a browser user agent. The live verification itself stays where the spec puts it: in the run evidence (evidence/link-and-claim-verification.md), refreshed during this run.

2. test_station_count_accurate_r3: the test's own station counter returned 0 against the current tree. The factory's station catalog is the stations/ directory loaded by anvil/stations.py (StationRegistry): it holds 27 stations, which is exactly what the README claims, up from 25 before the capability program added the checks-gate and reviewer-ux stations. Fix: the counter counts the registry the factory itself loads and asserts the README claim equals it.

3. test_factory_suite_can_run shells out to pytest, which is not a project dependency and is absent from the run environment. The canonical suite command is the unittest discover command the checks gate itself executes, so a nested suite invocation inside the suite is redundant and recursive. Fix: remove the nested invocation, or reduce it to a collection-only check that does not execute the suite.

Discipline for this loopback, per the wo-gh-7 closing precedent: the builder does not touch tests/, anvil.json or pipelines/ (protected paths passed in run 1 and must keep passing); the three test fixes belong to the test-writer station. The README product from run 1 stands as the base: this loopback changes the three tests and refreshes run evidence only. The operator has staged Playwright and Chromium in the execute workflow (the same staging the wo-gh-9 line needed), so the rendered README capture the spec requires can be produced in this run; a capture_failure.txt citing missing Playwright must not recur for the desktop capture.
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
