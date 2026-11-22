# Run Report

Work Order: wo-gh-47
Title: Live progress sinks: a run seen while it runs, on the work order's issue and optionally on a GitHub Projects board
Kind: feature
Status: new

## Intake Outcome

Outcome: accepted

Risk: high

Surfaces: api, security, data, content

## Routing

**Decision**: High risk: full panel at policy models, no reduction applied; Security surface: reviewer-security at strong model

**Selected reviewers** (5):
- reviewer-spec (model: review-balanced)
- reviewer-security (model: review-strong)
- reviewer-tests (model: review-balanced)
- reviewer-architecture (model: review-balanced)
- reviewer-design (model: review-balanced)

**Routed out** (1):
- reviewer-ux: Routed out: no UI surface

## Verdict

Verdict: gate_failed

The run ended (checks_stopped) before the approver step, so no reviews were aggregated into a verdict.

## Steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: failed
- loopback: loopback
- builder: executed
- checks-gate: failed
- loopback: loopback
- builder: executed
- checks-gate: failed
- reviewer-spec: not_run
- reviewer-security: not_run
- reviewer-tests: not_run
- reviewer-architecture: not_run
- reviewer-design: not_run
- reviewer-ux: not_run
- approver: not_run
- triage-human: not_run
- deployer: not_run
- observer: not_run

