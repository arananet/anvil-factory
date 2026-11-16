# Task packet: reviewer-spec

## Station prompt

# Reviewer Spec

## Role
Check the implementation against the spec, nothing else.

## Inputs
- spec
- code change

## Outputs
- review

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.

## Output Format

Return a JSON object with this structure:

{
  "station": "reviewer-spec",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-spec", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.

## Consumption discipline

Read the spec and the relevant upstream artifacts first. Search before opening files; read only the relevant ranges. Bound command output and summarize long test logs with failures and a path to the full log. Run focused checks while editing and the required project checks at handoff. Reuse valid upstream work. Keep the final handoff concise, with changed files, evidence and unresolved issues. Preserve the required output contract.


## Practices

Promoted practices that resolved for this station. Follow each rule.

- P-14 (Cross-order spec conflict detection): Before execution, check a new order's hard assertions (pinned counts, unconditional property pins, exact file sets) against standing contracts from prior orders on the same project; a collision is surfaced in the filing for an owner decision, never discovered by the checks gate mid-run.

## Work order

- id: wo-gh-43
- kind: feature
- title: ANVIL attribution by default: every shipped web project credits the factory
- source: github-issue
- description: Implement the spec in .openspec/specs/attribution-default/spec.md. Pipeline for this order is sdlc-default (see anvil.json). Mode: brownfield, the factory improving itself. Domain: factory core, station guidance and project scaffolding.

OWNER RULE (stated 2026-11-15): every project the factory ships carries an ANVIL attribution by default. The owner audited the shipped projects and found the rule is not true today: Sentia carries a bespoke credit, and Doom Fire, Mochi Smash, Platform25 and the live C64 page carry none. This order makes the factory itself produce the attribution by default, so future projects ship compliant without a retrofit. Retrofits of already shipped projects are separate orders (the Doom Fire retrofit is filed in its own repo); this order changes only the factory.

DEFAULT WORDING AND COMPLIANCE:
- Default attribution text, exact: "Made with ANVIL, an open source software factory." with a link to the ANVIL landing https://anvil-landing-7x1.pages.dev (the factory repo link is an accepted alternative target).
- A project bespoke credit that names ANVIL as the builder counts as compliant. Precedent, Sentia: "Sentia is a concept product, designed and built end to end by ANVIL, an open source software factory. Developed by Eduardo Arana."
- Placement: the page footer or an equivalent visible spot. On a game surface, a credits or footer element that does not break gameplay.
- No em dashes in any text this order writes.

BUILD, per the spec requirements:
- R1, the rule and its wording, as above, recorded in the spec and in the decision record of R5.
- R2, scaffold and onboard: anvil/scaffold.py new_project seeds the attribution requirement for web blueprints (blueprints/static-site.json, and blueprints/cloudflare-worker.json where it ships pages), so the seeded site-shell spec and project brain carry the footer requirement from the first build. anvil/onboard.py records the same requirement for onboarded web projects in its onboard output, without overwriting any existing project file (onboard never overwrites).
- R3, station guidance: stations/builder/PROMPT.md and stations/publisher/PROMPT.md carry the rule, the default wording, the placement guidance and the exception path (an owner approved exception recorded in the project spec).
- R4, deterministic check: the checks gate (anvil/gates.py, checks_gate) verifies, for a shipped web deliverable, that the deliverable HTML carries an attribution naming ANVIL: the default line, or a bespoke credit naming ANVIL as the builder. The gate fails when no attribution is present. Web deliverables only: orders and projects without an HTML deliverable are unaffected. A recorded owner exception in the project spec or project configuration is honoured.
- R5, decision record: brain/decisions/0012-anvil-attribution-default.md captures the rule as a long term factory decision, in the format of the existing records.
- R6, tests: tests cover the check passing on the default line, passing on a bespoke Sentia style credit, failing when no attribution exists, and not applying to a non web deliverable. The full factory suite stays green: python -m unittest discover -s tests -p 'test_*.py'.

AUTHORISED SURFACE (full legitimate surface for this spec): anvil/scaffold.py, anvil/onboard.py, anvil/gates.py, a new anvil/ module for the check if the line prefers one, blueprints/static-site.json, blueprints/cloudflare-worker.json, stations/builder/PROMPT.md, stations/publisher/PROMPT.md, brain/decisions/0012-anvil-attribution-default.md, .openspec/specs/attribution-default/spec.md, and tests/ for the new attribution tests only (per spec exception to the anvil.json protected_paths entry for tests/: the new tests are written by the test-writer station; the builder does not edit existing tests). No other protected path changes: anvil.json and pipelines/ stay untouched.

TOKEN CAP: 6,000,000, the factory standing proven configuration in anvil.yaml (max_run_tokens 6000000, max_agent_calls 32, max_runtime_turns 40), left unchanged. Calibration basis: the comparable factory feature order wo-gh-39 (configurable station timeout, code plus tests) measured 1,504,285 tokens total and was approved; this order touches more files but the same order of magnitude, and the standing cap leaves headroom above the largest single station of every comparable factory run.

REQUIRED LITERALS in the builder report: "Made with ANVIL, an open source software factory.", "0012", ".openspec/specs/attribution-default/spec.md", "S1", "S2", "S3", "S4", "S5", and the full suite result line.

The run stops at the human gate. Nothing merges without the owner gate word reported back through the operator.

- risk_hints: checks gate changes can false-fail other projects runs; the spec confines the check to web deliverables, accepts bespoke ANVIL credits, and honours a recorded owner exception
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: failed
- checks-gate: failed
- loopback: loopback
- builder: executed
- checks-gate: passed

## Run context

Read the upstream work before you start; it is the input your station builds on.

- Spec for this order: .openspec/specs/attribution-default/spec.md
- Output of intake: runs/wo-gh-43/intake.output.md
- Output of spec-writer: runs/wo-gh-43/spec-writer.output.md
- Output of test-writer: runs/wo-gh-43/test-writer.output.md
- Output of builder: runs/wo-gh-43/builder.output.md
- Output of builder: runs/wo-gh-43/builder.output.md

## Loopback feedback (attempt 2 of 3)

This is a re-review. The previous attempt was sent back by checks-gate to builder. Judge the work as it is now, and check that each finding below is resolved; do not pass a finding that is still open.

Reason: Gate checks failed; artifact validation: Builder report artifact /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/builder.output.md is missing. Required literal not found in full in the builder report: Made with ANVIL, an open source software factory. Required literal not found in full in the builder report: 0012

- # Checks Gate: pre-review
  Basis: builder_delta
  Attempt: 1
  
  # Protected Path Additions (Observed, Not Violations)
  Protected path addition (observed): tests/test_attribution_default.py (matches tests/)
  
  # Check Commands
  ## Command 1: python -m unittest discover -s tests -p 'test_*.py'
  Exit code: 1
  Output:
  ```
  ce for reviewers, not a final verdict. Record what you observe; reviewers are not bound by your self-assessment.\n\nThis verification step only applies when the Quality Charter section is present in your packet. For non-visual work, this step does not apply.\n\n## Definition of done\n- Every spec scenario for this order is satisfied on the final tree, not only the ones a test happens to cover.\n- The project check command passes on the final tree. You ran it and read the output. You did not edit, skip or delete a test to get there.\n- You exercised the change the way a user would (ran it, opened it, called it) and it works.\n- For anything a person will see, you looked at the rendered result at the sizes the spec names and it meets the stated bar, the project design system and the Craft skills in your packet.\n- The change stays inside the write set the work order allows.\n\n## Before you hand off\nRe-read your whole diff as a reviewer would and fix what you find. Then write the builder report: what changed and which scenario each change serves, the exact verification commands with their real summary lines, and plainly what is unmet, unverified or left open. A gap you repo

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-43/reviewer-spec.review.json. The free output transcript stays as provenance and is never parsed for a review.
