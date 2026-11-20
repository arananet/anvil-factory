# Line Yield Metrics: First Pass, Survival and the Verification Share

Status: draft (not filed)
Slug: line-yield-metrics

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

The status page answers what the factory produced and where each job is. It does not answer whether the line works. Three numbers are missing.

First pass yield. Commit subjects across all refs of this repository record the verdict of every run. Of the work orders wo-gh-1 to wo-gh-32 that have a run on record, fourteen show at least one no_reviews verdict (wo-gh-6 shows six), and later orders repeat the shape (wo-gh-35, wo-gh-36, wo-gh-39, wo-gh-44). The pattern is visible only to someone reading git history.

Survival. An approved and merged order counts as a success forever, even when a later order exists only to repair it. docs/COST-MEASUREMENT.md already states the standard: "Compare total usage across all attempts per owner-accepted change". Nothing computes it.

Verification share. status/usage.json carries tokens by station, so the split between producing and verifying is derivable, but it is not shown and it rests on partial measurement (23 measured calls of 211 at the 2026-11-14 generation).

This order computes the three from records the factory already keeps and publishes them with their coverage stated.

## Requirements

### R1. First pass yield
- For each work order, the run history (runs/<id>/report.json and runs/<id>/history/) yields: the number of runs, the verdict of each in order, and whether the first run that executed reviewers ended approved.
- The status page shows per project: orders with a run on record, orders approved on their first run, the first pass yield as a count and a ratio, and the count of runs by verdict (approved, changes_requested, rejected, no_reviews, no-report, budget_exceeded).
- A run with verdict no_reviews or no-report is a line failure, counted separately from a judgment against the work (changes_requested, rejected).

### R2. Survival
- A work order may declare repairs: a list of work order ids whose merged result it corrects. Intake validates that each id names a merged order of the same project.
- A merged order survives when no later order declares it in repairs and no commit on main reverts its merge commit. The status page shows merged orders, survivors, and the ratio, with the repairing order linked.
- Orders filed before this change have no repairs field; they are shown as not assessed, never as survivors.

### R3. Verification share
- Project configuration gains station_roles, a map from station id to one of produce, verify, coordinate. The shipped default: spec-writer and builder produce; test-writer, checks-gate, verify and every reviewer verify; intake, approver, triage-human, deployer, observer, supervisor coordinate.
- The status page shows measured tokens by role and the verify share of produce plus verify, always next to the measurement coverage (measured calls of total calls). When coverage is below complete the figure is labelled partial; it is never presented as a total.

### R4. Reviewer yield
- Per reviewer station and project: counted reviews, verdicts by kind, findings raised, and measured tokens. No judgment is derived; the table exists so the owner can decide which reviewers earn their spend.

### R5. Cost per accepted change
- Per owner-accepted order: the sum of measured tokens, and the priced amount where the price table covers the executed models, across every run of that order including failed ones. Unmeasured runs are counted and named, and make the figure partial.

### R6. Regression tests
- New test files under tests/ with fixture run records: (a) an order with runs no_reviews then approved is not first pass and shows one line failure; (b) an order named in a later order's repairs is not a survivor and links the repairer; an order filed without the field is not assessed; (c) verification share from fixture usage matches a hand computed value and is labelled partial when coverage is partial; (d) cost per accepted change sums across runs and marks unmeasured runs.

### Guardrails
- Read only over existing run records; no station, no model call, no change to how runs execute.
- Additive to the report and status schemas; pages render for projects whose records predate the change.
- Frozen: cost-measurement semantics (totals are sums of measured steps; unmeasured stays unmeasured and says why); the lifecycle stage derivation; the review parse contract.
- Relationship to continuous run accounting (wo-gh-41): that order makes killed runs leave complete records; this order reads whatever records exist and states coverage. It is more accurate after 41 lands and does not require it.
- Existing test files at the base ref are not modified or deleted. No em dash or en dash character in any produced file.

## Scenarios

- S1: Given an order whose runs ended no_reviews then approved, when the status page is generated, then the order is not counted as first pass and the project shows one line failure.
- S2: Given a merged order later named in another order's repairs, when the status page is generated, then it is not a survivor and the repairing order is linked.
- S3: Given usage with 23 measured calls of 211, when the verification share is shown, then it carries the coverage and the label partial.
- S4: Given an order with three runs, one unmeasured, when cost per accepted change is shown, then it sums the two measured runs and names the unmeasured one.
- S5: Given a project whose records predate this change, when the status page is generated, then it renders, with survival shown as not assessed.
