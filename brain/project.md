# ANVIL Project Brain

## What ANVIL is
ANVIL is a composable software factory framework. Work moves down a line of stations, each station has a clear contract, and the artifacts stay in the repo.

## Principles
- Spec before code: a change starts with an OpenSpec spec under .openspec/specs/.
- Tests before implementation: scenario tests are written before the builder runs.
- The station that builds never approves its own work: builders and reviewers are different stations.
- Human gate on risk: work with auth, payments, data deletion, production deploy or secrets risk hints needs a human.
- Everything is an artifact in the repo: specs, tests, reviews, packets, envelopes, reports and swimlanes are files.

## Core Four
Every project has an anvil.yaml at its root. For each station it can set context, model, prompt and tools. See docs/ARCHITECTURE.md.
