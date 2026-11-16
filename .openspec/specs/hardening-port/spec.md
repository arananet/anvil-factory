# Hardening port: the enterprise hardening programme on current main

## Problem

Two patches supplied by the owner on 2026-11-15 carry a complete hardening
programme for the factory, produced outside this repository against a
divergent base: eleven capability specs with their implementations
(classification floor, run checkpoint, run resume, write authority, sealed
tests, station token caps, scaffold checks, pre build gate, in run
loopback, outcome metrics, clean review), a new reviewer station, a new
pipeline, documentation, and their tests. The programme answers the same
five failure modes the factory recorded in its own runs (FM1 to FM5) and
adds six capabilities taken from other factories. None of it is in this
repository, and the patches do not apply to current main as they stand.

## Decision basis

Owner's order, 2026-11-15: port both patches into ANVIL, and never commit
anything that carries an employer reference. On that rule:

- The core patch passed the operator's full fingerprint scan verbatim
  (employer and brand names, internal project codenames, people, emails,
  URLs) and is committed as supplied.
- The repo files patch carried two employer references: a repository
  link in the landing page that pointed at an employer organization, and
  the same internal repository name in the README quickstart text. The
  operator redacted both before commit, replacing them with the public
  factory repository, and the sanitized artifact passed the same scan
  clean. The unsanitized original is never committed anywhere. The
  landing page file itself is excluded from this port (R11).

Decisions 0008, 0010 and 0012 stand and correct the patches where they
describe an older design:

- Runtimes are claude-gateway (default) and copilot, reaching Anthropic
  models only. Any Codex runtime wording in the patches' docs and specs
  is corrected to that design.
- The clean reviewer's "different model family from the builder" is a
  different Anthropic model: reviewer-clean runs claude-fable-5-2
  against the builder's claude-opus-5-5. No non-Anthropic model is
  introduced anywhere by this port.

Overlaps, stated so the gate can judge them:

- wo-gh-40, wo-gh-41 and wo-gh-42 (staged) cover overlapping ground:
  classification floor and write authority against 40, run checkpoint
  against 41, station token caps against 42. This order does not close
  or supersede them; their fate is an owner decision at this gate.
- wo-gh-44 (enterprise port) touches telemetry.py, scaffold.py and the
  operator guide. It merged nothing. This order parents on main and does
  not depend on that branch.

Execution is STAGED. The line's producing stations failed across three
projects on 2026-11-15 (wo-gh-44, run 43796424330: spec-writer,
test-writer and builder failed, verdict no_reviews). This order fires on
the owner's word after that failure is diagnosed, not before.

## Requirements

R1. Fingerprint discipline. No produced file contains an employer or
organization name beyond ANVIL and arananet. If the port finds a further
fingerprint in the source artifacts, it redacts it the same way, reports
it at the gate, and never commits it.

R2. Classification floor (FM1), per the patch's classification-floor
spec: intake proposes, deterministic rules decide; intake may raise risk
and add surfaces, never lower or remove; a low rating is refused on an
unrated order carrying a scanned risk hint; after the builder, changed
paths can add surfaces and raise low to medium, and reviewers are routed
again. Decisions and escalations are recorded in routing.json and
report.md.

R3. Run checkpoint (FM2), per the run-checkpoint spec: report.json is
saved atomically after every station and before every agent call, with
run_state in_progress, completed or aborted; an interrupted run keeps its
completed steps, the station in flight and its reported usage; SIGTERM
becomes a recorded exit. Run resume, per the run-resume spec: anvil run
--resume continues an aborted run from its first unfinished station.

R4. Write authority and sealed tests (FM3), per the write-authority and
sealed-tests specs: the runner hashes protected files around every
executed agent station; an unauthorized modification or deletion rejects
the run at the approver and fails the pre-review gate; protected files
are restored from the runner's sealed copies so the checks gate judges
the tests as written, with the violation still recorded; the report
gains an integrity section. Default protected paths are tests/,
.openspec/, anvil.json and .anvil/, with spec-writer and blueprint
owning .openspec/ and test-writer owning tests/.

R5. Station token caps (FM4), per the station-token-caps spec:
efficiency.max_station_tokens (500000 in new projects) and per station
overrides cap one station call; the station receives the smaller of its
cap and the remaining run pool; an overrun is marked
station_cap_exceeded with a report warning.

R6. Scaffold checks (FM5), per the scaffold-checks spec: blueprints may
name checks; new-project writes them and the default protected paths
into anvil.json; init and onboard write the protected paths with an
empty checks list; BLUEPRINT.md states the checks. The python-service
blueprint runs the unittest discovery command.

R7. Pre-build gate, per the pre-build-gate spec: before the builder is
called, deterministic code checks that every scenario of the working
specs appears in the tests and, when require_checks is set, that the
project has a check command. A failure ends the run gate_failed without
paying for the build.

R8. In-run loopback, per the in-run-loopback spec: with loopback_mode
in_run, failed work returns inside the same run with the findings and
the gate output, bounded by max_loopbacks and the run budget. The
default stays record.

R9. Outcome metrics, per the outcome-metrics spec: first pass approval,
approval and loopback rates, gate failure rate, objections per reviewer
and tokens per approved work order, computed from the reports on record;
shown on the status page, written to status/usage.json, printed by anvil
metrics.

R10. Clean review, per the clean-review spec as corrected above: the
reviewer-clean station (station 28) judges the change alone, with no
spec, builder report or other review, on claude-fable-5-2; the
sdlc-clean-review pipeline (pipeline 9) opts into it; sdlc-default is
unchanged.

R11. Repository files, from the sanitized repo files patch: CHANGELOG.md
and README.md gain the hardening entries with the corrections of this
spec; the factory's own anvil.json gains .openspec/ and .anvil/ in
protected_paths (the single anvil.json edit this order authorizes,
owner-supplied in the patch, and it strengthens protection);
site/index.html is excluded from the port entirely.

R12. Specs and tests. The eleven capability specs land under
.openspec/specs/ with the corrections of this spec applied. The patches'
tests land as new files; the three existing test files the core patch
modifies (tests/test_anvil.py, tests/test_gates.py,
tests/test_review_parsing_integrity.py) may be modified exactly as the
patch modifies them, because they encode the new behaviour; every other
existing test file is protected. The full factory suite passes and
check-skills passes.

## Scenarios

S1. An intake outcome that lowers a filed risk or removes a surface is
refused by the deterministic floor; the routing record shows the filed
values and the refusal.

S2. A run killed after the builder leaves a report.json whose run_state
is aborted, with the builder step complete and its usage recorded; anvil
run --resume continues it from the checks gate.

S3. A station that edits a test file it does not own has the file
restored from the sealed copy, the violation recorded in the integrity
section, and the run rejected.

S4. A station call that reaches its token cap is marked
station_cap_exceeded and the run continues or stops per the recorded
accounting, never silently.

S5. reviewer-clean under the sdlc-clean-review pipeline receives the
change alone and records claude-fable-5-2 as its configured model; no
station in the run records a non-Anthropic model.
