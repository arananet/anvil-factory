# Task packet: reviewer-design

## Station prompt

# Reviewer Design

## Role
Judge interface output against the project's own design system: its design tokens, component and layout rules, motion rules, and quality bars.

## Inputs
- design system (tokens, rules, quality bars from design/DESIGN.md and design/tokens.json)
- interface output (HTML, React components, CSS, user-facing pages, or other interface artifacts)

## Outputs
- review (JSON format with verdict and findings)

## Rules
- Work only from the inputs listed above and the work order in the packet.
- If the project has no design system (no design/DESIGN.md), your verdict MUST be `changes_requested` with a finding stating that no design system exists for the project.
- If the project has a design system, review the interface output against:
  - Design tokens: Are the correct colors, typography, spacing values being used?
  - Component and layout rules: Do components follow the documented patterns?
  - Motion rules: Does any animation or transition follow the motion guidelines?
  - Quality bars: Does the interface meet the stated quality bars for visual hierarchy, scale contrast, spacing rhythm, and responsive behavior?
- Focus on the design system the project has defined. Do not impose external design opinions or preferences that are not documented in the project's design system.
- A design token marked as "TODO" or placeholder means the project hasn't defined that value yet. Flag missing values as findings only if the interface output actually uses undefined tokens.
- Findings should be specific and actionable: cite which quality bar was violated, which token was used incorrectly, or which rule was not followed.
- Your verdict must be one of: `pass`, `fail`, or `changes_requested`.
- Produce the output as a JSON object, not as chat text.

## Output Format

Return a JSON object with this structure:

{
  "station": "reviewer-design",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-design", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.

## Examples

Example 1: No design system exists
- verdict: changes_requested
- finding: "No design system exists for this project. The project must define design/DESIGN.md and design/tokens.json before interface output can be reviewed against design standards."

Example 2: Interface violates quality bar
- verdict: changes_requested
- findings:
  * "Quality bar violation: Scale Contrast - The button text has only 2.8:1 contrast ratio against its background, failing the minimum 4.5:1 requirement stated in the quality bars."
  * "Token usage: The page uses hardcoded color '#FF5733' instead of the defined primary color token."

Example 3: Interface meets design system
- verdict: pass
- findings: (empty list)


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

GATE LOOPBACK 2 (after run 41743622244, verdict no_reviews: the checks gate failed the suite with exactly one error, so no reviews were produced). The loopback 1 implementation is verified correct by direct operator read; the single remaining defect is in the S4 test itself. Fix exactly this; nothing else is in scope.

Defect: tests/test_risk_routing.py, test_config_above_policy_fails_load_s4. Its second half calls load_routing_config(proj) bare (line 525) and only validates manually afterwards. Now that Finding A is wired, load_routing_config raises RoutingConfigError at that bare call: Station 'reviewer' configured with model 'review-strong' exceeds policy ceiling 'review-balanced'. That raise is the required S4 behavior; the test must expect it at the load.

Fix: in that test, wrap the load_routing_config(proj) call in assertRaises(RoutingConfigError) and assert the error message names the station kind (reviewer), the configured model (review-strong) and the policy model (review-balanced). Keep the direct validate_model_assignment assertions in the first half of the test unchanged. The test-writer station writes this fix. The builder changes nothing unless a test failure proves an implementation defect, and must not modify tests/, anvil.json or pipelines/.

Expected outcome: the factory suite passes in full (242 tests at loopback 1 count) and the checks gate passes, so the five reviewers run and judge findings A to E from loopback 1.
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
- reviewer-architecture: executed

## Project design

### Design tokens

```json
{
  "colors": {
    "primary": "TODO",
    "secondary": "TODO",
    "accent": "TODO",
    "background": "TODO",
    "surface": "TODO",
    "text": "TODO",
    "text-secondary": "TODO",
    "error": "TODO",
    "warning": "TODO",
    "success": "TODO",
    "info": "TODO"
  },
  "typography": {
    "font-family-base": "TODO",
    "font-family-heading": "TODO",
    "font-family-mono": "TODO",
    "font-size-base": "TODO",
    "font-size-scale": "TODO",
    "line-height-base": "TODO",
    "line-height-heading": "TODO"
  },
  "spacing": {
    "unit": "TODO",
    "scale": [
      "TODO"
    ]
  },
  "layout": {
    "max-width": "TODO",
    "breakpoint-mobile": "TODO",
    "breakpoint-tablet": "TODO",
    "breakpoint-desktop": "TODO"
  },
  "motion": {
    "duration-fast": "TODO",
    "duration-base": "TODO",
    "duration-slow": "TODO",
    "easing-standard": "TODO",
    "easing-enter": "TODO",
    "easing-exit": "TODO"
  }
}
```

### Quality bars

for Product Pages

These bars apply to every product page or interface this project ships.

### Visual Hierarchy
- [ ] Clear content hierarchy with size, weight, and spacing
- [ ] Important actions are visually prominent
- [ ] Related elements are grouped

### Scale Contrast
- [ ] Minimum 4.5:1 contrast ratio for normal text
- [ ] Minimum 3:1 contrast ratio for large text (18pt+)
- [ ] Interactive elements have sufficient contrast

### Spacing Rhythm
- [ ] Consistent spacing scale used throughout
- [ ] Whitespace creates clear content boundaries
- [ ] Spacing adapts appropriately to different screen sizes

### Responsive Behavior
- [ ] Layout works on mobile, tablet, and desktop
- [ ] Touch targets are at least 44x44px on mobile
- [ ] Text is readable without zooming on any device
- [ ] No horizontal scrolling on standard viewports


## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-8/reviewer-design.review.json. The free output transcript stays as provenance and is never parsed for a review.
