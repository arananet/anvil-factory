import json
import os
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
    "supervisor": "reasoning-strong",
}

# model-migration R10: tier resolution at hand-off. Station definitions and
# routing speak in abstract tier labels; the runtime dispatcher only knows
# concrete models. This one total map resolves every label the runner can
# produce. A value that is already concrete passes through unchanged; any
# other value also passes through so the dispatcher fails on it loudly.
MODEL_TIER_MAP = {
    "review-cheap": "claude-sonnet-5-5",
    "review-balanced": "claude-sonnet-5-5",
    "review-strong": "claude-sonnet-5-5",
    "fast-builder": "claude-opus-5-5",
    "reasoning-strong": "claude-opus-5-5",
    "writing-strong": "claude-sonnet-5-5",
    "fast-reader": "claude-sonnet-5-5",
    "media-gen": "claude-sonnet-5-5",
    "default": "claude-sonnet-5-5",
}

CONCRETE_MODELS = ("claude-opus-5-5", "claude-sonnet-5-5")


def resolve_model(label):
    """Resolve a tier label to its concrete model (R10); concrete values pass through."""
    if label is None:
        return None
    return MODEL_TIER_MAP.get(label, label)

# S1: Token estimator constant (visible in config per spec)
CHARS_PER_TOKEN = 3.5

# S1: Factory defaults for packet budgets
DEFAULT_STATION_BUDGETS = {
    "builder": 50000,
    "writer": 50000,
    "media-producer": 50000,
    "brief-writer": 50000,
    "reviewer-design": 50000,
}

# S2: Factory default for contact sheet max width
DEFAULT_CONTACT_SHEET_MAX_WIDTH = 1600

# station-timeout (decision 0011): the wall clock one station invocation may
# use before the wrapper kills it. Resolution order: the environment variable
# ANVIL_STATION_TIMEOUT_SECONDS, then runtime.station_timeout_seconds in
# anvil.yaml (the executor hands it to the wrapper through that same
# variable), then the station class default below. No path exceeds the
# ceiling: a larger value is clamped to it so a runaway station still dies.
STATION_TIMEOUT_ENV = "ANVIL_STATION_TIMEOUT_SECONDS"
STATION_TIMEOUT_CEILING = 7200
PRODUCING_STATION_TIMEOUT = 3600
DEFAULT_STATION_TIMEOUT = 1500
# Margin the command executor keeps above the station timeout, so the wrapper
# is the binding cap and writes its timeout record before the executor kills it.
EXECUTOR_TIMEOUT_MARGIN = 60
DEFAULT_EXECUTOR_TIMEOUT = 300
# SYNC: the same eight ids as WRITE_STATIONS in tools/claude_station.py
# (tests/test_station_timeout_config.py checks that the two agree).
PRODUCING_STATIONS = frozenset({"builder", "test-writer", "spec-writer", "blueprint",
                                "brief-writer", "researcher", "writer", "media-producer"})


def parse_station_timeout(raw, source):
    """Validate one configured timeout value; returns (seconds, requested).

    seconds is clamped to STATION_TIMEOUT_CEILING; requested is the value as
    configured. A non integer or non positive value raises ValueError naming
    the value and where it came from.
    """
    if isinstance(raw, bool):
        raise ValueError(f"{source} must be a positive integer number of seconds, got {raw!r}")
    try:
        requested = int(str(raw).strip())
    except ValueError:
        raise ValueError(f"{source} must be a positive integer number of seconds, got {raw!r}") from None
    if requested <= 0:
        raise ValueError(f"{source} must be a positive integer number of seconds, got {raw!r}")
    return min(requested, STATION_TIMEOUT_CEILING), requested


def station_class_default(station):
    return PRODUCING_STATION_TIMEOUT if station in PRODUCING_STATIONS else DEFAULT_STATION_TIMEOUT


def resolve_station_timeout(station, environ=None, configured=None):
    """Resolve the timeout for one station: {"seconds", "requested", "source"}."""
    environ = os.environ if environ is None else environ
    raw = environ.get(STATION_TIMEOUT_ENV)
    if raw is not None and str(raw).strip() != "":
        seconds, requested = parse_station_timeout(raw, STATION_TIMEOUT_ENV)
        return {"seconds": seconds, "requested": requested, "source": STATION_TIMEOUT_ENV}
    if configured is not None:
        seconds, requested = parse_station_timeout(configured, "runtime.station_timeout_seconds")
        return {"seconds": seconds, "requested": requested, "source": "runtime.station_timeout_seconds"}
    default = station_class_default(station)
    return {"seconds": default, "requested": default, "source": "class default"}


def station_timeout_seconds(station, environ=None, configured=None):
    """The effective timeout in seconds for one station (see resolve_station_timeout)."""
    return resolve_station_timeout(station, environ, configured)["seconds"]


def effective_executor_timeout(configured, environ=None, station_configured=None):
    """The command executor timeout: never lower than the largest station
    timeout in effect plus EXECUTOR_TIMEOUT_MARGIN.

    configured is runtime.timeout_seconds (None when unset); station_configured
    is runtime.station_timeout_seconds.
    """
    base = DEFAULT_EXECUTOR_TIMEOUT if configured is None else int(configured)
    # An override applies to every station alike, and without one the
    # producing default is the larger class default, so a producing station
    # always resolves to the largest timeout in effect.
    largest = station_timeout_seconds("builder", environ, station_configured)
    return max(base, largest + EXECUTOR_TIMEOUT_MARGIN)


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

def health_config(config):
    if not isinstance(config, dict):
        return None
    health = config.get("health")
    return health if isinstance(health, dict) else None

def build_default_config(station_ids):
    from .telemetry import DEFAULT_EFFICIENCY
    stations = {}
    for sid in station_ids:
        stations[sid] = {
            "context": ["brain/project.md", ".openspec/specs/"],
            "model": default_model(sid),
            "prompt": f"stations/{sid}/PROMPT.md",
            "tools": [],
        }
    return {"version": 1, "efficiency": dict(DEFAULT_EFFICIENCY), "stations": stations}

def render_anvil_yaml(station_ids):
    # JSON is valid YAML, so this file is both machine simple and YAML legal.
    return json.dumps(build_default_config(station_ids), indent=2) + "\n"

def get_station_budget(config, station_id):
    """S1: Get the budget for a station, using factory defaults as fallback."""
    if not isinstance(config, dict):
        return DEFAULT_STATION_BUDGETS.get(station_id, 50000)

    budgets = config.get("station_budgets", {})
    if not isinstance(budgets, dict):
        return DEFAULT_STATION_BUDGETS.get(station_id, 50000)

    return budgets.get(station_id, DEFAULT_STATION_BUDGETS.get(station_id, 50000))

def get_contact_sheet_max_width(config):
    """S2: Get contact sheet max width from config."""
    if not isinstance(config, dict):
        return DEFAULT_CONTACT_SHEET_MAX_WIDTH

    return config.get("contact_sheet_max_width", DEFAULT_CONTACT_SHEET_MAX_WIDTH)
