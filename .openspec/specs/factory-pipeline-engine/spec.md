# Factory Pipeline Engine

Status: approved
Slug: factory-pipeline-engine

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
Load, validate and order composable pipelines, load station manifests, and run a line in dry run mode with packets, envelopes, loopback and a swimlane.

## Requirements
- Pipelines are JSON with ordered stages, a stage is one station or a parallel group.
- Unknown, duplicate, empty and undersized parallel groups are rejected.
- Agent stations produce packets, never a claim that a model ran.
- The approver aggregates only reviews produced during the same run. Standing project reviews under reviews/<slug>/ are the project record read by `anvil check`; they are never run inputs, so a run whose reviewer stations only produced packets ends with verdict no_reviews.
- Run reports explain their decisions: report.json records the work order risk hints and a decision object whose approver entry lists the reviews counted in the run, the reviewer stations the pipeline expected, and one plain sentence naming the aggregation branch that produced the verdict, and whose human gate entry states whether a human is required, the risk hints that matched, and one plain sentence naming the gate branch taken. The sentences are generated from the same values the code acted on, at the moment the decision is made, and the same two sentences appear in swimlane.md under a Decision heading.

## Scenarios

### Scenario: Valid pipeline loads and flattens in order
- S1: Given a valid pipeline file, when it loads, then topological_order returns the stations in stage order.

### Scenario: Unknown station is rejected
- S2: Given a pipeline naming a station that does not exist, when it validates, then ValueError names the unknown station.

### Scenario: Duplicate station is rejected
- S3: Given a pipeline using one station twice, when it validates, then ValueError names the duplicate.

### Scenario: Empty pipeline is rejected
- S4: Given a pipeline with no stages, when it validates, then ValueError says the pipeline is empty.

### Scenario: Parallel group needs at least two stations
- S5: Given a parallel group with one station, when it validates, then ValueError says a parallel group needs at least 2 stations.

### Scenario: Registry loads all stations
- S6: Given the factory stations directory, when the registry loads, then it contains 24 stations including scout, blueprint, the content stations and the supervisor.

### Scenario: Dry run writes packets, envelopes and a swimlane
- S7: Given a work order, when the runner runs in dry run mode, then agent stations get packet files, every finished step gets an envelope, and a swimlane is written.

### Scenario: Project config overrides station defaults
- S8: Given an anvil.yaml override for a station model, when the registry is loaded with that config, then the station carries the overridden model.

### Scenario: Failing review loops back instead of approving
- S9: Given a review with verdict fail produced during the run, when the runner aggregates it, then the report contains a loopback step returning work to builder and no approval.

### Scenario: Approver only aggregates reviews from the same run
- S10: Given a project whose standing reviews under reviews/<slug>/ all pass, when a fresh run's reviewer stations only produce packets and no reviews are produced during the run, then the approver verdict is no_reviews, not approved.

### Scenario: Run report records why the approver and the human gate decided as they did
- S11: Given a run that finishes with a verdict and a human gate outcome, when the runner writes report.json, then the report carries the work order risk hints and a decision object whose approver rule sentence names the branch that produced the verdict (all counted reviews passed, a named reviewer returned fail, a named reviewer requested changes, or no reviews were produced in the run), whose human gate entry records whether a human is required, the risk hints that matched, and a rule sentence naming the branch taken (verdict not approved, approved verdict with a matched risk hint, or approved verdict with no matched risk hints), and swimlane.md repeats both sentences under a Decision heading.
