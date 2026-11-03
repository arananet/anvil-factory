# Community Files By Default

Status: approved
Slug: community-by-default

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
GitHub's community profile measures whether a stranger can learn how to work with a project and how to report a problem safely. This repository's own profile measured 42 percent before wo-gh-19 added the missing files by hand: a description, a README and a license were present, while the code of conduct, the contributing guide, the issue templates and the pull request template were missing. A project ANVIL creates should not start there. This spec makes the full community file set part of what the factory lays down when it creates a project, in both directions the factory starts work: the greenfield scaffold and the brownfield onboarding. The set is defined once, rendered from the project's own metadata, and never overwrites a file a project already has.

## Requirements
- The community set is exactly these files, landing where GitHub reads them: CONTRIBUTING.md, CODE_OF_CONDUCT.md and SECURITY.md at the project root; .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/work_order.md and .github/ISSUE_TEMPLATE/config.yml; .github/pull_request_template.md. LICENSE and README.md are out of scope: standing factory rules already cover them (Apache 2.0 and the house README template).
- The set is defined in exactly one place: template files under templates/community/ in this repository, rendered by one function in a new module anvil/community.py. No second copy of the content may live in scaffold.py, onboard.py or anywhere else; both doors call the one renderer.
- Greenfield door: init_project in anvil/scaffold.py writes the community set for every project it lays down, and new_project, which builds on init_project, inherits it. Both init_project and new_project accept optional description and contact parameters; new_project forwards them to init_project. Existing call sites and the CLI keep working unchanged. The existing files the scaffold writes today are unchanged in content.
- Brownfield door: onboard_project in anvil/onboard.py adds the community set through its existing _write_if_missing path, so each community file is either created and listed in the report's created list, or already present, byte untouched, and listed in the kept list. The ONBOARDING.md report names the community files like any other created or kept file.
- Metadata: the renderer takes the project name, a description and a contact. Values resolve from project configuration only: explicit arguments to the scaffold or onboard entry points first, then values the project configuration already states (anvil.json fields description and contact, the README description line for onboarded projects). No template and no default may hardcode a person's name, email or organization. Where no contact is configured, the enforcement and reporting lines point at the project's own GitHub surface (its private vulnerability reporting and its issue tracker) in real sentences, never at a placeholder.
- Input validation: the renderer validates all metadata before rendering. The project name is required and cannot be empty. Name and contact are single line fields: any value containing a newline or carriage return character is rejected with a ValueError. The contact, when provided, must match email address format; malformed contacts are rejected. Length limits are enforced: project name at most 200 characters, contact at most 100 characters, description at most 500 characters. Values exceeding these limits are rejected with a ValueError. No metadata value is rendered without passing these checks.
- CONTRIBUTING.md is written in ANVIL terms: work enters as a work order, a spec is written under .openspec/specs/ before implementation, reviewer stations judge the change, and a human gate decides before anything merges or ships. It tells a contributor how to propose work (the work order issue template, or a good first issue) and what a reviewable change looks like. The opening paragraph renders the project description from the supplied metadata, so contributors see what the project is in the project's own words.
- CODE_OF_CONDUCT.md is the current version of the Contributor Covenant with its version attribution intact. The only substitution is the enforcement contact, taken from the resolved metadata. No clause is weakened, removed or reworded.
- SECURITY.md states the supported versions (the main branch and the latest release) and the private reporting route: GitHub private vulnerability reporting is named as the preferred route, with the configured contact as the fallback where one exists. It promises no specific response timelines.
- The bug report template asks for what happened, what was expected, steps to reproduce, the environment, and run evidence where relevant (run report, station output, workflow run link). The work order template asks for the problem, the proposed scope, what is out of scope, the acceptance evidence, and risk hints from this project's own list (auth, payments, data deletion, production deploy, secrets, publishing). The chooser configuration disables blank issues, matching the intake discipline of this factory. The chooser configuration contains no contact_links section: the renderer metadata contract supplies name, description and contact only, with no repository slug, so the rendered config.yml omits that section entirely and contains no URL and no "owner/repo" string.
- The pull request template asks for the work order, the spec link, a summary of the change, and an evidence checklist (tests run and their result, the run report for factory executed work, rendered evidence where the change is visual, documentation or changelog where they apply). It states that the author never approves their own work: reviewer stations and the human gate decide.
- Rendered output contains no template residue: no double brace tokens, no TODO markers, no bracketed insert instructions from the covenant source may survive rendering. The covenant's own bracketed contact instruction is the one substitution point and is always replaced. No rendered file contains the literal string "owner/repo".
- Runtime code stays on the Python standard library only. No produced or modified file contains an em dash or an en dash.
- Tests prove the behavior in the factory's existing test style (unittest, tempfile fixtures), in a test module for this capability: the scaffold fixture test, the onboard preservation test, and the one canonical set agreement test named in the scenarios. A pre-existing test that legitimately enumerates the exact file set scaffold or onboard produces may be updated to the new set; no other test expectation changes.

## Scenarios

### Scenario: A scaffolded project is born with the full community set
- S1: Given a fixture project created through init_project with a name, a description and a contact supplied, when the scaffold finishes, then CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/work_order.md, .github/ISSUE_TEMPLATE/config.yml and .github/pull_request_template.md all exist, the project name, description and contact appear where each file calls for them, the supplied description string appears in the rendered CONTRIBUTING.md, and no file contains a double brace token, a TODO marker, a bracketed insert instruction, or the literal string "owner/repo".

### Scenario: Onboarding adds only what is missing and never overwrites
- S2: Given a fixture project that already has its own CONTRIBUTING.md with recognizable content and none of the other community files, when onboard_project runs, then its CONTRIBUTING.md is byte identical after onboarding and appears in the kept list, every other community file is created and appears in the created list, and ONBOARDING.md reflects both.

### Scenario: Both doors render the one canonical set
- S3: Given the same project metadata, when the community set is rendered through the scaffold door and through the onboard door, then the seven community files are identical between the two, proving both doors draw from the single definition under templates/community/ and anvil/community.py.

### Scenario: Identity comes from configuration, never from the factory
- S4: Given the templates and the renderer, when they are inspected, then no person's name, email address or organization is hardcoded anywhere; the enforcement contact in CODE_OF_CONDUCT.md and the reporting fallback in SECURITY.md are exactly the contact the project configuration supplied, and with no contact configured those lines name the project's GitHub private reporting and issue tracker instead.

### Scenario: The contributor facing content teaches the ANVIL flow
- S5: Given the rendered CONTRIBUTING.md, the issue templates and the pull request template, when a new contributor reads them, then they can state how work starts (a work order), what is written before implementation (a spec under .openspec/specs/), what decides a merge (reviewer stations plus the human gate, never the author), how to report a bug with run evidence, and which private route a vulnerability report takes (GitHub private vulnerability reporting first, configured contact as fallback).

### Scenario: The factory suite stays green
- S6: Given the change is complete, when the full factory test suite runs, then it passes, with only the file set enumerations of scaffold and onboard updated to include the community set.

### Scenario: Dogfooding boundary is respected
- S7: Given this capability and the separate order wo-gh-19, when this change is inspected, then it adds no community files to this repository itself (wo-gh-19 owns that), and its diff touches only the canonical set definition, the two doors, the metadata plumbing, and the tests.

### Scenario: Input validation prevents injection attacks
- S8: Given a project name containing newline characters and markdown injection syntax (the literal string 'MyProject\n\n## Malicious Section\n[Click](http://evil.com)'), when the renderer is called with that name, then it raises a ValueError and no file content is produced. Given a contact value that does not match email address format, when the renderer is called, then it raises a ValueError. Given metadata values exceeding the length limits (name over 200 characters, contact over 100 characters, or description over 500 characters), when the renderer is called, then it raises a ValueError. Given an empty project name, when the renderer is called, then it raises a ValueError.

### Scenario: The greenfield blueprint path carries metadata
- S9: Given new_project is called with name, description and contact parameters, when it completes, then the community files in the created project contain the supplied description and contact values, proving new_project accepted and forwarded the metadata to init_project.
