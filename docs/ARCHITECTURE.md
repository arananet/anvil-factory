# ANVIL Architecture

## Layers
- Model layer: anvil/model.py holds WorkOrder, Review and slugify. No logic beyond shape and validation.
- Pipeline layer: anvil/pipeline.py loads and validates pipeline JSON. Pipelines are data, not code.
- Station layer: stations/ holds one folder per station with station.json and, for agent stations, PROMPT.md. anvil/stations.py loads and validates them.
- Gate layer: anvil/gates.py and anvil/approver.py are deterministic. They never call a model.
- Runner layer: anvil/runner.py walks a pipeline, runs deterministic stations, and writes packets for agent stations.
- Scaffold layer: anvil/scaffold.py creates new projects and specs from templates.
- Intake layer: intake-worker/ is a small Cloudflare Worker that normalizes incoming requests into work orders.

## Artifact flow
A work order enters, a spec is written under .openspec/specs/, tests map to spec scenarios, a builder changes code, four reviewers write JSON reviews under reviews/, the approver aggregates them, human triage checks risk, and a run leaves its report, packets, envelopes and swimlane under runs/.

## Gates
- Spec gate: a spec exists, has a Status line and at least one Scenario line.
- TDD gate: every scenario id in the spec appears in the tests.
- Review gate: all four reviewer files exist and pass.
- Human gate: risk hints decide whether a human must look before the work moves on.

## Risk triage
Risk hints are explicit strings on the work order: auth, payments, data-deletion, production-deploy and secrets. Any match means human review is required. A verdict that is not approved also forces human review.

## The Core Four config
Each project has one anvil.yaml at its root. For every station it can set four things:
- context: the files that station reads
- model: a free text model label, so the factory stays model agnostic
- prompt: the path to the prompt file for that station
- tools: the list of tools that station may use

The file is written as JSON, which is valid YAML. That keeps parsing inside the Python standard library with no extra dependency, and it is stated here honestly instead of pretending a full YAML parser ships with the standard library. Project values in anvil.yaml override the defaults in station.json when the registry loads for that project.

## Model stack per station
Different stations get different default model labels because their jobs differ. Spec writing and test writing default to reasoning-strong, building to fast-builder, scouting to fast-reader, and reviewing, deploying and observing to review-balanced. These are labels, not vendor names. A project changes them in anvil.yaml without touching station code.

## Gate loopback
When review aggregation fails, the runner does not approve and does not stop silently. It records a loopback step that names where the work returns to and why: builder for implementation failures, spec-writer for spec failures, with the review findings as the reason. A run allows at most max_loopbacks loopbacks, 2 by default, and the report records both the limit and how many happened.

## Envelopes
Stations do not hand work to each other in chat. Each finished step writes a typed envelope under runs/<work-order-id>/envelopes/ with the schema anvil/envelope@1 and the fields from_station, to_station, work_order_id, artifact_path and created_at. The shared run directory is the session: anyone can replay what happened from the files alone.

## Observability
Every run writes report.json and swimlane.md. Each step records status, a real measured duration_ms, and the artifacts it produced. Cost is written as null with a note in the swimlane: model runtimes report cost when they actually run a station, and ANVIL never invents a number for a run that only wrote packets.

## Workflow sizes
Small work does not need the full line. The scout pipeline is one read only station. The plan-build-test pipeline covers spec, tests, build and a test review. The default SDLC pipeline is the full line. Size the line to the work.

## Adding a station
1. Create stations/<id>/station.json with id, name, kind, inputs, outputs and description, plus the Core Four defaults.
2. For an agent station, add PROMPT.md with role, inputs, outputs and rules.
3. Reference the station id in a pipeline JSON.
4. Run validate-pipeline to confirm the line still validates.

## Greenfield mode

Brownfield work starts from an existing repo. Greenfield work starts from an idea, and the factory treats that as a first class entry, not as a missing repo.

- Intake accepts work orders of kind idea next to feature, bug, incident and task.
- The blueprint station reads the idea brief and the blueprint catalog in blueprints/. Each catalog entry is data, not code: stack, structure and the first spec slugs for one starting shape. The station output is BLUEPRINT.md in the new project.
- The deterministic half is anvil new-project: it scaffolds the project with init, writes BLUEPRINT.md, seeds brain/project.md with the idea, points anvil.json at the greenfield pipeline, and scaffolds the first spec from the blueprint, so spec-writer starts from a shape instead of a blank page.
- From spec-writer on, greenfield and brownfield share every station, gate and review. Nothing about the build, review or approval path is special once the project exists.
