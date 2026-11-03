# Contributing to {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}

Thank you for considering contributing to {{PROJECT_NAME}}. This project uses the ANVIL workflow to manage contributions, specs, and changes.

## How work enters the project

All work starts with a work order. A work order describes the problem, the proposed scope, what is out of scope, the acceptance evidence, and any risk hints. You can propose work in two ways:

1. **Work order issue**: Use the work order issue template in this repository to propose a new unit of work.
2. **Good first issue**: If an issue is already tagged as a good first issue, you can pick it up and propose a spec.

## The ANVIL workflow

This project follows the ANVIL workflow:

1. **Work order**: The problem and scope are stated in a work order.
2. **Spec first**: Before any implementation, a spec is written under `.openspec/specs/`. The spec describes the purpose, requirements, and scenarios. It is the contract between the contributor and the reviewers.
3. **Implementation**: The builder station implements the spec. The change is mapped to the spec scenarios where they apply.
4. **Review**: Multiple reviewer stations examine the change (spec adherence, security, tests, architecture, design). Each reviewer writes their review to an authoritative review file.
5. **Human gate**: A human approves or rejects the work based on the reviews. The author never approves their own work.

## What makes a reviewable change

A reviewable change:

- Is mapped to a spec under `.openspec/specs/`
- Includes tests that prove the scenarios
- Includes run evidence (test results, workflow run links, screenshots where visual)
- Updates documentation or changelog where applicable
- Is small enough to review in one sitting

## Proposing a change

1. Open a work order issue using the template.
2. Wait for triage and approval.
3. Write a spec under `.openspec/specs/<slug>/spec.md` before writing code.
4. Implement the spec and open a pull request.
5. Respond to reviewer feedback.
6. Wait for the human gate to approve.

## Pull request requirements

When you open a pull request, use the pull request template. Include:

- The work order number or link
- The spec link (path under `.openspec/specs/`)
- A summary of the change
- Evidence checklist:
  - Tests run and their result
  - Run report (for factory executed work)
  - Rendered evidence (screenshots, recordings) where the change is visual
  - Documentation or changelog updates where they apply

## Code of conduct

This project has a Code of Conduct. By participating, you agree to uphold it. See CODE_OF_CONDUCT.md.

## Questions

If you have questions about the workflow, open a discussion or ask in an issue.
