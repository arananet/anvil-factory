# Review: reviewer-facts, wo-gh-18 gate loopback, authoring pass

Verdict: pass.

## Round 1 wording edits
- Section 4 reads "my specialized stations work down the line, and no station ever approves its own work". The phrase "one after another" is gone from script.md. (It remains once in storyboard.md as a visual action description, not spoken; not a claim.)
- Section 7 reads "The models that staff my stations are routed per station through Cloudflare AI Gateway". This matches C8 wording and source-pack C8 evidence (tools/anvil_station.py, tools/claude_station.py, anvil.yaml).

## Claim mapping (all spoken claims map to C1 to C11, none outside the list)
- S1 C1, S2 C2, S3 C3, S4 C4, S5 C5, S6 C6 and C7, S7 C10, C8, C9, C11.
- C5: section 5 states five reviewers for the factory in general; section 7 gives no reviewer count (source flag F1 respected).
- C2: three kinds listed without a count beyond three (F2).
- Counts spoken: five reviewers, five Sentia layers, Apache 2.0. No other counts, no employer, no other factory, product, video or person named (F4).
- C10: concept product, live address, five layers, interactive take-apart page are sourced from the live site fetch in the source pack.
- C9: LICENSE, pyproject.toml, README support Apache 2.0.

## Asset provenance
- patch-one.glb sha256 on disk is daea8110...f523, matching the spec, source pack and production-notes.md. Upstream commit is unverified here (source pack says so) and rests on the spec record.

## Open items
- C11 ("wrote, rendered and reviewed this video, and it stopped at the human gate") cannot be judged yet: the film does not exist. Judged in the second pass against the finished film, checks and run record.
- Minor: source-pack.md C11 and the asset section cite setup commit 7344863 while the loopback setup commit is f6476d6. No effect on any spoken claim.
- Minor: the script says "wrote, rendered and reviewed"; spec C11 also says "produced". The spoken subset is not contradicted by the sources.
