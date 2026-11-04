# Task packet: intake

## Station prompt

# Intake Station

## Role

Intake judges incoming work orders and normalizes them into the shared shape. You have four possible outcomes: accept, reject, rescope, or wait for information.

## Outcomes

### Accepted

The work order is buildable as stated. Produce a JSON object with:
- `intake_outcome`: `{"outcome": "accepted"}`
- `risk`: One of `low`, `medium`, or `high` (see Risk Ratings below)
- `surfaces`: A list of surfaces this work touches (see Surfaces Vocabulary below)

### Rejected

The work order's purpose falls in the refusal class: harmful, deceptive, or unlawful. Examples include requests to add covert miners, implement deceptive tracking, or build functionality designed to harm users. Never quietly reformulate refused work into something buildable.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "rejected", "reasons": ["reason 1", "reason 2", ...]}`

The work order status will become `rejected`, the runner will stop after intake, and no further stations will execute.

### Rescoped

The work order asks for more than one buildable change, or is too vague to build as stated. Cut it down to one buildable scope and record what was removed and why.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "rescoped", "rescoped_description": "The buildable scope", "reasons": ["what was cut and why"]}`
- `risk`: Risk rating for the rescoped work
- `surfaces`: Surfaces the rescoped work touches

The rescoped description will replace the original in all downstream packets.

### Waiting for Information

The work order lacks information you need to judge it. Record your questions.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "waiting_info", "questions": ["question 1", "question 2", ...]}`

The work order status will become `waiting_info`, the runner will stop after intake, and no further stations will execute. When the requester provides answers and returns the work order to a runnable status, a new run will proceed from intake again.

## Risk Ratings

- **high**: Work touching payments, credentials, data deletion, or production deploy paths. High blast radius or irreversible changes.
- **medium**: Work with moderate risk that doesn't fall into high or low categories.
- **low**: Small, reversible changes with limited blast radius.

## Surfaces Vocabulary

Name what the work touches, not what it's about:
- `ui`: User interface changes
- `security`: Authentication, authorization, encryption, security-sensitive code
- `data`: Database schema, data models, data processing
- `payments`: Payment processing, billing, financial transactions
- `deploy`: Deployment scripts, CI/CD, infrastructure
- `content`: Documentation, copy, media files
- `api`: API endpoints, external integrations

Use the surfaces that apply. One work order can touch multiple surfaces.

## Output Format

Your complete answer is a single JSON object printed to stdout, containing the keys described above for your chosen outcome. The runner parses this JSON to determine how to proceed.


## Work order

- id: wo-gh-11
- kind: feature
- title: Design knowledge base for the design stations
- source: github-issue
- description: Implement the spec in .openspec/specs/design-knowledge/spec.md in the factory. The spec defines the UX module's base layer and its guide designation.

Build, per the spec scenarios:

S1: the built in starter knowledge dataset, original content authored for ANVIL in the factory's voice, as data files under design-knowledge/ (styles.json, palettes.json organized by product type, fonts.json, guidelines.json, product-types.json), with a loader that validates required fields per entry and fails naming the file and entry on a malformed entry.

S2: deterministic slice matching: the project's declared product type selects the product type note plus the styles, palettes and pairings it references and the general guidelines; same inputs, same slice.

S3: packet injection of a Design knowledge section (slice plus authority statement) for reviewer-design, for the builder on a UI surface, and for the design authoring path (a station whose work order targets design/DESIGN.md); other stations' packets unchanged; the slice is computed once per run.

S4: authority stated in the injected section and in reviewer-design's contract: the project's design system wins on conflict, and a deviation from the knowledge base alone is never a finding.

S5: an undeclared or unknown product type selects the general guidelines only and the packet records that no product type slice matched.

S6: citation discipline in the station contracts: a Design knowledge sources note in DESIGN.md citing entries by data kind and entry name (pack supplied entries cited as operator supplied pack entries), and reviewer-design names the knowledge entry behind any suggestion.

S7 and S8: operator supplied knowledge packs at runtime. A work order may name a pack by a filesystem path (knowledge_pack field): a directory outside any repository tree holding manifest.json (pack name, format version, product types covered, data files) plus data files in the same five kinds. The runner loads and validates the pack at run start, prefers pack entries for the product types the pack covers, falls back to the built in dataset otherwise, and records the pack in the run report as an operator supplied input (name, manifest product types, file list). The runner never writes pack files into the project or factory tree, and a factory test proves a pack handed in with a work order reaches the design packets while the repository tree after the run contains no pack file and no committed file contains pack content.

S9: a pack path that does not resolve or a manifest that fails validation stops the run at intake with the failure recorded and no station spawned.

S10: the guide designation recorded in the catalog: the design stations that apply the base (design authoring stations, the builder's UI surface role, reviewer-design) carry the guided design station designation in their catalog entries, naming the design model from the recorded routing policy (openai/gpt-6-astra) as their designated model.

Tests covering S1 to S10 in the factory suite style, docs updated (a docs page describing the UX module: the knowledge base layer, packs, the authority rule, and the guided stations), CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/11

Operator standing note for every round of this order: the builder must not create or modify anything under .github/workflows/ (the Actions token cannot push workflow changes; a run that touches them loses its commit-back). Tooling the run needs is staged by the operator in the workflow before the line step. Test changes are written by the test-writer station; the builder must not modify tests/, anvil.json or pipelines/. Tests must be real: every test calls the implementation it names and asserts behavior, never the mere existence of data structures.

GATE LOOPBACK 1 (after run 41768971456, verdict changes_requested, reviews counted 5 of 5; reviewer-architecture is the only requesting reviewer). The knowledge data layer and rendering exist; the runtime wiring does not. Fix exactly these counted findings:

1. Wire S3 into packet building: the runner's packet construction must include the Design knowledge section (slice plus authority statement) for reviewer-design, for the builder on a UI surface, and for the design authoring path, by calling the knowledge module (packet_knowledge_section or its successor) from the packet pipeline (anvil/runner.py packet_step and anvil/design.py as appropriate). Other stations' packets stay unchanged, and the slice is computed once per run (S2).

2. Wire the runtime pack flow (S7, S8, S9): at run start the runner reads the work order's knowledge_pack field when present, loads and validates the pack, prefers pack entries for the product types the pack covers, falls back to the built in dataset otherwise, and records the pack in the run report as an operator supplied input (name and manifest product types at minimum).

3. S10 guide designation: the station catalogs must stop hardcoding a design model string. The guide designation reads the design model from the recorded routing policy (anvil/routing.py) at the point of use, whatever model the policy currently records; no model name is duplicated across station.json files.

4. Defense in depth on pack loading (approver note): the pack loader rejects paths that resolve into sensitive system locations (for example /etc, /sys, /proc) with a named error at load, covered by a test. The existing whitelist based filename validation stays.

Real tests for the wiring, written by the test-writer station: a run level test proving a design station packet contains the knowledge section and a non design packet does not; a pack loading test proving preference, fallback and report recording; a sensitive path rejection test. The builder must not modify tests/, anvil.json, pipelines/ or .github/workflows/. Keep the whole suite green and every pipeline valid. Update CHANGELOG Unreleased.

GATE LOOPBACK 2 (after run 41771847615, verdict changes_requested, reviews counted 5 of 5; reviewer-tests and reviewer-architecture request changes). The packet and pack wiring from loopback 1 stands (reviewer-spec, reviewer-security and reviewer-design pass). Remaining, verbatim in substance:

1. S10 is declared but not wired into the runtime (reviewer-architecture): the station.json files declare guided and designation for the guided stations, but the Station dataclass in anvil/stations.py has no guided field, so load_registry drops it, and the runner never applies the design model from the routing policy to guided stations. get_design_model_from_routing exists in anvil/knowledge.py and is never called. Fix: add the guided field to the Station dataclass, preserve it in load_registry, and in the runner apply the design model read from the recorded routing policy (the policy's designer entry) at the point of use when a station is guided.

2. Three tests skip instead of testing (reviewer-tests): test_s1_malformed_entry_fails_validation imports a nonexistent load_knowledge and skips; it must import load_builtin_knowledge and actually assert that a malformed entry fails naming the file and entry. test_s10_guide_designation_names_design_model imports a nonexistent load_routing_policy and skips; it must use the real accessor and assert the guided stations resolve to the policy's design model. test_s1_builtin_dataset_exists_and_validates never calls the loader; it must call load_builtin_knowledge() and assert it succeeds. Remove the import failure skip pattern from these tests: a test that cannot import its subject must fail, not skip.

The test-writer station owns the test fixes; the builder owns the stations and runner wiring and must not modify tests/, anvil.json, pipelines/ or .github/workflows/. Keep the whole suite green and every pipeline valid. Update CHANGELOG Unreleased if the change set changes.
- risk_hints: 
- status: new

## Upstream steps

- (none)
