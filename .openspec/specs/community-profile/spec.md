# GitHub Community Profile

Status: approved
Slug: community-profile

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
GitHub's community profile for this repository reports 42 percent health: a description, a README and an Apache 2.0 license are present, while the code of conduct, the contributing guide, the issue templates and the pull request template are missing, and no security policy exists. These files are how a stranger learns how to work with the project and how to report a problem safely. This spec adds exactly those files, written for this project and its way of working, so the community profile reflects the same discipline the factory applies to code: work enters in the open, with a spec, and a human decides.

## Requirements
- This order adds new files only. It modifies no existing file, no station, no pipeline and no test.
- The files land where GitHub reads them: CONTRIBUTING.md, CODE_OF_CONDUCT.md and SECURITY.md at the repository root; the issue templates under .github/ISSUE_TEMPLATE/; the pull request template at .github/pull_request_template.md; the template chooser configuration at .github/ISSUE_TEMPLATE/config.yml.
- CONTRIBUTING.md explains how work enters this project: every change starts as a work order, a spec is written under .openspec/specs/ before implementation, tests map to the spec scenarios where the change touches code, and a human gate decides before anything merges or ships. It tells an external contributor how to propose work (open an issue with the work order template, or pick up a good first issue) and what a reviewable change looks like. It states the standing project rules that bind contributors: runtime code stays on the Python standard library only, and new projects follow the house README template. Its substance agrees with the Contributing section the README already carries; it expands that section, it does not contradict it.
- CODE_OF_CONDUCT.md is the current version of the Contributor Covenant, with its version attribution intact. The only project specific content is the enforcement contact, which is the contact this repository already publishes: info@arananet.net. No clause of the covenant is weakened, removed or reworded.
- SECURITY.md states which versions are supported (the main branch and the latest release), and how to report a vulnerability privately. GitHub private vulnerability reporting is not enabled on this repository (checked by the operator on 2026-11-02), so the policy routes reports to the published contact, info@arananet.net, and asks reporters not to open public issues for vulnerabilities. It names the security relevant surfaces of this project that reports are especially welcome against: the deterministic checks gate and its base ref enforcement, the review parsing contract, and the gateway credential routing. It makes no promise of specific response timelines.
- The bug report template (.github/ISSUE_TEMPLATE/bug_report.md) asks for what happened, what was expected, steps to reproduce, the environment, and run evidence where the bug comes from a factory run (run report, station output or workflow run link).
- The work order template (.github/ISSUE_TEMPLATE/work_order.md) frames a proposal the way ANVIL consumes it: the problem, the proposed scope, what is explicitly out of scope, the acceptance evidence that would prove it done, and risk hints drawn from the project's own list (auth, payments, data deletion, production deploy, secrets, publishing).
- The template chooser configuration (.github/ISSUE_TEMPLATE/config.yml) disables blank issues, so every issue starts from a template that matches how the project works.
- The pull request template (.github/pull_request_template.md) asks for the work order and the spec it implements, a summary of the change, and an evidence checklist: tests run and their result, the run report for factory executed work, rendered evidence where the change is visual, and documentation or changelog updates where they apply. It reminds the author that nobody approves their own work: in this project the reviewer stations and the human gate decide, and the author is never the approver.
- Project style rules bind these files as they bind everything the project publishes: no em dashes and no en dashes anywhere in the produced files.

## Scenarios

### Scenario: The community profile files exist where GitHub reads them
- S1: Given the change is merged, when GitHub computes the community profile, then the code of conduct, contributing, issue template and pull request template entries are no longer null, and SECURITY.md exists at the repository root.

### Scenario: The contributing guide describes the project's real flow
- S2: Given a reader who knows nothing about ANVIL, when they read CONTRIBUTING.md, then they can state how a change starts (a work order), what is written before implementation (a spec under .openspec/specs/), what decides a merge (review plus the human gate), and how they would propose work themselves (the work order issue template or a good first issue).

### Scenario: The code of conduct is the covenant with the project's contact
- S3: Given CODE_OF_CONDUCT.md, when its text is compared with the current Contributor Covenant, then the covenant text and version attribution match, and the only project specific substitution is the enforcement contact info@arananet.net.

### Scenario: The security policy routes reports to a working private channel
- S4: Given SECURITY.md, when a reporter follows it, then they learn that main and the latest release are supported, that private vulnerability reporting on GitHub is not enabled for this repository, and that reports go privately to info@arananet.net instead of a public issue. The checks gate and its base ref enforcement are named as security relevant surfaces.

### Scenario: Issues start from the project's templates
- S5: Given a visitor opening a new issue, when the template chooser appears, then they can pick the bug report or the work order template, blank issues are disabled, the bug report asks for reproduction steps and run evidence, and the work order template asks for problem, scope, out of scope, acceptance evidence and risk hints.

### Scenario: A pull request carries its evidence
- S6: Given an author opening a pull request, when the template loads, then it asks for the work order, the spec link, and the evidence checklist, and it states that the author never approves their own work.

### Scenario: The change is additions only, in the project's style
- S7: Given the diff of this work order, when it is inspected, then every changed file is one of the new community files named in this spec, no existing file is modified, and no produced file contains an em dash or an en dash.
