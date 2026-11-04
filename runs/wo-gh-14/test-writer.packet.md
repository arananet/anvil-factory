# Task packet: test-writer

## Station prompt

# Test Writer

## Role
Write tests that map to spec scenarios before implementation.

## Inputs
- spec

## Outputs
- tests

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


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

- risk_hints: production-deploy
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
