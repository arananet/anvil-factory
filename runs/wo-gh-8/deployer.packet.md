# Task packet: deployer

## Station prompt

# Deployer

## Role
Prepare and carry out the release step described by the project.

## Inputs
- approved change

## Outputs
- release record

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


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

GATE LOOPBACK 1 (after run 41741068693, verdict changes_requested, reviews counted 5 of 5). Fix exactly the counted findings below; nothing else is in scope.

Finding A (all four requesting reviewers; S4 not wired): validate_model_assignment exists at anvil/routing.py:71 but is never called during configuration loading, so a project routing configuration that assigns a model above the policy ceiling loads silently. Wire it: during load_routing_config, validate every model assignment in the merged configuration against the policy ceiling; loading must fail with an error naming the station kind, the configured model and the policy model it exceeds.

Finding B (reviewer-security and reviewer-architecture): load_routing_config merges project overrides without validating the configuration structure. At load time, validate that the reviewer lists (reduced_panel_reviewers and full_panel_reviewers) contain only valid reviewer station ids, and that every model referenced in the configuration exists in MODEL_HIERARCHY. Invalid references fail at load with the offending value named.

Finding C (reviewer-architecture): the policy ceiling is hardcoded in MODEL_POLICY while docs/ROUTING.md documents policy_ceilings as a configurable field, and the docs use a key naming that does not match the code. Align them: load_routing_config honors a policy_ceilings section in the project configuration when present, falling back to MODEL_POLICY when absent, and docs/ROUTING.md names station kinds exactly as the code does.

Finding D (reviewer-tests): three tests in tests/test_risk_routing.py are placeholders that pass without real assertions: test_config_above_policy_fails_load_s4, test_default_routing_table_exists and test_project_can_override_routing_config. Replace them with real tests that exercise the actual routing.py implementation; the S4 test must drive load_routing_config with an over-policy assignment and assert that the load fails naming the violation.

Finding E (reviewer-security, recorded as a by design observation): routing trusts the work order risk and surfaces fields completely. Address it in one of two ways: either keep reviewer-security mandatory whenever the change touches security sensitive paths (auth, credentials, secrets, tokens) regardless of the stamped surfaces, with a routing record entry naming that rule; or record the accepted risk explicitly in docs/ROUTING.md, stating that routing consumes the intake outcomes as produced and that unrated work defaults to the full panel. One of the two, not neither.

Discipline: test changes are written by the test-writer station. The builder implements in anvil/routing.py and the docs only, and must not modify tests/, anvil.json or pipelines/ (protected paths under the checks gate). Keep the whole suite green and every pipeline valid. Update CHANGELOG Unreleased.
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
- reviewer-architecture: skipped
- reviewer-design: skipped
- approver: completed
- triage-human: completed
