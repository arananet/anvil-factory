# ANVIL Landing Page

Status: proposed
Slug: landing-page

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

The factory repo explains itself in pieces: a showcase README for readers who already arrived, a generated status page that reports runs, and a documentation set written for operators. Nothing in the repo is a front door: a page a visitor can land on that says what ANVIL is, what problem it solves, how the line works, and what makes it different from a single agent with a long prompt. The repo homepage still points at the run status page, a target the owner dismissed on 2026-11-04 because it does not tell the story and does not show the factory's products. This order builds that front door as a designed landing page living in this repo, written and reviewed by the line itself, with every claim on it verified the way the factory verifies everything else.

## Requirements

### R1. One self contained page in the repo
- The page is a single HTML file at site/index.html in this repo. Its CSS is inline in the file. It references no external asset: no webfonts, no CDN files, no external images, no external stylesheets or scripts. It contains no JavaScript and renders completely with scripts disabled.
- The page is in English. It carries a descriptive title and a meta description naming ANVIL and its expansion, Agentic Network for Verified Implementation Lifecycle.

### R2. Content: what the page must explain
- Sections, in this order, each with its own anchor: (1) Hero: the name ANVIL, its expansion, the one line promise (a software factory where no agent approves its own work), and two calls to action, the GitHub repo and the quickstart section. (2) The problem: agents that write, test and approve their own work, and demos nobody can audit after the fact. (3) How it works: the sdlc-default line as the visual centerpiece (intake, spec writer, test writer, builder, the five reviewers in parallel, approver, human gate, deployer, observer), plus the facts that pipelines are composable and that specs are written before implementation. (4) What makes it different: no self approval, with each reviewer writing only its own review file; verified memory, whose learnings enter station context only after deterministic code checks their provenance against the run record, with proposals quarantined until then; a deterministic checks gate that runs the project suite before any model station; rendered design review, where interface work is judged from rendered captures, not from code alone; post deploy health verification; and per run cost recorded in the run report. (5) Proof: ANVIL built real things, with links: Sentia, Platform25, this factory's own work orders, and release v0.1.0. (6) Quickstart: the exact commands from the README quickstart. (7) What ANVIL is not: not a single agent, not a prompt library, and not unsupervised autonomy; the human gate is presented as a feature. (8) Footer: Apache 2.0 license with Copyright Eduardo Arana, Developer Eduardo Arana, and links to the repo, the release, the documentation index and the run status page.

### R3. Claims hygiene
- Every number printed on the page (station count, pipeline count, reviewer count in sdlc-default, test suite size, release version) is verified at build time from the tree or by running the suite, and the page states counts as of its build. At filing time the operator verified 27 stations and 8 pipelines on main; those figures are a starting point for the builder to re-verify, not text to copy blindly.
- Only merged, shipped capabilities may be described as factory capabilities. Work that is filed or staged but unmerged at build time (at filing time: the deterministic preflight of issue 28 and the memory consolidation of issue 33) must not appear on the page as something ANVIL does today. The builder re-checks main at build time; if such work has merged by then, it may be included only with the merge as evidence.
- The page names no employer of the owner, links no unpublished article or video, and repeats no claim the README showcase pass already corrected.

### R4. Design bar
- Production quality landing page, not a styled report. It uses the Arananet dark palette the status page established (near black background, orange accent FF5C00, light text) with a real landing hierarchy: an oversized display headline in the hero, a consistent spacing scale, the line diagram rendered as inline SVG with every label spelled correctly, cards for the differences section, and monospace type reserved for code and labels.
- Responsive: the layout adapts down to a 360 px wide phone viewport with no horizontal scrolling. All text meets WCAG 4.5:1 contrast minimums. Interactive targets are at least 44 px. The builder produces desktop and mobile rendered captures of the finished page as run evidence, and reviewer-design judges the page from those captures like any other interface work.

### R5. Deterministic page checks
- New tests in the factory suite read the real site/index.html and assert: the file exists and is one HTML document with a viewport meta; it loads no external asset (no script or stylesheet references and no externally hosted image, font or media source); the eight section anchors of R2 are present in order; the station and pipeline counts printed on the page equal the counts computed from the stations and pipelines trees at test time; the quickstart commands printed on the page appear in the README quickstart; and the file contains no em dash or en dash character.
- The tests must read the page and the trees themselves. A test that asserts against a copy of the content, or that never opens site/index.html, is a facade test and fails this spec on sight (the lesson of issue 9).

### R6. Scope limits and hosting readiness
- This order creates site/index.html, docs/LANDING-PAGE.md and the new test files. It changes nothing under anvil/, nothing in the status page or its generator, nothing in the README, and no workflow. It deploys nothing, enables no GitHub Pages, and changes no repo metadata.
- docs/LANDING-PAGE.md records how to preview the page locally and the two hosting routes with their exact steps: (a) Cloudflare Pages serving the site/ folder, the route the run status page already uses, deployable by the operator with the vault credential; (b) GitHub Pages, which the owner must enable in the repo Settings because the vault token cannot (see docs/OPERATOR-REQUIREMENTS.md). The document recommends route (a) and records that, after the owner approves the page at the human gate, the operator deploys it and updates the repo homepage to the page URL, retiring the status page URL the owner dismissed. Those steps are operator follow up after this order, not part of its run.

### Guardrails
- Python standard library only for the tests, consistent with the factory spine. No new dependency, no site generator, no framework.
- Frozen surfaces: the review parse contract, the reviewer prompts and their Output Format sections, the review producer mechanisms, the checks gate behavior, and the status page generator.
- No em dash or en dash character in any produced file (project style rule).
- Nothing in this order publishes or deploys anything, and no page content goes live anywhere during the run.

## Scenarios

### Scenario: The page exists and stands alone
- S1: Given the run has completed, when a reader opens site/index.html from a plain file server with scripts disabled, then the page renders completely, loads no external asset, and every image or diagram it shows is inline in the file.

### Scenario: The story is complete and in order
- S2: Given the finished page, when its anchors are listed, then the eight sections of R2 appear in the specified order, the hero names ANVIL and its expansion, and the footer carries the Apache 2.0 license line with Copyright Eduardo Arana.

### Scenario: Printed counts equal the tree
- S3: Given the factory suite runs, when the R5 tests compute the station and pipeline counts from the trees, then the counts printed on the page equal those computed counts, and a page edited to a wrong count fails the suite.

### Scenario: Quickstart commands are the real ones
- S4: Given the finished page, when its quickstart block is compared with the README, then every command it prints appears in the README quickstart section.

### Scenario: The design evidence is rendered, not asserted
- S5: Given the finished page, when the run evidence is inspected, then it contains desktop and mobile captures of the page itself, the mobile capture shows no horizontal scrolling at phone width, and reviewer-design's review cites the captures.

### Scenario: The run stays inside its fence
- S6: Given the run delta, when the changed files are listed, then every change is inside site/, docs/LANDING-PAGE.md, or the new test files; no file under anvil/, no workflow, no README and no status page file changed.

### Scenario: Hosting is documented and nothing was deployed
- S7: Given docs/LANDING-PAGE.md, when it is read, then it names both hosting routes and their steps, recommends Cloudflare Pages, and states that this order deployed nothing and that the homepage update happens after the owner's gate approval.
