#!/usr/bin/env python3
"""Command executor target that runs ANVIL station packets through Claude Code.

ANVIL's command executor invokes this script with the rendered packet path
and the output path (see anvil.yaml, runtime.command). The script reads the
packet, learns the station id from the packet's first line ("# Task packet:
<station-id>", the marker the runner writes at the top of every packet),
and runs Claude Code in print mode with the packet content as the prompt:

    claude -p <packet> --model <configured-model> --output-format json

Claude Code reaches the Cloudflare AI Gateway through the environment
(ANTHROPIC_BASE_URL, ANTHROPIC_API_KEY, ANTHROPIC_CUSTOM_HEADERS), which
the workflow supplies from the CF_AIG_TOKEN secret. This script never reads
or prints those values; it only inherits the environment.

Station permissions follow the ANVIL separation of duties:

- Producing stations (builder, test-writer, spec-writer, blueprint,
  brief-writer, researcher, writer, media-producer) may edit the working
  tree, because each is told to produce its output as a file. Every station runs
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
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.telemetry import UsageRecorder, normalize_usage, sum_usage
from anvil.config import resolve_station_timeout, STATION_TIMEOUT_CEILING
sys.path.insert(0, str(Path(__file__).resolve().parent))


class _GatewayOnlyRuntime:
    """Stand-in used when copilot_runtime.py cannot be found anywhere.

    Only the default runtime (Claude Code through the gateway) works with
    it. Asking for Copilot fails the station loudly, naming the missing file.
    """

    GATEWAY_NAMES = {"", "claude-gateway", "claude", "claude-code", "gateway"}

    def __init__(self, searched):
        self.searched = searched

    def selected_runtime(self, environ=None):
        raw = (environ if environ is not None else os.environ).get("ANVIL_RUNTIME", "")
        if raw.strip().lower() in self.GATEWAY_NAMES:
            return "claude-gateway"
        raise ValueError(
            f"ANVIL_RUNTIME '{raw}' needs tools/copilot_runtime.py, which was not found in: "
            + ", ".join(self.searched))


def load_copilot_runtime(environ=None):
    """Find copilot_runtime.py: beside this wrapper, else in the factory's tools.

    A project that runs the line from a pinned factory checkout (the runner
    spine) carries its own synced copy of the station wrappers, and that copy
    may lack copilot_runtime.py. The factory checkout always has it, at
    ANVIL_FACTORY_ROOT/tools (the CLI sets that variable) or next to the anvil
    package that is running. With no copy anywhere the gateway runtime still
    works; only ANVIL_RUNTIME=copilot fails, with the reason.
    """
    import importlib.util
    env = environ if environ is not None else os.environ
    here = Path(__file__).resolve().parent
    if (here / "copilot_runtime.py").is_file():
        import copilot_runtime as module  # the usual case: the file sits beside this wrapper
        return module
    candidates = [here]
    if env.get("ANVIL_FACTORY_ROOT"):
        candidates.append(Path(env["ANVIL_FACTORY_ROOT"]) / "tools")
    try:
        import anvil
        candidates.append(Path(anvil.__file__).resolve().parent.parent / "tools")
    except ImportError:
        pass
    seen = []
    for folder in candidates:
        if folder in seen:
            continue
        seen.append(folder)
        source = folder / "copilot_runtime.py"
        if source.is_file():
            spec = importlib.util.spec_from_file_location("copilot_runtime", source)
            module = importlib.util.module_from_spec(spec)
            sys.modules["copilot_runtime"] = module
            spec.loader.exec_module(module)
            return module
    return _GatewayOnlyRuntime([str(folder) for folder in seen])


copilot_runtime = load_copilot_runtime()

# Stations that produce an artifact in the tree may edit it: each is told to
# produce its output as a file. Reviewers and the read only stations (scout,
# observer, supervisor) never get edit tools.
CODE_WRITE_STATIONS = {"builder", "test-writer"}
ARTIFACT_WRITE_STATIONS = {"spec-writer", "blueprint", "brief-writer",
                           "researcher", "writer", "media-producer"}
WRITE_STATIONS = CODE_WRITE_STATIONS | ARTIFACT_WRITE_STATIONS
NO_EDIT_TOOLS = "Edit,Write,NotebookEdit"
# station-budgets-completeness R3: the in-flight ceiling. The runner hands
# the tokens left of the station's partition (efficiency.station_budgets) in
# ANVIL_STATION_BUDGET_TOKENS and the partition itself in
# ANVIL_STATION_PARTITION. With a ceiling set, the Claude CLI streams its
# events (stream-json), the wrapper sums the usage each model call reports
# while the session runs, and kills the session once that usage reaches the
# ceiling, the same kill-and-record shape as the station timeout.
STATION_BUDGET_ENV = "ANVIL_STATION_BUDGET_TOKENS"
STATION_PARTITION_ENV = "ANVIL_STATION_PARTITION"
BUDGET_EXIT = 11
CORRECTION_REFUSED_EXIT = 12
# SYNC: the same text as CORRECTION_REFUSED in anvil/runner.py, which reads it
# from the failure detail to record the refusal.
CORRECTION_REFUSED = "partition exhausted before the correction re-dispatch"
# The station timeout is configuration (station-timeout, decision 0011): see
# anvil.config.resolve_station_timeout for the resolution order, the class
# defaults and the ceiling. It bounds the whole invocation, correction
# attempt included, so the executor margin above it always holds.


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


def failure_reason(stdout):
    """One line naming why a runtime call failed, read from its result envelope.

    The envelope carries the reason (is_error, subtype, result) after its usage
    block, and the command executor keeps only the first 500 characters of a
    failure, so the raw envelope alone loses the reason. Returns "" when the
    output is not a result envelope.
    """
    try:
        data = json.loads(stdout or "")
    except (ValueError, TypeError):
        return ""
    if not isinstance(data, dict):
        return ""
    parts = []
    for key in ("is_error", "subtype", "api_error_status", "stop_reason", "num_turns"):
        if data.get(key) is not None:
            parts.append(f"{key}={data[key]}")
    text = " ".join(str(data.get("result") or "").split())
    if text:
        parts.append(f"result={text[:300]}")
    return "; ".join(parts)


def parse_ceiling(environ):
    """(ceiling, partition) from the environment, or (None, None) when unset.

    A value that is not a positive integer raises ValueError naming it.
    """
    raw = environ.get(STATION_BUDGET_ENV)
    if raw is None or str(raw).strip() == "":
        return None, None
    values = []
    for name, value in ((STATION_BUDGET_ENV, raw), (STATION_PARTITION_ENV, environ.get(STATION_PARTITION_ENV, raw))):
        try:
            number = int(str(value).strip())
        except ValueError:
            number = 0
        if number <= 0:
            raise ValueError(f"{name} must be a positive integer number of tokens, got {value!r}")
        values.append(number)
    return values[0], values[1]


def streamed_total(per_message):
    """Usage summed over the model calls a stream reported so far, or None.

    The CLI may repeat one message's usage on several events (one per
    content block), so usage is kept per message id and the latest wins.
    """
    return sum_usage(u for u in (normalize_usage(v, "claude") for v in per_message.values()) if u)


def run_with_ceiling(command, cwd, timeout, ceiling):
    """Run one streaming CLI call; stop it when its measured usage reaches ceiling.

    Returns {"outcome": "finished" | "budget" | "timeout", "returncode",
    "stdout" (the result envelope line, or an envelope carrying the usage
    streamed so far when the session ended without one), "stderr",
    "usage" (the streamed usage, None when nothing was reported)}.
    """
    proc = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, start_new_session=True)
    per_message = {}
    result_line = []
    stderr_lines = []
    crossed = threading.Event()

    def read_stdout():
        for line in proc.stdout:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if not isinstance(event, dict):
                continue
            if event.get("type") == "result":
                result_line.append(line.strip())
            elif event.get("type") == "assistant" and isinstance(event.get("message"), dict):
                message = event["message"]
                if isinstance(message.get("usage"), dict):
                    per_message[message.get("id") or f"message-{len(per_message)}"] = message["usage"]
                    total = streamed_total(per_message)
                    if total and total["total_tokens"] >= ceiling:
                        crossed.set()

    readers = [threading.Thread(target=read_stdout, daemon=True),
               threading.Thread(target=lambda: stderr_lines.extend(proc.stderr), daemon=True)]
    for reader in readers:
        reader.start()
    deadline = time.monotonic() + timeout
    outcome = "finished"
    while proc.poll() is None:
        if crossed.wait(0.05) and proc.poll() is None:
            outcome = "budget"
        elif time.monotonic() >= deadline:
            outcome = "timeout"
        else:
            continue
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            proc.kill()
        break
    proc.wait()
    for reader in readers:
        reader.join(timeout=5)
    usage = streamed_total(per_message)
    stdout = result_line[-1] if result_line else ""
    if not stdout and usage is not None:
        stdout = json.dumps({"type": "result", "result": "", "usage": usage})
    return {"outcome": outcome, "returncode": proc.returncode, "stdout": stdout,
            "stderr": "".join(stderr_lines), "usage": usage}


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

    try:
        timeout = resolve_station_timeout(station, os.environ)
    except ValueError as e:
        print(f"claude_station: {e}", file=sys.stderr)
        return 10
    timeout_seconds = timeout["seconds"]
    if timeout["requested"] != timeout_seconds:
        print(f"claude_station: {timeout['source']} {timeout['requested']}s is above the ceiling of "
              f"{STATION_TIMEOUT_CEILING}s; station {station} runs with {timeout_seconds}s",
              file=sys.stderr)

    # Which runtime reaches the model: Claude Code through the Cloudflare AI
    # Gateway (the default), or GitHub Copilot CLI with the GitHub account.
    try:
        runtime = copilot_runtime.selected_runtime()
        if runtime == "copilot":
            copilot_runtime.copilot_model(model)
    except ValueError as e:
        print(f"claude_station: {e}", file=sys.stderr)
        return 9
    provider = "copilot" if runtime == "copilot" else "claude"
    cli = "copilot" if runtime == "copilot" else "claude"
    try:
        ceiling, partition = parse_ceiling(os.environ)
    except ValueError as e:
        print(f"claude_station: {e}", file=sys.stderr)
        return 10
    if runtime == "copilot" and ceiling is not None:
        # Copilot reports usage only when the session ends, so it cannot be
        # stopped mid flight; the runner's pre-call check still applies.
        print(f"claude_station: the in-flight ceiling needs streamed usage, which the copilot runtime "
              f"does not expose; station {station} runs without it", file=sys.stderr)
        ceiling = None

    repo_root = Path(os.environ.get("ANVIL_PROJECT_ROOT") or Path(__file__).resolve().parent.parent).resolve()
    correction_used = False
    usage_recorder = UsageRecorder()
    station_started = time.perf_counter()

    def timed_out(raw, call_started):
        """Record what is knowable about a station killed at its timeout."""
        reason = f"station timeout of {timeout_seconds}s reached ({timeout['source']})"
        usage_recorder.record(
            raw, provider, "timed_out", (time.perf_counter() - call_started) * 1000, model,
            {"station": station, "timeout_seconds": timeout_seconds, "reason": reason})
        print(f"claude_station: station {station} timed out after {timeout_seconds}s", file=sys.stderr)
        return 4

    def budget_stopped(streamed, call_started):
        """Record a session killed at the station's partition (R3).

        Same honest record fields as a timeout: station, reason naming the
        configured limit, the dispatched model and the partial usage the
        runtime exposed. The undone work is not resumed in this dispatch.
        """
        measured = (streamed["usage"] or {}).get("total_tokens")
        reason = (f"station token partition reached: measured {measured} tokens against the "
                  f"{ceiling} left of partition {partition} (efficiency.station_budgets {station})")
        usage_recorder.record(
            streamed["stdout"], provider, "budget_exceeded", (time.perf_counter() - call_started) * 1000,
            model, {"station": station, "partition": partition, "ceiling_tokens": ceiling, "reason": reason})
        print(f"claude_station: station {station} stopped at its token partition: {reason}", file=sys.stderr)
        return BUDGET_EXIT

    # Run station (with one potential correction attempt for reviewers)
    for attempt in range(min(2, int(os.environ.get("ANVIL_MAX_ATTEMPTS", "2")))):
        if attempt and not usage_recorder.within_budget():
            print("claude_station: token threshold reached before correction", file=sys.stderr)
            return 8
        spent = (usage_recorder.summary()["usage"] or {}).get("total_tokens") or 0
        if attempt and ceiling is not None and spent >= ceiling:
            # R2: the in-session correction re-dispatch passes the pre-call
            # check too; a refusal makes no model call.
            print(f"claude_station: station {station} {CORRECTION_REFUSED}: measured {spent} tokens "
                  f"against the {ceiling} left of partition {partition}", file=sys.stderr)
            return CORRECTION_REFUSED_EXIT
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
            "--output-format", "json",
            "--dangerously-skip-permissions",
        ]
        if station not in WRITE_STATIONS:
            command += ["--disallowedTools", NO_EDIT_TOOLS]
        if os.environ.get("ANVIL_MAX_RUNTIME_TURNS"):
            command += ["--max-turns", os.environ["ANVIL_MAX_RUNTIME_TURNS"]]
        if ceiling is not None:
            # Streamed events carry each model call's usage while the session
            # runs; print mode needs --verbose for stream-json.
            command[command.index("json")] = "stream-json"
            command.append("--verbose")

        copilot_usage = Path(str(output_path) + ".copilot-usage.json")
        if runtime == "copilot":
            # Same station, same permissions, reached through the GitHub
            # account: a producing station may use every tool, any other may
            # only read, run commands and write inside its run directory.
            copilot_usage.unlink(missing_ok=True)
            command = copilot_runtime.copilot_command(
                prompt, model, station in WRITE_STATIONS, packet_path.resolve().parent, copilot_usage)

        def raw_result(stdout):
            return copilot_runtime.result_envelope(stdout, copilot_usage) if runtime == "copilot" else stdout

        call_started = time.perf_counter()
        remaining = timeout_seconds - (call_started - station_started)
        if remaining <= 0:
            return timed_out(None, call_started)
        if ceiling is not None:
            try:
                streamed = run_with_ceiling(command, str(repo_root), remaining, ceiling)
            except FileNotFoundError:
                print(f"claude_station: the {cli} CLI is not on PATH", file=sys.stderr)
                return 5
            if streamed["outcome"] == "timeout":
                return timed_out(streamed["stdout"], call_started)
            if streamed["outcome"] == "budget":
                return budget_stopped(streamed, call_started)
            proc = subprocess.CompletedProcess(command, streamed["returncode"], streamed["stdout"],
                                               streamed["stderr"])
        else:
            try:
                proc = subprocess.run(command, cwd=str(repo_root), capture_output=True,
                                      text=True, timeout=remaining)
            except subprocess.TimeoutExpired as exc:
                # On POSIX the partial stdout arrives as bytes even in text mode.
                partial = exc.stdout
                if isinstance(partial, bytes):
                    partial = partial.decode("utf-8", errors="replace")
                return timed_out(raw_result(partial), call_started)
            except FileNotFoundError:
                print(f"claude_station: the {cli} CLI is not on PATH", file=sys.stderr)
                return 5

        parsed = usage_recorder.record(raw_result(proc.stdout), provider,
                                      "succeeded" if proc.returncode == 0 else "failed",
                                      (time.perf_counter() - call_started) * 1000, model)
        if proc.returncode != 0 or parsed.get("is_error"):
            detail = (proc.stderr or proc.stdout or "").strip()[:2000]
            # The reason goes first so it survives the executor's 500 character cut.
            reason = failure_reason(raw_result(proc.stdout))
            if reason:
                detail = f"{reason} | {detail}"
            print(f"claude_station: {cli} exited {proc.returncode} for station {station}: {detail}",
                  file=sys.stderr)
            return 2

        output = parsed["output"]
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
            print(f"claude_station: {cli} produced empty output for station {station}",
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
