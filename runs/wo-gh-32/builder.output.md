I've written the operator requirements document, added its README row and added the CHANGELOG entry. Every check in `scenario-checks.md` passes, and the full test suite is green (580 passed, 6 skipped).

**Files changed** (nothing else touched, nothing under `tests/`):
- **`docs/OPERATOR-REQUIREMENTS.md`** (new). It has three sections:
  - **GitHub:** a table with each permission, the call that works with it and the failure without it. It also covers the standing facts (secrets are write-only, merges API, what the PAT can't do, the social preview image upload) and why a GitHub App client secret is not a personal access token.
  - **Cloudflare:** what the vault token can and can't do, the gateway authorization shape and why the placeholder shape gives a false 401, how each repo gets its `CF_AIG_TOKEN`, the gateway settings on record, and how Wrangler authenticates.
  - **Placement and care:** the closing section, as the spec requires. It says where each credential lives, what breaks without each permission, and the two never-again lessons.
- **`README.md`:** one row added to the Documentation table, in the same style as the others.
- **`CHANGELOG.md`:** one Unreleased entry.

**Checks:**
- The scan for credential-shaped strings and 32-character hex ids finds nothing in the three files. Credentials appear by name and purpose only.
- There are no em or en dashes in any of the three files.

**Gap in the inputs:** the work order gives no failure-without-it for **Contents** or **Secrets write**. Rather than invent one, those two table rows say "No isolated failure on record". A reviewer or the owner should fill them in if a real observed failure exists.

pytest wasn't installed on the runner, so I installed it to run the suite. The Quality Charter comparison step doesn't apply because this work produces no visual output.
{"model": "claude-opus-5-5"}
