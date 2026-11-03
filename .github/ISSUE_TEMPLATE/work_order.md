---
name: Work Order
about: Propose a new feature, change, or task for ANVIL
title: ''
labels: work-order
assignees: ''

---

## Problem

A clear statement of the problem this work order solves.

## Proposed Scope

What this work order includes. Be specific about what will change.

## Out of Scope

What this work order explicitly does not include. This is important for setting boundaries.

## Acceptance Evidence

What evidence would prove this work order is complete? Examples:

- Tests pass
- Spec scenarios are satisfied
- Feature works in the demo environment
- Documentation is updated
- Run report shows all stations passed

## Risk Hints

Check all that apply to this work order:

- [ ] auth (authentication or authorization changes)
- [ ] payments (payment processing or billing)
- [ ] data deletion (deletes user data or records)
- [ ] production deploy (changes production infrastructure or configuration)
- [ ] secrets (handles credentials, API keys, or sensitive data)
- [ ] publishing (publishes content or releases to external systems)

If any risk hints are checked, this work order will stop at the human gate before deployment.
