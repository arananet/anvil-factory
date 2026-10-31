I wrote the source pack to `content/youtube-anvil/source-pack.md`. It covers all 11 claims from the spec's closed list, and each one cites a repository file or the live Sentia site. Eight are fully sourced. C2, C10 and C11 are only partly sourced, and the pack gives the writer "safe wording" for each.

- **C2 (intake):** the repository supports feature, idea and GitHub issue as entry points. It also lists bug, incident and task, so the writer should not say "exactly" or "only" three.
- **C10 (Sentia):** the live site says it was "designed and built end to end by" ANVIL and calls it a concept product. Nothing I found says it is the first product ANVIL built. The writer should leave out "first" unless the operator confirms it.
- **C11 (this video):** `pipelines/content-video.json` and the work order support it. `production-notes.md` doesn't exist yet, so the record of the video's production can only be confirmed after the media-producer runs.

C5's five reviewers (spec, security, tests, architecture, design) are the software pipeline's panel, not this video's. The pack warns that the narration shouldn't imply those five reviewed the video.

I did not name the author or any employer, although the author's name appears in the live site footer. No claim outside the list went in.

I did not run git commands, so `source-pack.md` is not committed.

{"model": "claude-sonnet-5-5", "runtime": "claude-code"}
