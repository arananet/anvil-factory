I checked `brief.md` and `source-pack.md` against the spec, including the polish amendment, and kept both unchanged. I found no concrete error in either. The record is in `runs/wo-gh-18/brief-writer.output.md`.

- **Scope:** the polish amendment only changes scene and layout, so the audience, angle, claims and sources are untouched.
- **Claims:** the list stays closed at C1 to C11. C11 gets re-judged against the new film in the second pass, once the film exists.
- **Asset:** the sha256 of `assets/patch-one.glb` matches the spec's value.
- **Dashes:** I found no em or en dashes in either file.
- **Frozen files:** `git status` shows no change to the frozen content files.
- **Missing inputs:** none. I ran no render, encode or contact sheet extraction.

I didn't re-read `brief.md` or `source-pack.md` line by line this time. I relied on their being unchanged since the last round, which I last verified in full then.

{"model": "claude-sonnet-5-5", "runtime": "claude-code"}
