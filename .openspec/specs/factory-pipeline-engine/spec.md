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
- S6: Given the factory stations directory, when the registry loads, then it contains 23 stations including scout, blueprint and the content stations.

### Scenario: Dry run writes packets, envelopes and a swimlane
- S7: Given a work order, when the runner runs in dry run mode, then agent stations get packet files, every finished step gets an envelope, and a swimlane is written.

### Scenario: Project config overrides station defaults
- S8: Given an anvil.yaml override for a station model, when the registry is loaded with that config, then the station carries the overridden model.

### Scenario: Failing review loops back instead of approving
- S9: Given a review with verdict fail, when the runner aggregates it, then the report contains a loopback step returning work to builder and no approval.
