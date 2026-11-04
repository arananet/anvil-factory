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


PURE VERIFICATION ROUND (round 4). Full history, disclosed: round 1 built anvil/health.py and the S4 metrics slot but never wired the module into the runner (verdict rejected, 5 of 5 counted; reviewer-spec fail, security, architecture and design changes_requested, tests pass). Round 2 implemented the wiring (runner integration, config loading, human gate forcing, swimlane step, SSRF hardening, responsive fix, demonstration wiring) but its checks gate failed the suite on one error in its own new test, which patched the non-stdlib requests package; all reviewers were skipped (no_reviews). Round 3 fixed exactly that test to patch urllib.request.urlopen, and the gate's own output shows the suite green on the resulting tree (387 tests, OK) -- but the gate then failed the run on a protected path violation, because the fixed test file existed in that run's recorded base ref and the builder was barred from modifying it; all reviewers were skipped again (no_reviews).

The standing tree at this round's start therefore already contains the complete item: the health module, the runner wiring, the hardening, the responsive fix and the corrected test, with the suite green. THIS ROUND MAKES NO CHANGES. The builder is barred from modifying, adding or deleting any file; its task is to verify the standing state (suite passes, pipelines valid, the report health section appears when a run carries a health target, the demonstration record exists) and report verification only. Reviewers: judge the standing tree against the spec scenarios S1 to S5 and the round 1 findings list, exactly as listed in the round 2 brief items 1 to 6; the verdict of this round is the item's verdict of record. If a reviewer finds the standing tree genuinely incomplete against the spec, say so with the specific gap; do not request changes that this verification round is barred from making without naming them as the item's remaining findings for the record.

- risk_hints: production-deploy
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: passed
- reviewer-spec: executed
- reviewer-security: routed_out
- reviewer-tests: executed
- reviewer-architecture: routed_out
- reviewer-design: routed_out
- reviewer-ux: routed_out
- approver: completed
- triage-human: completed
