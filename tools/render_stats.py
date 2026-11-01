#!/usr/bin/env python3
"""Deterministic render statistics for the YouTube ANVIL video v2 (wo-gh-18).

Used by the loopback workflow (.github/workflows/anvil-execute-content-video-v2.yml)
after the deterministic render step. It aggregates the per chunk logs that
blender/render_all.sh leaves under content/youtube-anvil-v2/frames/logs/
(each chunk log carries one SECTION_RENDER_DONE line with its frame count
and its render seconds), counts the PNG frames on disk per section as the
ground truth, and then:

- writes content/youtube-anvil-v2/render-stats.json (the statistics record);
- makes sure content/youtube-anvil-v2/production-notes.md carries the
  statistics block between the markers below, replacing the block if it is
  already there and appending it if it is not. The block states the Blender
  version and the total frames figure in the form the deterministic checks
  (tools/video_checks_v2.py, scenario S8) read.

This script never edits the piece itself and never invents a number: every
figure comes from the chunk logs, the frame files, durations.json or the
blender binary's own version output.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIECE = ROOT / "content" / "youtube-anvil-v2"
START = "<!-- render-stats:start -->"
END = "<!-- render-stats:end -->"


def blender_version():
    try:
        out = subprocess.run(["blender", "--version"], capture_output=True,
                             text=True, timeout=60).stdout
        m = re.search(r"Blender\s+(\d+\.\d+\.\d+)", out)
        return m.group(1) if m else "unknown"
    except Exception:
        return "unknown"


def main():
    logs_dir = PIECE / "frames" / "logs"
    sections = {}
    if logs_dir.exists():
        for log in sorted(logs_dir.glob("render-s*.log")):
            for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
                m = re.search(r"SECTION_RENDER_DONE s(\d+) frames=(\d+) seconds=([\d.]+)", line)
                if m:
                    s = sections.setdefault(m.group(1), {"frames_rendered": 0,
                                                         "render_seconds": 0.0,
                                                         "chunks": 0})
                    s["frames_rendered"] += int(m.group(2))
                    s["render_seconds"] += float(m.group(3))
                    s["chunks"] += 1
    # Ground truth: PNG frames on disk per section.
    for s in list(sections):
        d = PIECE / "frames" / f"s{s}"
        on_disk = len(list(d.glob("f_*.png"))) if d.exists() else 0
        sections[s]["frames_on_disk"] = on_disk
        sections[s]["render_seconds"] = round(sections[s]["render_seconds"], 1)
    total_frames = sum(v.get("frames_on_disk", 0) for v in sections.values())
    total_seconds = round(sum(v["render_seconds"] for v in sections.values()), 1)

    planned = {}
    durations = PIECE / "durations.json"
    if durations.exists():
        data = json.loads(durations.read_text(encoding="utf-8"))
        planned = {k: v.get("frames") for k, v in data.get("sections", {}).items()}

    version = blender_version()
    stats = {
        "blender_version": version,
        "renderer": "Eevee",
        "resolution": "1920x1080",
        "fps": 30,
        "sections": sections,
        "planned_frames": planned,
        "total_frames_on_disk": total_frames,
        "total_render_seconds_logged": total_seconds,
        "rendered_by": "deterministic workflow step (parallel chunked headless Blender, at most 4 processes)",
    }
    (PIECE / "render-stats.json").write_text(json.dumps(stats, indent=2) + "\n",
                                             encoding="utf-8")

    per_section = ", ".join(
        f"section {s}: {sections[s].get('frames_on_disk', 0)} frames in "
        f"{sections[s]['render_seconds']} s across {sections[s]['chunks']} chunks"
        for s in sorted(sections, key=int))
    block = "\n".join([
        START,
        "## Render statistics (recorded by the deterministic workflow render step)",
        "",
        f"Rendered with Blender {version}, Eevee, at 1920x1080 and 30 fps by the "
        "workflow's deterministic render step (parallel chunked headless Blender, "
        "at most 4 processes at once), outside any model station session.",
        f"Total frames rendered: {total_frames} frames.",
        f"Per section: {per_section}.",
        f"Logged render time in total: {total_seconds} s of Blender render time "
        "summed across chunks (chunks ran in parallel, so wall time was lower).",
        "The full record is in render-stats.json next to this file.",
        END,
    ])

    notes = PIECE / "production-notes.md"
    if notes.exists():
        body = notes.read_text(encoding="utf-8")
        if START in body and END in body:
            body = re.sub(re.escape(START) + r".*?" + re.escape(END), block,
                          body, flags=re.S)
        else:
            body = body.rstrip() + "\n\n" + block + "\n"
        notes.write_text(body, encoding="utf-8")
    else:
        notes.write_text(
            "# Production notes\n\n"
            "The media-producer station's production notes were not present when "
            "the deterministic workflow steps ran, so this file carries only the "
            "render statistics block for now.\n\n" + block + "\n",
            encoding="utf-8")
    print(f"render-stats: Blender {version}, {total_frames} frames on disk, "
          f"{total_seconds} s logged render time across {len(sections)} sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
