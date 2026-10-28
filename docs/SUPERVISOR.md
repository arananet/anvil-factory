# The bounded supervisor

Fixed teams stall in recognizable ways: the same reviewer keeps
failing, the loopback budget runs out, runs end with no reviews at all,
a deploy lands but verification fails. A supervisor that watches the
run record and reorganizes the line is the known answer. A supervisor
that can invent anything it wants is unauditable, so ANVIL bounds it:
reorganization happens inside a verified envelope.

## What the supervisor is

The supervisor is a station in the catalog (`stations/supervisor/`,
agent kind). It runs between runs, not inside one, so it appears in no
shipped pipeline. `anvil supervise <project>` drives it.

## Stall signals

Detection is deterministic code over `runs/*/report.json`, never a
model judgment. Each signal is `{kind, detail, evidence: [run ids]}`:

- `reviewer_fail_repeated`: a reviewer station returned verdict fail in
  2 or more runs.
- `loopbacks_exhausted`: the latest run used all of its loopbacks
  (`loopbacks >= max_loopbacks`).
- `no_reviews_repeated`: verdict `no_reviews` in 2 or more of the last
  3 runs.
- `deployed_unverified`: the latest run ended `deployed_unverified`.

With no signals, `anvil supervise` prints `no stalls detected` and
writes nothing.

## The proposal lifecycle

1. With signals, packet mode writes the supervisor packet
   (`work-orders/supervisor.packet.md`) and a work order
   (`work-orders/supervisor-proposal.json`, kind task) whose title
   names the first signal.
2. With `--execute`, the packet goes to the configured runtime like any
   other station packet, and the runtime answers with one JSON
   proposal: `{"name", "pipeline", "rationale", "addresses"}`.
3. Deterministic validation runs two layers: the pipeline object must
   pass the existing pipeline validator against the station catalog,
   and it must pass the constitution (below).
4. An accepted proposal is written to `pipelines/proposals/<name>.json`
   with a `PROPOSAL.md` beside it carrying the rationale, the signal
   addressed, the evidence run ids and the validation result. A
   rejected one lands in `pipelines/proposals/rejected-<name>.json`
   with a `REJECTED.md` naming each failed check.
5. Nothing auto applies. A proposal becomes active only when a human
   points `anvil.json` or a run at it.

## The constitution

A proposal is legal only when all of these hold:

- It is built only from station ids in the catalog. Inventing or
  renaming a station fails validation.
- It includes `intake`, `approver` and `triage-human`.
- Its reviewer station set is a superset of (or equal to) the reviewer
  set of the pipeline it would replace: the project's configured
  default from `anvil.json`, falling back to `sdlc-default`. Reviewers
  may be reordered or added; coverage may not shrink.
- It passes the ordinary pipeline rules (no empty line, no duplicate
  stations, parallel groups of at least two).

## What the supervisor can never do

- Edit the gates, the risk hints or the triage rules. Those are
  deterministic code, not configuration, and no proposal field reaches
  them. The station prompt says so in plain words.
- Weaken review coverage, drop the approver, or remove the human
  triage station.
- Apply its own proposal, or anyone else's. Filing is the end of its
  authority.
- Change the signals. What counts as a stall is decided by
  `detect_stalls` in code; the supervisor only answers signals that
  already fired.
