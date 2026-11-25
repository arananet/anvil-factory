# 0018: Run evidence stays with its run

Status: proposed 2026-11-24, operator change outside the line.

## Context

Test-writers assert facts about their own order's run: the tree against the
base ref, files the order must not touch, lines the order adds. Those tests
stay in the suite after the order merges. From then on they compare a later
order's tree with an old ref and fail it at the checks gate, where the
builder cannot change them. wo-gh-47 lost two runs to evidence tests of
wo-gh-42 (about 8 million tokens each), and an evidence test of wo-gh-41
failed whenever an operator fixed an existing test on a run branch.

The rule was first written into each order's issue. That is prose, the
weakest layer of the pyramid, and it has to be remembered every time.

## Decision

- A test file that carries a full commit id or a comparison with factory
  main must carry a guard binding it to its order: a skip unless
  ANVIL_WORK_ORDER_ID names the order, or a check of the run branch name.
- tests/test_run_evidence_scoping.py enforces it over every test file, so
  the checks gate of the order that writes such a test fails it at once,
  while the test-writer and builder can still fix it.
- The test-writer prompt states the rule and names the check. It also
  forbids comparing wall clock figures between two runs for equality, the
  other cause of a test that fails for no reason of the order.

## Consequences

- The check reads text, not behavior: a guard that is present but wrong
  passes. It closes the case that happened, a guard that is absent.
- Orders no longer need the rule repeated in their issue.
