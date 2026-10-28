# Verified Memory

Status: approved
Slug: verified-memory

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
A project brain is memory that later stations trust as context. Agent written learnings are useful and dangerous in the same way: one wrong observation, written early and never checked, is read by every later team as fact. That is benign memory contamination. This spec gates memory writes the way the line gates code: a learning becomes station context only after deterministic code verifies its provenance against the run record.

## Requirements
- The verified store is brain/learnings.md. Each entry is a headed block "## L-<n>: <claim>" followed by a "Provenance:" line carrying the run id, the artifact path, and the evidence kind (for example "verdict approved" or "verify pass").
- Proposed learnings live in brain/inbox/, one markdown file per proposal with the fields Claim:, Source-Run:, Artifact: and Evidence:. Inbox content is quarantined by definition: it is never station context.
- Promotion is the only way in. `anvil promote-learning` validates a proposal against the run record on disk: the cited run report runs/<id>/report.json exists, the cited artifact exists, and the evidence claim matches the report ("verdict approved" requires the report verdict to be approved, "verify pass" requires a verify_results entry with status pass). Only a passing proposal is appended to learnings.md with its provenance, and its inbox file is removed.
- `anvil check-brain` re-verifies every verified entry the same way and fails when one no longer verifies. Inbox items are listed as quarantined and never fail the check.
- Demotion is recorded, not silent: the entry gains a "Status: demoted" marker in learnings.md and a decision record is written under brain/decisions/. Demoted entries stop being station context.
- Station packets gain a "Verified learnings" section sourced only from non demoted verified entries. When a project has no verified learnings, packets are unchanged.

## Scenarios

### Scenario: Promotion succeeds with real supporting evidence
- S1: Given an inbox proposal whose run report exists, whose artifact exists, and whose evidence matches the report, when promote-learning runs, then the entry is appended to brain/learnings.md with its provenance line, and the inbox file is removed.

### Scenario: Promotion is refused when evidence cannot be verified
- S2: Given an inbox proposal whose run does not exist, whose artifact is missing, or whose evidence contradicts the report (the claim says "verdict approved" and the report says rejected), when promote-learning runs, then it refuses with the specific reason, the inbox file stays, and learnings.md is unchanged.

### Scenario: Check-brain catches a stripped or stale verified entry
- S3: Given a verified entry in learnings.md whose provenance line was hand edited away or whose cited run no longer supports the evidence, when check-brain runs, then it fails, names the entry, and exits non zero.

### Scenario: Inbox proposals are quarantined, not errors
- S4: Given a project with inbox proposals (valid or not) and a valid verified store, when check-brain runs, then it passes, and it lists the inbox items as quarantined.

### Scenario: Packets carry verified learnings only
- S5: Given a project with one verified entry and one inbox proposal, when a run writes a station packet, then the packet's Verified learnings section contains the verified claim and does not contain the inbox claim anywhere.

### Scenario: Demotion marks the entry and removes it from context
- S6: Given a verified entry, when demote-learning runs with a reason, then the entry carries a "Status: demoted" marker in learnings.md, a decision record exists under brain/decisions/ naming the entry and the reason, and later packets no longer include the claim.

### Scenario: Scaffolding creates the memory layout without overwriting
- S7: Given init, new-project or onboard, when the project lacks brain/learnings.md or brain/inbox/, then scaffolding creates them; an existing brain/learnings.md is never overwritten.
