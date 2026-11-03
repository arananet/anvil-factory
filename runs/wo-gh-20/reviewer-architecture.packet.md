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

LOOPBACK ROUND 2 (operator addendum after the round 1 verdict rejected; reviews counted 4 of 5: reviewer-spec fail, reviewer-security changes_requested, reviewer-tests pass, reviewer-design pass; reviewer-architecture not counted, review_parse_failed true, its prose findings are item 4 below). Fix exactly these findings, in anvil/community.py, anvil/scaffold.py, templates/community/ and tests/test_community.py only. Everything else from round 1 stands.

1. PLACEHOLDER IN RENDERED OUTPUT (reviewer-spec FAIL, verbatim): "issue_config.yml contains 'owner/repo' placeholder in rendered output at line 4. The spec requires 'Rendered output contains no template residue: no double brace tokens, no TODO markers, no bracketed insert instructions' and 'never at a placeholder'. The code at anvil/community.py:49 replaces {{REPO_PLACEHOLDER}} with the literal string 'owner/repo', which is still a placeholder." Fix per the reviewer's own accepted solution: the renderer has no repository slug in its metadata contract (name, description, contact only), so when rendering issue_config.yml, omit the contact_links section entirely. The rendered config keeps blank_issues_enabled: false and contains no URL and no "owner/repo" string. Strengthen the S1 test to assert the rendered set contains no "owner/repo" anywhere.

2. CONTENT INJECTION AND VALIDATION (reviewer-security, verbatim core): "The name and contact parameters are inserted directly into markdown files without sanitization. An attacker can inject arbitrary markdown sections, malicious links, and HTML by including newlines and markdown syntax. Example: name='MyProject\n\n## Malicious Section\n[Click](http://evil.com)' successfully injects a new header and link." And: "No input validation. The function accepts arbitrary strings for name, description, and contact parameters without validating format, length, or content. The contact parameter should be validated as a proper email address format. Empty strings are accepted and produce malformed output. No maximum length enforced." Fix: in the renderer, treat name and contact as single line fields: reject values containing newline or carriage return characters with a clear ValueError (do not silently render them); validate a non-empty contact as an email shape and reject anything else; enforce length limits (name at most 200 characters, contact at most 100, description at most 500); reject an empty project name. Add regression tests using the reviewer's injection example verbatim: rendering with that name value must raise, and no file content is produced; plus a test that an over length or malformed contact raises.

3. DESCRIPTION NEVER RENDERED (reviewer-security, verbatim): "The description parameter is accepted but never used in template rendering." Fix: render the project description in the CONTRIBUTING template (its opening paragraph is the natural place: what the project is, in the project's own words, before the how to contribute flow), so the metadata substitution the spec requires is real. Strengthen the S1 fixture test to assert the supplied description string appears in the rendered community set.

4. GREENFIELD BLUEPRINT PATH CANNOT CARRY METADATA (reviewer-architecture, uncounted in round 1 only because its review failed to parse; finding verified by the operator in its output): new_project does not accept or forward description and contact; it calls init_project with only (path, name), so projects created through the blueprint path cannot receive metadata for the community files. Fix: new_project accepts optional description and contact parameters and forwards them to init_project; existing call sites and the CLI keep working unchanged.

5. REVIEW CHANNEL DISCIPLINE FOR THIS ROUND: every reviewer states its verdict as exactly one JSON object in its station output, the shape the other reviewers used in round 1 and the shape its packet requires. Round 1 reviewer-architecture wrote prose and a separate file under reviews/ and its verdict was not counted (review_parse_failed). Do not repeat that.

Keep the full factory suite green and report its result. No em dash or en dash in any produced or modified file. Do not touch this repository's own community files (wo-gh-19 owns them).
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: executed
- test-writer: executed
- builder: executed
- reviewer-spec: executed
- reviewer-security: executed
- reviewer-tests: executed
