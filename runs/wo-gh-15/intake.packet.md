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

- id: wo-gh-15
- kind: feature
- title: A standing quality standard for visual deliverables
- source: github-issue
- description: Implement the spec in .openspec/specs/quality-standard/spec.md in the factory. It is the tenth work order of the capability program and runs after the post-deploy health work in the same sequence.

Build, per the spec scenarios:

S1: reviewer-design's contract gains the anchor comparison duty as a separate, named quality section of its recorded review, alongside design system compliance. On a fixture visual run for a physical consumer product whose anchors show photoreal product boards, a stylized toy-like output must fail the quality section, naming gap categories from materials, light, scale and contact measured against the cited anchor, even when the compliance section passes. reviewer-ux carries the same duty for the experiential side once it exists in the catalog.

S2: a visual run with no anchors under design/reference/ and none named by the work order proceeds under the charter floor alone: the charter criteria for the product type are present in the generating and reviewing packets, and the run report carries a visible warning that the run had no reference anchors.

S3: a run with no visual surfaces never receives the charter: no packet contains the charter text or its criteria and the report makes no mention of the quality standard.

S4: a station that produces imagery verifies each output by reading it against the run's anchors and the charter criteria before the review step runs, and the comparison lands in the run evidence per output (anchor cited, criteria checked, gaps found or an explicit none at the charter bar). The record is evidence, not a verdict, and reviewers are not bound by it.

S5: composition order is anchors first, then the project design system and verified brain learnings, then the charter floor. Anchors showing a deliberately stylized product make the stylized reading the bar; anything below the charter floor is a named floor gap, never silently waived.

S6: for a game or illustration product, the charter requires the project's own standard stated in observable terms and the review applies that standard; the physical product photorealism criteria are absent from the judgment.

Also build the charter itself: a versioned factory level charter document stating production quality as the default bar for visual deliverables, defined per product type with observable criteria (materials, light, contact and scale for a physical consumer product; a stated per product standard for game and illustration work), included by reference in the packets of imagery generating and imagery reviewing stations on visual runs. Project design system scaffolding creates design/reference/ under the never overwrite discipline and visual work orders name or inherit the project's anchors.

S7: a work order producing a set of related visual deliverables designates one canonical identity reference inside the set, the generating stations work from it, and reviewer-design runs a same subject test across the whole set against it on the identity traits the work order's spec enumerates (finish, detail colors, mounting or attachment, proportions and markings for a physical product, equivalents stated per product type). Any divergence fails the quality judgment with the divergent asset and trait named, even when every asset individually passes the anchor comparison, and such a run does not approve.

Tests covering S1 to S7 in the factory suite style, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/15

GATE LOOPBACK (round 2). Round 1 verdict was changes_requested with 5 of 5 reviews counted after routing (reviewer-spec and reviewer-tests pass; reviewer-security, reviewer-architecture and reviewer-design changes_requested). Close exactly the counted findings:

1. WIRE THE QUALITY MODULE INTO THE RUNNER (reviewer-architecture). anvil/quality.py defines packet_quality_charter_section() and packet_anchor_section() but anvil/runner.py never calls them; the module is orphaned. packet_step() must call both and pass their results to _packet_text(), which gains quality_charter_section and anchor_section parameters, following the established pattern of packet_design_section, packet_rendered_evidence_section and packet_knowledge_section. Wire the S2 warning the same way: on a visual run with no anchors, the run report carries the visible no-reference-anchors warning the quality module generates.

2. STATION CONTRACTS (reviewer-architecture, spec S1 and S4). stations/reviewer-design/PROMPT.md must document the dual-section review structure the code validates ({compliance: {verdict, findings}, quality: {verdict, findings, anchor}} per validate_reviewer_quality_section), the anchor comparison duty as a separate named quality section, and the requirement to name gap categories by criterion (materials, light, scale, contact). The imagery generating station prompts (stations/builder/, stations/media-producer/, stations/brief-writer/) gain the S4 duty: verify each produced output against the run's anchors and charter criteria before the review step and record the comparison in the run evidence per output. reviewer-ux's prompt carries the same quality section duty for the experiential side, per S1.

3. PATH AND INPUT VALIDATION (reviewer-security). WorkOrder.from_dict must validate the anchors, identity_reference and deliverable_set path fields: relative paths only, no parent traversal, no absolute paths, following the validate_path_component discipline already in the codebase; malformed values are rejected with a named error. quality.py is_visual_run and get_product_type must not assume attribute presence or types (defensive access or structural validation). Work order controlled strings interpolated into packet output are sanitized of control characters.

4. RENDERED SURFACE (reviewer-design). In the surface rendered as this run's evidence: secondary text (the 'configured:' lines) must reach at least 4.5:1 contrast against the dark background at both breakpoints, and the station data table at 390x844 needs responsive treatment (no horizontal scrolling; touch targets at least 44x44px; card layout, scrollable region with clear affordance, or progressive disclosure). Capture rendered evidence at 390x844 and 1440x900 in this run showing both fixed.

5. TESTS. Add regression tests in the factory suite style proving the wiring: a visual run's generating and reviewing packets contain the charter section and the anchor section; a visual run with no anchors produces the report warning; a non-visual run contains no charter text anywhere (S3); the reviewer-design dual-section output validates against the contract; traversal paths in the new WorkOrder fields are rejected.

Guardrails: the charter document and quality.py's criteria content were not faulted; do not rewrite them beyond the wiring. No changes to the review parsing contract beyond the reviewer-design dual-section contract item 2 names (the parser and producer mechanisms themselves are frozen), the checks gate base ref behavior, or other items' modules. Keep the full suite green and every pipeline valid; docs and CHANGELOG Unreleased updated for the wiring. No em dash or en dash characters in any produced file.

- risk_hints: 
- status: new

## Upstream steps

- (none)
