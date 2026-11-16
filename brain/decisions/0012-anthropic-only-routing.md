# 0012: Anthropic-only routing; Opus 5.5 default, Fable 5.2 for critical decisions

Status: accepted 2026-11-15, by the owner's order. Spec:
.openspec/specs/anthropic-only-routing/spec.md.

## Context

Decision 0004 (2026-11-03) moved the design stations (UI builder,
reviewer-design, reviewer-ux) to openai/gpt-6.1-sol on executed benchmark
evidence: equal quality, about a fifth of the retired Astra's cost per task.
That bought a second vendor runtime into the line. Since then the second
path produced its own failure family (wo-gh-37: design reviewers lost to
"Codex empty output" while their review files existed), and the owner's
standing preference is one vendor, one runtime path, with model strength
spent where judgement concentrates.

## Decision

- Every OpenAI model is removed from ANVIL's standing routing. No station
  in the factory's configuration or tier resolution may resolve to a
  non-Anthropic model. This supersedes decision 0004's assignment of the
  design stations to openai/gpt-6.1-sol; the rest of 0004 (the retirements
  of claude-sonnet-4-5 and openai/gpt-6-astra, and executed-model evidence
  in run reports) stays in force.
- claude-opus-5-5 is the workhorse for everything else: builder, all
  reviewers including design and ux, spec-writer, test-writer, writer,
  media-producer, brief-writer, researcher, blueprint, intake, scout,
  observer, deployer, triage-human. Every tier label in MODEL_TIER_MAP
  resolves to claude-opus-5-5.
- claude-fable-5-2 is reserved for the two stations whose output is a
  critical decision about the run itself: approver (the verdict) and
  supervisor (run oversight and intervention). A "critical-decision" tier
  label resolves to it. No other station may be assigned fable without a
  new decision record.
- claude-sonnet-5-5 remains a permitted Anthropic model (it stays in
  CONCRETE_MODELS) but is no longer assigned by any factory default.

## Consequences

- Cost: Opus everywhere costs more per call than the Sonnet mix it replaces
  on the cheap stations, and fable (8 USD input / 40 USD output per million
  tokens at launch pricing) is the most expensive model in the routing.
  The owner accepts this trade explicitly; per-station budgets (wo-gh-42,
  filed) become the control that keeps it honest.
- Verification: claude-fable-5-2 is a real Anthropic model (released
  2026-11-09, API id claude-fable-5-2). Its first executed run on the
  gateway must record the executed model from runtime evidence, per the
  standing rule in 0004; until that evidence exists, the fable assignment
  is configured, not yet proven in production.
- Consumer projects keep their own anvil.yaml files. Projects whose design
  stations still name openai/gpt-6.1-sol are outside this decision's edit
  scope and are swept separately, on the owner's word.
