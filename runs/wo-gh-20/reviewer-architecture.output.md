Architecture review complete for wo-gh-20. 

**Verdict: changes_requested**

The core architecture is sound: single definition site (templates/community/), single renderer (anvil/community.py), both doors consume the same mapping, no parallel mechanisms. The full test suite passes.

**Critical finding:** `new_project` doesn't accept or forward `description` and `contact` parameters. It's a public greenfield entry point used by the CLI, but calls `init_project` with only `(path, name)`. Projects created via blueprint path cannot receive metadata for community files.

**Secondary finding:** The `issue_config.yml` template produces a non-functional GitHub URL with literal "owner/repo" since the renderer lacks repo information. This technically satisfies "no double brace tokens" but leaves a placeholder. May be acceptable given the metadata contract limits inputs to name/description/contact.

Review written to `reviews/reviewer-architecture-wo-gh-20.json`.
