Excellent! All 100 tests pass. The implementation is complete. Let me provide a summary of what was built:

## Implementation Summary

I've successfully implemented community files by default for every ANVIL project. Here's what was created:

### 1. Templates (templates/community/)
- **code_of_conduct.md** - Contributor Covenant 2.1 with enforcement contact substitution
- **contributing.md** - Teaches the ANVIL workflow (work orders, specs, reviewers, human gate)
- **security.md** - Supported versions, GitHub private vulnerability reporting, contact fallback
- **bug_report.md** - Issue template for bug reports with evidence requirements
- **work_order.md** - Issue template for work orders with risk hints
- **issue_config.yml** - Disables blank issues
- **pull_request_template.md** - PR template with work order, spec link, and evidence checklist

### 2. Renderer (anvil/community.py)
- Single function `render_community_files()` that takes name, description, and contact
- Returns mapping of relative paths to rendered content
- Handles contact fallback to GitHub when not configured
- No template residue in output

### 3. Integration
- **scaffold.py** - Added optional `description` and `contact` parameters to `init_project`, writes all seven community files
- **onboard.py** - Added optional `description` and `contact` parameters to `onboard_project`, uses `_write_if_missing` to preserve existing files

### 4. Tests (tests/test_community.py)
- ✓ S1: Scaffolded projects have all seven files with no template residue
- ✓ S2: Onboarding preserves existing CONTRIBUTING.md, creates the other six
- ✓ S3: Both doors produce identical files from same metadata
- ✓ S4: Contact substitution works, no hardcoded personal data, GitHub fallback works
- ✓ S6: Full factory suite stays green (100 tests pass)

The implementation follows the spec exactly: one canonical set defined in templates/community/, one renderer in anvil/community.py, both doors use the same renderer, no template residue, and all tests pass.
