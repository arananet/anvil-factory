# Anthropic-only routing: Opus 5.5 default, Fable 5.2 for critical decisions

## Problem

Decision 0004 (2026-11-03) assigned the design stations to openai/gpt-6.1-sol,
executed through a second vendor runtime. The owner has now ordered every
OpenAI model out of ANVIL: one vendor, Anthropic, with claude-opus-5-5 as the
workhorse for code, review, media and writing, and claude-fable-5-2 reserved
for the very few stations whose output is a critical decision about the run
itself. Keeping a second vendor in the routing buys a per-task cost saving on
design stations (the 0004 benchmark) at the price of a second runtime path,
a second failure family (the wo-gh-37 "Codex empty output" mode), and a
configured-versus-executed divergence risk the factory has already paid for
once.

## Decision basis

Owner's order, 2026-11-15: remove every OpenAI model from ANVIL, leave
everything on Anthropic; opus 5.5 for code, review, video editing and the
rest; fable 5.2 for reasoning only in very, very critical decisions.
claude-fable-5-2 is a real Anthropic model (released 2026-11-09, API id
claude-fable-5-2, frontier reasoning tier). Anthropic's own guidance matches
the owner's split: Opus 5.5 as the daily driver, Fable 5.2 when the decision
justifies it.

## Requirements

R1. No station in the factory's standing wiring resolves to a non-Anthropic
model. The tier map (anvil/config.py MODEL_TIER_MAP) resolves every tier
label to an Anthropic model, and no factory configuration names an OpenAI
model as a station assignment. Historical records (work order files, run
reports, decision 0004 itself) are history and do not change.

R2. Workhorse default: claude-opus-5-5. In the factory's own anvil.yaml,
builder, spec-writer, test-writer, every reviewer (including reviewer-design
and reviewer-ux), intake, scout, observer, deployer and triage-human carry
claude-opus-5-5. Every tier in MODEL_TIER_MAP resolves to claude-opus-5-5,
so any station definition still speaking in tier labels (writer,
media-producer, brief-writer, researcher, blueprint) also lands on Opus.

R3. Critical decisions: claude-fable-5-2, only where the station's output is
a decision about the run. In anvil.yaml, approver and supervisor carry
claude-fable-5-2 and no other station does. A new tier label
"critical-decision" resolves to claude-fable-5-2 in MODEL_TIER_MAP, and
DEFAULT_MODELS assigns supervisor to it. CONCRETE_MODELS includes
claude-fable-5-2 so the dispatcher treats it as a known Anthropic model on
the Claude route.

R4. Decision record: brain/decisions/0012 records this change and supersedes
decision 0004's assignment of design stations to openai/gpt-6.1-sol. The
rest of 0004 (retirement of claude-sonnet-4-5 and gpt-6-astra, executed
model recorded from runtime evidence) stays in force.

R5. Tests that encode the superseded policy are updated to encode this one;
tests that record history (the 0004 migration, past runs) are not rewritten.
The full factory suite stays green and check-skills passes.

## Scenarios

S1. Resolving every tier label in MODEL_TIER_MAP yields claude-opus-5-5,
except "critical-decision", which yields claude-fable-5-2.

S2. Reading the factory's anvil.yaml, the only models named are
claude-opus-5-5 and claude-fable-5-2; approver and supervisor are the fable
stations.

S3. A run on the new wiring records, for the approver station, configured
model claude-fable-5-2 and an executed model from runtime evidence on the
Claude route, never an OpenAI runtime.
