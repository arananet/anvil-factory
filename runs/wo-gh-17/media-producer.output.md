I produced the video, the four sample frames and the production notes. One deterministic check (S3 word count) still fails, and that failure comes from `script.md`, which I didn't edit. Nothing is committed or published, and I haven't approved anything.

The files are in `content/youtube-anvil/`:
- **`anvil-youtube.mp4`:** 1920x1080 at 30 fps, H.264 video with AAC audio, 80.17 s. A full decode pass was clean.
- **`audio/s1.mp3` to `s5.mp3`:** one narration file per section, made with edge-tts, voice en-US-ChristopherNeural. The default speech rate gave 77.6 s of speech, so I didn't adjust it.
- **`frames/frame-1.png` to `frame-4.png`:** taken at 15, 40, 65 and 88 percent, each 1920x1080. Frames 1 and 2 both land in section 2, so the hook isn't sampled.
- **`production-notes.md`:** records how each asset was made, the voice, per-section durations, the commands used, and which assets are AI generated (the two diagrams).

The visuals follow the storyboard crops:
- **Hook:** the hero frame is cropped to the headline and photo band.
- **Dashboard:** it is cropped to the left two columns, which removes the personal names and the third-party network.
- **Close card:** it is rendered from text on dark ink, with no asset file.

`python3 tools/video_checks.py` passes everything except one check:
- **S3 word count:** it reports 237 words against the 150 to 200 limit. The spoken narration is 189 words. The checker counts the "Target timing" lines and block headings as narration, so someone at the operator or writer step needs to decide whether to change the checker or the script.

A few things you should know:
- **Timing:** the video runs 80 s, longer than the 1:10 total in the script's target timings. S2 passes. The notes say the measured durations are the ones that count.
- **ffmpeg install:** ffmpeg wasn't on the runner, so I installed it with apt.
- **Filter error:** my first build printed "No space left on device" on four clips, though the disk had space. I discarded that run and rebuilt with the duration limit on the output side, which ran with no errors. The final file and frames come from the clean run.
- **Dashboard crop:** the storyboard's crop cuts the hydration chart at the right edge. reviewer-design may flag it.

{"model": "claude-sonnet-5-5", "runtime": "claude-code"}
