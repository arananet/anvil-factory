# 0008: One runtime, Anthropic models only

Status: accepted 2026-11-12, by the owner's order ("Quitemos codex de la ecuación").

Supersedes: the OpenAI part of decision 0004 (reviewer-design, reviewer-ux and
the guided builder on openai/gpt-6.1-sol through Codex). The rest of 0004
stands: per station models, no fallback, executed model from runtime evidence.

## Decision

The factory runs one station runtime, Claude Code print mode through the
gateway Anthropic route. The design stations (reviewer-design, reviewer-ux,
and the builder when the work order has the ui surface) use claude-opus-5-5.
tools/codex_station.py, the OpenAI smoke probes and the Codex install step
are removed. A non Anthropic model fails the step loudly.

## Why

A second runtime doubled what could break between the issue and the pull
request: a second CLI to install, a second credential path, a second output
format, and a tree guard that kept reviewers from ever running concurrently.

Opus is the design model because it is the one with evidence: the benchmark
recorded in decision 0004 put Astra, Opus 5.5 and Sol level on quality
(reviewer recall 10 of 10, builder token compliance 12 of 12).

## Consequences

- Cost: the same benchmark measured 0.137 USD per task for Opus against 0.038
  for Sol, so design steps cost about 3.6 times more per task. claude-sonnet-5-5
  for the design reviewers would be cheaper but was not benchmarked; switching
  is one line per station in anvil.yaml and should follow a measurement.
- efficiency.tool_output_tokens is accepted but no supplied wrapper applies it.
- Historical run records under runs/ and the specs that describe the Codex
  runtime (model-migration) are left as written; they describe what ran then.
- Provenance: owner-authored work outside the line (decision 0006). The line
  neither produced nor reviewed this change.
