import json
import os
import re
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
    "supervisor": "critical-decision",
}

# model-migration R10: tier resolution at hand-off. Station definitions and
# routing speak in abstract tier labels; the runtime dispatcher only knows
# concrete models. This one total map resolves every label the runner can
# produce. A value that is already concrete passes through unchanged; any
# other value also passes through so the dispatcher fails on it loudly.
MODEL_TIER_MAP = {
    "review-cheap": "claude-opus-5-5",
    "review-balanced": "claude-opus-5-5",
    "review-strong": "claude-opus-5-5",
    "fast-builder": "claude-opus-5-5",
    "reasoning-strong": "claude-opus-5-5",
    "writing-strong": "claude-opus-5-5",
    "fast-reader": "claude-opus-5-5",
    "media-gen": "claude-opus-5-5",
    "default": "claude-opus-5-5",
    "critical-decision": "claude-fable-5-2",
}

CONCRETE_MODELS = ("claude-opus-5-5", "claude-sonnet-5-5", "claude-fable-5-2")


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
    except json.JSONDecodeError:
        data = None
    if isinstance(data, dict):
        validate_sinks(data)
        return data
    # Tiny fallback: top level keys with scalar values only, lines like "key: value"
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        result[k.strip()] = v.strip()
    return result

def validate_sinks(config):
    """live-progress-sinks R1.1, R3.1, R5.3: observability.sinks is a list of known, well formed entries.

    Raises ValueError naming observability.sinks (or the zero based entry) and
    the offending key or type. Absent or empty means no sink.
    """
    from .executor import STATION_ENV_DENY
    from .sinks import ALLOWED_KEYS, PHASES, REQUIRED_KEYS
    observability = config.get("observability")
    if not isinstance(observability, dict) or "sinks" not in observability:
        return
    sinks = observability["sinks"]
    if not isinstance(sinks, list):
        raise ValueError(f"observability.sinks must be a list of sink entries, got {type(sinks).__name__}")
    runtime = config.get("runtime") if isinstance(config.get("runtime"), dict) else {}
    keep = {str(n) for n in runtime.get("env_keep") or []}
    deny = set(STATION_ENV_DENY) | {str(n) for n in runtime.get("env_deny") or []}

    def text(value):
        return isinstance(value, str) and value.strip() != ""

    for index, entry in enumerate(sinks):
        where = f"observability.sinks[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{where} must be an object with a type, got {type(entry).__name__}")
        kind = entry.get("type")
        if kind not in ALLOWED_KEYS:
            raise ValueError(f"{where}: type {kind!r} is unknown (known: {', '.join(sorted(ALLOWED_KEYS))})")
        for key in entry:
            if key != "type" and key not in ALLOWED_KEYS[kind]:
                raise ValueError(f"{where}: key {key!r} is not allowed for type {kind}")
        for key in sorted(REQUIRED_KEYS[kind]):
            if key not in entry:
                raise ValueError(f"{where}: type {kind} requires key {key!r}")
        for key in ("owner", "status_field", "token_env"):
            if key in entry and not text(entry[key]):
                raise ValueError(f"{where}: {key} must be a non-empty string")
        if "number" in entry and (isinstance(entry["number"], bool) or not isinstance(entry["number"], int)
                                  or entry["number"] < 1):
            raise ValueError(f"{where}: number must be a positive integer")
        if "owner_type" in entry and entry["owner_type"] not in ("user", "organization"):
            raise ValueError(f"{where}: owner_type must be user or organization, got {entry['owner_type']!r}")
        if "columns" in entry:
            columns = entry["columns"]
            if not isinstance(columns, dict):
                raise ValueError(f"{where}: columns must be an object of phase to option name")
            for phase, name in columns.items():
                if phase not in PHASES:
                    raise ValueError(f"{where}: columns key {phase!r} is not a phase ({', '.join(PHASES)})")
                if not text(name):
                    raise ValueError(f"{where}: columns.{phase} must be a non-empty string")
        token_env = entry.get("token_env") or "GH_TOKEN"
        if token_env in keep or token_env not in deny:
            raise ValueError(f"{where}: token_env {token_env} would reach a station; list it in runtime.env_deny "
                             f"and not in runtime.env_keep")

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
    # live-progress-sinks R4.2: a new project's runs are visible on their issue without setup.
    return {"version": 1, "efficiency": dict(DEFAULT_EFFICIENCY),
            "observability": {"sinks": [{"type": "github-issue"}]}, "stations": stations}

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


# station-budgets-completeness R1: per-station token partitions inside the
# run cap. efficiency.station_budgets maps a station id to the tokens that
# station may consume across one run; efficiency.default_station_budget is
# the partition of a model station the map does not name. Both differ from
# the top level station_budgets key above (get_station_budget), which caps
# the size of one packet, not what a station consumes. An absent default
# leaves unnamed stations unpartitioned (bounded by max_run_tokens alone) and
# adds nothing to the worst case.
# Stations that call a model although their manifest says deterministic.
MODEL_CALLING_DETERMINISTIC = frozenset({"intake"})
# Stations treated as deterministic when no registry is given (the runner's
# own fallback for stations it does not know).
DETERMINISTIC_FALLBACK = frozenset({"approver", "triage-human", "checks-gate"})


def _positive_tokens(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer number of tokens, got {value!r}")
    return value


def station_budget_settings(config):
    """Validated (station_budgets, default_station_budget) from the efficiency section.

    Returns ({station: tokens}, default or None). A malformed map, a station
    id that is not a non empty string or a value that is not a positive
    integer raises ValueError naming the key and the station.
    """
    efficiency = config.get("efficiency") if isinstance(config, dict) else None
    efficiency = efficiency if isinstance(efficiency, dict) else {}
    raw = efficiency.get("station_budgets")
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError(f"efficiency.station_budgets must be a map from station id to tokens, got {raw!r}")
    budgets = {}
    for station, value in raw.items():
        if not isinstance(station, str) or not station.strip():
            raise ValueError(f"efficiency.station_budgets has an invalid station id {station!r}")
        budgets[station] = _positive_tokens(value, f"efficiency.station_budgets.{station}")
    default = efficiency.get("default_station_budget")
    if default is not None:
        default = _positive_tokens(default, "efficiency.default_station_budget")
    return budgets, default


def is_model_station(station_id, registry=None):
    """True when the station calls a model (agent kind, or intake)."""
    if station_id in MODEL_CALLING_DETERMINISTIC:
        return True
    if registry is not None and station_id in registry:
        return registry.get(station_id).kind == "agent"
    return station_id not in DETERMINISTIC_FALLBACK


def pipeline_partitions(config, pipeline, registry=None):
    """{station: partition} for one pipeline: named stations, then the default
    for each unnamed model station. Deterministic stations the map does not
    name (the checks gate) take no partition."""
    budgets, default = station_budget_settings(config)
    result = {}
    for station in pipeline.topological_order():
        if station in budgets:
            result[station] = budgets[station]
        elif default is not None and is_model_station(station, registry):
            result[station] = default
    return result


def validate_station_budgets(config, pipelines, registry=None):
    """Check the partition set against max_run_tokens for every pipeline (R1).

    Returns {pipeline name: worst case tokens}, the worst case being the sum
    of the pipeline's partitions (pipeline_partitions). A worst case above
    max_run_tokens raises ValueError naming each such pipeline and its
    excess; a worst case equal to the cap is accepted.
    """
    efficiency = config.get("efficiency") if isinstance(config, dict) else None
    cap = efficiency.get("max_run_tokens") if isinstance(efficiency, dict) else None
    worst = {}
    excess = []
    for pipeline in pipelines:
        total = sum(pipeline_partitions(config, pipeline, registry).values())
        worst[pipeline.name] = total
        if cap is not None and total > cap:
            excess.append(f"pipeline {pipeline.name}: worst case {total} tokens exceeds "
                          f"max_run_tokens {cap} by {total - cap}")
    if excess:
        raise ValueError("efficiency.station_budgets exceed the run cap: " + "; ".join(excess)
                         + ". Lower the partitions or the default; the run cap is the outer bound.")
    return worst


# Stop futile loops (spec stop-futile-loops R4.1, R5.2). Three deterministic
# stops, each on by default and turned off per project under efficiency. The
# defaults live here rather than in anvil/telemetry.py so the efficiency
# defaults a new project is generated with stay as they were (decision 0016).
FUTILE_LOOP_SWITCHES = ("stop_on_owner_ruling", "stop_on_no_progress", "stop_on_repeated_gate_failure")
# Lines that name a failing test: unittest FAIL: and ERROR:, pytest FAILED,
# TAP not ok as printed by node --test (indented for subtests).
DEFAULT_GATE_FAILURE_PATTERNS = (r"^FAIL:", r"^ERROR:", r"^FAILED\b", r"^\s*not ok\b")


def futile_loop_settings(config):
    """The validated stop switches and compiled gate failure patterns.

    Returns {"stop_on_owner_ruling": bool, "stop_on_no_progress": bool,
    "stop_on_repeated_gate_failure": bool, "gate_failure_patterns": [re.Pattern]}.
    A switch that is not a boolean, or gate_failure_patterns that is not a
    list of strings or holds a pattern that does not compile, raises
    ValueError naming the key; nothing falls back silently.
    """
    efficiency = (config or {}).get("efficiency") or {}
    if not isinstance(efficiency, dict):
        raise ValueError("efficiency must be an object")
    settings = {}
    for key in FUTILE_LOOP_SWITCHES:
        value = efficiency.get(key, True)
        if not isinstance(value, bool):
            raise ValueError(f"efficiency.{key} must be a boolean, got {value!r}")
        settings[key] = value
    raw = efficiency.get("gate_failure_patterns", list(DEFAULT_GATE_FAILURE_PATTERNS))
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise ValueError(f"efficiency.gate_failure_patterns must be a list of regular expression strings, "
                         f"got {raw!r}")
    compiled = []
    for item in raw:
        try:
            compiled.append(re.compile(item))
        except re.error as exc:
            raise ValueError(f"efficiency.gate_failure_patterns: pattern {item!r} does not compile ({exc})") from None
    settings["gate_failure_patterns"] = compiled
    return settings
