# Task packet: deployer

## Station prompt

# Deployer

## Role
Prepare and carry out the release step described by the project.

## Inputs
- approved change

## Outputs
- release record

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.

## Consumption discipline

Read the spec and the relevant upstream artifacts first. Search before opening files; read only the relevant ranges. Bound command output and summarize long test logs with failures and a path to the full log. Run focused checks while editing and the required project checks at handoff. Reuse valid upstream work. Keep the final handoff concise, with changed files, evidence and unresolved issues. Preserve the required output contract.


## Work order

- id: wo-gh-44
- kind: feature
- title: Enterprise port: secret hygiene, Copilot telemetry and operator guide on the single-runtime design
- source: github-issue
- description: Port of an owner-supplied patch (produced outside this repository on 2026-11-15) with corrected scope, per the spec in .openspec/specs/enterprise-port/spec.md on branch anvil/run-enterprise-port.

What the port brings in: the secret hygiene package (hardened factory .gitignore, a project .gitignore template installed by the scaffold, a secret scanning test), Copilot runtime telemetry (token usage and failure reasons from the session output), the usage sync --allow-private flag, and a consolidated operator guide.

Corrections to the patch as supplied, decided by the owner before filing:
- Anthropic only (decisions 0008 and 0012): the patch's Copilot model mapping names openai/gpt-6.1-sol; the ported mapping contains only Anthropic models, and a non-Anthropic id under any runtime fails loudly.
- Single runtime design (decisions 0008 and 0010): the patch arrives as a second station wrapper (tools/copilot_station.py). The port strengthens the existing wrapper path (tools/claude_station.py and tools/copilot_runtime.py) instead; no parallel wrapper is created.
- The patch does not apply to current main (its dispatch base diverged), so this is a hand port guided by the patch as source material, not a git apply.

The patch itself is committed on the branch as the order's source artifact. The run stops at the owner human gate; nothing merges, publishes or deploys.

GitHub issue: https://github.com/arananet/anvil-factory/issues/44
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
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
- reviewer-architecture: skipped
- reviewer-design: skipped
- reviewer-ux: skipped
- approver: completed
- triage-human: completed

## Run context

Read the upstream work before you start; it is the input your station builds on.

- Output of intake: runs/wo-gh-44/intake.output.md

## Loopback feedback (attempt 3 of 3)

The previous attempt was sent back by checks-gate to builder. Resolve every finding below. Keep what already passed; do not start over.

Reason: Gate checks failed; artifact validation: Builder report artifact /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-44/runs/wo-gh-44/builder.output.md is missing.

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
  ................................................................................................................................../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 36399)>
    if method() is not None:
  ResourceWarning: Enable tracemalloc to get the object allocation traceback
  .../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 45213)>
    if method() is not None:
  ResourceWarning: Enable tracemal
