# The memory gate: verified learnings

A project's brain is memory that later stations trust as context. That
trust is exactly what makes agent written memory dangerous. One wrong
"empirical observation", written down early by an agent and never
checked, gets read by every later run with the authority of the project
record behind it. In the memory literature this is benign memory
contamination: nothing malicious happened, the memory is simply trusted
more than it earned.

ANVIL gates memory writes the way the line gates code. A learning
becomes station context only after deterministic code verifies its
provenance against the run record on disk.

## The layout

- `brain/learnings.md` is the verified store. Each entry is a headed
  block:

  ```
  ## L-1: The store rejects empty titles with a 400
  Provenance: run wo-taskline-001, artifact runs/wo-taskline-001/notes.md, evidence verdict approved
  ```

- `brain/inbox/` holds proposed learnings, one markdown file per
  proposal:

  ```
  Claim: The store rejects empty titles with a 400
  Source-Run: wo-taskline-001
  Artifact: runs/wo-taskline-001/notes.md
  Evidence: verdict approved
  ```

- Demotions are recorded as decisions under `brain/decisions/`, never
  done silently.

Scaffolding (`anvil init`, `anvil new-project`, `anvil onboard`) creates
the store and the inbox when missing and never overwrites an existing
`brain/learnings.md`.

## The flow

1. Propose. Anything (an agent at the observer station, a human, a
   script) writes a proposal into the inbox, for example with
   `anvil.brain.propose_learning`. A proposal is a claim plus a pointer
   at the evidence, nothing more.
2. Quarantine. Inbox content is listed by `anvil check-brain` as
   quarantined. It is never station context and never fails the check.
   Being written down earns a proposal nothing.
3. Promote. `anvil promote-learning <project> <inbox-file>` verifies the
   proposal: the cited run report `runs/<id>/report.json` exists, the
   cited artifact exists, and the evidence matches the report
   (`verdict approved` requires the report verdict to be approved;
   `verify pass` requires a `verify_results` entry with status pass).
   Only a passing proposal is appended to `brain/learnings.md` with its
   provenance line, and its inbox file is removed. A refusal names the
   exact reason and changes nothing on disk.
4. Use. Every station packet gains a `## Verified learnings` section
   listing the non demoted verified entries. When the store is empty,
   packets are unchanged.
5. Re-verify. `anvil check-brain <project>` re-checks every verified
   entry the same way and fails (exit 1) when one no longer verifies,
   for example after a hand edit stripped its provenance line.
6. Demote. `anvil demote-learning <project> L-1 --reason "..."` marks
   the entry `Status: demoted` in the store and writes a decision
   record under `brain/decisions/`. The entry stays readable as history
   and stops being station context.

## Why provenance, not confidence

A learning that says "trust me, the run approved this" is a claim. The
gate turns it into a checkable pointer: run id, artifact, evidence kind.
If the run record does not back the claim, the learning does not enter
the store, no matter how plausible it reads. That is the whole defense:
memory earns authority from the record, not from being written first.
