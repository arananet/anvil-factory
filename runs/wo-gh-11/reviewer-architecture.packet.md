# Task packet: reviewer-architecture

## Station prompt

# Reviewer Architecture

## Role
Check fit with the project structure and decisions.

## Inputs
- code change
- brain/decisions

## Outputs
- review

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.

## Output Format

Return a JSON object with this structure:

{
  "station": "reviewer-architecture",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-architecture", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.


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
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: passed
- reviewer-spec: executed
- reviewer-security: executed
- reviewer-tests: executed

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-11/reviewer-architecture.review.json. The free output transcript stays as provenance and is never parsed for a review.
