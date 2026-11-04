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

- id: wo-gh-10
- kind: feature
- title: Per job cost measurement in run reports
- source: github-issue
- description: Implement the spec in .openspec/specs/cost-measurement/spec.md in the factory.

Build, per the spec scenarios:

S1: each run step gains a cost record (measured flag, input and output token usage when reported, the model priced from, the amount when measured). For stations executed by a runtime that leaves session transcripts with token usage, the executor sums the usage attributable to the step's execution window; usage that cannot be attributed to a step is not spread across steps.

S2: for HTTP gateway executions, the executor reads the usage object from the gateway response when present and attaches it the same way; a response with no usage object leaves the step unmeasured.

S3: a step with no usage source, or an executed model with no price table entry, records measured false, a null amount, and the stated reason. Nothing is estimated.

S4: the run report gains a cost section whose total is the sum of measured steps only, with measured and unmeasured step counts; the swimlane shows the total with its coverage counts.

S5: prices live in configuration as a price table mapping model names to input and output prices per million tokens, every entry labelled with its source and the date recorded; the loader rejects an entry missing either label.

Cost measurement changes no verdict: the approver, the gates and the human gate read nothing from the cost section. Tests covering S1 to S5 in the factory suite style, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/10

Operator standing note for every round of this order: the builder must not create or modify anything under .github/workflows/ (the Actions token cannot push workflow changes; a run that touches them loses its commit-back). Tooling the run needs is staged by the operator in the workflow before the line step. Test changes are written by the test-writer station; the builder must not modify tests/, anvil.json or pipelines/. Tests must be real: every test calls the implementation it names and asserts behavior, never the mere existence of data structures.
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

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-10/reviewer-tests.review.json. The free output transcript stays as provenance and is never parsed for a review.
