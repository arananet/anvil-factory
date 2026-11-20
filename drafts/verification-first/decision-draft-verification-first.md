# Draft decision: verification first

Status: draft, not recorded. Written 2026-11-19 outside the line at the owner's request. The line neither produced nor reviewed it (decision 0006 conditions apply if it is adopted).

## Context

On 2026-11-19 the owner compared ANVIL with the method Lauren Tan described for the Grok Bot team (AI Engineer Code Summit talk "All Code Is Slop (Except Mine)", 2026-11-11; figures are the team's own, read from public write-ups, not from the talk transcript). The comparison was checked against factory main 65aae7cc. What held:

- Corrections: 12 of 15 promoted practices are enforced as prompt text, 3 as gates.
- Runtime: rendered evidence is one still per breakpoint; nothing uses the built app.
- Proof: no first pass, survival or verification share figure is published; usage is measured for 23 of 211 calls in the 2026-11-14 status data.
- Base: blueprints carry no checks, so each greenfield project starts with an empty base.

## Decision proposed

Adopt the method where it transfers, in this order:

1. line-yield-metrics: publish first pass yield, survival, verification share and cost per accepted change. It reads existing records and changes no run, so it lands first and measures the effect of the rest.
2. runtime-verification: a feature map and a verify stage that drives the built app before review.
3. practice-enforcement-ladder: gate by default; P-9, P-10 and P-11 become checks.
4. blueprint-guardrails: blueprints carry checks that new projects are born with.

Land the staged accounting orders first (wo-gh-41 continuous run accounting, wo-gh-42 budgets and completeness): the metrics are only as good as the run records.

## Deferred, each with its trigger

- Fewer reviewer stations. Not decided here. Trigger: two weeks of reviewer yield data from line-yield-metrics. A reviewer whose findings never change a verdict is a candidate for replacement by a check.
- Outer loop (after deploy, use the product, file repair orders automatically). Trigger: runtime-verification live and first pass yield stable. Automating an inner loop that fails on first pass multiplies the failures.
- Model checking of the run lifecycle (TLA+ on run states, gate transitions, checkpoint and resume). Trigger: the hardening port (wo-gh-45) merged, so there is a settled state machine to model.

## Not adopted

- Dropping the spec before production. Tan's position rests on an existing codebase that already states intent. A greenfield order has only the spec. The spec stays; the feature map becomes its user-facing core.
- A ban on comments in produced code. Without the lint base of blueprint-guardrails it is style policing. Revisit after order 4.
- Proofs of library correctness (Lean). Outside the factory's deliverable mix.
- Her throughput as a target. It is one team on one mature product with a framework built for it.
