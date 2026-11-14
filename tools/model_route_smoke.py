#!/usr/bin/env python3
"""Smoke test for the model routes through Cloudflare AI Gateway.

Probes the models the factory uses on the runtime ANVIL_RUNTIME selects:
the Anthropic route of the gateway (claude-gateway, the default) or GitHub
Copilot CLI (copilot). Uses only the environment credentials the workflow
supplies and never prints credential values.

Routes tested:
- claude-sonnet-5-5 (text)
- claude-opus-5-5 (text)
- claude-opus-5-5 (vision: small image; the design stations judge captures)

Exits 0 if every route passes, non-zero if any fails, naming the route.
"""

import base64
import json
import os
import struct
import sys
import urllib.error
import urllib.request
import zlib

TEXT_MODELS = ("claude-sonnet-5-5", "claude-opus-5-5")
VISION_MODEL = "claude-opus-5-5"


def _tiny_png():
    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
    raw = b"\x00\xff\x00\x00\x00\xff\x00\x00"
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 1, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
    return base64.b64encode(png).decode("ascii")


def _gateway_headers():
    """Extra headers from ANTHROPIC_CUSTOM_HEADERS ("name: value" per line)."""
    headers = {}
    for line in os.environ.get("ANTHROPIC_CUSTOM_HEADERS", "").splitlines():
        name, sep, value = line.partition(":")
        if sep and name.strip():
            headers[name.strip()] = value.strip()
    return headers


def probe_anthropic(model, description, content="Say 'ok'"):
    """Probe one model on the Anthropic route. Returns (ok, message)."""
    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not base_url or not api_key:
        return False, "Missing ANTHROPIC_BASE_URL or ANTHROPIC_API_KEY environment variables"
    payload = {"model": model, "max_tokens": 10, "messages": [{"role": "user", "content": content}]}
    secrets = [api_key] + [v for v in _gateway_headers().values() if v]
    try:
        req = urllib.request.Request(f"{base_url.rstrip('/')}/v1/messages",
                                     data=json.dumps(payload).encode("utf-8"), method="POST")
        req.add_header("User-Agent", "anvil-model-route-smoke/1.0")
        req.add_header("Content-Type", "application/json")
        req.add_header("x-api-key", api_key)
        req.add_header("anthropic-version", "2023-06-01")
        for name, value in _gateway_headers().items():
            req.add_header(name, value)
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        if body.get("content"):
            return True, f"{description}: ok"
        return False, f"{description}: unexpected response structure"
    except Exception as exc:
        detail = str(exc)[:200]
        for secret in secrets:
            detail = detail.replace(secret, "[redacted]")
        return False, f"{description}: {detail}"


def probe_anthropic_vision(model, description):
    content = [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": _tiny_png()}},
               {"type": "text", "text": "You were given an image. Say 'ok'"}]
    return probe_anthropic(model, description, content)


def probe_copilot(model, description):
    """Probe one model through GitHub Copilot CLI. Returns (ok, message)."""
    import subprocess
    from copilot_runtime import copilot_model
    name = copilot_model(model)
    try:
        proc = subprocess.run(["copilot", "-p", "Reply with exactly: ok", "--model", name, "--silent", "--no-color",
                               "--no-ask-user", "--no-auto-update", "--disable-builtin-mcps"],
                              capture_output=True, text=True, timeout=180)
    except FileNotFoundError:
        return False, f"{description}: the copilot CLI is not on PATH"
    except subprocess.TimeoutExpired:
        return False, f"{description}: timed out"
    if proc.returncode == 0 and proc.stdout.strip():
        return True, f"{description} ({name}): ok"
    detail = (proc.stderr or proc.stdout or "").strip()[:200]
    for secret in (os.environ.get("COPILOT_GITHUB_TOKEN"), os.environ.get("GH_TOKEN")):
        if secret:
            detail = detail.replace(secret, "[redacted]")
    return False, f"{description} ({name}): exit {proc.returncode}: {detail}"


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from copilot_runtime import selected_runtime
    try:
        runtime = selected_runtime()
    except ValueError as exc:
        print(f"FAIL {exc}")
        return 1
    if runtime == "copilot":
        failed = False
        for model in TEXT_MODELS:
            ok, message = probe_copilot(model, f"Copilot CLI, {model}")
            print(("PASS " if ok else "FAIL ") + message)
            failed = failed or not ok
        return 1 if failed else 0
    probes = [(probe_anthropic, model, f"Anthropic route, {model}, text") for model in TEXT_MODELS]
    probes.append((probe_anthropic_vision, VISION_MODEL, f"Anthropic route, {VISION_MODEL}, vision"))
    failed = False
    for probe, model, description in probes:
        ok, message = probe(model, description)
        print(("PASS " if ok else "FAIL ") + message)
        failed = failed or not ok
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
