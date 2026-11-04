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

- id: wo-gh-12
- kind: feature
- title: A dedicated UX reviewer station (reviewer-ux), separate from reviewer-design
- source: github-issue
- description: Implement the spec in .openspec/specs/reviewer-ux/spec.md in the factory. It builds on the routing capability and the design knowledge capability, both landed earlier in this program's sequence, and on the rendered evidence capability where screenshots exist.

Build, per the spec scenarios:

S1: stations/reviewer-ux/ in the catalog (agent kind, standard review format) whose contract judges the experience: user flows and task completion, usability heuristics, accessibility basics, and clarity of the interface copy; the contract explicitly excludes visual system compliance (tokens, type scale, palette) as reviewer-design's lens, and the catalog entry carries the guided design station designation naming the design model from the recorded routing policy.

S2: reviewer-ux joins the reviewer group of sdlc-default, content-default and content-short (the pipelines reviewer-design serves). The routing step activates it when the work order carries a ui surface; its packet then carries the design knowledge guidelines slice for the project's product type and, where the run produced rendered screenshots, the rendered evidence.

S3: on work with no ui surface the router routes reviewer-ux out before execution, records it as routed out with the surface rule named, and the approver's expected review count excludes it; no reviewer-ux step executes and non-UI work pays nothing for the lens.

S4: the run report and swimlane list reviewer-design and reviewer-ux as separate entries with independent verdicts and findings.

S5: when a ui surface run has no rendered screenshots, reviewer-ux's recorded review states it judged from source and the knowledge slice without rendered evidence.

Tests covering S1 to S5 in the factory suite style, including the ui-surface selection and the non-ui skip, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/12

Operator standing note for every round of this order: the builder must not create or modify anything under .github/workflows/ (the Actions token cannot push workflow changes; a run that touches them loses its commit-back). Tooling the run needs is staged by the operator in the workflow before the line step. Test changes are written by the test-writer station; the builder must not modify tests/, anvil.json or pipelines/. Tests must be real: every test calls the implementation it names and asserts behavior, never the mere existence of data structures.
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: failed
- loopback: loopback
- reviewer-spec: skipped
- reviewer-security: skipped
- reviewer-tests: skipped

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-12/reviewer-architecture.review.json. The free output transcript stays as provenance and is never parsed for a review.
