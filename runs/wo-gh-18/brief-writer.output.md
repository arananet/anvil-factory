I verified `content/youtube-anvil-v2/brief.md` against the spec, including the gate loopback and polish amendments. I found no concrete error, so I kept it byte for byte and corrected nothing.

- **Spec match:** the brief matches the spec on every point I checked.
  - It has the seven sections, with the exact on screen text for each.
  - It carries the closed claim list C1 to C11 with their sources.
  - It states the first person voice rules and the allowed counts of three, five and five.
  - It states the format: 1920x1080, 30 fps, 60 to 90 seconds, edge-tts voice en-US-ChristopherNeural.
  - It carries the S5 pronoun and forbidden-phrase rules.
- **Dashes and names:** it has no em or en dashes, and it names no employer, other factory, product, video or person.
- **Open point for the researcher:** the brief flags the four reviewer content variant against the five parallel reviewer claim C5. It tells the researcher to cite the scope and not to rephrase the claim, which matches the spec.
- **Frozen inputs:** `git diff HEAD` shows no changes to `brief.md`, `source-pack.md`, `script.md` or `storyboard.md`.
- **Polish amendment:** it changes only scene and layout, not the brief. The brief's section plan and on screen text stay valid, so adding the four advisories to it would not be a correction. I left them for `production-notes.md` and the scene scripts.
- **Missing inputs:** nothing blocks the brief. The design tokens are still all TODO, so the visual language comes from the spec (paper, ink green, teal). The media-producer picks exact values and records them in `production-notes.md`.

I did not render, encode or extract anything, and I did not approve any work.

{"model": "claude-sonnet-5-5", "runtime": "claude-code"}
