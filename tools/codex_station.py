#!/usr/bin/env python3
"""Command executor target that runs openai/* station packets through the Codex CLI.

The agentic OpenAI runtime (model-migration R3, R12). It mirrors
claude_station.py: it reads the packet, learns the station from its first
line, and runs Codex headlessly in the repo working tree with the packet as
the task:

    codex exec --model gpt-6.1-sol ... <packet>

Codex can read the tree and run shell commands, so reviewers write their own
review file and the builder can edit. There is no plain completion path for
station execution: if the codex CLI is absent or the gateway environment is
missing, the station fails loudly.

Environment variables (model-migration R11: the gateway environment the
execute workflows already supply; no OPENAI_* variables and no new secrets):
- ANTHROPIC_BASE_URL: gateway coordinates; the OpenAI provider route is
  derived from it by swapping the trailing anthropic provider segment for openai
- ANVIL_GATEWAY_OPENAI_URL: optional explicit OpenAI provider route, wins when set
- CF_AIG_TOKEN: gateway credential, used directly when set
- ANTHROPIC_CUSTOM_HEADERS: when CF_AIG_TOKEN is not set, the credential is
  taken from its 'cf-aig-authorization: Bearer <token>' header, which is how
  the standing workflows carry it. The value is never printed or written.
- ANVIL_CONFIGURED_MODEL: the assigned model (openai/gpt-6.1-sol); the bare id
  gpt-6.1-sol is what the gateway is called with

Station permissions and review contract match claude_station.py exactly.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

WRITE_STATIONS = {"builder", "test-writer"}
TIMEOUT_SECONDS = 1500
CODEX_PROVIDER = "anvil_gateway"
# Child-only environment variables carrying the gateway credential to Codex.
KEY_ENV = "ANVIL_CODEX_GATEWAY_KEY"
AUTH_HEADER_ENV = "ANVIL_CODEX_GATEWAY_AUTH"
NO_EDIT_INSTRUCTIONS = (
    "ANVIL station permissions: this station has no edit tools. Do not call apply_patch "
    "and do not change the code under judgment. Read the tree and run commands through "
    "the shell. A reviewer writes exactly one file, its own review file, through the shell."
)


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


def _header_credential(headers):
    """Return the bearer token of the cf-aig-authorization header, or "".

    headers is the ANTHROPIC_CUSTOM_HEADERS value: one 'Name: value' header
    per line (LF or CRLF). The header name matches case-insensitively.
    """
    for line in (headers or "").splitlines():
        name, sep, value = line.partition(":")
        if not sep or name.strip().lower() != "cf-aig-authorization":
            continue
        value = value.strip()
        if value[:7].lower() == "bearer ":
            value = value[7:].strip()
        if value:
            return value
    return ""


def gateway_openai_config():
    """Build (endpoint, token) for the gateway OpenAI provider route (R11).

    Raises RuntimeError naming the missing variables, never their values.
    """
    token = os.environ.get("CF_AIG_TOKEN", "").strip() or _header_credential(
        os.environ.get("ANTHROPIC_CUSTOM_HEADERS", ""))
    explicit = os.environ.get("ANVIL_GATEWAY_OPENAI_URL", "").strip()
    anthropic_base = os.environ.get("ANTHROPIC_BASE_URL", "").strip()
    missing = []
    if not token:
        missing.append("CF_AIG_TOKEN (or a cf-aig-authorization header in ANTHROPIC_CUSTOM_HEADERS)")
    if not explicit and not anthropic_base:
        missing.append("ANTHROPIC_BASE_URL (or ANVIL_GATEWAY_OPENAI_URL)")
    if missing:
        raise RuntimeError("gateway environment absent, missing: " + ", ".join(missing))
    if explicit:
        route = explicit.rstrip("/")
    else:
        base = anthropic_base.rstrip("/")
        route, count = re.subn(r"/anthropic(/.*)?$", "/openai", base)
        if count != 1:
            raise RuntimeError("cannot derive the gateway OpenAI route: ANTHROPIC_BASE_URL "
                               "does not end in an anthropic provider segment; set "
                               "ANVIL_GATEWAY_OPENAI_URL")
    return route, token


def call_openai_api(prompt, model, max_tokens=4000):
    """Route probe only; never used for station execution (R12).

    Delegates to the plain completion probe in tools/model_route_smoke.py,
    the one place a bare completion may live. main() below never calls this:
    station execution runs the agentic Codex CLI and has no completion fallback.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from model_route_smoke import route_completion
    return route_completion(prompt, model, max_tokens=max_tokens, timeout=TIMEOUT_SECONDS)


def bare_model_id(model):
    """openai/gpt-6.1-sol -> gpt-6.1-sol. Anything not openai/* is refused."""
    if not model.startswith("openai/") or not model.split("/", 1)[1]:
        raise ValueError(f"codex_station: refusing non-OpenAI model '{model}'")
    return model.split("/", 1)[1]


def codex_command(prompt, bare_model, route, station):
    """Build the headless Codex invocation (argv carries no credential).

    Codex is pointed at a custom provider for the gateway OpenAI route. Its
    credential comes from the child environment: env_key supplies the
    Authorization bearer and env_http_headers supplies cf-aig-authorization.
    Every station bypasses Codex's own approval prompts and sandbox (headless
    exec cannot answer prompts; the throwaway runner is the sandbox), mirroring
    claude_station.py's --dangerously-skip-permissions.

    Stations outside WRITE_STATIONS get NO_EDIT_INSTRUCTIONS as Codex developer
    instructions: no apply_patch edit tool, shell only, the runtime equivalent
    of Claude's Edit/Write/NotebookEdit denylist. Codex 0.166 has no setting
    that drops apply_patch without replacing the whole model catalog, so for
    reviewers the wrapper also enforces the rule after the run
    (reviewer_tree_violations): a reviewer that changed anything besides its own
    review file fails loudly.
    """
    provider = CODEX_PROVIDER
    wire_api = os.environ.get("ANVIL_CODEX_WIRE_API", "").strip() or "responses"
    command = [
        "codex", "exec",
        "--model", bare_model,
        "--skip-git-repo-check",
        "--dangerously-bypass-approvals-and-sandbox",
        "-c", f"model_provider={json.dumps(provider)}",
        "-c", f"model_providers.{provider}.name={json.dumps('ANVIL gateway OpenAI route')}",
        "-c", f"model_providers.{provider}.base_url={json.dumps(route)}",
        "-c", f"model_providers.{provider}.env_key={json.dumps(KEY_ENV)}",
        "-c", f"model_providers.{provider}.wire_api={json.dumps(wire_api)}",
        "-c", (f"model_providers.{provider}.env_http_headers="
               f"{{\"cf-aig-authorization\" = {json.dumps(AUTH_HEADER_ENV)}}}"),
    ]
    if station not in WRITE_STATIONS:
        command += ["-c", f"developer_instructions={json.dumps(NO_EDIT_INSTRUCTIONS)}"]
    command.append(prompt)
    return command


def codex_env(token):
    """Child environment: the credential travels only here, never in argv."""
    env = os.environ.copy()
    env[KEY_ENV] = token
    env[AUTH_HEADER_ENV] = f"Bearer {token}"
    return env


def tree_snapshot(repo_root):
    """Map every changed or untracked path (git status) to a content digest.

    Covers the code under judgment: tracked files (including force-added
    evidence under runs/) and new files that are not git-ignored. Ignored
    scratch space (runs/ outputs, caches) is outside the guard's view.
    """
    git = shutil.which("git") or shutil.which("git", path=os.defpath)
    if not git:
        raise RuntimeError("git is not available; cannot guard the reviewer's tree")
    proc = subprocess.run([git, "status", "--porcelain=v1", "-z", "--untracked-files=all"],
                          cwd=str(repo_root), stdin=subprocess.DEVNULL,
                          capture_output=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError("git status failed; cannot guard the reviewer's tree")
    entries = proc.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    snapshot, skip = {}, False
    for entry in entries:
        if skip:
            skip = False
            continue
        if len(entry) < 4:
            continue
        status, path = entry[:2], entry[3:]
        if "R" in status or "C" in status:
            skip = True  # the next field is the rename source
        target = repo_root / path
        try:
            digest = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else "dir"
        except OSError:
            digest = "missing"
        snapshot[path] = (status, digest)
    return snapshot


def reviewer_tree_violations(before, after, allowed, own_prefix=None):
    """Paths a reviewer changed besides the allowed ones (its own review file).

    own_prefix, when given, also allows the station's own run tree namespace
    (runs/<wo>/<station>.*: its transcript and working notes). Those are run
    records, not code under judgment, so they never destroy the review
    (station artifact contract S4b). Every other path still fails the guard.
    """
    changed = {path for path in set(before) | set(after) if before.get(path) != after.get(path)}
    leftover = changed - set(allowed)
    if own_prefix:
        leftover = {p for p in leftover
                    if not (p.startswith(own_prefix) and "/" not in p[len(own_prefix):])}
    return sorted(leftover)


def reviewer_allowed_paths(repo_root, work_order_id, station, output_path):
    """The reviewer's own review file plus the wrapper's own output files, repo relative."""
    allowed = [f"runs/{work_order_id}/{station}.review.json"]
    for path in (output_path, transcript_path(output_path, station)):
        try:
            allowed.append(Path(path).resolve().relative_to(Path(repo_root).resolve()).as_posix())
        except ValueError:
            pass
    return allowed


def _redact(text, token):
    return text.replace(token, "[redacted]") if token else text


def transcript_path(output_path, station):
    """Where the chat reply goes when the station wrote its own output artifact."""
    return output_path.with_name(f"{station}.transcript.md")


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

    # Configure before invoking anything; any gap fails the station loudly.
    try:
        bare_model = bare_model_id(model)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 7
    if shutil.which("codex") is None:
        print("codex_station: the codex CLI is not on PATH; there is no fallback "
              "runtime for station execution", file=sys.stderr)
        return 5
    try:
        route, token = gateway_openai_config()
    except RuntimeError as e:
        print(f"codex_station: {e}", file=sys.stderr)
        return 2
    child_env = codex_env(token)

    repo_root = Path(__file__).resolve().parent.parent
    correction_used = False
    reviewer = station.startswith("reviewer") and work_order_id
    if reviewer:
        try:
            before = tree_snapshot(repo_root)
        except (RuntimeError, OSError, subprocess.TimeoutExpired) as e:
            print(f"codex_station: {e}", file=sys.stderr)
            return 8

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

        command = codex_command(prompt, bare_model, route, station)
        try:
            # stdin closed: codex exec appends piped stdin to the task and would wait on it
            proc = subprocess.run(command, cwd=str(repo_root), env=child_env,
                                  stdin=subprocess.DEVNULL, capture_output=True,
                                  text=True, timeout=TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            print(f"codex_station: station {station} timed out after {TIMEOUT_SECONDS}s",
                  file=sys.stderr)
            return 4
        except FileNotFoundError:
            print("codex_station: the codex CLI is not on PATH", file=sys.stderr)
            return 5

        if proc.returncode != 0:
            detail = _redact((proc.stderr or proc.stdout or "").strip()[:2000], token)
            print(f"codex_station: codex exited {proc.returncode} for station {station}: {detail}",
                  file=sys.stderr)
            return 2

        output = _redact(proc.stdout or "", token)
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
            print(f"codex_station: codex produced empty output for station {station}",
                  file=sys.stderr)
            return 3

        if station_wrote_output:
            if output.strip():
                transcript_path(output_path, station).write_text(output, encoding="utf-8")
            output = output_path.read_text(encoding="utf-8", errors="replace")
        else:
            output_path.write_text(output, encoding="utf-8")

        if reviewer:
            # Hard guard: a reviewer changes nothing but its own review file.
            try:
                violations = reviewer_tree_violations(before, tree_snapshot(repo_root),
                                                      reviewer_allowed_paths(repo_root, work_order_id,
                                                                             station, output_path),
                                                      own_prefix=f"runs/{work_order_id}/{station}.")
            except (RuntimeError, OSError, subprocess.TimeoutExpired) as e:
                print(f"codex_station: {e}", file=sys.stderr)
                return 8
            if violations:
                print(f"codex_station: reviewer {station} changed files outside its review "
                      f"file: {', '.join(violations[:20])}", file=sys.stderr)
                return 8

        # For reviewer stations, validate the review file
        if reviewer:
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
