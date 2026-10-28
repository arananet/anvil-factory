import json
from pathlib import Path

# anvil.yaml is written as JSON, which is valid YAML 1.2. That choice keeps the
# parser in the standard library with no extra dependency. The loader also
# accepts a tiny flat subset fallback for hand edits described in the docs.

DEFAULT_MODELS = {
    "blueprint": "reasoning-strong",
    "spec-writer": "reasoning-strong",
    "test-writer": "reasoning-strong",
    "builder": "fast-builder",
    "scout": "fast-reader",
    "brief-writer": "reasoning-strong",
    "researcher": "fast-reader",
    "writer": "writing-strong",
    "media-producer": "media-gen",
}

def default_model(station_id):
    if station_id in DEFAULT_MODELS:
        return DEFAULT_MODELS[station_id]
    if station_id.startswith("reviewer-"):
        return "review-balanced"
    if station_id in {"deployer", "observer", "publisher"}:
        return "review-balanced"
    return "default"

def load_anvil_config(path):
    p = Path(path)
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    # Tiny fallback: top level keys with scalar values only, lines like "key: value"
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        result[k.strip()] = v.strip()
    return result

def station_overrides(config):
    if not isinstance(config, dict):
        return {}
    stations = config.get("stations", {})
    return stations if isinstance(stations, dict) else {}

def apply_overrides(registry, config):
    overrides = station_overrides(config)
    for station_id, override in overrides.items():
        if station_id not in registry or not isinstance(override, dict):
            continue
        station = registry.get(station_id)
        if "context" in override:
            station.context = list(override["context"])
        if "model" in override:
            station.model = str(override["model"])
        if "prompt" in override:
            station.prompt_path = str(override["prompt"])
            # If the override prompt file exists relative to a project, caller may load it.
            # The registry keeps the path; prompt text stays as the station default unless loaded.
        if "tools" in override:
            station.tools = list(override["tools"])
    return registry

def runtime_config(config):
    if not isinstance(config, dict):
        return None
    runtime = config.get("runtime")
    return runtime if isinstance(runtime, dict) else None

def deploy_config(config):
    if not isinstance(config, dict):
        return None
    deploy = config.get("deploy")
    return deploy if isinstance(deploy, dict) else None

def build_default_config(station_ids):
    stations = {}
    for sid in station_ids:
        stations[sid] = {
            "context": ["brain/project.md", ".openspec/specs/"],
            "model": default_model(sid),
            "prompt": f"stations/{sid}/PROMPT.md",
            "tools": [],
        }
    return {"version": 1, "stations": stations}

def render_anvil_yaml(station_ids):
    # JSON is valid YAML, so this file is both machine simple and YAML legal.
    return json.dumps(build_default_config(station_ids), indent=2) + "\n"
