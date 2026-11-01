The film matches the spec and the storyboard. I held the content files and only added a verification section to `production-notes.md`.

**Confirmed**
- **Format:** `anvil-youtube-v2.mp4` is H.264 at 1920x1080 and 30 fps, with one AAC audio stream. Duration is 83.83 s, inside the 60 to 90 s window.
- **Frames:** The frames on disk per section match `durations.json`, 2515 in total. The encoded stream holds 2514 frames, one fewer than planned. The duration still matches, and I recorded the difference in the notes.
- **Stills:** `contact-sheet.png` is 2560x1440. There are 15 sampled stills under `frames/`.
- **Deterministic checks:** `checks.txt` reports PASS with 0 failing checks. The GLB sha256 matches the spec.
- **Frozen files:** `script.md` and `storyboard.md` are unchanged.

**Notes file**
- I added "Film review pass verification" after the render statistics block. The block is byte for byte as recorded; I checked that the earlier text is an exact prefix of the new file.
- The new text has no em or en dashes.
- The synthetic speech disclosure stands, so the YouTube AI generated content label must be set at publish time.

**Design observations for reviewer-design** (I recorded them and did not correct them)
- Some section-start frames are nearly empty paper, for example the first frame of section 3.
- In the section 6 midpoint, the "Verified memory." and "A human approves." captions are on screen together and partly overlap.
- In section 4, a station post partly covers the "Stations build" caption.

I did not approve anything. The film stops at the human gate, and nothing was published.

{"model": "claude-sonnet-5-5", "runtime": "claude-code"}
