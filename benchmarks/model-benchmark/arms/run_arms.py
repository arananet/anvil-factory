#!/usr/bin/env python3
"""Operator runner for the design station model benchmark (wo-gh-22).

Runs the six benchmark arms as single controlled requests through the
Cloudflare AI Gateway: for each of the three models, one reviewer-design
arm and one builder arm. Packets are assembled from the fixture files in
this repository so the packet content is identical across models; only
the model id and the provider native wire encoding differ.

Sealing: this script never opens fixture/ground-truth.json. The requests
are plain HTTP calls, so a model cannot read anything beyond its packet
and the one attached capture.

Outputs land in benchmarks/model-benchmark/arms/results/:
- <arm>.request.json   the request body, image payload replaced by a hash
- <arm>.response.json  http status plus the raw API response
- <arm>.output.txt     the extracted message text
- <arm>.page.html      builder arms only: the extracted HTML deliverable
- arms-summary.json    per arm status, wall time, usage, output size

Environment: GW_BASE (gateway base URL) and CF_AIG_TOKEN come from the
workflow. Standard library only.
"""

import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path.cwd()
BENCH = ROOT / "benchmarks" / "model-benchmark"
RESULTS = BENCH / "arms" / "results"

GW_BASE = os.environ["GW_BASE"].rstrip("/")
TOKEN = os.environ["CF_AIG_TOKEN"]

# The reviewer output contract suffix, copied verbatim from
# tools/claude_station.py on this branch (REVIEW_SUFFIX), which is what a
# reviewer station session receives after its packet in production runs.
REVIEW_SUFFIX = (
    "\n\n## Output contract\n\n"
    "Answer with a single JSON object and nothing else, in exactly this shape:\n"
    '{"station": "<your station id>", "verdict": "pass", "findings": ["..."]}\n'
    "The verdict must be one of: pass, fail, changes_requested. "
    "Findings must be concrete and checkable against the spec, the code and the tests.\n"
)

ARMS = [
    ("reviewer-astra", "reviewer", "openai", "gpt-6-astra", 3000),
    ("reviewer-opus", "reviewer", "anthropic", "claude-opus-5-5", 3000),
    ("reviewer-sol", "reviewer", "openai", "gpt-6.1-sol", 3000),
    ("builder-astra", "builder", "openai", "gpt-6-astra", 6000),
    ("builder-opus", "builder", "anthropic", "claude-opus-5-5", 6000),
    ("builder-sol", "builder", "openai", "gpt-6.1-sol", 6000),
]


def read(path):
    return Path(path).read_text(encoding="utf-8")


def build_packets():
    station_prompt = read(ROOT / "stations" / "reviewer-design" / "PROMPT.md")
    design_md = read(BENCH / "fixture" / "design" / "DESIGN.md")
    tokens = read(BENCH / "fixture" / "design" / "tokens.json")
    page = read(BENCH / "fixture" / "src" / "page.html")
    tpl = read(BENCH / "arms" / "reviewer-packet-template.md")
    reviewer_text = (tpl.replace("{{STATION_PROMPT}}", station_prompt)
                        .replace("{{DESIGN_MD}}", design_md)
                        .replace("{{TOKENS_JSON}}", tokens)
                        .replace("{{PAGE_HTML}}", page)
                        .replace("{{REVIEW_SUFFIX}}", REVIEW_SUFFIX))
    brief = read(BENCH / "arms" / "builder-brief-template.md")
    builder_text = brief.replace("{{DESIGN_MD}}", design_md)
    image_bytes = (BENCH / "fixture" / "evidence" / "contact-sheet.png").read_bytes()
    return reviewer_text, builder_text, image_bytes


def call_openai(model, text, image_b64, max_tokens, ua):
    content = [{"type": "text", "text": text}]
    if image_b64 is not None:
        content.append({"type": "image_url",
                        "image_url": {"url": "data:image/png;base64," + image_b64}})
    body = {"model": model, "max_completion_tokens": max_tokens,
            "messages": [{"role": "user", "content": content}]}
    headers = {"Authorization": "Bearer " + TOKEN,
               "cf-aig-authorization": "Bearer " + TOKEN,
               "Content-Type": "application/json", "User-Agent": ua}
    return body, headers, GW_BASE + "/openai/chat/completions"


def call_anthropic(model, text, image_b64, max_tokens, ua):
    content = [{"type": "text", "text": text}]
    if image_b64 is not None:
        content.append({"type": "image",
                        "source": {"type": "base64", "media_type": "image/png",
                                   "data": image_b64}})
    body = {"model": model, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": content}]}
    headers = {"cf-aig-authorization": "Bearer " + TOKEN,
               "x-api-key": TOKEN, "anthropic-version": "2023-06-01",
               "Content-Type": "application/json", "User-Agent": ua}
    return body, headers, GW_BASE + "/anthropic/v1/messages"


def extract_text(provider, payload):
    try:
        data = json.loads(payload)
    except Exception:
        return "", None
    if provider == "openai":
        try:
            return data["choices"][0]["message"]["content"] or "", data.get("usage")
        except Exception:
            return "", data.get("usage")
    parts = []
    for block in data.get("content", []):
        if block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "".join(parts), data.get("usage")


def extract_html(text):
    m = re.search(r"<!DOCTYPE html.*?</html>", text, re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(0)
    m = re.search(r"```(?:html)?\s*(<html.*?</html>)", text, re.IGNORECASE | re.DOTALL)
    if m:
        return "<!DOCTYPE html>\n" + m.group(1)
    return text


def redact_image(obj, image_hash, image_len):
    if isinstance(obj, dict):
        return {k: redact_image(v, image_hash, image_len) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact_image(v, image_hash, image_len) for v in obj]
    if isinstance(obj, str) and obj.startswith("data:image/png;base64,"):
        return {"image_data_uri": "redacted", "image_sha256": image_hash,
                "image_bytes": image_len}
    if isinstance(obj, str) and len(obj) > 5000 and image_hash and obj[:40] == obj[:40] and _looks_b64(obj):
        return {"image_base64": "redacted", "image_sha256": image_hash,
                "image_bytes": image_len}
    return obj


def _looks_b64(s):
    return re.fullmatch(r"[A-Za-z0-9+/=\s]+", s) is not None


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    reviewer_text, builder_text, image_bytes = build_packets()
    image_b64 = base64.b64encode(image_bytes).decode()
    image_hash = hashlib.sha256(image_bytes).hexdigest()
    summary = {"packets": {
        "reviewer_text_sha256": hashlib.sha256(reviewer_text.encode()).hexdigest(),
        "reviewer_text_chars": len(reviewer_text),
        "builder_text_sha256": hashlib.sha256(builder_text.encode()).hexdigest(),
        "builder_text_chars": len(builder_text),
        "contact_sheet_sha256": image_hash,
        "contact_sheet_bytes": len(image_bytes)}, "arms": []}

    for name, kind, provider, model, max_tokens in ARMS:
        ua = "anvil-benchmark/wo-gh-22-" + name
        text = reviewer_text if kind == "reviewer" else builder_text
        img = image_b64 if kind == "reviewer" else None
        if provider == "openai":
            body, headers, url = call_openai(model, text, img, max_tokens, ua)
        else:
            body, headers, url = call_anthropic(model, text, img, max_tokens, ua)
        (RESULTS / f"{name}.request.json").write_text(
            json.dumps(redact_image(body, image_hash, len(image_bytes)), indent=2))
        started = time.time()
        status, payload, error = 0, "", ""
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                         headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=600) as resp:
                status = resp.status
                payload = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            status = e.code
            payload = e.read().decode("utf-8", errors="replace")
        except Exception as e:  # recorded, never hidden
            error = f"{type(e).__name__}: {e}"
        wall = round(time.time() - started, 2)
        (RESULTS / f"{name}.response.json").write_text(json.dumps(
            {"http_status": status, "error": error, "response": payload}, indent=2))
        out_text, usage = extract_text(provider, payload) if payload else ("", None)
        (RESULTS / f"{name}.output.txt").write_text(out_text)
        if kind == "builder":
            (RESULTS / f"{name}.page.html").write_text(extract_html(out_text))
        entry = {"arm": name, "kind": kind, "provider": provider, "model": model,
                 "http_status": status, "error": error, "wall_seconds": wall,
                 "usage": usage, "output_chars": len(out_text)}
        summary["arms"].append(entry)
        print(name, status, wall, "s, output chars:", len(out_text), error[:120])

    (RESULTS / "arms-summary.json").write_text(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
