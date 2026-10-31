#!/usr/bin/env python3
"""Command executor target that runs ANVIL station packets through Claude Code.

Adapted on this run branch from the Sentia project's wrapper, which itself
descends from the factory's original: the model is NOT hardcoded. The
dispatcher (tools/anvil_station.py) passes the station's configured model
from anvil.yaml as argv[3], and this wrapper runs:

    claude -p <packet> --model <configured model> --output-format text

For this run that means the writer station executes with claude-opus-5-5
and the reviewer stations with claude-sonnet-5-5, per the work order.

Claude Code reaches the Cloudflare AI Gateway through the environment
(ANTHROPIC_BASE_URL, ANTHROPIC_API_KEY, ANTHROPIC_CUSTOM_HEADERS), which
the workflow supplies from the CF_AIG_TOKEN secret. This script never reads
or prints those values; it only inherits the environment.

Station permissions follow the ANVIL separation of duties:

- Producing stations (builder, test-writer, spec-writer, and the content
  line's brief-writer, researcher, writer and media-producer) may edit the
  working tree: their output is files in the repo.
- Reviewer stations (and any other station) get Edit, Write and
  NotebookEdit disallowed, so they can read and run commands but cannot
  change the work they are judging.

Reviewer output contract: the factory docs/EXECUTION.md states that
reviewer stations answer with a review JSON. For reviewer stations this
wrapper appends a short suffix restating that contract (one JSON object
with station, verdict and findings); without it the runner cannot parse a
review and the station contributes nothing to the approver.

Provenance: after a successful run the wrapper appends one JSON line,
{"model": <model>, "runtime": "claude-code"}, reporting the model it
dispatched this station to. That is the runtime reporting its own model,
which is exactly what the runner records as executed_model; nothing is
inferred from the model's prose.

Failure behavior: a non-zero Claude exit, a timeout, or empty output makes
this script exit non-zero, so the runner marks the step failed. It never
writes a partial or placeholder output and calls it success.
"""

import json
import subprocess
import sys
from pathlib import Path

WRITE_STATIONS = {
    "builder",
    "test-writer",
    "spec-writer",
    "brief-writer",
    "researcher",
    "writer",
    "media-producer",
}
NO_EDIT_TOOLS = "Edit,Write,NotebookEdit"
TIMEOUT_SECONDS = 1500

REVIEW_SUFFIX = (
    "\n\n## Output contract\n\n"
    "Answer with a single JSON object and nothing else, in exactly this shape:\n"
    '{"station": "<your station id>", "verdict": "pass", "findings": ["..."]}\n'
    "The verdict must be one of: pass, fail, changes_requested. "
    "Findings must be concrete and checkable against the spec, the code and the tests.\n"
)


def station_of(packet_text):
    for line in packet_text.splitlines():
        if line.startswith("# Task packet:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def main():
    if len(sys.argv) != 4:
        print("usage: claude_station.py <packet> <output> <model>", file=sys.stderr)
        return 64
    packet_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    model = sys.argv[3]
    packet_text = packet_path.read_text(encoding="utf-8")
    station = station_of(packet_text)

    prompt = packet_text
    if station.startswith("reviewer"):
        prompt += REVIEW_SUFFIX

    # Never let a previous run's output survive into this one: the executor
    # prefers a non-empty output file, so a stale file would be mistaken
    # for this station's answer.
    try:
        output_path.unlink()
    except FileNotFoundError:
        pass

    command = [
        "claude", "-p", prompt,
        "--model", model,
        "--output-format", "text",
        "--dangerously-skip-permissions",
    ]
    if station not in WRITE_STATIONS:
        command += ["--disallowedTools", NO_EDIT_TOOLS]

    repo_root = Path(__file__).resolve().parent.parent
    try:
        proc = subprocess.run(command, cwd=str(repo_root), capture_output=True,
                              text=True, timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        print(f"claude_station: station {station} timed out after {TIMEOUT_SECONDS}s",
              file=sys.stderr)
        return 4
    except FileNotFoundError:
        print("claude_station: the claude CLI is not on PATH", file=sys.stderr)
        return 5

    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()[:2000]
        print(f"claude_station: claude exited {proc.returncode} for station {station}: {detail}",
              file=sys.stderr)
        return 2

    output = proc.stdout or ""
    if not output.strip():
        print(f"claude_station: claude produced empty output for station {station}",
              file=sys.stderr)
        return 3

    report = json.dumps({"model": model, "runtime": "claude-code"})
    output_path.write_text(output.rstrip() + "\n\n" + report + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
