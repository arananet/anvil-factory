# 0019: A review that passed is counted again, not asked again

Status: proposed 2026-11-25, operator change outside the line.

## Context

When the approver returned the work to the builder, every reviewer ran
again on the next attempt, including those that had passed. In the approved
run of wo-gh-47 the five reviewers that ran took 6.5 of 34 minutes and about
1.2 of 3.1 USD by the runtime's estimate; wo-gh-42 ran five reviewers three
times over one finding.

Running the reviewers at the same time was considered and left out. It
saves minutes, no tokens, and the runner's accounting, in-flight budgets and
progress record assume one station at a time.

## Decision

- `efficiency.carry_passed_reviews`, boolean, default false. When true, a
  review with verdict pass and no owner ruling is kept across a loopback
  from the approver to the builder and counted again without a dispatch.
- The step of a kept review has status `carried` and names the attempt it
  comes from; the approver's decision lists `reviews_carried`.
- A loopback to the spec-writer drops every kept review. The checks gate is
  never skipped.
- The factory turns it on.

## Consequences

- A loopback costs the builder, the gate and only the reviewers that asked
  for changes.
- A fix that breaks something a kept reviewer covers is seen only by the
  gate and by the reviewers still asking. A project that wants every
  reviewer on every attempt leaves the switch off.
