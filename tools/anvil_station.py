#!/usr/bin/env python3
"""ANVIL runtime dispatcher for the factory repo: one runtime command, per station routing.

Adapted on this run branch from the established per station pattern used by
the Sentia project (tools/anvil_station.py there), with the difference this
repo needs: every model configured for this run is a Claude model, so all
routes go through tools/claude_station.py with the station's configured
model as the argument. The factory supports exactly one runtime command per
project, so per station routing lives here:

- The dispatcher reads the station id from the packet and the station's
  configured model from anvil.yaml.
- claude-* models run through tools/claude_station.py (Claude Code against
  the gateway Anthropic route), which records the model it dispatched as
  the executed model provenance line.
- Any other model value fails loudly. There is no silent substitution and
  no fallback from one model to another: if a station's configured route is
  down, the step fails and the run records it.

Usage: anvil_station.py <packet> <output>   (invoked by the factory command
executor with the rendered packet path and the output path).
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def station_of(packet_text):
    for line in packet_text.splitlines():
        if line.startswith("# Task packet:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def configured_model(station_id):
    try:
        config = json.loads((REPO_ROOT / "anvil.yaml").read_text(encoding="utf-8"))
        return str(config["stations"][station_id]["model"])
    except Exception:
        return "default"


def main():
    if len(sys.argv) != 3:
        print("usage: anvil_station.py <packet> <output>", file=sys.stderr)
        return 64
    packet_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    station = station_of(packet_path.read_text(encoding="utf-8"))
    model = configured_model(station)

    if model.startswith("claude"):
        wrapper = REPO_ROOT / "tools" / "claude_station.py"
        proc = subprocess.run(
            [sys.executable, str(wrapper), str(packet_path), str(output_path), model],
            cwd=str(REPO_ROOT),
        )
        return proc.returncode

    print(f"anvil_station: no runtime route for station {station} with configured "
          f"model {model!r}; refusing to substitute another model", file=sys.stderr)
    return 6


if __name__ == "__main__":
    sys.exit(main())
