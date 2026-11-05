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

- id: wo-gh-30
- kind: feature
- title: Verification run: model migration routes on merged main
- source: github-issue
- description: Pure verification run on merged main (model migration, issue 29, merged at 7e426af0). NO CODE CHANGES: the builder is barred from modifying, adding or deleting any file; the standing tree on main is the deliverable under judgment.

Purpose: prove the new per-station model wiring end to end on merged main. The run report is the evidence and must show, per executed step, configured_model and executed_model agreeing with the migration policy:
- builder: claude-opus-5-5
- spec-writer, test-writer: claude-sonnet-5-5
- reviewer-spec, reviewer-tests, reviewer-security, reviewer-architecture: claude-sonnet-5-5
- reviewer-design, reviewer-ux: openai/gpt-6.1-sol, executed through the agentic Codex runtime, each writing its own counted review file
- intake, observer: claude-sonnet-5-5

The surface under review is the factory status page (the project's servable UI: anvil.yaml declares static_root status, page_path /index.html): reviewers judge the status page as rendered after the migration (rendered evidence is captured by the line after the builder step), the standing wiring files (anvil.yaml, tools/dispatch_station.py, tools/codex_station.py, tools/claude_station.py, anvil/routing.py, anvil/knowledge.py), decision record brain/decisions/0004-model-migration.md, and the route smoke script tools/model_route_smoke.py, all as they stand on main. Reviewers: a station that cannot execute on its assigned route, a configured/executed model disagreement, or a missing self-report is a fail with the evidence named; if every route executes as assigned, pass.

GitHub issue: https://github.com/arananet/anvil-factory/issues/30

VERIFICATION ROUND 2 (on current main, after the wo-gh-31 tier totality merge). Round 1 verdict: no_reviews; the gate failed on two test defects, both since resolved at the root:
1. This run's own test-writer encoded the builder policy as always claude-opus-5-5 and flagged the builder's actual assignment. OPERATOR RULING: on a work order carrying a UI surface, the guided design model assignment for the builder (openai/gpt-6.1-sol) is the correct policy behavior (migration spec R5); the policy the evidence test must encode is: builder is claude-opus-5-5 on non-UI work and openai/gpt-6.1-sol on UI-surface work, with executed_model self-reported and equal to the assignment. The test-writer corrects its round 1 test accordingly; that correction is the only test change this round.
2. The readme showcase link test failed because the runs/ evidence tree was missing from main's tree at that time (a merge artifact, since repaired on main at d5368392 and confirmed present). No action needed here; the suite on current main is the judge.
Everything else in the round 1 brief stands: no code changes by the builder; reviewers judge the routes as executed on current main, reviewer-design and reviewer-ux on openai/gpt-6.1-sol included.
- risk_hints: 
- status: new

## Upstream steps

- (none)
