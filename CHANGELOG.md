# Changelog

## Unreleased
- Verified memory gate: brain/learnings.md is a verified store behind a provenance check. Proposals wait quarantined in brain/inbox/ and are promoted only when deterministic code confirms the cited run report exists, the cited artifact exists, and the evidence matches the report. Packets carry a Verified learnings section sourced only from non demoted verified entries; demotions are recorded as decisions. New commands: check-brain, promote-learning, demote-learning.
- Bounded supervisor: a 24th station that runs between runs. Deterministic stall signals over the run record (repeated reviewer fails, exhausted loopbacks, repeated no_reviews, deployed_unverified) trigger a supervisor packet; executed proposals are validated against the catalog plus a constitution (intake, approver and triage-human required, reviewer coverage may not shrink) and filed under pipelines/proposals/. Nothing auto applies.
- Model provenance: every step and envelope records configured_model in all modes; executed steps record executed_model and an executor object {kind, detail}. An http executor's executed model is its configured endpoint model; a command runtime's model is recorded only when its own output reports one, never guessed. The status page shows the model under each station name.
- Agent execution: `anvil run --execute` with a `runtime` object in anvil.yaml. Command executors (shell template with {packet} and {output}) and HTTP executors (OpenAI style endpoint, key from a named environment variable) run station packets, write output artifacts, and record reported usage tokens while cost stays null unless reported.
- Run scoped approver: the approver now aggregates only reviews produced during the same run. A run whose reviewers only produce packets ends with verdict no_reviews; standing project reviews remain the record read by `anvil check`.
- Automatic deploy and verification: a `deploy` object in anvil.yaml lets an approved execute mode run with no human gate blocking run its deploy command, then a deterministic verification gate. Deployment status is reported as deployed_verified, deployed_unverified or deploy_failed, with verify findings written for failed verification.
- Intake worker: POST /github accepts GitHub webhook deliveries for issues, with optional HMAC signature verification through GITHUB_WEBHOOK_SECRET, mapping opened or anvil labeled issues to work orders.
- Run status page: `anvil status-page <project>` renders every run report in a project into one self contained HTML page (Arananet style, inline CSS, no external assets) for Cloudflare Pages, GitHub Pages or any static host, with skipped unreadable runs noted in the footer.

## 0.1.0 - 2026-10-28
- First release: deterministic pipeline engine, gates, approver and runner.
- 23 stations and 8 pipelines: sdlc-default, hotfix, docs-only, scout, plan-build-test, greenfield, content-default and content-short.
- Content domain on the same core: 9 content stations, brief and disclosure gates, publishing as a human gate risk hint, a content brief template and a worked content example.
- License: Apache 2.0, matching the OpenSpec template (LICENSE carries Copyright 2026 Eduardo Arana).
- Existing project onboarding: anvil onboard analyzes a codebase read only, adds only missing factory files, drafts a baseline spec and reports gaps as suggested first work orders. The intake worker is deployed live at anvil-intake on Cloudflare (workers.dev).
- Greenfield mode: idea work orders, a blueprint station, a blueprint catalog (python-service, cloudflare-worker, static-site) and the anvil new-project command that scaffolds a project from zero.
- Core Four project config in anvil.yaml with per station overrides.
- Runner packets, typed envelopes, gate loopback and swimlane observability.
- Project scaffolding, spec templates and brain structure.
- Cloudflare intake worker with node tests.
- Taskline example built on the line, in its own repo.
