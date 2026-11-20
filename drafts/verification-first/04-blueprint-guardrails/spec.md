# Blueprint Guardrails: New Projects Are Born With Their Checks

Status: draft (not filed)
Slug: blueprint-guardrails

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

A blueprint today describes a project: stack, structure, first specs, deploy targets (blueprints/static-site.json, python-service.json, cloudflare-worker.json). It carries no checks. Every greenfield project therefore starts with an empty base: whatever the factory learned on the last project of the same kind reaches the next one only as reviewer prose or producer guidance, and the first builder writes the patterns every later builder will copy.

The factory builds many projects of few kinds. The place where a learning pays on every future project is the blueprint. This order lets a blueprint carry a guardrail pack (checks with stable ids, each with the reason and the fix in its failure message) that scaffolding installs into the new project and the checks gate runs from the first work order.

## Requirements

### R1. Guardrail pack
- A blueprint may carry a pack at blueprints/<id>/guardrails/: a manifest (rules, each with id, title, why, fix, and the command or callable that decides it) and the rule implementations.
- A rule's failure output names the rule id, the file and location, why the rule exists and what to do instead. The reason lives in the failure message, not in a comment in the produced code.
- The manifest is validated at load: unique ids, non-empty why and fix, resolvable implementation. A malformed pack fails blueprint loading naming the rule.

### R2. Installation at scaffolding
- Creating a project from a blueprint with a pack copies the pack into the project (verification/guardrails/) and appends its command to the project's checks in anvil.json, so the checks gate runs it on the first work order.
- The installed pack records the blueprint id and pack version it came from. anvil onboard reports, for an existing project, whether its pack is behind its blueprint's and lists the rules it lacks; it never rewrites a project's pack without a work order.

### R3. Rules arrive with provenance
- A rule enters a pack only through the practice door: a promoted practice with enforcement gate whose scope names the blueprint, with the rule id as its Check (order practice-enforcement-ladder). No rule ships on taste.
- This order ships the mechanism and, per blueprint, the rules the owner selects at filing from promoted practices and the proposals waiting in brain/inbox. A blueprint with no selected rule ships an empty, valid pack.

### R4. Zero dependency for build free stacks
- A pack for a stack with no build step (static-site) runs with the Python standard library only, so the blueprint's "no build step until a spec needs one" holds.

### R5. Regression tests
- New test files under tests/: (a) a fixture pack with one rule fails on a violating fixture project and its output carries id, location, why and fix; (b) scaffolding from a blueprint with a pack yields a project whose anvil.json checks include the pack command and whose pack records blueprint and version; (c) a pack with a duplicate id or empty why fails to load naming the rule; (d) onboard on a project with an older pack lists the missing rules and changes nothing; (e) a blueprint without a pack scaffolds exactly as before.

### Guardrails
- Authorized changes stated up front per practice P-15: blueprints/ (new guardrails directories and manifests), anvil/ scaffolding and onboarding modules, docs, new tests. Existing blueprint JSON files gain at most one optional key naming the pack.
- Frozen: the checks gate's behavior (the pack is one more configured command); existing projects' anvil.json (untouched until a work order updates them); deploy targets.
- Existing test files at the base ref are not modified or deleted. No em dash or en dash character in any produced file.

## Scenarios

- S1: Given a blueprint with a pack holding one rule, when a project is scaffolded from it, then the project carries the pack and its anvil.json checks run it.
- S2: Given that project and a change that violates the rule, when the checks gate runs, then it fails and the output names the rule id, the location, the reason and the fix, and no reviewer is dispatched.
- S3: Given a pack whose manifest repeats a rule id, when the blueprint loads, then loading fails naming the rule.
- S4: Given a project scaffolded before a rule was added to its blueprint's pack, when anvil onboard runs, then it lists the missing rule and writes nothing.
- S5: Given a blueprint with no pack, when a project is scaffolded, then the result is identical to the result before this change.
