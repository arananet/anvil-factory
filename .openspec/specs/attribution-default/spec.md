# ANVIL Attribution by Default

Status: filed for wo-gh-43
Slug: attribution-default

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
The owner rule, stated 2026-11-15: every project the factory ships carries an ANVIL attribution by default. An operator audit of the shipped projects on 2026-11-15 found the rule is not true today. Sentia carries a bespoke credit ("Sentia is a concept product, designed and built end to end by ANVIL, an open source software factory. Developed by Eduardo Arana.", the owner chosen wording of 2026-10-30), while Doom Fire, Mochi Smash, Platform25 and the live C64 page carry no attribution at all. Nothing in the factory produces the attribution: the scaffold does not seed it, the builder and publisher guidance do not state it, and the checks gate cannot see its absence. This spec makes the factory produce it by default, so future projects ship compliant and only the already shipped projects need retrofits, which are separate orders in their own repos.

## Requirements
- R1, the rule and the default wording. Every web project the factory scaffolds or onboards carries, by default, a visible attribution reading exactly "Made with ANVIL, an open source software factory." with a link to the ANVIL landing (https://anvil-landing-7x1.pages.dev) or to the factory repository. A project bespoke credit that names ANVIL as the builder counts as compliant and is never replaced by the default line; the Sentia credit quoted in the Purpose is the standing example. Placement is the page footer or an equivalent visible spot; on a game surface, a credits or footer element that does not break gameplay. No em dashes in the attribution text or in any text this order writes.
- R2, scaffold and onboard. anvil/scaffold.py (new_project) seeds the attribution requirement for web blueprints (blueprints/static-site.json, and blueprints/cloudflare-worker.json where it ships pages): the seeded first spec (site-shell) and the seeded project brain state the footer requirement, its default wording and the compliance rule of R1, so the first build of a new project includes it. anvil/onboard.py records the same requirement for an onboarded web project in its onboard output. Onboard never overwrites an existing project file, and this order does not change that: for onboarded projects the requirement is recorded, not forced into their pages.
- R3, station guidance. stations/builder/PROMPT.md and stations/publisher/PROMPT.md state the rule of R1: build the attribution in by default on web deliverables, keep a compliant bespoke credit when the project has one, place it per R1, and treat its absence at publish time as a defect. The only way a project ships without an attribution is an owner approved exception recorded in that project spec, named in the guidance.
- R4, deterministic check. The checks gate (anvil/gates.py, checks_gate) gains an attribution check for shipped web deliverables: given the deliverable HTML of a web project (dist/, public/ or the project root index, following the project layout), the check passes when the visible text carries an attribution naming ANVIL (the default line of R1, or a bespoke credit naming ANVIL as the builder), and fails the gate when no attribution naming ANVIL is present. The check applies only when the order ships a web deliverable; projects and orders without an HTML deliverable are unaffected. A recorded owner exception (R3) is honoured and passes with the exception named in the check output.
- R5, decision record. brain/decisions/0012-anvil-attribution-default.md records the rule as a long term factory decision, following the format of the existing decision records: context (the audit and its findings), the decision (R1 to R4 in brief), and consequences (future projects compliant by default, shipped projects retrofitted by their own orders, exceptions only by recorded owner approval).
- R6, tests. The factory test suite gains tests for the check of R4: pass on the default line, pass on a bespoke Sentia style credit, fail when no attribution exists, pass with a recorded exception, and not applicable to a non web deliverable. The full suite stays green under the project check command: python -m unittest discover -s tests -p 'test_*.py'.

## Authorised surface
anvil/scaffold.py, anvil/onboard.py, anvil/gates.py, a new anvil/ module for the check if the line prefers one, blueprints/static-site.json, blueprints/cloudflare-worker.json, stations/builder/PROMPT.md, stations/publisher/PROMPT.md, brain/decisions/0012-anvil-attribution-default.md, this spec, and tests/ for the new attribution tests only (per spec exception to the anvil.json protected_paths entry for tests/: new tests are written by the test-writer station, existing tests are not edited by the builder). anvil.json and pipelines/ stay untouched.

## Scenarios
- S1, scaffold seeds the rule: a new static-site project scaffolded after this change carries the attribution requirement in its seeded site-shell spec and brain, naming the default wording and the bespoke compliance rule.
- S2, check passes: a web deliverable whose footer reads "Made with ANVIL, an open source software factory." passes the attribution check; a deliverable carrying the Sentia bespoke credit also passes.
- S3, check fails: a web deliverable with no attribution naming ANVIL fails the checks gate, and the gate output names the missing attribution as the reason.
- S4, exception honoured: a web deliverable from a project whose spec records an owner approved exception passes, with the exception named in the check output.
- S5, non web unaffected and suite green: an order with no HTML deliverable runs the checks gate with no attribution failure, and the full factory test suite passes, including the new tests of R6.
