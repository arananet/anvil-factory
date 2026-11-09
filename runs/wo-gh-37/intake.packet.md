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

- id: wo-gh-37
- kind: feature
- title: Station artifact contract: station results are artifacts, validated deterministically, and failed reviewers are never silently dropped
- source: github-issue
- description: Implement the spec in .openspec/specs/station-artifact-contract/spec.md. Owner's instruction 2026-11-09, verbatim: "arreglemos anvil y esto, si es un software factory es una castana". Pipeline for this order is sdlc-default, selected by the run workflow.

THE DEFECT FAMILY (full evidence with run ids and exact failure strings in issue 37): across every run of two consumer projects (arananet/foryou-lab and arananet/giana-3d), station channels returned conversation or nothing where file artifacts were expected, and the approver silently approved on the remaining votes. Reviewer-design and reviewer-ux were never counted in any run: design failed with "Codex empty output" although its review.json existed with substantive findings; ux failed with "changed files outside its review file: runs/wo-gh-1/reviewer-*.output.md", executor exited 8, configured openai/gpt-6.1-sol, executed_model null. The builder station's chat reply landed AS runs/<wo>/builder.output.md twice in Dreamrun: R7 a 263 byte stub falsely claiming all 159 tests pass, and R8 (a loopback filed only to restore that report) a first-person chat summary that abbreviates the required sha256 as 67217b9d...c83b86f so the full literal never appears.

BUILD, per the spec scenarios:
S1: a station result is the artifact file or files named in its packet, read back from the run tree; conversational stdout is never the result; missing, empty or shape-failing artifacts fail the station fast with the reason and the real executed model recorded in report.json.
S2: deterministic artifact validation in the checks gate after the builder and before any reviewer spend (owner preflight doctrine, 2026-11-04): builder report exists and contains every work-order-declared required literal in full; reviewer review.json files exist and parse. Failure returns the work to the builder without launching reviewers.
S3: approver honesty: an expected reviewer that failed or was not counted makes the verdict human_required (or changes_requested), never a silent approved, with the uncounted stations named in the decision text.
S4: regression tests as NEW files under tests/ reproducing the three observed modes with fixtures: empty captured output with a valid review.json written; a reviewer writing an extra .output.md outside its review file; a builder chat summary lacking a required literal bounced by the S2 check.
S5: no regressions: the existing factory suite stays green, pipelines unchanged, healthy-station behavior identical.

GUARDRAILS: implement in the spine (anvil/: runner, checks gate, approver). Pipeline files under pipelines/ are protected paths in anvil.json; the contract must hold without editing them. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. Python standard library only, no new dependency. Channel-agnostic: validate artifacts, never special-case a model brand. Do not weaken the review parse contract or the existing protected-path gate behavior. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner's human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/37
- risk_hints: 
- status: new

## Upstream steps

- (none)
