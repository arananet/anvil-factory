#!/usr/bin/env python3
"""Command executor target that runs ANVIL station packets through Claude Code.

ANVIL's command executor invokes this script with the rendered packet path
and the output path (see anvil.yaml, runtime.command). The script reads the
packet, learns the station id from the packet's first line ("# Task packet:
<station-id>", the marker the runner writes at the top of every packet),
and runs Claude Code in print mode with the packet content as the prompt:

    claude -p <packet> --model claude-sonnet-4-5 --output-format text

Claude Code reaches the Cloudflare AI Gateway through the environment
(ANTHROPIC_BASE_URL, ANTHROPIC_API_KEY, ANTHROPIC_CUSTOM_HEADERS), which
the workflow supplies from the CF_AIG_TOKEN secret. This script never reads
or prints those values; it only inherits the environment.

Station permissions follow the ANVIL separation of duties:

- builder and test-writer may edit the working tree. Every station runs
  with --dangerously-skip-permissions because headless print mode cannot
  answer permission prompts; the sandbox is the throwaway Actions runner
  plus the tool denylist below.
- Reviewer stations (and any other station) get Edit, Write and
  NotebookEdit disallowed, so they can read and run commands (Bash stays
  available, for example so a tests reviewer can run the suite) but cannot
  change the code they are judging.

Reviewer output contract: the factory docs/EXECUTION.md states that
reviewer stations answer with a review JSON and that their prompts ask for
it. The shipped station prompts do not actually include that instruction,
so for reviewer stations this wrapper appends a short suffix restating the
documented contract (one JSON object with station, verdict and findings).
Without it the runner cannot parse a review and the station contributes
nothing to the approver.

Failure behavior: a non-zero Claude exit, a timeout, or empty output makes
this script exit non-zero, so the runner marks the step failed. It never
writes a partial or placeholder output and calls it success.
"""

import subprocess
import sys
from pathlib import Path

MODEL = "claude-sonnet-4-5"
WRITE_STATIONS = {"builder", "test-writer"}
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
    if len(sys.argv) != 3:
        print("usage: claude_station.py <packet> <output>", file=sys.stderr)
        return 64
    packet_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
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
        "--model", MODEL,
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

    output_path.write_text(output, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
