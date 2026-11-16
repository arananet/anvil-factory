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

## Out of scope
- Retrofits of already shipped projects (Sentia, Doom Fire, Mochi Smash, Platform25, the live C64 page); each is its own order in its own repo.
- Forcing the attribution into the pages of an already onboarded project; onboard records the requirement only and never overwrites an existing project file.
- Any change to anvil.json, pipelines/, anvil.yaml (token cap stays 6,000,000, max_agent_calls 32, max_runtime_turns 40) or existing tests.
- Any gate change that affects orders or projects without an HTML deliverable.

## Exception record (R3, R4)
An owner approved exception is a line in the project spec of the form `Attribution exception: approved by <owner> on <YYYY-MM-DD>: <reason>`. The check honours only that exact line prefix, and names the quoted line in its output. (Form proposed by the spec writer because the order names the record but not its shape; the owner may change it before the build.)

## Compliance test for R4
Visible text means the text of the deliverable HTML with tags, script and style content, and comments removed. An attribution naming ANVIL is visible text that contains the exact default line, or contains the word "ANVIL" (case sensitive) in a sentence stating that ANVIL built or made the project (for example "built end to end by ANVIL"). The word in a comment, attribute or script only does not count. A deliverable file set passes when at least one HTML file in it carries the attribution; with several HTML files, the index page is the one checked.

## Scenarios
Each scenario names the requirement it proves.
- S1 (proves R1, R2), scaffold seeds the rule: a new static-site project scaffolded after this change carries the attribution requirement in its seeded site-shell spec and its seeded brain/project.md, each containing the exact default line, the landing URL https://anvil-landing-7x1.pages.dev, the footer placement, and the bespoke compliance rule. The same holds for blueprints/cloudflare-worker.json when it ships pages. An onboard run on a web project writes the same requirement into its onboard output and leaves every pre-existing project file byte-identical.
- S2 (proves R1, R4), check passes: a web deliverable whose footer reads "Made with ANVIL, an open source software factory." linked to https://anvil-landing-7x1.pages.dev passes the attribution check; a deliverable carrying the Sentia credit "Sentia is a concept product, designed and built end to end by ANVIL, an open source software factory. Developed by Eduardo Arana." also passes and is not flagged for replacement.
- S3 (proves R4), check fails: a web deliverable whose index.html has no attribution naming ANVIL (also: "ANVIL" present only inside an HTML comment) fails the checks gate, and the gate output names the missing attribution as the reason.
- S4 (proves R3, R4), exception honoured: a web deliverable with no attribution, from a project whose spec contains `Attribution exception: approved by Eduardo Arana on 2026-11-16: brand-neutral kiosk build`, passes, and the check output contains that exception line.
- S5 (proves R4, R6), non web unaffected and suite green: an order with no HTML deliverable runs the checks gate with no attribution failure and no attribution output; `python -m unittest discover -s tests -p 'test_*.py'` exits 0, including the new tests for S2, S3, S4 and this case.
- S6 (proves R3), station guidance: stations/builder/PROMPT.md and stations/publisher/PROMPT.md each contain the exact default line, the placement rule, the keep-bespoke rule, and the words "owner approved exception"; the publisher text treats a missing attribution as a defect.
- S7 (proves R5), decision record: brain/decisions/0012-anvil-attribution-default.md exists with the context, decision and consequences sections in the format of 0011-station-timeout.md, mentions the 2026-11-15 audit and the default line, and contains no em dash. No file written by this order contains an em dash (check: grep for U+2014 over the changed files returns nothing).
- S8 (proves R1), placement: on a game surface the attribution is in a credits or footer element outside the canvas and outside the input-handling region, so that removing it changes no gameplay behaviour; checked by the deliverable having the line in a footer or credits element that is not the game canvas container.
