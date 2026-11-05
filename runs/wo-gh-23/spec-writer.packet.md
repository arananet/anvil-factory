# Task packet: spec-writer

## Station prompt

# Spec Writer

## Role
Write or revise an OpenSpec spec from a work order.

## Inputs
- work order
- brain

## Outputs
- spec

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


## Work order

- id: wo-gh-23
- kind: task
- title: Showcase README: first screen demo, Built by ANVIL, quickstart, trust section
- source: github-issue
- description: Implement the spec in .openspec/specs/readme-showcase/spec.md: rewrite README.md of this repository into the launch showcase, keeping the existing documentation below the fold. Pipeline for this order is sdlc-default (software domain, full reviewer set), selected by the run workflow. The run touches README.md, README assets under docs/ or assets/ as the builder judges cleanest, and run evidence only. No factory code changes.

SEQUENCING GATE: execute this order only from a main that already carries the capability minimum, issues 6 to 10 (wo-gh-6 checks gate with the S4 base ref fix, wo-gh-7 intake outcomes, wo-gh-8 risk and surface routing, wo-gh-9 rendered design review, wo-gh-10 per job cost) merged. Verify their presence in the branch history before building (the checks gate code and docs, the intake outcomes, the routing, the rendered review and the cost fields in run reports). If the minimum is not in the history, stop and report instead of running.

Build, per the spec requirements:

R1, first screen: house template header (title, stack badges plus OpenSpec and Apache 2.0 badges, the quoted one line description), then in order: (1) the animated demo of one real run cycle (work order, spec, tests, build, reviews, human gate, merged), GIF or embedded MP4 under 90 seconds, produced from a real run's own evidence (captures and report data of runs already on record in this repo, for example a capability run or wo-gh-20), never a mockup or a staged animation of events that did not happen; if a truthful animated demo cannot be produced inside the line, say so plainly in the run output and ship the README with the strongest truthful static evidence instead; (2) the Built by ANVIL block with live links to Sentia (https://sentia.info-693.workers.dev), Platform25 (https://platform25.pages.dev) and the status board (https://anvil-status.pages.dev), one line each on what it proves; (3) the quickstart against arananet/anvil-example-taskline, under 5 minutes, which the line EXECUTES from a clean clone during the run and records (commands, duration, output tail) as evidence.

R2, trust section: the three mechanisms (no station approves its own work, with verdicts read from authoritative review files and parsing that fails closed; memory promoted only with run report provenance, the CONTAM-Bench answer; a human gate before publishing or production deploys), each claim linked to the repo file, test or report that backs it.

R3, claim hygiene: verify every number against the tree at run time (station count, pipeline count, factory suite size measured fresh, reviewer counts corrected to five wherever the current README says four, including the approver line in the station table). Cite S4 and the capability items only as merged fact, because the gate above guarantees they are in main; anything not in main goes to a roadmap section labelled as roadmap or stays out.

R4, metadata is an OPERATOR step after the merge, not the line's: the line's part is only to produce the social preview image (1280 by 640, ANVIL wordmark, simplified station line, the one line quote, production quality, any generated text verified letter by letter) as a run evidence file named social-preview.png, and to record in its output that the homepage, topics and image upload are operator steps. The line does not call the GitHub settings API and does not change the repo description.

R5, closing: the house template sections (Contributing pointing at OpenSpec, Documentation, License Apache 2.0 with Copyright Eduardo Arana, Developer Eduardo Arana, the ko-fi block), and exactly one star call to action, worded exactly as the spec states, at the end of the first screen and repeated at the close.

Tests and evidence, per the spec: a link and claim check over the produced README recorded in the run evidence (relative links resolve in the tree, the three showcase links answer live during the run, the R3 claim list item by item against the tree); a capture of the rendered README from the real GitHub view of the run branch at desktop width; the quickstart execution record. The factory suite must stay green; any suite change is reported, not fixed inside this order.

Guardrails: no em dash or en dash character in any produced file (project style rule). The reviewer writes its review to the authoritative review file named in its packet; prose outside that file is not a review. Nothing in this order publishes anything: no posts, no release, no metadata changes by the line.

GitHub issue: https://github.com/arananet/anvil-factory/issues/23
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
