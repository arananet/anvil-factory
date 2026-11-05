#!/usr/bin/env python3
"""Smoke test for model routes through Cloudflare AI Gateway.

Probes the Anthropic and OpenAI routes with the models the factory uses,
using only environment credentials that the workflows supply. Never prints
credential values.

Routes tested:
- Anthropic route: claude-sonnet-5-5 (text)
- Anthropic route: claude-opus-5-5 (text)
- OpenAI route: gpt-6.1-sol (text)
- OpenAI route: gpt-6.1-sol (vision: small image)

Exits 0 if all routes pass, non-zero if any route fails with the failing
route named.
"""

import base64
import json
import os
import sys
import urllib.request


def probe_anthropic(model, description):
    """Probe Anthropic route through AI Gateway."""
    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not base_url or not api_key:
        return False, "Missing ANTHROPIC_BASE_URL or ANTHROPIC_API_KEY environment variables"

    # Simple text probe
    payload = {
        "model": model,
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Say 'ok'"}]
    }

    try:
        req = urllib.request.Request(
            f"{base_url}/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            method="POST"
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("x-api-key", api_key)
        req.add_header("anthropic-version", "2023-06-01")

        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        # Check for valid response structure
        if "content" in body and len(body["content"]) > 0:
            return True, f"{description}: ok"
        else:
            return False, f"{description}: unexpected response structure"

    except Exception as e:
        return False, f"{description}: {str(e)[:200]}"


def probe_openai_text(model, description):
    """Probe OpenAI route through AI Gateway with text."""
    base_url = os.environ.get("OPENAI_BASE_URL")
    api_key = os.environ.get("OPENAI_API_KEY")

    if not base_url or not api_key:
        return False, "Missing OPENAI_BASE_URL or OPENAI_API_KEY environment variables"

    # Use bare model id for OpenAI
    bare_model = model.split("/")[-1] if "/" in model else model

    payload = {
        "model": bare_model,
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Say 'ok'"}]
    }

    try:
        req = urllib.request.Request(
            f"{base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            method="POST"
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {api_key}")

        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        # Check for valid response structure
        if "choices" in body and len(body["choices"]) > 0:
            return True, f"{description}: ok"
        else:
            return False, f"{description}: unexpected response structure"

    except Exception as e:
        return False, f"{description}: {str(e)[:200]}"


def probe_openai_vision(model, description):
    """Probe OpenAI route through AI Gateway with vision (small image)."""
    base_url = os.environ.get("OPENAI_BASE_URL")
    api_key = os.environ.get("OPENAI_API_KEY")

    if not base_url or not api_key:
        return False, "Missing OPENAI_BASE_URL or OPENAI_API_KEY environment variables"

    # Generate a tiny 1x1 red PNG
    # PNG signature + IHDR + IDAT + IEND
    tiny_png = base64.b64encode(
        b'\x89PNG\r\n\x1a\n'
        b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        b'\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x18\xdd\x8d\xb4'
        b'\x00\x00\x00\x00IEND\xaeB`\x82'
    ).decode('ascii')

    # Use bare model id for OpenAI
    bare_model = model.split("/")[-1] if "/" in model else model

    payload = {
        "model": bare_model,
        "max_tokens": 20,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "What color is this image?"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{tiny_png}"}}
            ]
        }]
    }

    try:
        req = urllib.request.Request(
            f"{base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            method="POST"
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {api_key}")

        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        # Check for valid response structure
        if "choices" in body and len(body["choices"]) > 0:
            return True, f"{description}: ok"
        else:
            return False, f"{description}: unexpected response structure"

    except Exception as e:
        return False, f"{description}: {str(e)[:200]}"


def main():
    """Run smoke tests on all model routes."""
    tests = [
        ("anthropic", "claude-sonnet-5-5", "Anthropic route claude-sonnet-5-5 text", probe_anthropic),
        ("anthropic", "claude-opus-5-5", "Anthropic route claude-opus-5-5 text", probe_anthropic),
        ("openai-text", "gpt-6.1-sol", "OpenAI route gpt-6.1-sol text", probe_openai_text),
        ("openai-vision", "gpt-6.1-sol", "OpenAI route gpt-6.1-sol vision", probe_openai_vision),
    ]

    failed = []

    for test_type, model, description, probe_func in tests:
        success, message = probe_func(model, description)
        print(message)

        if not success:
            failed.append(description)

    if failed:
        print(f"\nFailed routes: {', '.join(failed)}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
