# README Showcase

Status: proposed
Slug: readme-showcase

## Roles
- implementer: rewrites the README and produces its assets and evidence
- reviewer: checks the change against this spec, including the claim list against main
- qa: checks the scenarios below with executed evidence
- product_owner: owns the purpose and accepts the result at the human gate

## Purpose
A visitor arriving cold from Hacker News, LinkedIn or an awesome list should understand in 30 seconds what ANVIL is, see proof working in under 2 minutes, and have a concrete reason to leave a star. The current README documents well but is written for a reader who already arrived convinced: no demo, no Built by ANVIL proof block, no quickstart above the fold, and stale reviewer counts (it says four software reviewers and four content reviewers where the real count is five). This order turns the README into the showcase without losing the documentation: the existing content moves below the fold, it is not deleted.

## Sequencing requirement
- This order executes only after capability issues 6 to 10 (work orders wo-gh-6 to wo-gh-10: checks gate with protected paths, intake outcomes, risk and surface routing, rendered design review, per job cost) are merged to main. R3 forbids citing capabilities that are not in main, so running earlier would make the showcase untruthful by construction. If the run starts and the capability minimum is not in the branch history, the builder stops and reports instead of writing around it.

## Requirements

### R1. First screen (above the fold)
- Title and badges per the house README template (stack badges, the OpenSpec badge and the Apache 2.0 badge), the quoted one line description, then, in this order:
  1. An animated demo of one real run's cycle: work order, spec, tests, build, reviews, human gate, merged. GIF or embedded MP4, under 90 seconds, produced from a real run's evidence (captures and run reports), never a mockup. If a truthful animated demo cannot be produced inside the line, the run reports that plainly and the README ships with the strongest truthful evidence available instead of a fabricated demo.
  2. A Built by ANVIL block with live links, each with one line on what it proves: Sentia (https://sentia.info-693.workers.dev), Platform25 playable (https://platform25.pages.dev) and the status board (https://anvil-status.pages.dev).
  3. A quickstart of under 5 minutes against arananet/anvil-example-taskline: clone, `anvil onboard` or the example run, and what the reader sees at the end. The quickstart is executed from a clean clone as part of this order's evidence (production form: the quickstart is run, not described).

### R2. Trust section (why you can trust the output)
- Three mechanisms, each with a link to its evidence in the repo, no exceptions:
  1. No station approves its own work: independent reviewers, verdicts read from authoritative review files, parsing that fails closed.
  2. Memory with provenance: the brain learns only through verified promotion against a run report (the project's answer to benign memory contamination, CONTAM-Bench).
  3. A human gate always stands before publishing or deploying to production.

### R3. Claim hygiene
- Every number in the README is verified against the main tree at execution and merge time: station count (25 at 2026-11-02), pipeline count (8), the factory suite test count (94 on main at 2026-11-02, to be re-measured after the capability merges), and any figure the capability items add.
- Corrections this order carries: wherever the current README says four software reviewers, four different reviewers for content, or the approver aggregating four reviews, the real count is five reviewers per line.
- Nothing may be stated as fact that has not landed: the S4 fix is mentioned only because and when it is merged in main, and capability items are cited only when their runs are approved and merged. The roadmap section may name unlanded work only when labelled as roadmap.

### R4. Repo metadata (operator steps after the merge, recorded on the issue)
- Homepage: https://anvil-status.pages.dev
- Topics, exactly this list: ai-agents, multi-agent-systems, software-factory, sdlc, llm, code-generation, code-review, openspec, spec-driven-development, ai-coding, developer-tools, python
- Description: the current one stays. A tightened alternative exists in the launch package and is NOT applied by this order; it needs the owner's confirmation.
- Social preview image, 1280 by 640: the ANVIL wordmark, the simplified station line and the one line quote, at production quality, with generated text verified letter by letter. The line produces the file as run evidence in the workspace launch package; the upload is a GitHub settings web step the API cannot perform, so it is reported as ready for that step, never as applied.

### R5. Closing of the README
- The sections the house template already requires: Contributing (OpenSpec), Documentation, License (Apache 2.0, Copyright Eduardo Arana), Developer (Eduardo Arana) and the ko-fi block.
- Exactly one call to action, at the end of the first screen and repeated at the close, with no variants and no insistence: "If ANVIL is useful to you, a star helps other builders find it."

## Scenarios
- S1: a reader who sees only the first screen can say what ANVIL is, what it built, and how to try it.
- S2: every claim in the trust section links to a file, test or report that backs it.
- S3: a reviewer with the claim list and the main tree can confirm each claim in under a minute per claim.
- S4: the repo card, when shared on LinkedIn, X or Slack, shows the correct image, title and description (image ready per R4; its upload is the named manual step).
- S5: the quickstart, executed from a clean clone by the line, completes in under 5 minutes and its output is recorded as evidence.

## Tests and verification
- A link and claim check over the produced README: every relative link resolves in the tree, every external showcase link answers on the merge day, and the R3 claim list is checked item by item against main. These checks are recorded in the run evidence.
- The rendered README is verified in the real GitHub view (a capture of the rendered page on the run branch), desktop width, with no broken tables or dead images.
- The factory suite stays green; this order changes no factory code, so any suite change is a regression to report, not to fix inside this order.

## Out of scope
- No factory code changes. This order touches README.md, README assets and run evidence only.
- No publishing: no launch posts, no Show HN, no LinkedIn, and no release creation by the line. The release is an operator step after the merge. The order ends at the human gate with the rendered README as evidence.

## Acceptance criteria
- Rendered README verified in the real GitHub view, desktop and mobile, no broken tables or dead images.
- Quickstart executed from a clean clone with its output as evidence, inside the 5 minute budget.
- The R3 claim list signed off by the reviewers against main.
- Built by ANVIL links verified live on the merge day (live check, not from memory).
