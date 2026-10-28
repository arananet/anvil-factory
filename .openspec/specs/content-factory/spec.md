# Content Factory

Status: approved
Slug: content-factory

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
The same factory core runs a content line, not only a software line. A topic enters as a work order, a brief replaces the spec, sources replace the test base, four content reviewers work in parallel, and publishing always passes a human gate.

## Requirements
- The station catalog includes content stations next to the software stations, in one registry.
- Content pipelines compose those stations with the shared intake, approver, triage and observer stations.
- Deterministic gates check the content brief and the AI generated disclosure on the draft.
- Publishing is a risk hint, so the human gate is always required before the publisher station.

## Scenarios

### Scenario: Content stations load in the shared registry
- S1: Given the factory stations directory, when the registry loads, then the content stations are present alongside the software stations.

### Scenario: Content pipelines validate
- S2: Given the content pipelines, when they validate against the registry, then content-default runs four content reviewers in parallel and content-short reuses two of them.

### Scenario: Brief and disclosure gates
- S3: Given a content piece with a complete brief and a disclosed draft, when the content gates run, then both pass, and each fails with a clear reason when its file or field is missing.

### Scenario: Publishing requires a human
- S4: Given a content work order with the publishing risk hint, when the human gate runs, then it returns required even when every review passed.
