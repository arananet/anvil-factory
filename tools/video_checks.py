#!/usr/bin/env python3
"""Deterministic checks for the YouTube ANVIL video work order (wo-gh-17).

Implements the deterministic scenarios of
.openspec/specs/youtube-anvil-video/spec.md (S1 to S6) against the executed
run's outputs under content/youtube-anvil/. Prints one line per check and
exits non-zero if any check fails. The workflow records the output at
content/youtube-anvil/checks.txt; this script never edits the piece.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIECE = ROOT / "content" / "youtube-anvil"

failures = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'} {name} {detail}".rstrip())
    if not ok:
        failures.append(name)


def ffprobe_json(path):
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True, timeout=120,
    )
    return json.loads(out.stdout)


def main():
    video = PIECE / "anvil-youtube.mp4"
    script = PIECE / "script.md"
    storyboard = PIECE / "storyboard.md"
    notes = PIECE / "production-notes.md"

    # S1 and S2: format, streams, duration.
    if video.exists():
        info = ffprobe_json(video)
        streams = info.get("streams", [])
        vstreams = [s for s in streams if s.get("codec_type") == "video"]
        astreams = [s for s in streams if s.get("codec_type") == "audio"]
        if vstreams:
            v = vstreams[0]
            check("S1-resolution", v.get("width") == 1920 and v.get("height") == 1080,
                  f"({v.get('width')}x{v.get('height')})")
        else:
            check("S1-resolution", False, "(no video stream)")
        check("S1-streams", bool(vstreams) and bool(astreams),
              f"(video={len(vstreams)} audio={len(astreams)})")
        duration = float(info.get("format", {}).get("duration", 0))
        check("S2-duration", 60.0 <= duration <= 90.0, f"({duration:.2f}s)")
    else:
        check("S1-resolution", False, "(anvil-youtube.mp4 missing)")
        check("S2-duration", False, "(anvil-youtube.mp4 missing)")

    # S3: narration word count and per section timings in the script.
    if script.exists():
        text = script.read_text(encoding="utf-8")
        m = re.search(r"## Narration(.*?)(?=\n## |\Z)", text, re.S)
        narration = m.group(1) if m else ""
        words = len(re.findall(r"[A-Za-z0-9']+", narration))
        check("S3-word-count", 150 <= words <= 200, f"({words} words)")
        timings = re.findall(r"\d+:\d{2}", text)
        check("S3-timings", len(timings) >= 5, f"({len(timings)} timing marks)")
    else:
        check("S3-word-count", False, "(script.md missing)")

    # S4: forbidden strings in the piece's text files.
    forbidden = ["nestlé", "nestle", "—", "–"]
    for f in (script, storyboard, notes):
        if f.exists():
            body = f.read_text(encoding="utf-8").lower()
            bad = [s for s in forbidden if s in body]
            check(f"S4-clean-{f.name}", not bad, f"(found: {bad})" if bad else "")
        else:
            check(f"S4-clean-{f.name}", False, "(file missing)")

    # S5: storyboard visuals exist.
    assets = PIECE / "assets"
    expected = ["sentia-page-hero.png", "diagram-line.png", "diagram-memory.png",
                "sentia-dashboard.png"]
    for name in expected:
        check(f"S5-asset-{name}", (assets / name).exists())

    # S6: sample frames.
    frames = sorted((PIECE / "frames").glob("frame-*.png")) if (PIECE / "frames").exists() else []
    check("S6-frame-count", len(frames) >= 4, f"({len(frames)} frames)")
    for f in frames[:4]:
        info = ffprobe_json(f)
        streams = info.get("streams", [])
        if streams:
            s = streams[0]
            check(f"S6-frame-{f.name}", s.get("width") == 1920 and s.get("height") == 1080,
                  f"({s.get('width')}x{s.get('height')})")

    print(f"RESULT: {'FAIL' if failures else 'PASS'} ({len(failures)} failing checks)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
