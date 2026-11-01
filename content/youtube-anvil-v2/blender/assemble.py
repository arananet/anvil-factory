"""Assembly: encode each section's PNG sequence at 30 fps, concatenate with hard cuts, mix the
narration and the bed, write anvil-youtube-v2.mp4. Then the contact sheet and sampled stills."""
import json, pathlib, subprocess, sys
root = pathlib.Path(__file__).resolve().parent.parent
D = json.load(open(root / "durations.json"))
S = D["sections"]
FF = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
BED_GAIN = 0.20      # bed level relative to the narration (about -14 dB)
(root / "clips").mkdir(exist_ok=True)
lead = D["lead"]

def run(cmd):
    subprocess.run(cmd, check=True)

mode = sys.argv[1] if len(sys.argv) > 1 else "all"
if mode in ("all", "video"):
    lst = []
    for s in sorted(S, key=int):
        n = S[s]["frames"]
        out = root / "clips" / f"s{s}.mp4"
        run(FF + ["-framerate", "30", "-i", str(root / "frames" / f"s{s}" / "f_%04d.png"), "-frames:v", str(n),
                  "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-r", "30", str(out)])
        lst.append(f"file '{out}'")
    (root / "clips" / "list.txt").write_text("\n".join(lst) + "\n")
    run(FF + ["-f", "concat", "-safe", "0", "-i", str(root / "clips" / "list.txt"), "-c", "copy", str(root / "clips" / "video.mp4")])
    # narration track: each section starts at its section start plus the lead
    inputs, filt, t0, labels = [], [], 0.0, []
    for i, s in enumerate(sorted(S, key=int)):
        inputs += ["-i", str(root / "audio" / f"s{s}.mp3")]
        ms = int((t0 + lead) * 1000)
        filt.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=mono,adelay={ms}[a{i}]")
        labels.append(f"[a{i}]")
        t0 += S[s]["frames"] / 30
    filt.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest[narr]")
    inputs += ["-i", str(root / "audio" / "bed.wav")]
    filt.append(f"[{len(labels)}:a]volume={BED_GAIN}[bed]")
    filt.append("[narr][bed]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95,atrim=0:" + f"{D['total_seconds']}[mix]")
    run(FF + inputs + ["-filter_complex", ";".join(filt), "-map", "[mix]", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", str(root / "clips" / "audio.m4a")])
    run(FF + ["-i", str(root / "clips" / "video.mp4"), "-i", str(root / "clips" / "audio.m4a"), "-map", "0:v", "-map", "1:a",
              "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(root / "anvil-youtube-v2.mp4")])
if mode in ("all", "sheet"):
    fr = root / "frames"
    picks = []
    for s in sorted(S, key=int):
        n = S[s]["frames"]
        picks.append((f"frame-mid-{s}.png", s, n // 2))
    for a in (1, 3, 5, 6):   # transitions: last frame of section a, first frame of section a+1
        picks.append((f"frame-cut-{a}-last.png", str(a), S[str(a)]["frames"]))
        picks.append((f"frame-cut-{a + 1}-first.png", str(a + 1), 1))
    for name, s, f in picks:
        (fr / name).write_bytes((fr / f"s{s}" / f"f_{f:04d}.png").read_bytes())
    inputs, labels = [], []
    for i, (name, s, f) in enumerate(picks):
        inputs += ["-i", str(fr / name)]
        labels.append(f"[{i}:v]scale=640:360[t{i}]")
    cols = 4
    rows = -(-len(picks) // cols)
    filt = ";".join(labels) + ";" + "".join(f"[t{i}]" for i in range(len(picks))) + f"xstack=inputs={len(picks)}:layout=" + \
        "|".join(f"{(i % cols) * 640}_{(i // cols) * 360}" for i in range(len(picks)))
    run(FF + inputs + ["-filter_complex", filt, "-frames:v", "1", str(root / "contact-sheet.png")])
    print("contact sheet", len(picks), "tiles")
