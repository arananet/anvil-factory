# Task packet: reviewer-spec

## Station prompt

# Reviewer Spec

## Role
Check the implementation against the spec, nothing else.

## Inputs
- spec
- code change

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
  "station": "reviewer-spec",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-spec", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.


## Work order

- id: wo-gh-8
- kind: feature
- title: Risk and surface routing of reviewer sets and station models
- source: github-issue
- description: Implement the spec in .openspec/specs/risk-routing/spec.md in the factory. It consumes the risk and surfaces the intake outcomes capability stamps on the work order; that capability lands before this one in the same program, so build against its model fields.

Build, per the spec scenarios:

S1: a deterministic routing step after intake and before the reviewer stage; low risk with no ui and no security surface selects the reduced reviewer set (reviewer-spec and reviewer-tests) at the cheaper configured reviewer model, with the rule named as the reason.

S2: a security surface at any risk level always keeps reviewer-security in the set at the strong configured reviewer model.

S3: a null risk rating defaults to the full panel at the policy models, with the routing record stating the default applied because the work was unrated. A ui surface keeps reviewer-design in the set whenever the pipeline has it. Medium risk is the full panel at policy models; high risk the same with no reduction recorded.

S4: the recorded model routing policy is a ceiling: routing may reduce, never exceed it, and a project routing configuration that assigns a model above the policy for a station kind fails at config load naming the violation.

S5: a routed out reviewer is recorded as routed out with its rule; the approver treats it as not expected, and its review count names the expected count after routing.

S6: the routing record lands in the run report as its own section (selected set, selected models, reason per decision) and the swimlane shows a one line summary.

Routing rules live in project configuration with a factory shipped default table. Routing never changes the checks gate or the scenario-to-test gates. Tests covering S1 to S6 in the factory suite style, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/8
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: failed
- checks-gate: passed

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-8/reviewer-spec.review.json. The free output transcript stays as provenance and is never parsed for a review.
