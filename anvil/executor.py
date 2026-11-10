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
Usage is runtime evidence. Command wrappers record a versioned attempt
ledger; HTTP executors return response usage. The runner calculates cost
only when the corresponding sourced prices are configured.
"""

import json
import os
import shlex
import subprocess
import urllib.request
from pathlib import Path
from .telemetry import normalize_usage


class ExecutorError(RuntimeError):
    def __init__(self, message, result=None):
        super().__init__(message)
        self.result = result or {}


class CommandExecutor:
    kind = "command"
    # The command runs in the project tree, so a station can write the
    # artifacts its packet names (station artifact contract).
    writes_artifacts = True

    def __init__(self, config):
        self.template = str(config.get("command", "")).strip()
        self.timeout = int(config.get("timeout_seconds", 300))
        self.name = "command"

    def execute(self, packet_text, station_id, packet_path=None, output_path=None, cwd=None, configured_model=None):
        if not self.template:
            raise ExecutorError("command executor has an empty command template")
        packet_path = Path(packet_path).resolve() if packet_path is not None else None
        output_path = Path(output_path).resolve() if output_path is not None else None
        command = self.template
        if packet_path is not None:
            command = command.replace("{packet}", shlex.quote(str(packet_path)))
        if output_path is not None:
            command = command.replace("{output}", shlex.quote(str(output_path)))

        # Set up environment with configured model
        env = os.environ.copy()
        env["ANVIL_PROJECT_ROOT"] = str(Path(cwd).resolve() if cwd else Path.cwd())
        if configured_model:
            env["ANVIL_CONFIGURED_MODEL"] = configured_model

        usage_path = Path(str(output_path) + ".usage.json").resolve() if output_path is not None else None
        if usage_path:
            usage_path.unlink(missing_ok=True)
            env["ANVIL_USAGE_PATH"] = str(usage_path)
        else:
            env.pop("ANVIL_USAGE_PATH", None)
        # Runtime controls are explicit handoffs from the current run config.
        for name, value in getattr(self, "limits", {}).items():
            env[name] = str(value)

        def evidence():
            if usage_path:
                try:
                    data = json.loads(usage_path.read_text(encoding="utf-8"))
                    if isinstance(data, dict) and data.get("schema") == "anvil/usage@1":
                        return {"usage": normalize_usage(data.get("usage")), "telemetry": data}
                except (OSError, ValueError):
                    pass
            return {"usage": None}

        try:
            proc = subprocess.run(command, shell=True, cwd=str(cwd) if cwd else None,
                                  env=env, capture_output=True, text=True, timeout=self.timeout)
        except subprocess.TimeoutExpired:
            raise ExecutorError(f"command executor timed out after {self.timeout}s", evidence())
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "").strip()[:500]
            raise ExecutorError(f"command executor exited {proc.returncode}: {detail}", evidence())
        output = proc.stdout or ""
        # A template may redirect into {output} itself; prefer the file then.
        if output_path is not None:
            try:
                file_text = output_path.read_text(encoding="utf-8")
                if file_text.strip():
                    output = file_text
            except (OSError, UnicodeDecodeError):
                pass

        # The executed model is recorded only from runtime self-report evidence
        # found in the output (see runner._reported_model). configured_model is
        # a hand-off to the runtime, never a record of what ran.
        return {"output": output, **evidence()}


class HttpExecutor:
    kind = "http"
    # A completion endpoint returns text only; it cannot write a run tree file.
    writes_artifacts = False

    def __init__(self, config):
        self.endpoint = str(config.get("endpoint", "")).strip()
        self.model = str(config.get("model", ""))
        self.api_key_env = str(config.get("api_key_env", ""))
        self.timeout = int(config.get("timeout_seconds", 300))
        self.name = f"http:{self.model}" if self.model else "http"

    def execute(self, packet_text, station_id, packet_path=None, output_path=None, cwd=None, configured_model=None):
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

    def execute(self, packet_text, station_id, packet_path=None, output_path=None, cwd=None, configured_model=None):
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
