# Task packet: reviewer-tests

## Station prompt

# Reviewer Tests

## Role
Check that tests are real, mapped, and passing.

## Inputs
- spec
- tests

## Outputs
- review

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.

## Output Format

Return a JSON object with this structure:

{
  "station": "reviewer-tests",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-tests", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.


## Work order

- id: wo-gh-35
- kind: feature
- title: ANVIL landing page in the factory repo: a designed page that explains what ANVIL is
- source: github-issue
- description: Implement the spec in .openspec/specs/landing-page/spec.md. Owner's request 2026-11-07: a good looking page for ANVIL in its own repo that explains what it is. Pipeline for this order is sdlc-default (software domain, full reviewer set including reviewer-design), selected by the run workflow. The run creates site/index.html (one self contained page, inline CSS, no external assets, no JavaScript, English), docs/LANDING-PAGE.md (preview and hosting notes), and new test files. It changes no spine code.

STAGING: this order is filed and staged only. Execution starts on the owner's word. At filing time the AI Gateway Anthropic route answers 402 insufficient_balance (verified in the gateway logs on 2026-11-07), so no run can complete until the owner tops up the gateway; do not fire the run before that is resolved, and do not present a gateway failure as a page failure.

Build, per the spec requirements:

R1, the artifact: a single HTML file at site/index.html, inline CSS, zero external assets, zero JavaScript, descriptive title and meta description naming ANVIL (Agentic Network for Verified Implementation Lifecycle).

R2, the story, in order: hero (name, expansion, the one line promise that no agent approves its own work, calls to action to the repo and the quickstart); the problem (self approving agents, unauditable demos); how it works (the sdlc-default line as inline SVG centerpiece: intake, spec writer, test writer, builder, five reviewers in parallel, approver, human gate, deployer, observer; composable pipelines; spec before implementation); what makes it different (no self approval and one authoritative review file per reviewer; verified memory with provenance checked against the run record and proposals quarantined; the deterministic checks gate before model spend; rendered design review from captures; post deploy health verification; per run cost in the report); proof (Sentia, Platform25, this repo's own work orders, release v0.1.0, all linked); quickstart (the exact README commands); what ANVIL is not (not a single agent, not a prompt library, not unsupervised autonomy; the human gate as a feature); footer (Apache 2.0, Copyright Eduardo Arana, Developer Eduardo Arana, links to the repo, the release, the docs index and the run status page).

R3, claims hygiene: verify every printed number from the tree or the suite at build time (operator verified 27 stations and 8 pipelines on main at filing; re-verify, do not copy blindly). Describe only merged capabilities: issues 28 and 33 are staged and unmerged at filing time and must not appear as shipped capabilities unless they have merged into main before this run executes, with the merge as evidence. Name no employer of the owner; link no unpublished article or video.

R4, design bar: production quality landing in the Arananet dark palette (near black background, orange accent FF5C00, light text), oversized hero headline, consistent spacing scale, the line diagram as inline SVG with every label spelled correctly, cards for the differences, monospace only for code and labels. Responsive to a 360 px phone viewport with no horizontal scrolling, WCAG 4.5:1 text contrast, interactive targets at least 44 px. Produce desktop and mobile rendered captures of the finished page as run evidence for reviewer-design.

R5, deterministic checks: new suite tests read the real site/index.html and assert single document with viewport meta, no external asset loading, the eight section anchors in order, printed station and pipeline counts equal to the counts computed from the trees at test time, quickstart commands present in the README quickstart, and no em or en dash characters. Tests that never open the real page are facade tests and fail the order (issue 9's lesson).

R6, scope and hosting readiness: create only site/index.html, docs/LANDING-PAGE.md and the new test files. docs/LANDING-PAGE.md records the local preview steps and both hosting routes (Cloudflare Pages from site/, recommended, deployable by the operator with the vault credential; GitHub Pages, which the owner must enable in Settings because the vault token cannot), and states that this order deploys nothing and that the repo homepage update happens as operator follow up after the owner's gate approval.

Guardrails: Python standard library only for tests; no site generator, no framework, no new dependency. Frozen surfaces: the review parse contract, the reviewer prompts and their Output Format sections, the review producer mechanisms, the checks gate behavior, and the status page generator. Do not create, modify, or delete any file under tests/ that exists at the base ref (the checks gate protects base ref test files); new tests arrive as new files. No changes under anvil/, no README changes, no workflow changes, no status page changes. No em dash or en dash character in any produced file. The reviewer writes its review to the authoritative review file named in its packet; prose outside that file is not a review. Nothing in this order publishes or deploys anything.

GitHub issue: https://github.com/arananet/anvil-factory/issues/35
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: passed
- reviewer-spec: executed
- reviewer-security: routed_out

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-35/reviewer-tests.review.json. The free output transcript stays as provenance and is never parsed for a review.
