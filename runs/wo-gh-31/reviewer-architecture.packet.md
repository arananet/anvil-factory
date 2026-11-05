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

- id: wo-gh-31
- kind: feature
- title: Tier map totality: resolve review-cheap
- source: github-issue
- description: Implement the spec in .openspec/specs/model-tier-map/spec.md. One bounded fix on merged main:

1. Add the missing entry to MODEL_TIER_MAP in anvil/config.py: review-cheap resolves to claude-sonnet-5-5 (owner policy: every non-design reviewer runs claude-sonnet-5-5).
2. Add a totality regression test in a NEW test file: enumerate every tier label from the routing module's own vocabulary (anvil.routing MODEL_HIERARCHY plus every model value the routing rules can select, including the reduced panel's review-cheap assignment in the default routing table) and assert resolve_model maps each to a member of CONCRETE_MODELS. The test must read the vocabulary from the routing module, not hardcode a copy of the label list, so a future unmapped label fails the suite.
3. CHANGELOG Unreleased entry.

Guardrails: do not modify or delete any existing file under tests/ (new tests only in new files; the checks gate protects base ref test files). Routing's vocabulary and rules unchanged; the dispatcher keeps failing loudly on unmapped non-concrete values. Full suite green. No em dash or en dash characters in any produced file.

GitHub issue: https://github.com/arananet/anvil-factory/issues/31
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: passed
- reviewer-spec: failed
- reviewer-security: routed_out
- reviewer-tests: failed

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-31/reviewer-architecture.review.json. The free output transcript stays as provenance and is never parsed for a review.
