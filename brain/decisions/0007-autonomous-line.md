# 0007: The line runs itself between the issue and the human gate

Status: recorded 2026-11-12 at the owner's request ("Arregla todo. Debe ser funcional.").

## Context

An audit of the engine, the workflows and the 22 recorded runs on 2026-11-12
found that the factory depended on an operator at every joint: a loopback was
recorded but nothing ran again (wo-gh-36 needed a copied workflow,
anvil-execute-practice-skills-r2.yml), each work order had its own workflow
file, the intake worker forwarded nothing, the human gate could not be
answered, `anvil run` always exited 0, the publisher ran behind a closed
gate, and routing dropped every content reviewer.

## Decision

The engine owns what the operator was doing by hand: re-running stations on a
loopback, the branch and commit of a run, the exit code, the recorded human
approval and the resume after it. One workflow serves every order. Spec:
.openspec/specs/autonomous-line/spec.md.

Merging stays the owner's act (auto merge is an opt-in repository variable),
and a human approval is always a named, recorded act bound to one run.

## Provenance

Owner-authored work outside the line, under decision 0006. The line neither
produced nor reviewed it. The evidence is tests/test_autonomous_line.py and
intake-worker/dispatch.test.js; the workflow itself has not yet run on
GitHub Actions at the time of this record.

## Consequences

- The 24 anvil-execute-*.yml workflows are removed; their runs remain in runs/.
- Default max_agent_calls is 32 (was 16) so one full correction fits.
- Reviewers still run sequentially. The reviewer tree guard that blocked
  parallel reviewers left with the Codex runtime (decision 0008); the runner's
  between-call budget checks are what remains.
