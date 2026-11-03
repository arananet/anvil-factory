# Task packet: reviewer-spec

## Station prompt

# Reviewer Spec

## Role
Check the implementation against the spec, nothing else.

## Inputs
- spec
- code change

## Outputs
- review

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


## Work order

- id: wo-gh-20
- kind: task
- title: Community files by default in every project ANVIL generates
- source: github-issue
- description: Implement the spec in .openspec/specs/community-by-default/spec.md in the factory. Pipeline for this order is sdlc-default, selected by the run workflow.

THE CHANGE: every project ANVIL creates is born with the full GitHub community file set, defined once and rendered from project metadata, wired into the factory's two existing doors. Do not invent a parallel mechanism.

Canonical set (one definition site, exactly):
- Create templates/community/ holding the template for each file: CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, ISSUE_TEMPLATE/bug_report.md, ISSUE_TEMPLATE/work_order.md, ISSUE_TEMPLATE/config.yml, pull_request_template.md (template file names inside templates/community/ are the builder's choice, but the set lives only there).
- Create anvil/community.py with one renderer function that takes project root metadata (name, description, contact) and returns the mapping of relative path to rendered content for the seven files. Both doors consume this mapping; neither door embeds community file content itself.
- CODE_OF_CONDUCT.md template is the current Contributor Covenant text with version attribution, with exactly one substitution point: the enforcement contact. SECURITY.md names GitHub private vulnerability reporting as the preferred private route and the configured contact as fallback, states supported versions (main branch and latest release), promises no response timelines. config.yml disables blank issues. The pull request template asks for work order, spec link, summary and an evidence checklist (tests and result, run report, rendered evidence where visual, docs or changelog where they apply) and states the author never approves their own work. CONTRIBUTING.md teaches the ANVIL flow: work orders, spec under .openspec/specs/ before implementation, reviewer stations, human gate, how to propose work. The bug report asks what happened, expected, reproduction steps, environment and run evidence; the work order template asks problem, proposed scope, out of scope, acceptance evidence and risk hints (auth, payments, data deletion, production deploy, secrets, publishing).

Greenfield door: in anvil/scaffold.py, init_project writes the community set alongside the files it already writes, and new_project inherits it through init_project. Files the scaffold already writes keep their current content.

Brownfield door: in anvil/onboard.py, onboard_project adds the community set through the existing _write_if_missing helper so each file lands in the created list or, when the project already has it, stays byte untouched and lands in the kept list. The ONBOARDING.md report picks them up through the existing created and kept lists.

Metadata plumbing: name, description and contact resolve from project configuration only: explicit arguments to the scaffold and onboard entry points (add optional parameters without breaking current call sites or the CLI), then anvil.json fields description and contact where present, then for onboard the description the project's README already states. No hardcoded personal data anywhere. With no contact configured, the covenant enforcement line and the SECURITY.md fallback point at the project's GitHub private vulnerability reporting and issue tracker in real sentences. Rendered output must contain no double brace tokens, no TODO markers and no bracketed insert instructions.

Tests (new module tests/test_community.py, unittest with tempfile fixtures, scenario tagged docstrings like the existing suite):
- S1: init_project on a fixture with name, description and contact supplied produces all seven files with the values substituted and no template residue.
- S2: onboard a fixture that already has a CONTRIBUTING.md with sentinel content: after onboarding it is byte identical and in the kept list; the other six files are created and in the created list.
- S3: the same metadata rendered through the scaffold door and the onboard door produces identical community files.
- S4 support: render with a distinctive contact and assert it, and only it, appears as enforcement and reporting contact; no other email shaped string appears in any rendered file.
- Update any pre-existing test that enumerates the exact scaffold or onboard file set to include the community set; change no other test expectation.

Constraints: Python standard library only; no em dash or en dash character in any produced or modified file; do not add community files to this repository itself (the separate order wo-gh-19 owns that); keep the full factory suite green and report its result.

The reviewers write their reviews to the authoritative review files named in their packets; prose outside those files is not a review.

GitHub issue: https://github.com/arananet/anvil-factory/issues/20
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: executed
- test-writer: executed
- builder: executed
