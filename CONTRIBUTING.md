# Contributing to ANVIL

Thank you for your interest in contributing to ANVIL. This guide explains how work enters this project and what makes a change reviewable.

## How Work Enters the Project

Every change in ANVIL starts with a work order. Work orders come from GitHub issues, the intake worker, or a file. No code is written without one.

The flow is:

1. **Work order**: A problem statement, proposed scope, what is explicitly out of scope, acceptance evidence, and risk hints.
2. **Spec**: A spec is written under `.openspec/specs/` before implementation begins. Specs use the OpenSpec format. Every spec defines scenarios that show what success looks like.
3. **Tests**: Where the change touches code, tests are written that map to the spec scenarios before implementation.
4. **Implementation**: Code is written to make the tests pass and satisfy the spec.
5. **Review**: Reviewer stations check the change against the spec, security risks, test quality, and architectural fit.
6. **Human gate**: A human decides before anything merges or ships. The author never approves their own work.

This is the discipline ANVIL applies to itself. Spec first, tests first, and no station approves its own work.

## How to Propose Work

If you are an external contributor, you can propose work in two ways:

1. **Open a work order issue**: Use the work order issue template in this repository. Describe the problem you want to solve, the proposed scope, what is out of scope, and the evidence that would prove the change works. The project maintainers will review your proposal.

2. **Pick up a good first issue**: Issues labeled `good first issue` are work orders that are ready for implementation. If you see one that interests you, comment on the issue to claim it, then follow the flow above.

## What Makes a Change Reviewable

A reviewable change in ANVIL is one that:

- Has a work order that states the problem and the scope.
- Has a spec under `.openspec/specs/` that describes the change.
- Has tests that map to the spec scenarios, where the change touches code.
- Passes all tests.
- Includes evidence: test results, run reports for factory executed work, rendered screenshots where the change is visual, and documentation or changelog updates where they apply.

When you open a pull request, the PR template will ask for this evidence.

## Standing Project Rules

These rules bind all contributors:

1. **Runtime code stays on the Python standard library only.** ANVIL runtime code does not depend on third party packages. Tests, examples, and the intake worker are not runtime code and may use dependencies, but the core factory does not.

2. **New projects follow the house README template.** If your change scaffolds a new project type (a new blueprint, a new catalog entry), it must follow the README structure documented in `templates/README.md`.

## Code of Conduct

This project follows the Contributor Covenant Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to info@arananet.net.

## Questions

If you have questions about contributing, open an issue with the bug report or work order template, or reach out to the maintainers at info@arananet.net.
