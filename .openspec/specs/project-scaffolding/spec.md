# Project Scaffolding

Status: approved
Slug: project-scaffolding

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
Scaffolding creates a ready to use project skeleton and new specs from the shared template.

## Requirements
- Init creates the OpenSpec, brain, tests and reviews structure plus anvil.yaml and anvil.json.
- New spec fills the shared template placeholders.

## Scenarios

### Scenario: Init creates the project skeleton
- S1: Given a new path, when init runs, then the OpenSpec, brain, tests and reviews structure exists.

### Scenario: Init writes the Core Four config
- S2: Given a new path, when init runs, then anvil.yaml exists and sets context, model, prompt and tools per station.

### Scenario: New spec uses the template
- S3: Given an initialized project, when new-spec runs, then the spec file exists with Status draft, the title, and scenario S1.

### Scenario: Slugify normalizes titles
- S4: Given a title with spaces and punctuation, when slugify runs, then it returns a lowercase hyphenated slug.
