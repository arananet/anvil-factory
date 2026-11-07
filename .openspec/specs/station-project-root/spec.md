# Station Project Root

Status: draft
Slug: station-project-root

## Roles
- implementer: fixes the station wrappers described here
- reviewer: checks the fix and its tests against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
The station wrappers (tools/claude_station.py and tools/codex_station.py) must execute every station inside the project being built, never inside the factory checkout. Today both wrappers resolve repo_root as the parent directory of their own tools folder. When a project's runtime command points at a factory checkout inside the project (for example python3 .anvil-factory/tools/dispatch_station.py, the wiring a real project shipped with), every station session runs in the factory tree: reviewers read the factory's specs and stale run outputs, write their review files where the project runner never looks, and the run ends no_reviews with zero counted reviews despite the reviewers having executed. Evidence: arananet/foryou-lab run 42336853184 (issue 34). docs/EXECUTION.md already promises the correct contract: stations run in the project root, with ANVIL_WORK_ORDER_ID in the environment. This spec makes the code keep that promise regardless of where the wrapper files live.

## Requirements
- Both wrappers resolve the project root from the execution context, identically: the packet path and output path the runner passes (both live under the project's runs directory), the process working directory, or an explicit environment value the runner sets. The wrapper's own file location must never decide the project root on its own.
- If the project root cannot be determined unambiguously, the wrapper fails loudly with a nonzero exit and a message naming the problem. Executing in a guessed tree is worse than not executing.
- Reviewer review files and correction metadata are written and validated under the resolved project root, at runs/<work-order-id>/<station>.review.json.
- Builder and test-writer edits land in the resolved project root's working tree.
- The in-factory layout keeps working: when the factory repo is its own project, the resolved root is the factory repo and behaviour is unchanged.
- docs/EXECUTION.md is updated only if the contract wording changes; the code must match the doc either way.
- Done means: the scenarios below pass as automated tests in the factory suite, the full suite stays green, and no station behaviour other than root resolution changes.

## Scenarios

### Scenario: External layout, reviewer file lands in the project
- S1: Given a project directory P and a separate factory checkout F inside or beside P, when a reviewer station is executed through F's tools with a packet that lives under P/runs/<wo>/, then the station session's working directory is P, and a valid review file appears at P/runs/<wo>/<station>.review.json, where the runner counts it. No file is created under F/runs/.

### Scenario: External layout, builder edits the project tree
- S2: Given the same external layout, when the builder station executes, then its file edits are present in P's working tree afterwards, and F's tree is byte-identical to before the run.

### Scenario: In-factory layout unchanged
- S3: Given the factory repo as its own project (packet under the factory's runs/), when any station executes through the factory's own tools, then the resolved root is the factory repo and outputs, review files and edits land exactly where they land today.

### Scenario: Undeterminable root fails loudly
- S4: Given a packet path and output path that do not identify a project root and no usable environment value, when a wrapper is invoked, then it exits nonzero with an error naming the project root problem, and it runs no station session.

### Scenario: Both wrappers agree
- S5: Given the S1 layout, when the same packet is dispatched once through the Claude wrapper and once through the Codex wrapper, then both resolve the same project root P.
