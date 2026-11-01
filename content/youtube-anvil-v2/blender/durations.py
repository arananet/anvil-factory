"""Measure each narration file and set each section's visual length: narration plus a short pad.
Writes durations.json. Lead 0.15 s before the voice, tail 0.45 s after it (0.6 s pad in total)."""
import json, re, subprocess, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
LEAD, TAIL, MIN_S3 = 0.15, 0.45, 5.0
out = {}
for i in range(1, 8):
    r = subprocess.run(["ffmpeg", "-i", str(root / "audio" / f"s{i}.mp3")], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r).groups()
    narr = int(h) * 3600 + int(m) * 60 + float(s)
    dur = max(narr + LEAD + TAIL, MIN_S3 if i == 3 else 0)
    out[i] = dict(narration=round(narr, 3), visual=round(dur, 3), frames=round(dur * 30))
tot = sum(v["frames"] for v in out.values())
json.dump(dict(sections=out, total_frames=tot, total_seconds=round(tot / 30, 3), lead=LEAD, tail=TAIL), open(root / "durations.json", "w"), indent=1)
print(tot, tot / 30)
