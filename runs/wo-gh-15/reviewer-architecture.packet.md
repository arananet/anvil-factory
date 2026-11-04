# Task packet: reviewer-architecture

## Station prompt

# Reviewer Architecture

## Role
Check fit with the project structure and decisions.

## Inputs
- code change
- brain/decisions

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
  "station": "reviewer-architecture",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-architecture", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.


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
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: passed
- reviewer-spec: executed
- reviewer-security: executed
- reviewer-tests: executed

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-15/reviewer-architecture.review.json. The free output transcript stays as provenance and is never parsed for a review.
