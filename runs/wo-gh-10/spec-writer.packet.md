# Task packet: spec-writer

## Station prompt

# Spec Writer

## Role
Write or revise an OpenSpec spec from a work order.

## Inputs
- work order
- brain

## Outputs
- spec

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


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

GATE LOOPBACK 1 (after run 41761646614, verdict changes_requested, reviews counted 5 of 5; reviewer-architecture is the only requesting reviewer). Fix exactly these counted findings:

1. Process violation: the builder created tests/test_cost_measurement.py and tests/test_cost_measurement_README.md, which the work order forbids. In this round the builder removes both files from its change and does not recreate them. The cost measurement tests are authored by the test-writer station in its own step; if the suite needs them, the test-writer writes them.

2. Out of scope changes: the intake station changes (anvil/config.py DEFAULT_MODELS and the stations/intake/station.json model field) are unrelated to the cost measurement spec. The builder reverts them; this order changes nothing about the intake station's model configuration.

3. Legacy cost override: anvil/runner.py (around lines 864-866) lets usage.cost override the calculated cost, and the spec does not document that behavior. Either remove the legacy path, or document it in the cost measurement spec and docs as intentional backwards compatibility. State which option was taken in the builder output. The suite stays green either way.

Everything else from round 1 stands (reviewer-spec, reviewer-security, reviewer-tests and reviewer-design passed; the architecture review confirms anvil/cost.py separates concerns correctly and cost does not affect verdicts). Standing discipline unchanged: the builder must not modify tests/, anvil.json, pipelines/ or .github/workflows/. Keep the whole suite green and every pipeline valid. Update CHANGELOG Unreleased if the change set changes.

CLOSING VERIFICATION RUN (after run 41764193801, verdict no_reviews: the checks gate failed on protected paths because the loopback builder deleted the round 1 test files, and deleting base ref files under tests/ is itself a protected path violation; the suite itself passed). Operator audit of the standing tree: the legacy cost override is removed, the builder test files are gone, BUT the intake changes are still present (anvil/config.py DEFAULT_MODELS gained an intake entry and stations/intake/station.json model was changed), so finding 2 is not closed. This run closes the order with a minimal builder delta:

1. The builder reverts exactly the two intake changes and nothing else: remove the "intake": "reasoning-strong" entry it added to DEFAULT_MODELS in anvil/config.py, and restore the stations/intake/station.json model field to "default". The builder must not add, modify or delete anything under tests/, anvil.json, pipelines/ or .github/workflows/ in this run; the absence of the round 1 builder test files is the correction and stays.

2. The test-writer station authors the cost measurement tests in its own step: real tests mapped to the cost measurement spec scenarios, calling the implementation (anvil/cost.py and the runner's cost recording) and asserting measured cost, unmeasured null handling and report contents. The builder-authored copies were removed in the loopback; coverage must come from the test-writer.

3. Everything else stands as audited: anvil/cost.py, the price table configuration, the cost section in run reports, and the removed legacy override (anvil/runner.py no longer lets usage.cost override the calculated cost).

On an approved verdict this order closes. Keep the whole suite green and every pipeline valid.

TEST CORRECTION RUN (after run 41765781560, verdict no_reviews: protected paths passed and the intake revert landed, but the gate suite failed on exactly two of the test-writer's new tests). Operator audit against .openspec/specs/cost-measurement/spec.md: both failures come from the tests pricing the intake step. The intake station's configured model is 'default', which has no price table entry; per spec S3, a step whose model has no price entry records measured false with a null amount. The tests contradict the spec, not the implementation:

1. test_gateway_response_with_usage (S2) runs only the intake station through a usage-reporting gateway executor and asserts its cost is not None. Correct the test to exercise S2 with a station whose configured model has a price table entry (the priced amount and measured true are then asserted on that step), or assert the intake step as the S3 unmeasured case. Do not change the intake station's production configuration (anvil/config.py DEFAULT_MODELS and stations/intake/station.json stay as reverted).

2. test_run_report_includes_cost_section (S4) asserts measured_steps equals 2 for an intake plus builder pipeline. Per S4's own premise (a mix of measured and unmeasured steps), correct the expectation to the spec: the builder step measured, the intake step unmeasured, measured_steps 1, unmeasured_steps 1, and the total equal to the measured step's amount only.

The test-writer station makes these corrections in its own step. The builder changes nothing unless a corrected test exposes an implementation defect, and must not modify tests/, anvil.json, pipelines/ or .github/workflows/. Everything else stands as audited (cost implementation, removed legacy override, reverted intake configuration). Keep the whole suite green and every pipeline valid. On an approved verdict this order closes.
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
