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

- id: wo-gh-19
- kind: task
- title: Complete the GitHub community profile
- source: github-issue
- description: Implement the spec in .openspec/specs/community-profile/spec.md in the factory. Pipeline for this order is docs-only (intake, builder, reviewer-spec, approver), selected by the run workflow.

Build, per the spec scenarios, exactly these new files and no others. Modify no existing file.

S1 and S7: CONTRIBUTING.md, CODE_OF_CONDUCT.md and SECURITY.md at the repository root; .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/work_order.md and .github/ISSUE_TEMPLATE/config.yml; .github/pull_request_template.md. Additions only, and no em dash or en dash character in any produced file (project style rule).

S2: CONTRIBUTING.md explains the project's real flow: every change starts as a work order; a spec is written under .openspec/specs/ before implementation; tests map to spec scenarios where the change touches code; reviewer stations judge and a human gate decides before anything merges or ships. It tells external contributors how to propose work (the work order issue template, or a good first issue) and names the standing rules that bind contributors: runtime code stays on the Python standard library only, and new projects follow the house README template. It expands the README's existing Contributing section without contradicting it.

S3: CODE_OF_CONDUCT.md is the current version of the Contributor Covenant with its version attribution intact. The only project specific substitution is the enforcement contact: info@arananet.net, the contact this repository already publishes. No covenant clause is weakened, removed or reworded.

S4: SECURITY.md states the supported versions (the main branch and the latest release) and the private reporting route. GitHub private vulnerability reporting is NOT enabled on this repository (operator checked 2026-11-02), so reports go privately to info@arananet.net and reporters are asked not to open public issues for vulnerabilities. Name the security relevant surfaces reports are especially welcome against: the deterministic checks gate and its base ref enforcement, the review parsing contract, and gateway credential routing. Promise no specific response timelines.

S5: bug_report.md asks for what happened, what was expected, steps to reproduce, environment, and run evidence where relevant (run report, station output, workflow run link). work_order.md asks for the problem, the proposed scope, what is out of scope, the acceptance evidence, and risk hints from the project's own list (auth, payments, data deletion, production deploy, secrets, publishing). config.yml disables blank issues so every issue starts from a template.

S6: .github/pull_request_template.md asks for the work order, the spec link, a change summary, and an evidence checklist (tests run and result, run report for factory executed work, rendered evidence where the change is visual, documentation or changelog where they apply), and states that the author never approves their own work: reviewer stations and the human gate decide.

The reviewer writes its review to the authoritative review file named in its packet; prose outside that file is not a review.

GitHub issue: https://github.com/arananet/anvil-factory/issues/19
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- builder: executed
