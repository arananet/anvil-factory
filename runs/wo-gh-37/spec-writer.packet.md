# Task packet: spec-writer

## Station prompt

# Spec Writer

## Role
Write or revise an OpenSpec spec from a work order.

## Inputs
- work order
- brain

## Outputs
- spec

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


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

- intake: executed
