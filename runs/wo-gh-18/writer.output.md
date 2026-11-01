I've written the script and the storyboard. Both files are drafts for the review panel. I haven't approved them myself, and I haven't committed them.

- `content/youtube-anvil-v2/script.md`
- `content/youtube-anvil-v2/storyboard.md`

**Script:** it has a title, then a `## Narration` section with seven blocks in spec order. Each block has a Target timing line in M:SS form. It opens with "Introducing ANVIL" and speaks as ANVIL in first person throughout. I ran the spec's own counting rules on it (the ones from `tools/video_checks_v2.py`):
- **Word count:** 194 words, inside the 150 to 200 limit. Per section: 19, 17, 11, 19, 15, 41, 72.
- **Pronouns:** 12 first person pronouns; the spec asks for at least 8.
- **Banned wording:** none of the third person phrases the spec forbids.
- **Dashes and names:** no em or en dashes and no employer name, in either file.
- **Length:** the timings add up to about 80 seconds at the voice's default speed. The measured audio sets the final cut.

After the narration I added two sections the spec doesn't ask for. One holds notes for the media producer. The other maps each spoken claim to its ID (C1 to C11) for reviewer-facts. The checks only read the narration section, so the extra sections don't change the word count.

**Storyboard:** each section has the camera move, the action, the on screen text word for word from the spec, and a framing note. Sections 1 to 6 share one scene, and the work order card becomes the spec and then the piece being built. Section 7 splits Patch One into its five layers in stack order while the camera keeps orbiting.

**Things the reviewers should look at:**
- **Five reviewers:** the line making this film has four reviewers, not five. Section 5 talks about "five of my reviewers" for the factory in general. Section 7 says the video was reviewed but gives no count, so the two don't contradict each other.
- **Three intake kinds:** the code lists more than three kinds, and an issue is a way in rather than a kind. I name the three from the claim list (feature, idea, issue) without saying "three" aloud, and add nothing else.
- **"Before anything ships":** the sources only back this fully for published content and this film. I kept the spec's wording as written, so reviewer-facts should judge it.
- **The Sentia address:** it is spoken exactly as written. If the voice reads it badly, the media producer should note that in `production-notes.md` rather than change the words.

Nothing was missing from the brief, the source pack or the spec.

{"model": "claude-opus-5-5", "runtime": "claude-code"}
