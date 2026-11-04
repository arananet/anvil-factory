# Task packet: builder

## Station prompt

# Builder

## Role
Implement the spec so the scenario tests pass.

## Inputs
- spec
- tests

## Outputs
- code change

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.
- **Design citation**: When authoring or revising design/DESIGN.md, include a "Design knowledge sources" note citing the knowledge entries you drew from by data kind and entry name (e.g., "Style: modern-minimal", "Palette: metrics-blue", "Guideline: accessibility - contrast ratio"). If the knowledge came from an operator-supplied pack, cite it as "operator-supplied pack entry" without naming the pack's origin.


## Work order

- id: wo-gh-14
- kind: feature
- title: Application metrics and post-deploy health verification
- source: github-issue
- description: Implement the spec in .openspec/specs/post-deploy-health/spec.md in the factory. It is the ninth and final work order of the capability program and runs after the status dashboard work in the same sequence.

Build, per the spec scenarios:

S1: post-deploy health verification as a deterministic step after the deploy step: a project declares a health target in its configuration (deployed base URL, key routes with expected statuses, optional platform signal source). Route checks are plain HTTP requests recording route, expected and observed status or transport error, and latency. Where the project declares a Cloudflare Workers source, the verification reads the Worker's request and error signals through the Cloudflare API for the window since the deploy, through the operator's existing credential path. All checks passing and no platform errors reads healthy, recorded in a health section in the run report, reflected in the deployment status as deployed and healthy, and shown as a health step in the swimlane.

S2: any failing route or platform errors above the configured acceptable level reads unhealthy, with the failing signals quoted in the record (route and observed status, or error counts), the deployment status reading deployed and unhealthy, and the human gate forced with the health reason in the decision record even when the approver verdict was approved.

S3: no health target, or every signal source failing to read, reads unknown with the reason named and a warning that health could not be verified; unknown is never rendered or aggregated as healthy anywhere.

S4: the application metrics slot: anvil init, anvil new-project and anvil onboard configurations gain an opt-in metrics section (empty endpoint and provider key placeholder fields, an explanatory comment, no vendor name or endpoint shape anywhere in the factory core or the generated config); onboard still never overwrites an existing configuration.

S5: demonstrate on a factory owned target (the published status page or the intake Worker; choose whichever is deployable and checkable from the executed-run environment and record the choice and reason), with the demonstration run's report carrying the health section and its evidence.

Health verification is deterministic, never a model station, and never blocks a run whose project declares no target. Tests from fixtures covering S1 to S5 in the factory suite style, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/14

GATE LOOPBACK (round 2). Round 1 verdict was rejected with 5 of 5 reviews counted (reviewer-spec fail; reviewer-security, reviewer-architecture and reviewer-design changes_requested; reviewer-tests pass). The counted findings converge on one core defect plus hardening and one rendering fix. Close exactly these:

1. RUNNER INTEGRATION (reviewer-spec and reviewer-architecture, critical). anvil/health.py implements verify_health() but anvil/runner.py never imports or calls it; the module is operationally inert. Wire it: after the deploy step completes, the runner calls verify_health() with the project health target; RunReport gains a health field and to_dict() serializes it as the report health section; the deployment status reflects the outcome (deployed and healthy, deployed and unhealthy, unknown never rendered or aggregated as healthy anywhere); an unhealthy outcome forces the human gate with the health reason in the decision record even when the approver verdict was approved (feed the health result's requires_human_gate into the gates or triage logic); the swimlane (runs/<id>/swimlane.md) shows a health step after the deployer step with the outcome and duration.

2. CONFIG CONTRACT (reviewer-spec). Nothing loads the health target from project configuration today. Load and validate the declared health target (base_url, routes with expected statuses, optional platform source) from the project configuration (anvil.json or anvil.yaml) and pass it to the verification. No health target declared still means the verification records unknown with the reason named and never blocks the run.

3. DEMONSTRATION WIRING (reviewer-spec S5). select_demonstration_target and is_deployable in anvil/health.py are never called. The demonstration must actually execute in a run: the chosen factory owned target (status page or intake Worker) and the reason are recorded, and the demonstration run's report carries the health section with its evidence. This loopback run's own report is the natural carrier once items 1 and 2 land.

4. SSRF AND INPUT HARDENING (reviewer-security). In anvil/health.py: validate that base_url uses http or https only before any request; reject targets that resolve to private RFC1918 ranges, loopback, or link-local addresses (including 169.254.169.254 cloud metadata); validate account_id and worker_name interpolated into the Cloudflare API URL to alphanumerics, hyphens and underscores only; sanitize exception details recorded into health results so internal topology or credential detail cannot leak into run reports; validate expected_status is within 100 to 599. In docs/EXECUTION.md, warn explicitly against putting provider credentials in config files and point to environment variables or secrets management.

5. RESPONSIVE TABLE (reviewer-design). The five-column table in the rendered surface scrolls horizontally at 390x844, violating the quality bar. Apply responsive handling (overflow container, column prioritization, or media queries) so no horizontal scrolling is needed at 390x844, and capture rendered evidence at 390x844 and 1440x900 in this run.

6. TESTS. Add runner-level regression tests in the factory suite style proving the wiring: a run whose project declares a health target gains a health section in its report; an unhealthy outcome forces the human gate with the health reason recorded; an unknown outcome never reads as healthy; the SSRF rejections above are covered by fixtures. S4 (metrics slot) was verified correct by reviewer-spec and reviewer-architecture and is out of scope; do not churn it.

Guardrails: health verification stays deterministic, never a model station. No changes to the review parsing contract, the reviewer prompts or Output Format sections, the wo-gh-24 producer mechanisms, or the checks gate base ref behavior. Keep the full suite green and every pipeline valid; update docs and CHANGELOG Unreleased for the wiring. No em dash or en dash characters in any produced file.


CLOSING VERIFICATION ROUND (round 3). Round 2 implemented the loopback scope but its run produced no verdict: the checks gate failed the suite on exactly one error and every reviewer was skipped (verdict no_reviews, 0 counted). The gate output is unambiguous: 387 tests ran, one error, in the run's own new test tests/test_post_deploy_health.py test_exception_sanitization_prevents_credential_leakage, which patches 'requests.get'; the factory is standard library only, the requests package is not installed, and anvil/health.py performs HTTP through the standard library. Every other test passed, including the new runner health integration tests.

This round's entire scope:
1. Rewrite that one test so it patches the standard library HTTP entry point anvil/health.py actually uses, keeping the sanitization assertion at full strength (a raised transport error carrying internal topology or credential detail must not surface those details in the recorded health result). Do not weaken, skip or delete any other test, and do not touch tests that round 2 did not author except this one file and only this one test.
2. Verify the round 2 wiring stands as briefed and complete only what is actually missing from it: the runner calls verify_health after the deploy step with the target loaded and validated from project configuration; the report carries the health section; the deployment status reflects the outcome; an unhealthy outcome forces the human gate with the health reason in the decision record; the swimlane shows the health step; the SSRF and input validations are in anvil/health.py; the 390x844 responsive fix with rendered evidence at both breakpoints; the demonstration target choice and reason recorded with the health evidence in a run report (this run's report is the carrier). If the demonstration record is still missing, produce it in this run through the wired path, choosing the factory owned target that is checkable from this environment and recording the choice and reason.
3. Nothing else changes. The review parsing contract, reviewer prompts, producer mechanisms, checks gate base ref behavior and the verified S4 metrics slot are frozen. Full suite green and every pipeline valid at the gate; docs and CHANGELOG already updated in round 2 stand unless the wiring completion requires a correction.

- risk_hints: production-deploy
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed

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


## Design knowledge

**Authority**: The project's own design system (design/DESIGN.md, design/tokens.json) is the authority for this project. The knowledge base below is reference material that the design system may draw from. On any conflict, the project's design system wins. A deviation from the knowledge base alone is not a finding; a deviation from the project's design system is.

**Note**: No product type slice matched. General guidelines only.

### Product Type: Undeclared

No specific product type declared. Using general guidelines only.

### UX Guidelines

**Accessibility:**
- Maintain minimum 4.5:1 contrast ratio for normal text, 3:1 for large text (18pt+)
- Touch targets must be at least 44x44px on mobile devices

**Feedback:**
- Loading states should appear after 300ms delay to avoid flashing
- Provide immediate visual feedback for user actions

**Forms:**
- Form fields should have clear labels and validation feedback
- Error messages should explain what went wrong and how to fix it

**Hierarchy:**
- Establish clear visual hierarchy using size, weight, and color
- Important actions should be visually prominent and easy to locate

**Motion:**
- Keep animation durations between 200-400ms for most transitions
- Provide reduced motion alternatives for users with vestibular sensitivity

**Responsive:**
- Test layouts at mobile (320-768px), tablet (768-1024px), and desktop (1024px+) breakpoints
- Avoid horizontal scrolling on standard viewports

**Spacing:**
- Use consistent spacing scale throughout (e.g., 4px, 8px, 16px, 24px, 32px)
- Group related elements together with whitespace separating distinct sections

