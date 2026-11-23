# 0017: Token budgets read cache reads at a weight

Status: proposed 2026-11-23, operator change outside the line (owner
direction of 2026-11-22: what makes the line cheaper is fixed from outside).

## Context

Every token budget (max_run_tokens, the station partitions of decision 0014,
the wrapper's in-flight ceiling) counted a token read from the prompt cache
like a fresh one. The usage artifacts of wo-gh-47 and wo-gh-49 show what
that measures: the test-writer of wo-gh-49 used 2141295 input tokens, of
which 2049857 were cache reads, in 33 turns, and the runtime's own estimate
for it was 1.46 USD. About 95 percent of all tokens were cache reads. The
limits were tracking turns, not cost, and they moved for reasons unrelated
to the work: intake stopped one run at 212779 tokens against 200000 and
used 66323 on the next run of the same order.

A budget in currency was considered. It needs either a price table kept up
to date per model, or the runtime's own estimate, which only some runtimes
report. A weight needs neither and works for anyone who copies ANVIL.

## Decision

- `efficiency.cache_read_weight`, a number from 0 to 1, default 1.0: what a
  cache read counts for against every token budget. The figure the budgets
  read is called budget tokens.
- Only budget decisions change. Usage artifacts, reports and state.json keep
  the raw counts; a budget message names the weight when it is not 1.0.
- The factory sets 0.1 and its table is recalibrated in budget tokens:
  max_run_tokens 3000000, about three times the measured consumption of a
  full run.
- The progress comment shows the runtime's cost estimate when there is one
  and no price table: the owner sees money while the limits stay in tokens.

## Consequences

- A project that does not set the key behaves exactly as before.
- Two existing tests pinned the factory cap at 15000000; they now assert
  that the partitions add up to whatever the cap is (operator edit).
- The weight is one number for all models. A runtime whose cache pricing
  differs sets its own.
