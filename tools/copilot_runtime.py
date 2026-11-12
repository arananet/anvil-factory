#!/usr/bin/env python3
"""GitHub Copilot CLI as a station runtime (ANVIL_RUNTIME=copilot).

The station wrapper (tools/claude_station.py) owns the station contract:
permissions by station, the review file check and its one correction, the
usage ledger. This module is only what differs when the model is reached
through a GitHub account instead of the Cloudflare AI Gateway: the command
line, the model names, and where token usage is read from.

The command line follows `copilot --help` of @github/copilot 1.0.109:

    copilot -p <packet> --model <model> --silent --usage-output-file <file> ...

Authentication is Copilot's own: COPILOT_GITHUB_TOKEN (a token with the
Copilot Requests permission), or a stored `copilot login` on a workstation.
This module never reads or prints a credential.
"""

import json
import os
import re

RUNTIMES = ("claude-gateway", "copilot")
RUNTIME_ALIASES = {"": "claude-gateway", "claude": "claude-gateway", "claude-code": "claude-gateway",
                   "gateway": "claude-gateway", "github-copilot": "copilot", "copilot-cli": "copilot"}
# Never left in the environment of the shell commands the agent runs.
SECRET_ENV_VARS = ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN", "ANTHROPIC_API_KEY",
                   "ANTHROPIC_CUSTOM_HEADERS", "CF_AIG_TOKEN")


def selected_runtime(environ=None):
    """The runtime named by ANVIL_RUNTIME; the gateway when it is unset."""
    raw = (environ if environ is not None else os.environ).get("ANVIL_RUNTIME", "")
    name = RUNTIME_ALIASES.get(raw.strip().lower(), raw.strip().lower())
    if name not in RUNTIMES:
        raise ValueError(f"unknown ANVIL_RUNTIME '{raw}'; use one of: {', '.join(RUNTIMES)}")
    return name


def copilot_model(model, environ=None):
    """The Copilot name of a factory model.

    The factory names models as the Anthropic API does (claude-opus-5-5);
    Copilot writes the version with a dot (claude-opus-5.5). A project can
    state the names itself in ANVIL_COPILOT_MODELS, a JSON object from
    factory model to Copilot model, which wins over the rule.
    """
    raw = (environ if environ is not None else os.environ).get("ANVIL_COPILOT_MODELS", "").strip()
    if raw:
        try:
            mapping = json.loads(raw)
        except ValueError:
            raise ValueError("ANVIL_COPILOT_MODELS is not valid JSON")
        if not isinstance(mapping, dict):
            raise ValueError("ANVIL_COPILOT_MODELS must be a JSON object")
        if model in mapping:
            return str(mapping[model])
    return re.sub(r"-(\d+)-(\d+)$", r"-\1.\2", model)


def copilot_command(prompt, model, may_write, run_dir, usage_file, environ=None):
    """The argv that runs one station through Copilot CLI.

    A producing station may use every tool. Any other station may read, run
    commands and write only inside its own run directory (its review file,
    its notes): there is no allow rule for editing the tree it is judging,
    and a non-interactive Copilot denies what no rule allows.
    """
    environ = environ if environ is not None else os.environ
    command = ["copilot", "-p", prompt, "--model", copilot_model(model, environ),
               "--silent", "--no-color", "--no-ask-user", "--no-auto-update", "--stream=off",
               # The built-in GitHub MCP server would act on GitHub with the
               # account's token; a station never needs that.
               "--disable-builtin-mcps",
               f"--usage-output-file={usage_file}",
               f"--secret-env-vars={','.join(SECRET_ENV_VARS)}"]
    if may_write:
        command.append("--allow-all-tools")
    else:
        command += ["--allow-tool=shell", "--allow-tool=read", f"--allow-tool=write({run_dir}/**)"]
    credits = str(environ.get("ANVIL_COPILOT_MAX_AI_CREDITS", "")).strip()
    if credits.isdigit():
        command.append(f"--max-ai-credits={credits}")
    return command


def _norm(key):
    return re.sub(r"[^a-z0-9]", "", str(key).lower())


_FIELDS = {
    "input_tokens": ("inputtokens", "input", "prompttokens"),
    "output_tokens": ("outputtokens", "output", "completiontokens"),
    "cached_input_tokens": ("cachereadtokens", "cachedinputtokens", "cachedtokens", "cacheread",
                            "cachereadinputtokens"),
    "cache_creation_input_tokens": ("cachewritetokens", "cachecreationtokens", "cachewrite",
                                    "cachecreationinputtokens"),
    "reasoning_tokens": ("reasoningtokens", "reasoning", "reasoningoutputtokens"),
}


def _counts(entry):
    """Token counts of one usage object, or None when it has none."""
    if not isinstance(entry, dict):
        return None
    flat = dict(entry)
    for value in entry.values():  # counts are sometimes one level down ("tokens", "usage")
        if isinstance(value, dict) and any(_norm(k) in _FIELDS["input_tokens"] for k in value):
            flat = dict(value)
            break
    found = {}
    for field, names in _FIELDS.items():
        for key, value in flat.items():
            if _norm(key) in names and isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                found[field] = value
                break
    if "input_tokens" not in found or "output_tokens" not in found:
        return None
    return found


def parse_copilot_usage(data):
    """Token usage from the file --usage-output-file writes, or None.

    The file reports tokens per model and per agent, so the same tokens
    appear in more than one breakdown. One breakdown is read, the per model
    one, and its entries are summed; totals at the top level are used when
    there is no per model breakdown. Anything that does not look like
    either yields None: usage stays unknown, it is never guessed.
    """
    if not isinstance(data, dict):
        return None
    entries = []
    for key, value in data.items():
        if "model" in _norm(key) and "agent" not in _norm(key):
            candidates = list(value.values()) if isinstance(value, dict) else value if isinstance(value, list) else []
            entries = [c for c in (_counts(item) for item in candidates) if c]
            if entries:
                break
    if not entries:
        top = _counts(data)
        entries = [top] if top else []
    if not entries:
        return None
    usage = {field: sum(e.get(field, 0) for e in entries) for field in _FIELDS}
    # Copilot's input count already includes what the prompt cache served.
    usage["input_tokens_includes_cache"] = True
    return usage


def result_envelope(stdout, usage_file):
    """One JSON envelope from the two places Copilot reports a run: the
    reply on stdout and the usage statistics file. The usage ledger parses
    this envelope (anvil/telemetry.py, provider copilot)."""
    usage = None
    try:
        with open(usage_file, encoding="utf-8") as handle:
            usage = parse_copilot_usage(json.load(handle))
    except (OSError, ValueError):
        pass
    return json.dumps({"type": "copilot_result", "result": stdout or "", "usage": usage})
