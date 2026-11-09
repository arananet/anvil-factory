#!/usr/bin/env python3
"""Command executor target that runs ANVIL station packets through Claude Code.

ANVIL's command executor invokes this script with the rendered packet path
and the output path (see anvil.yaml, runtime.command). The script reads the
packet, learns the station id from the packet's first line ("# Task packet:
<station-id>", the marker the runner writes at the top of every packet),
and runs Claude Code in print mode with the packet content as the prompt:

    claude -p <packet> --model <configured-model> --output-format text

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

import json
import os
import subprocess
import sys
from pathlib import Path

WRITE_STATIONS = {"builder", "test-writer"}
NO_EDIT_TOOLS = "Edit,Write,NotebookEdit"
TIMEOUT_SECONDS = 1500


def validate_path_component(component, name):
    """Validate that a path component does not contain traversal attempts.

    Rejects components with path separators or parent directory references
    to prevent path traversal attacks (F3).

    SYNC: This function is duplicated in anvil/model.py and tools/claude_station.py.
    Both implementations must remain identical. The wrapper cannot import from anvil.model,
    so the copies must be kept synchronized manually. Any change to validation logic
    in either location must be mirrored to the other.
    See: tests/test_review_producer.py::TestRound3Finding2PathValidationDuplication
    """
    if not component or component == "unknown":
        raise ValueError(f"{name} is unknown or empty")
    # Reject path separators and parent references
    dangerous = ["/", "\\", "..", "~"]
    for pattern in dangerous:
        if pattern in component:
            raise ValueError(f"{name} contains dangerous path component: {pattern}")
    # Reject absolute paths
    if component.startswith("/") or (len(component) > 1 and component[1] == ":"):
        raise ValueError(f"{name} looks like an absolute path")
    return component


def station_of(packet_text):
    for line in packet_text.splitlines():
        if line.startswith("# Task packet:"):
            station = line.split(":", 1)[1].strip()
            return validate_path_component(station, "station_id")
    return "unknown"


def work_order_id_of(packet_text):
    """Extract work order id from packet content."""
    for line in packet_text.splitlines():
        line = line.strip()
        if line.startswith("- id:"):
            work_order_id = line.split(":", 1)[1].strip()
            return validate_path_component(work_order_id, "work_order_id")
    return "unknown"


def review_suffix(work_order_id, station_id):
    """Build the canonical review contract wording, repeated word-for-word from anvil/runner.py.

    This repetition is intentional: loopback round 1 evidence showed 4 of 5 reviewers
    wrote prose when the contract was stated only in the packet. Repeating the canonical
    wording at the wrapper level puts it at the END of the prompt - the last thing the
    station sees before responding - which maximizes compliance likelihood.
    """
    return (
        f"\n\n## Runtime reminder\n\n"
        f"Your complete answer is exactly one review JSON object written to "
        f"runs/{work_order_id}/{station_id}.review.json. The free output transcript "
        f"stays as provenance and is never parsed for a review.\n"
    )


def validate_review_file(review_path, station_id):
    """Validate review file using same acceptance rules as parse_review (S4).

    Returns (is_valid, error_message).
    - File must exist
    - Content must parse as exactly one JSON object (surrounding whitespace and
      one markdown code fence allowed)
    - station field must equal station_id
    - verdict must be one of: pass, fail, changes_requested
    """
    if not review_path.exists():
        return False, f"Review file not found at {review_path}. You must write the review to this exact path."

    try:
        content = review_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"Could not read review file: {e}"

    if not content.strip():
        return False, "Review file is empty. Write a valid review JSON object."

    # Strip whitespace and optional markdown code fence (same logic as parse_review)
    text = content.strip()
    if text.startswith("```json") or text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]  # Remove opening fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]  # Remove closing fence
        text = "\n".join(lines).strip()

    # Parse as exactly one JSON object
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as e:
        return False, f"Review file does not contain valid JSON: {e}"

    if not isinstance(obj, dict):
        return False, "Review file must contain a JSON object, not a list or other type."

    # Validate required fields
    if "station" not in obj:
        return False, "Review object is missing required field: station"
    if "verdict" not in obj:
        return False, "Review object is missing required field: verdict"

    if obj["station"] != station_id:
        return False, f"Review station field is '{obj['station']}' but must be '{station_id}'"

    valid_verdicts = {"pass", "fail", "changes_requested"}
    if obj["verdict"] not in valid_verdicts:
        return False, f"Review verdict is '{obj['verdict']}' but must be one of: {', '.join(valid_verdicts)}"

    return True, ""


def transcript_path(output_path, station):
    """Where the chat reply goes when the station wrote its own output artifact."""
    return output_path.with_name(f"{station}.transcript.md")


def main():
    if len(sys.argv) != 3:
        print("usage: claude_station.py <packet> <output>", file=sys.stderr)
        return 64
    packet_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    # Get configured model from environment (set by dispatcher)
    model = os.environ.get("ANVIL_CONFIGURED_MODEL")
    if not model:
        print("claude_station: ANVIL_CONFIGURED_MODEL environment variable not set", file=sys.stderr)
        return 7

    try:
        packet_text = packet_path.read_text(encoding="utf-8")
        station = station_of(packet_text)
        work_order_id = work_order_id_of(packet_text) if station.startswith("reviewer") else None
    except ValueError as e:
        print(f"claude_station: path validation failed: {e}", file=sys.stderr)
        return 6

    repo_root = Path(__file__).resolve().parent.parent
    correction_used = False

    # Run station (with one potential correction attempt for reviewers)
    for attempt in range(2):
        prompt = packet_text
        if station.startswith("reviewer") and work_order_id:
            if attempt == 0:
                prompt += review_suffix(work_order_id, station)
            else:
                # Correction attempt: add specific error message
                prompt += (
                    f"\n\n## Review file correction needed\n\n"
                    f"The review file validation failed with this error:\n\n{validation_error}\n\n"
                    f"Please correct the issue and write a valid review JSON object to "
                    f"runs/{work_order_id}/{station}.review.json.\n"
                )

        # Never let a previous run's output survive into this one
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
        # Station artifact contract: the result is the artifact the station
        # wrote, not the chat reply. A station that wrote its own output file
        # keeps it; the reply is saved beside it as a transcript. Empty chat
        # output is fatal only when no artifact exists to stand on.
        station_wrote_output = output_path.is_file() and bool(
            output_path.read_text(encoding="utf-8", errors="replace").strip())
        review_written = False
        if station.startswith("reviewer") and work_order_id:
            review_written = validate_review_file(
                repo_root / "runs" / work_order_id / f"{station}.review.json", station)[0]
        if not output.strip() and not (station_wrote_output or review_written):
            print(f"claude_station: claude produced empty output for station {station}",
                  file=sys.stderr)
            return 3

        if station_wrote_output:
            if output.strip():
                transcript_path(output_path, station).write_text(output, encoding="utf-8")
            output = output_path.read_text(encoding="utf-8", errors="replace")
        else:
            output_path.write_text(output, encoding="utf-8")

        # For reviewer stations, validate the review file (S4)
        if station.startswith("reviewer") and work_order_id:
            review_path = repo_root / "runs" / work_order_id / f"{station}.review.json"
            is_valid, validation_error = validate_review_file(review_path, station)

            if is_valid:
                # Success - write metadata about correction if used
                if correction_used:
                    metadata_path = repo_root / "runs" / work_order_id / f"{station}.correction.json"
                    metadata = {"correction_used": True, "attempts": attempt + 1}
                    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
                break  # Exit loop on success
            elif attempt == 0:
                # First failure - allow one correction attempt (S4)
                correction_used = True
                continue  # Loop will run second attempt
            else:
                # Second failure - no more correction (S4)
                # validation_error will be handled by runner as review_file_missing or review_parse_failed
                break

        # Non-reviewer stations: exit after first attempt
        break

    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
