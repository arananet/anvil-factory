# Changelog

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
