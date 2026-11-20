# Task packet: reviewer-architecture

## Station prompt

# Reviewer Architecture

## Role
Check fit with the project structure and decisions.

## Inputs
- code change
- brain/decisions

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
  "station": "reviewer-architecture",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-architecture", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.

## Consumption discipline

Read the spec and the relevant upstream artifacts first. Search before opening files; read only the relevant ranges. Bound command output and summarize long test logs with failures and a path to the full log. Run focused checks while editing and the required project checks at handoff. Reuse valid upstream work. Keep the final handoff concise, with changed files, evidence and unresolved issues. Preserve the required output contract.


## Craft skills

Curated craft guidance resolved for this station and this work order. Order of authority: the work order and its spec, then the project design system and decisions, then promoted practices, then these skills. Where a skill conflicts with any of those, the skill yields. Apply what fits the work in front of you; a skill is a bar to meet, not a checklist to recite.

### Skill: architecture-fundamentals

Good architecture is the cheapest structure that makes the next change easy. Judge every structural choice by what it costs the next person who has to read or change it.

**Start from what exists**
- Read the project brain (brain/project.md, brain/decisions/) and the neighbouring code before you propose anything. Follow the existing structure and naming unless you can name the concrete problem that breaking it solves.
- A decision record that is already accepted is a constraint. If the work needs to break one, say so and record a new decision; do not quietly work around it.

**Boundaries**
- Give each module one reason to exist and a small interface that hides how it works. A module is deep when a lot of behaviour sits behind few entry points.
- Dependencies point one way: domain logic knows nothing about delivery (HTTP, CLI, UI) or storage; the edges depend on the core, never the reverse.
- Keep input and output at the edges. Parse and validate once at the boundary, then pass typed, trusted data inward. Pure functions in the middle are the ones you can test without a harness.
- One source of truth for every fact: a constant, a schema, a config value. A second copy is a future bug.

**Size the design to the problem**
- Choose the smallest stack and the fewest moving parts that ship the stated scope. Name what version one deliberately leaves out.
- Do not build for a requirement nobody has stated. No plugin system for one plugin, no abstraction with one implementation, no config flag for a value that never changes.
- Prefer boring, well documented technology already used in the project over a new dependency. Every new dependency needs a reason that a standard library or existing module cannot meet.

**State, failure and operation**
- Say where every piece of state lives, who owns it and how long it lives. Shared mutable state is the first place to look for a defect.
- Fail closed and loudly: an unknown input, a missing file or a malformed record is an error with a named reason, never a silent default.
- Make behaviour deterministic where it can be. Anything that can be decided by plain code should not be left to a model or to timing.
- Configuration comes from the environment or a config file, secrets never from the tree.

**Record the decision**
- When you make a choice that a reasonable engineer could have made differently, write down the context, the decision and the consequence in a few lines, where the project keeps decisions.
- State the trade off honestly: what this choice makes harder.

**Before you hand off, check**
- Can you describe each new module in one sentence without the word "and"?
- Does any new code reach across a boundary it should not?
- Is there a simpler structure that satisfies the same spec scenarios? If yes, use it.

## Work order

- id: wo-gh-41
- kind: feature
- title: Continuous run accounting: the run record is checkpointed after every station and completed on every exit path, budget death included
- source: github-issue
- description: Implement the spec in .openspec/specs/continuous-run-accounting/spec.md. Pipeline for this order is sdlc-default (software domain, the factory repo itself), selected by the run workflow.

STAGING: this order is filed and staged only. The spec and this work order record sit on the branch anvil/run-continuous-run-accounting, the issue carries no anvil label, and no run is fired. Execution starts on the owner's word. Run configuration baseline, unchanged by this filing: the order is parented on factory main 4675a131eb9aa88097741dc3cdc9772c3db17550 (the fixed spine merged by wo-gh-39), whose anvil.yaml carries max_run_tokens 6000000, max_runtime_turns 40 and max_packet_tokens 48000, and whose anvil.json wires the checks command (python -m unittest discover -s tests -p 'test_*.py').

EVIDENCE (the defect this order closes):
In the C64 blueprint chain (project c64-retro-hardware), work order wo-gh-6 (run 43668712644) exhausted its budget: the builder's single call measured 6,359,529 cache-inclusive tokens against the 6,000,000 run cap, and the run died with status budget_exceeded before the builder wrote its report. The branch held finished product but no builder report and no complete run record: 0 of 6 reviewers counted, and the run's own accounting did not exist. Work order wo-gh-7 then spent a second run (5,697,863 tokens measured) largely to write the paperwork wo-gh-6 never wrote, the builder report and the comparison records for work that already existed. The comparison against other software factories (factory research of 2026-11-15, report section "Mechanisms ANVIL Does Not Have", mechanisms 7 to 12 for failure mode 2) shows the standard shape elsewhere: mini-SWE-agent saves its trajectory in a finally block after every step and converts limit exceptions into recorded exit outcomes; Attractor checkpoints after every node and resumes from the last checkpoint; OpenHands treats an append-only event log as the run record.

BUILD, per the spec requirements:
R1: the runner writes the run record (runs/<work-order-id>/report.json with its step records) after every station completes, fails or is skipped, in the final report's shape plus a checkpoint field set (last completed station, elapsed milliseconds, measured usage so far). Writes are atomic (sibling temporary file, then rename), so a mid-run read always sees a valid report complete as of the last finished station. Checkpointing adds no station and no model call.
R2: every termination path completes the record before the process exits: normal completion, a verdict, budget exhausted (exit status budget_exceeded), a station timeout (using wo-gh-39's honest timeout records), the runtime turn limit, a checks gate stop, an intake stop, an uncaught exception in spine code, and the trappable external signals (SIGTERM, SIGINT). The completed record names the exit status, the termination reason, every station that ran with its outcome and executed model, every station that never ran as not run, and the cost section under cost-measurement semantics. A budget death is a complete recorded outcome carrying the measured consumption that crossed the cap and the station in flight, with its partial usage when exposed.
R3: inspecting or resuming after a killed run reads the checkpointed record as the run's accounting; tools/line_comment.py and the swimlane render a killed run's record with no station executing. A later run of the same work order preserves the killed run's record in the run history and never overwrites it.
R4: regression tests as new files under tests/, driving scripted runs through the runner with a fake runtime: (a) a run killed at the token cap mid-builder leaves a complete, parseable record (exit status budget_exceeded, per-station outcomes, the builder's measured partial usage, unrun stations named not run); (b) the same completeness holds for a station timeout death and for an injected uncaught error, each with its own exit status and reason; (c) a healthy scripted run checkpoints after each station and its final report equals the last checkpoint plus the verdict sections; (d) SIGTERM leaves a completed record naming the signal.

RECONCILIATION WITH ACTIVE SPECS (read before building; these are decisions, not discoveries for the line to make):
No active spec conflicts. The token-efficiency spec already requires per-attempt usage artifacts and that a budget stop preserves the report; this order generalizes that preservation to every exit path and makes it a runner property, using those artifacts as inputs. Cost-measurement semantics are frozen and reused as they stand (totals are sums of measured steps; unmeasured stays unmeasured with its reason). The station artifact contract's executed model honesty and the station-timeout record fields are inputs, unchanged.

BUILDER REPORT REQUIRED LITERALS: the builder report (runs/wo-gh-41/builder.output.md) must contain each of these in full, unabbreviated: 4675a131eb9aa88097741dc3cdc9772c3db17550, continuous-run-accounting, checkpoint, budget_exceeded. It must also state the base ref it verified the tree against, the exact full factory test count from the suite run, and the names of the new test files added.

GUARDRAILS: authorized surface for this order: anvil/runner.py, anvil/line.py, anvil/telemetry.py, anvil/cost.py, anvil/executor.py, anvil/cli.py (the resume and inspect paths), tools/line_comment.py, anvil/statuspage.py if it reads run reports, the factory docs that describe run reports or resume (docs/EXECUTION.md at minimum), CHANGELOG.md, one new decision record under brain/decisions/, and new test files under tests/. Pipeline files under pipelines/ are protected paths in anvil.json; the fix must hold without editing them. anvil.json itself is protected; do not edit it. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. Frozen: cost-measurement semantics, the station-timeout record fields, the review parse contract, the reviewer prompts. Python standard library only, no new dependency. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/41


GitHub issue: https://github.com/arananet/anvil-factory/issues/41
- risk_hints: 
- status: new

## Upstream steps

- intake: failed
- spec-writer: failed
- test-writer: failed
- builder: failed
- checks-gate: failed
- loopback: loopback
- builder: failed
- checks-gate: failed
- loopback: loopback
- builder: failed
- checks-gate: failed
- reviewer-spec: skipped
- reviewer-security: skipped
- reviewer-tests: skipped

## Loopback feedback (attempt 3 of 3)

This is a re-review. The previous attempt was sent back by checks-gate to builder. Judge the work as it is now, and check that each finding below is resolved; do not pass a finding that is still open.

Reason: Gate checks failed; artifact validation: Builder report artifact /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-41/runs/wo-gh-41/builder.output.md is missing.

- # Checks Gate: pre-review
  Basis: builder_delta
  Attempt: 2
  
  # Check Commands
  ## Command 1: python -m unittest discover -s tests -p 'test_*.py'
  Exit code: 0
  Output:
  ```
  anchName false"
  Switched to a new branch 'work-branch'
  .hint: Using 'master' as the name for the initial branch. This default branch name
  hint: will change to "main" in Git 3.0. To configure the initial branch name
  hint: to use in all of your new repositories, which will suppress this warning,
  hint: call:
  hint:
  hint: 	git config --global init.defaultBranch <name>
  hint:
  hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
  hint: 'development'. The just-created branch can be renamed via this command:
  hint:
  hint: 	git branch -m <name>
  hint:
  hint: Disable this message with "git config set advice.defaultBranchName false"
  Switched to a new branch 'work-branch'
  ................................................................................................................................../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 33281)>
    if method() is not None:
  ResourceWarning: Enable tracemalloc to get the object allocation traceback
  .../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 35267)>
    if method() is not None:
  ResourceWarning: Enable tracemal

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-41/reviewer-architecture.review.json. The free output transcript stays as provenance and is never parsed for a review.
