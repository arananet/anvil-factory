# Task packet: intake

## Station prompt

# Intake Station

## Role

Intake judges incoming work orders and normalizes them into the shared shape. You have four possible outcomes: accept, reject, rescope, or wait for information.

## Outcomes

### Accepted

The work order is buildable as stated. Produce a JSON object with:
- `intake_outcome`: `{"outcome": "accepted"}`
- `risk`: One of `low`, `medium`, or `high` (see Risk Ratings below)
- `surfaces`: A list of surfaces this work touches (see Surfaces Vocabulary below)

### Rejected

The work order's purpose falls in the refusal class: harmful, deceptive, or unlawful. Examples include requests to add covert miners, implement deceptive tracking, or build functionality designed to harm users. Never quietly reformulate refused work into something buildable.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "rejected", "reasons": ["reason 1", "reason 2", ...]}`

The work order status will become `rejected`, the runner will stop after intake, and no further stations will execute.

### Rescoped

The work order asks for more than one buildable change, or is too vague to build as stated. Cut it down to one buildable scope and record what was removed and why.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "rescoped", "rescoped_description": "The buildable scope", "reasons": ["what was cut and why"]}`
- `risk`: Risk rating for the rescoped work
- `surfaces`: Surfaces the rescoped work touches

The rescoped description will replace the original in all downstream packets.

### Waiting for Information

The work order lacks information you need to judge it. Record your questions.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "waiting_info", "questions": ["question 1", "question 2", ...]}`

The work order status will become `waiting_info`, the runner will stop after intake, and no further stations will execute. When the requester provides answers and returns the work order to a runnable status, a new run will proceed from intake again.

## Risk Ratings

- **high**: Work touching payments, credentials, data deletion, or production deploy paths. High blast radius or irreversible changes.
- **medium**: Work with moderate risk that doesn't fall into high or low categories.
- **low**: Small, reversible changes with limited blast radius.

## Surfaces Vocabulary

Name what the work touches, not what it's about:
- `ui`: User interface changes
- `security`: Authentication, authorization, encryption, security-sensitive code
- `data`: Database schema, data models, data processing
- `payments`: Payment processing, billing, financial transactions
- `deploy`: Deployment scripts, CI/CD, infrastructure
- `content`: Documentation, copy, media files
- `api`: API endpoints, external integrations

Use the surfaces that apply. One work order can touch multiple surfaces.

## Output Format

Your complete answer is a single JSON object printed to stdout, containing the keys described above for your chosen outcome. The runner parses this JSON to determine how to proceed.


## Work order

- id: wo-gh-13
- kind: feature
- title: Status dashboard shows the lifecycle stage per work order
- source: github-issue
- description: Implement the spec in .openspec/specs/status-lifecycle-stages/spec.md in the factory's status page generation.

Build, per the spec scenarios:

S1: stage derivation as a pure function of the job's latest run data: SPEC from the recorded spec stage, BUILD from the builder step, REVIEW from reviewer steps, APPROVED from the decision's approver verdict, the current stage being the furthest the evidence supports, and a job with no runs showing nothing reached.

S2: MERGED comes only from an actual merge record (merged pull request or merged run branch) in the merge data the generator consumes; an approved job with no merge record shows APPROVED and MERGED stays unmarked; with a merge record it shows MERGED. Derivation never infers merges from branch names or commit messages and never calls the network.

S3: NEEDS HUMAN derives from the decision's human_required flag for any reason it was set, rendered with a visually prominent badge treatment alongside the current stage; absent when the flag is false.

S4: intake states compose: a latest run that ended parked (waiting_info) shows PARKED and one that ended rejected shows REJECTED, instead of a stage progression.

S5: the generated page is one board: one row per work order carrying its id, title, the stage sequence with reached stages marked and the current stage highlighted, the NEEDS HUMAN badge when it applies, and a link from each row to that job's swimlane or run detail. Regenerating from the same data produces the same board. The derivation and rendering live in the factory's status page generator so every surface it generates (the factory status page and the example project's page) renders the board the same way.

Tests covering S1 to S5 from report fixtures in the factory suite style, including the approved-but-unmerged case and the human_required case, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/13

Operator standing note for every round of this order: the builder must not create or modify anything under .github/workflows/ (the Actions token cannot push workflow changes; a run that touches them loses its commit-back). Tooling the run needs is staged by the operator in the workflow before the line step. Test changes are written by the test-writer station; the builder must not modify tests/, anvil.json or pipelines/. Tests must be real: every test calls the implementation it names and asserts behavior, never the mere existence of data structures.

LOOPBACK 1 (after run 41783359038, verdict changes_requested, reviews counted 6 of 6, checks gate passed). The counted findings, verbatim in substance, all bounded:

A. Spec S5, also reviewer-ux's user flow and accessibility findings (reviewer-spec and reviewer-ux): board rows do not link to the job's detail. The work order ID renders as plain text in an h3, the row container carries the id, and the detailed run section has no id attribute, so anchor navigation is impossible and keyboard and screen reader users get no navigable element. Fix: each board row's work order ID becomes a real link, an a element with href pointing to that job's detailed run section (for example #wo-id-detail), and the detailed section carries the matching id attribute. Real links close the keyboard reachability and link semantics findings at the same time.

B. Contrast (reviewer-design): .muted (#9A9A9A at 13px), the footer (#8A8A8A at 13px) and .board-description (#9A9A9A at 13px) on the #0C0C0C background were flagged as possibly below the 4.5:1 minimum for normal text. Resolve with evidence: compute the WCAG contrast ratio for each of these foreground and background pairs from the actual CSS values; any pair below 4.5:1 gets its foreground lightened until it passes; the test-writer adds a test that computes the ratios from the stylesheet values and asserts every named pair is at least 4.5:1, so the bar is pinned either way.

C. Spacing rhythm (reviewer-design): the CSS hardcodes at least 15 different spacing values with no scale. Consolidate the board and status page spacing onto a small consistent spacing scale (CSS custom properties drawn from one scale) so spacing values come from the scale throughout.

D. Responsive behavior (reviewer-design): the .board-stages flex row of five stages can force horizontal scrolling below about 400px viewport width. Make the stages row wrap or adapt at narrow widths (flex-wrap or a media query) so no horizontal scrolling occurs on standard viewports.

E. Rendered evidence: the operator has staged Playwright and Chromium installation into this run's workflow before the line step, so the capture step can produce rendered evidence of the status page with the lifecycle board in this run; reviewer-design and reviewer-ux judge with those captures in their packets.

Discipline: the test-writer station writes the new and changed tests (the link structure assertions, the computed contrast test); the builder implements in the status page code and styles only and must not modify tests/, anvil.json, pipelines/ or .github/workflows/. Everything else from round 1 stands: the stage derivation, the NEEDS HUMAN badge, the intake state composition, and the docs and CHANGELOG updates were all confirmed correct by the counted reviews.
- risk_hints: 
- status: new

## Upstream steps

- (none)
