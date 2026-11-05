#!/usr/bin/env python3
"""Command executor target for OpenAI-based stations through Codex runtime.

Similar to claude_station.py but executes through an OpenAI-compatible agentic
runtime (Codex). Uses the same permission model and review contract as the
Claude runtime.

Environment variables:
- OPENAI_BASE_URL: API endpoint (e.g., Cloudflare AI Gateway OpenAI route)
- OPENAI_API_KEY: API key for authentication
- ANVIL_CONFIGURED_MODEL: The bare model id (e.g., gpt-6.1-sol)

Station permissions and review contract match claude_station.py exactly.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

NO_EDIT_TOOLS = "Edit,Write,NotebookEdit"
WRITE_STATIONS = {"builder", "test-writer"}
TIMEOUT_SECONDS = 1500


def validate_path_component(component, name):
    """Validate that a path component does not contain traversal attempts."""
    if not component or component == "unknown":
        raise ValueError(f"{name} is unknown or empty")
    dangerous = ["/", "\\", "..", "~"]
    for pattern in dangerous:
        if pattern in component:
            raise ValueError(f"{name} contains dangerous path component: {pattern}")
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
    """Build the canonical review contract wording."""
    return (
        f"\n\n## Runtime reminder\n\n"
        f"Your complete answer is exactly one review JSON object written to "
        f"runs/{work_order_id}/{station_id}.review.json. The free output transcript "
        f"stays as provenance and is never parsed for a review.\n"
    )


def validate_review_file(review_path, station_id):
    """Validate review file using same acceptance rules as parse_review."""
    if not review_path.exists():
        return False, f"Review file not found at {review_path}. You must write the review to this exact path."

    try:
        content = review_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"Could not read review file: {e}"

    if not content.strip():
        return False, "Review file is empty. Write a valid review JSON object."

    text = content.strip()
    if text.startswith("```json") or text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        obj = json.loads(text)
    except json.JSONDecodeError as e:
        return False, f"Review file does not contain valid JSON: {e}"

    if not isinstance(obj, dict):
        return False, "Review file must contain a JSON object, not a list or other type."

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


def call_openai_api(prompt, model, max_tokens=4000):
    """Call OpenAI chat completions API."""
    base_url = os.environ.get("OPENAI_BASE_URL")
    api_key = os.environ.get("OPENAI_API_KEY")

    if not base_url or not api_key:
        raise RuntimeError("Missing OPENAI_BASE_URL or OPENAI_API_KEY environment variables")

    # Use bare model id (strip openai/ prefix if present)
    bare_model = model.split("/")[-1] if "/" in model else model

    payload = {
        "model": bare_model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        req = urllib.request.Request(
            f"{base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            method="POST"
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {api_key}")

        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        if "choices" not in body or len(body["choices"]) == 0:
            raise RuntimeError("OpenAI API returned unexpected response structure")

        output = body["choices"][0].get("message", {}).get("content", "")
        if not output.strip():
            raise RuntimeError("OpenAI API returned empty response")

        return output

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"OpenAI API HTTP error {e.code}: {error_body}")
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {str(e)[:500]}")


def main():
    if len(sys.argv) != 3:
        print("usage: codex_station.py <packet> <output>", file=sys.stderr)
        return 64

    packet_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    # Get configured model from environment
    model = os.environ.get("ANVIL_CONFIGURED_MODEL")
    if not model:
        print("codex_station: ANVIL_CONFIGURED_MODEL environment variable not set", file=sys.stderr)
        return 7

    try:
        packet_text = packet_path.read_text(encoding="utf-8")
        station = station_of(packet_text)
        work_order_id = work_order_id_of(packet_text) if station.startswith("reviewer") else None
    except ValueError as e:
        print(f"codex_station: path validation failed: {e}", file=sys.stderr)
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
                prompt += (
                    f"\n\n## Review file correction needed\n\n"
                    f"The review file validation failed with this error:\n\n{validation_error}\n\n"
                    f"Please correct the issue and write a valid review JSON object to "
                    f"runs/{work_order_id}/{station}.review.json.\n"
                )

        # Never let a previous run's output survive
        try:
            output_path.unlink()
        except FileNotFoundError:
            pass

        try:
            output = call_openai_api(prompt, model)
        except RuntimeError as e:
            print(f"codex_station: {e}", file=sys.stderr)
            return 2

        output_path.write_text(output, encoding="utf-8")

        # For reviewer stations, validate the review file
        if station.startswith("reviewer") and work_order_id:
            review_path = repo_root / "runs" / work_order_id / f"{station}.review.json"
            is_valid, validation_error = validate_review_file(review_path, station)

            if is_valid:
                if correction_used:
                    metadata_path = repo_root / "runs" / work_order_id / f"{station}.correction.json"
                    metadata = {"correction_used": True, "attempts": attempt + 1}
                    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
                break
            elif attempt == 0:
                correction_used = True
                continue
            else:
                break

        # Non-reviewer stations: exit after first attempt
        break

    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
