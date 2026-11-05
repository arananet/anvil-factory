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

- id: wo-gh-31
- kind: feature
- title: Tier map totality: resolve review-cheap
- source: github-issue
- description: Implement the spec in .openspec/specs/model-tier-map/spec.md. One bounded fix on merged main:

1. Add the missing entry to MODEL_TIER_MAP in anvil/config.py: review-cheap resolves to claude-sonnet-5-5 (owner policy: every non-design reviewer runs claude-sonnet-5-5).
2. Add a totality regression test in a NEW test file: enumerate every tier label from the routing module's own vocabulary (anvil.routing MODEL_HIERARCHY plus every model value the routing rules can select, including the reduced panel's review-cheap assignment in the default routing table) and assert resolve_model maps each to a member of CONCRETE_MODELS. The test must read the vocabulary from the routing module, not hardcode a copy of the label list, so a future unmapped label fails the suite.
3. CHANGELOG Unreleased entry.

Guardrails: do not modify or delete any existing file under tests/ (new tests only in new files; the checks gate protects base ref test files). Routing's vocabulary and rules unchanged; the dispatcher keeps failing loudly on unmapped non-concrete values. Full suite green. No em dash or en dash characters in any produced file.

GitHub issue: https://github.com/arananet/anvil-factory/issues/31

PURE VERIFICATION ROUND (round 2). Round 1 verdict: no_reviews, with the expected self-reference shape, disclosed in full: the builder implemented the fix (MODEL_TIER_MAP gained review-cheap -> claude-sonnet-5-5, plus the totality regression test enumerating the routing vocabulary), the checks gate PASSED on the new tree (the totality test runs in a fresh process and proves the map), but this order's own two selected reviewers (reviewer-spec and reviewer-tests, reduced panel at low risk) still failed at dispatch with the unresolved review-cheap label, because the runner process of round 1 loaded the pre-fix map at startup. A fix to the hand-off cannot prove itself inside the run that carries it; that is what this round is for.

The standing tree at this round's start contains the complete fix with the gate green. THIS ROUND MAKES NO CHANGES: the builder is barred from modifying, adding or deleting any file; its task is verification and reporting only. The run starts on the fixed code, so routing's review-cheap assignments now resolve at hand-off. Reviewers: judge the standing tree against the spec (R1 the map entry, R2 the vocabulary-enumerating totality test, R3 nothing else changed, dispatcher still loud on unmapped values). If the tree is genuinely incomplete against the spec, name the specific gap for the record rather than requesting changes this round is barred from making.
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
