Updated the spec successfully. The spec now includes all loopback round 2 requirements:

**Key additions:**
- Input validation (reject newlines, validate email format, enforce length limits)
- Description rendering in CONTRIBUTING.md 
- new_project metadata forwarding
- Issue config.yml omits contact_links to avoid "owner/repo" placeholder
- S8 scenario: injection attack prevention tests
- S9 scenario: greenfield blueprint metadata forwarding test

The updated spec is at `.openspec/specs/community-by-default/spec.md` and ready for round 2 implementation.
