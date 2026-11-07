# Memory Consolidation and Selective Retrieval

Status: proposed
Slug: memory-consolidation

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

The verified memory gate (spec verified-memory) decides what the project brain may claim: proposals wait quarantined in brain/inbox/ and reach brain/learnings.md only when deterministic code verifies their provenance against the run record. The gate solved the trust half of agent memory and left the use half open. Two gaps are visible in the factory's own operation. First, retrieval is all or nothing: the runner computes one Verified learnings section per run from every non demoted entry and places it in the packet of every station, so each station pays for and reads learnings that have nothing to do with its task, and when a packet exceeds its budget the trim rule keeps only the most recent entries, relevant or not. Second, nothing closes the loop: a finished run produces a report, reviews and findings, but no step reads that record to propose what the project should remember, so learnings arrive only when a human or a script happens to call the proposal function by hand. A third, smaller gap sits inside the gate itself: promotion verifies that the cited run and artifact exist and that the evidence label matches the report, but not that the artifact's text supports the claim. This order closes the three gaps without weakening the gate: scoped learnings with deterministic selective retrieval, an end of run consolidation pass that may only propose into the quarantined inbox, and an optional literal quote check that binds a claim to the text of its artifact. The shape follows the factory's own record and Anthropic's agent memory study of 2026-11-06 (write, read, select, manage; offline consolidation between sessions), adapted to ANVIL's stricter rule that memory earns authority from the run record, never from being written down.

## Requirements

### R1. Scoped learnings
- The proposal format gains three optional fields after the existing four (Claim, Source-Run, Artifact, Evidence): Stations (a comma separated list of station ids), Specs (a comma separated list of spec slugs) and Keywords (a comma separated list of words or phrases). A proposal may carry any subset of the three, including none.
- A promoted entry records its scope on a Scope line inside its learnings.md block, in the same field order, omitting the fields it does not carry. Parsing an entry that has no Scope line yields an unscoped entry, and an unscoped entry is global: it matches every selection context, exactly as every entry behaves today.
- Scope matching is conjunctive across the fields an entry carries and disjunctive inside one field: an entry matches a context when every field it carries has at least one matching value in that context.

### R2. Selective retrieval
- Packet assembly computes the Verified learnings section per station instead of once per run. The selection context is the station id, the spec slug the work order declares (the folder name of its spec_path) when the order declares one, and the work order title and description for keyword matching. Keyword matching is case insensitive and matches a whole word or a full phrase contained in the title or the description.
- Only verified, non demoted entries are candidates. Selection can only narrow the set the verified-memory spec allows into a packet, never widen it: inbox content stays invisible and demoted entries stay excluded.
- When the selected set for a station is empty, that station's packet carries no Verified learnings section, exactly as a project with an empty store behaves today.
- The existing packet budget trim order is unchanged and operates on the selected set: selection first, budget trim after.
- Selection is deterministic and standard library only: no embeddings, no model call, no network access.

### R3. End of run consolidation
- A new agent station, consolidator, joins the station registry and is appended after observer in the sdlc-default and greenfield pipelines. All other pipelines are unchanged.
- The station is gated by the project config flag memory_consolidation (boolean, default off). When the flag is off or absent, the step records itself as not enabled and completes without a model call and without writing anything, the same pattern the deterministic preflight uses for an undeclared smoke command.
- When the flag is on, the consolidator packet carries: the run's verdict and decision summary, the counted reviews with their findings, the loopback count, the observer output when the pipeline produced one, the current verified learnings and the claims of the proposals already waiting in the inbox (both for deduplication), and the output contract below.
- Output contract: the consolidator may only create new proposal files in brain/inbox/, in the proposal format extended by R1 and R4, with Source-Run set to the current run's work order id, Artifact set to an artifact of the current run, and a Quote (R4) taken from that artifact. It proposes reusable rules and facts, covering what worked as well as what failed, and it does not propose one off incident detail with no reuse value. It writes nothing else, anywhere.
- A deterministic post check runs in the runner after the step. (a) Any file created or modified outside brain/inbox/ during the consolidator step is a boundary violation: the path is recorded in the run report's memory field set and the step is marked failed. (b) Each new inbox file is parsed: a file that does not parse as a proposal, that names a source run other than the current run, that cites a missing artifact, or that lacks a Quote is recorded as malformed, by file name and reason, and is left in the inbox, where quarantine already keeps it out of station context. (c) A proposal whose claim duplicates an existing verified claim or an earlier proposal from the same consolidation pass, compared after whitespace and case normalization, is deleted and recorded as a rejected duplicate.
- The consolidator never promotes and never demotes. Promotion remains the existing operator invoked gate, and nothing in this order changes who may promote.

### R4. Claim support quotes
- A proposal may carry a Quote field: a literal excerpt of the cited artifact. When a proposal carries a Quote, promotion additionally requires that the excerpt appears in the artifact's text after whitespace normalization (every run of whitespace collapsed to a single space, applied to both the excerpt and the artifact text). A quote that does not appear, or an artifact that cannot be read as text, refuses promotion with that reason and changes nothing on disk.
- A promoted entry records its quote on a Quote line inside its learnings.md block. check-brain re-verifies the quote of every entry that carries one and fails, naming the entry, when the quote no longer appears in the cited artifact. Entries without a quote verify exactly as they do today.
- Consolidator proposals must carry a Quote; the R3 post check records a consolidator proposal without one as malformed. Human and script proposals may omit the field, so every existing flow keeps working unchanged.

### R5. Reporting
- report.json gains a memory field set, distinct from the checks result and from any review verdict: the ids of the verified entries present at run start; for each station that received a packet, the ids selected for that station; and the consolidation outcome (not enabled, completed or failed) with the proposal files written, the duplicates rejected, the malformed proposals with their reasons, and any boundary violation paths.
- A run on a project whose brain has no verified entries and no consolidation records an empty memory field set and is otherwise unchanged.

### Guardrails
- Python standard library only, consistent with the factory spine. No new dependency.
- Frozen surfaces: the verified-memory scenarios S1 to S7 and the promotion gate's behavior for proposals that carry none of the new optional fields; the review parse contract and parse_review semantics; the canonical review contract wording; the reviewer prompts and their Output Format sections; the review producer mechanisms (scoped reviewer writes, no stdout transcription); the checks gate behavior.
- Backward compatibility is a requirement, not a hope: the factory repo's own brain, and the brain stores of projects already onboarded (Sentia, the example taskline), must pass check-brain and produce the same Verified learnings sections as the current code when no scope fields and no quotes are present and the consolidation flag is off.
- The consolidator's writes are confined to brain/inbox/ by its contract and by the deterministic post check. It never writes learnings.md.
- No em dash or en dash character in any produced file (project style rule).
- Nothing in this order publishes anything.

## Scenarios

### Scenario: Station scope selects per station
- S1: Given a verified entry scoped Stations: builder and an unscoped verified entry, when packets are assembled for a run, then the builder packet contains both entries and a reviewer packet contains only the unscoped one.

### Scenario: Spec and keyword scope follow the work order
- S2: Given a verified entry scoped Specs: memory-consolidation and a verified entry scoped Keywords: contact sheet, when a run executes a work order whose spec_path names the memory-consolidation spec and whose description mentions a contact sheet, then both entries are selected; and when a second run executes an order for a different spec whose text mentions neither, then neither entry is selected.

### Scenario: Selection never widens the verified set
- S3: Given a project with one verified entry, one demoted entry and one inbox proposal, when packets are assembled, then only the verified entry can appear in any packet, as the verified-memory spec already requires.

### Scenario: Selection is recorded in the run report
- S4: Given a run that selects different entry sets for two stations, when report.json is written, then its memory field set names the verified ids present at run start and the selected ids per station.

### Scenario: Consolidation proposes into quarantine only
- S5: Given a project with memory_consolidation enabled and a completed run, when the consolidator step finishes, then every new file it created sits in brain/inbox/, parses as a proposal naming the current run, cites an existing artifact of the run and carries a Quote; and brain/learnings.md is byte identical to before the step.

### Scenario: Boundary violations and malformed proposals are caught deterministically
- S6: Given a consolidator step that writes one file outside brain/inbox/ and one inbox proposal without a Quote, when the post check runs, then the outside path is recorded as a boundary violation and the step is marked failed, and the quoteless proposal is recorded as malformed and remains quarantined in the inbox.

### Scenario: Duplicate claims are rejected
- S7: Given a claim already verified in learnings.md, when the consolidator proposes the same claim with different casing and spacing, then the post check deletes the proposal file and records it as a rejected duplicate, and learnings.md is unchanged.

### Scenario: The quote gate binds promotion and re-verification
- S8: Given a proposal whose Quote appears in its cited artifact, when promote-learning runs, then the entry is appended with its Quote line. Given a second proposal whose Quote does not appear in its artifact, when promote-learning runs, then it refuses, naming the quote as the reason, and learnings.md is unchanged. Given a promoted entry whose artifact later changes so the quote no longer appears, when check-brain runs, then it fails naming that entry.

### Scenario: Flag off means no consolidation cost
- S9: Given a project without the memory_consolidation flag, when an sdlc-default run reaches the consolidator, then the step records not enabled, no model call happens, no file is written, and the rest of the run is unchanged.

### Scenario: Stores written before this change behave exactly as before
- S10: Given the factory repo's own brain store, written before this change, when check-brain runs and a packet is assembled with the consolidation flag off, then the check passes and the packet's Verified learnings section is identical to the one the current code produces.
