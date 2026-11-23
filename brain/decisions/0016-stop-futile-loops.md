# 0016: Three deterministic stops for loops that cannot change the outcome

Status: proposed 2026-11-23, work order wo-gh-49, spec stop-futile-loops.
Built by the line up to the checks gate and finished by the operator.

## Context

Two runs spent most of their budget on attempts that could not succeed.
wo-gh-41 (run 44682387438) failed the gate three times on one existing
protected test that asserted the opposite of the order. wo-gh-42 (run
44912754341) passed the gate three times while every reviewer asked for an
owner ruling the builder could not give; its third attempt changed no code.
In both the signal was on the record before the money was spent. The run
that built this order (45086042758) repeated the pattern: the same ten gate
failures twice, then the builder partition ran out, 8173266 tokens in all.

## Decision

- A review may carry one optional string field, `owner_ruling`. When a
  counted review carries it the run ends with exit status
  `owner_ruling_needed` and no loopback. The review and run verdict
  vocabularies do not grow.
- A builder attempt that answers a loopback and changes no file outside
  runs/ ends the run with `no_progress`, provided an earlier attempt of the
  same run did change the tree. The proviso is an operator amendment: a
  builder that never moved is left to the gate and the reviewers, which is
  what every run did before this decision and what ten existing tests with
  scripted runtimes rely on.
- A pre-review gate failure whose non-empty signature equals the previous
  attempt's ends the run with `checks_stuck`. An unrecognized failure never
  triggers it.
- The three stops are on by default and each has a switch under
  `efficiency`. The defaults live in anvil/config.py, so the efficiency
  block a new project is generated with is unchanged.

## Consequences

- The scenarios of tests/test_station_budgets_completeness.py script a
  builder that rewrites the same files on every attempt; their project
  fixture turns `stop_on_no_progress` off (operator edit of an existing
  test, one line, no assertion changed).
- A run that ends on one of these stops needs a person: the report states
  which stop ended it and the next human action.
- Lesson recorded for the operator: an order that changes the run spine of
  the factory itself is cheaper finished by hand than relaunched; the line
  is kept for product work.
