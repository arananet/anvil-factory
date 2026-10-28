"""Agent runtime executors.

An executor takes a rendered station packet (plain text) and returns the
runtime output as plain text. ANVIL ships two kinds:

- command: a shell command template with {packet} and {output} placeholders.
  This is how local agent CLIs are plugged in (for example `claude -p` or
  `codex exec` style commands prepared by the operator).
- http: an OpenAI style chat completions endpoint. The API key is read from
  the environment variable named by api_key_env at call time. It never comes
  from the config file and is never logged.

An executor result is a dict: {"output": str, "usage": dict or None}.
Usage is whatever the runtime reported; ANVIL records token counts when
present and keeps cost null unless a numeric cost is reported.
"""

import json
import os
import shlex
import subprocess
import urllib.request


class ExecutorError(RuntimeError):
    pass


class CommandExecutor:
    kind = "command"

    def __init__(self, config):
        self.template = str(config.get("command", "")).strip()
        self.timeout = int(config.get("timeout_seconds", 300))
        self.name = "command"

    def execute(self, packet_text, station_id, packet_path=None, output_path=None, cwd=None):
        if not self.template:
            raise ExecutorError("command executor has an empty command template")
        command = self.template
        if packet_path is not None:
            command = command.replace("{packet}", shlex.quote(str(packet_path)))
        if output_path is not None:
            command = command.replace("{output}", shlex.quote(str(output_path)))
        try:
            proc = subprocess.run(command, shell=True, cwd=str(cwd) if cwd else None,
                                  capture_output=True, text=True, timeout=self.timeout)
        except subprocess.TimeoutExpired:
            raise ExecutorError(f"command executor timed out after {self.timeout}s")
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "").strip()[:500]
            raise ExecutorError(f"command executor exited {proc.returncode}: {detail}")
        output = proc.stdout or ""
        # A template may redirect into {output} itself; prefer the file then.
        if output_path is not None:
            try:
                file_text = output_path.read_text(encoding="utf-8")
                if file_text.strip():
                    output = file_text
            except (OSError, UnicodeDecodeError):
                pass
        return {"output": output, "usage": None}


class HttpExecutor:
    kind = "http"

    def __init__(self, config):
        self.endpoint = str(config.get("endpoint", "")).strip()
        self.model = str(config.get("model", ""))
        self.api_key_env = str(config.get("api_key_env", ""))
        self.timeout = int(config.get("timeout_seconds", 300))
        self.name = f"http:{self.model}" if self.model else "http"

    def execute(self, packet_text, station_id, packet_path=None, output_path=None, cwd=None):
        if not self.endpoint:
            raise ExecutorError("http executor has no endpoint configured")
        payload = {"model": self.model, "station": station_id,
                   "messages": [{"role": "user", "content": packet_text}]}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.endpoint, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        if self.api_key_env:
            key = os.environ.get(self.api_key_env)
            if key:
                req.add_header("Authorization", f"Bearer {key}")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            raise ExecutorError(f"http executor request failed: {exc}")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            return {"output": body, "usage": None}
        output = ""
        choices = parsed.get("choices") if isinstance(parsed, dict) else None
        if choices:
            message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
            output = message.get("content", "") or ""
        if not output and isinstance(parsed, dict):
            output = parsed.get("output") or parsed.get("text") or ""
        usage = parsed.get("usage") if isinstance(parsed, dict) else None
        return {"output": output, "usage": usage if isinstance(usage, dict) else None}


class FailingExecutor:
    """An executor that always fails, used for unknown kinds so a run marks
    steps failed with the reason recorded instead of silently packing them."""

    def __init__(self, kind):
        self.kind = str(kind)
        self.name = f"unknown:{self.kind}"

    def execute(self, packet_text, station_id, packet_path=None, output_path=None, cwd=None):
        raise ExecutorError(f"unknown executor kind: {self.kind}")


def create_executor(runtime_cfg):
    if not isinstance(runtime_cfg, dict):
        return None
    kind = runtime_cfg.get("kind")
    if kind == "command":
        return CommandExecutor(runtime_cfg)
    if kind == "http":
        return HttpExecutor(runtime_cfg)
    return FailingExecutor(kind)
