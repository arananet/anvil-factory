# Greenfield Projects

Status: approved
Slug: greenfield-projects

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
The factory builds from zero, not only on existing code. An idea enters as a work order, a blueprint station turns it into a project shape, and the new-project command scaffolds a ready to run project whose first spec already exists.

## Requirements
- Work orders accept the kind idea, alongside feature, bug, incident and task.
- A blueprint catalog holds starting shapes with stack, structure and first specs, validated on load.
- The greenfield pipeline runs intake, blueprint, spec-writer, then the shared build and review stations.
- New project scaffolding writes BLUEPRINT.md, seeds the brain with the idea, points anvil.json at the greenfield pipeline, and scaffolds the first spec.

## Scenarios

### Scenario: Idea work orders are accepted
- S1: Given a work order with kind idea, when it is created, then it validates and keeps its kind.

### Scenario: Blueprint catalog loads and validates
- S2: Given the factory blueprints directory, when the catalog loads, then at least three blueprints are available and an unknown id raises a clear error.

### Scenario: New project scaffolds from a blueprint
- S3: Given a blueprint id and an idea, when new-project runs, then BLUEPRINT.md exists, the brain carries the idea, anvil.json names the greenfield pipeline, and the first spec from the blueprint exists.

### Scenario: Greenfield pipeline validates
- S4: Given the greenfield pipeline file, when it validates against the registry, then its order starts with intake, blueprint and spec-writer and reuses the four parallel reviewers.
