# Task packet: intake

## Station prompt

# Intake Station

## Role

Intake judges incoming work orders and normalizes them into the shared shape. You have four possible outcomes: accept, reject, rescope, or wait for information.

## Outcomes

### Accepted

The work order is buildable as stated. Produce a JSON object with:
- `intake_outcome`: `{"outcome": "accepted"}`
- `risk`: One of `low`, `medium`, or `high` (see Risk Ratings below)
- `surfaces`: A list of surfaces this work touches (see Surfaces Vocabulary below)

### Rejected

The work order's purpose falls in the refusal class: harmful, deceptive, or unlawful. Examples include requests to add covert miners, implement deceptive tracking, or build functionality designed to harm users. Never quietly reformulate refused work into something buildable.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "rejected", "reasons": ["reason 1", "reason 2", ...]}`

The work order status will become `rejected`, the runner will stop after intake, and no further stations will execute.

### Rescoped

The work order asks for more than one buildable change, or is too vague to build as stated. Cut it down to one buildable scope and record what was removed and why.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "rescoped", "rescoped_description": "The buildable scope", "reasons": ["what was cut and why"]}`
- `risk`: Risk rating for the rescoped work
- `surfaces`: Surfaces the rescoped work touches

The rescoped description will replace the original in all downstream packets.

### Waiting for Information

The work order lacks information you need to judge it. Record your questions.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "waiting_info", "questions": ["question 1", "question 2", ...]}`

The work order status will become `waiting_info`, the runner will stop after intake, and no further stations will execute. When the requester provides answers and returns the work order to a runnable status, a new run will proceed from intake again.

## Risk Ratings

- **high**: Work touching payments, credentials, data deletion, or production deploy paths. High blast radius or irreversible changes.
- **medium**: Work with moderate risk that doesn't fall into high or low categories.
- **low**: Small, reversible changes with limited blast radius.

## Surfaces Vocabulary

Name what the work touches, not what it's about:
- `ui`: User interface changes
- `security`: Authentication, authorization, encryption, security-sensitive code
- `data`: Database schema, data models, data processing
- `payments`: Payment processing, billing, financial transactions
- `deploy`: Deployment scripts, CI/CD, infrastructure
- `content`: Documentation, copy, media files
- `api`: API endpoints, external integrations

Use the surfaces that apply. One work order can touch multiple surfaces.

## Output Format

Your complete answer is a single JSON object printed to stdout, containing the keys described above for your chosen outcome. The runner parses this JSON to determine how to proceed.


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

- (none)
