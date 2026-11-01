#!/usr/bin/env python3
"""Deterministic checks for the YouTube ANVIL video v2 work order (wo-gh-18).

Implements the deterministic scenarios of
.openspec/specs/youtube-anvil-video-v2/spec.md (S1 to S8) against the
executed run's outputs under content/youtube-anvil-v2/. Prints one line per
check and exits non-zero if any check fails. The workflow records the output
at content/youtube-anvil-v2/checks.txt; this script never edits the piece.
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIECE = ROOT / "content" / "youtube-anvil-v2"
GLB_SHA256 = "daea8110b356865396b062bb1ca20944dd7103286758214cbc7804b43c50f523"

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


def narration_of(text):
    m = re.search(r"## Narration(.*?)(?=\n## |\Z)", text, re.S)
    return m.group(1) if m else ""


def main():
    video = PIECE / "anvil-youtube-v2.mp4"
    script = PIECE / "script.md"
    storyboard = PIECE / "storyboard.md"
    notes = PIECE / "production-notes.md"

    # S1 and S2: format, streams, frame rate, duration.
    if video.exists():
        info = ffprobe_json(video)
        streams = info.get("streams", [])
        vstreams = [s for s in streams if s.get("codec_type") == "video"]
        astreams = [s for s in streams if s.get("codec_type") == "audio"]
        if vstreams:
            v = vstreams[0]
            check("S1-resolution", v.get("width") == 1920 and v.get("height") == 1080,
                  f"({v.get('width')}x{v.get('height')})")
            rate = v.get("avg_frame_rate", "0/1")
            try:
                num, den = rate.split("/")
                fps = float(num) / float(den) if float(den) else 0.0
            except Exception:
                fps = 0.0
            check("S1-framerate", abs(fps - 30.0) < 0.6, f"({rate} = {fps:.2f} fps)")
        else:
            check("S1-resolution", False, "(no video stream)")
            check("S1-framerate", False, "(no video stream)")
        check("S1-streams", bool(vstreams) and bool(astreams),
              f"(video={len(vstreams)} audio={len(astreams)})")
        duration = float(info.get("format", {}).get("duration", 0))
        check("S2-duration", 60.0 <= duration <= 90.0, f"({duration:.2f}s)")
    else:
        check("S1-resolution", False, "(anvil-youtube-v2.mp4 missing)")
        check("S1-framerate", False, "(anvil-youtube-v2.mp4 missing)")
        check("S2-duration", False, "(anvil-youtube-v2.mp4 missing)")

    # S3, S4 and S5 read the script.
    if script.exists():
        text = script.read_text(encoding="utf-8")
        narration = narration_of(text)
        spoken = re.sub(r"^#.*$", "", narration, flags=re.M)
        spoken = re.sub(r"Target timing:.*", "", spoken)
        words = re.findall(r"[A-Za-z0-9']+", spoken)
        check("S3-word-count", 150 <= len(words) <= 200, f"({len(words)} words)")
        timings = re.findall(r"\d+:\d{2}", text)
        check("S3-timings", len(timings) >= 7, f"({len(timings)} timing marks)")

        plain = " ".join(spoken.split())
        check("S5-opening", plain.startswith("Introducing ANVIL"),
              f"(starts: {plain[:40]!r})")
        pronouns = re.findall(r"\b(I|we|my|our|me|us)\b", spoken, flags=re.I)
        check("S5-pronouns", len(pronouns) >= 8, f"({len(pronouns)} first person pronouns)")
        banned = ["ANVIL is a", "ANVIL is an", "ANVIL keeps", "ANVIL designed",
                  "ANVIL built", "the factory is", "the factory keeps"]
        found = [b for b in banned if b in spoken]
        check("S5-no-third-person", not found, f"(found: {found})" if found else "")
    else:
        check("S3-word-count", False, "(script.md missing)")
        check("S5-opening", False, "(script.md missing)")

    # S4: forbidden strings in the piece's text files.
    forbidden = ["nestlé", "nestle", "—", "–"]
    for f in (script, storyboard, notes):
        if f.exists():
            body = f.read_text(encoding="utf-8").lower()
            bad = [s for s in forbidden if s in body]
            check(f"S4-clean-{f.name}", not bad, f"(found: {bad})" if bad else "")
        else:
            check(f"S4-clean-{f.name}", False, "(file missing)")

    # S6: the committed GLB is the recorded first party asset.
    glb = PIECE / "assets" / "patch-one.glb"
    if glb.exists():
        digest = hashlib.sha256(glb.read_bytes()).hexdigest()
        check("S6-glb-sha256", digest == GLB_SHA256, f"({digest[:16]}...)")
    else:
        check("S6-glb-sha256", False, "(assets/patch-one.glb missing)")

    # S7: contact sheet and sampled stills.
    sheet = PIECE / "contact-sheet.png"
    if sheet.exists():
        info = ffprobe_json(sheet)
        s = info.get("streams", [{}])[0]
        check("S7-contact-sheet", (s.get("width") or 0) >= 1280,
              f"({s.get('width')}x{s.get('height')})")
    else:
        check("S7-contact-sheet", False, "(contact-sheet.png missing)")
    frames_dir = PIECE / "frames"
    stills = sorted(frames_dir.glob("frame-*.png")) if frames_dir.exists() else []
    check("S7-still-count", len(stills) >= 9, f"({len(stills)} sampled stills)")
    bad_stills = []
    for f in stills:
        info = ffprobe_json(f)
        s = info.get("streams", [{}])[0]
        if not (s.get("width") == 1920 and s.get("height") == 1080):
            bad_stills.append(f.name)
    check("S7-still-size", not bad_stills,
          f"(not 1920x1080: {bad_stills})" if bad_stills else "")

    # S8: Blender build scripts and render statistics in the notes.
    scripts = list((PIECE / "blender").glob("*.py")) if (PIECE / "blender").exists() else []
    check("S8-blender-scripts", len(scripts) >= 1, f"({len(scripts)} python scripts)")
    if notes.exists():
        body = notes.read_text(encoding="utf-8")
        has_version = re.search(r"Blender 4\.5", body) is not None
        has_frames = re.search(r"\d{3,5}\s*(frames|Frames)", body) is not None
        check("S8-render-stats", has_version and has_frames,
              f"(blender version noted: {has_version}, frames figure: {has_frames})")
    else:
        check("S8-render-stats", False, "(production-notes.md missing)")

    print(f"RESULT: {'FAIL' if failures else 'PASS'} ({len(failures)} failing checks)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
