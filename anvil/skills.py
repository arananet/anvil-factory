"""Curated craft skills.

A skill is a short craft guide (a SKILL.md with name and description
frontmatter) that tells a producing or reviewing station what good work
looks like in one domain: architecture, design, web, gaming, content.
Promoted practices are single rules earned from run evidence; skills are
the curated baseline a station starts from before any run has taught the
project anything.

Curation is explicit. A skill reaches a packet only when the catalog
(skills/catalog.json) lists it with a scope. Nothing is discovered by
walking directories and no model takes part in the choice: resolution is
deterministic standard library code, like practice resolution.

Two catalogs compose. The factory catalog ships with ANVIL. A project may
carry its own skills/catalog.json; a project entry with the same id
replaces the factory entry, and a new id adds a skill. A project may also
name skill ids in anvil.yaml skill_overrides to switch them off.

Authority is written into every rendered section: the work order and
spec, the project design system and the promoted practices all beat a
skill.
"""

import json
from pathlib import Path

CATALOG_NAME = "catalog.json"
SCOPE_DIMENSIONS = ("stations", "surfaces", "product_types", "kinds")
# A skill is packet text. The cap keeps one skill from crowding a packet;
# the catalog check fails on a larger body instead of trimming it silently.
MAX_SKILL_CHARS = 6000

AUTHORITY_NOTE = (
    "Curated craft guidance resolved for this station and this work order. "
    "Order of authority: the work order and its spec, then the project design "
    "system and decisions, then promoted practices, then these skills. Where a "
    "skill conflicts with any of those, the skill yields. Apply what fits the "
    "work in front of you; a skill is a bar to meet, not a checklist to recite."
)


class SkillCatalogError(ValueError):
    pass


def factory_root():
    return Path(__file__).resolve().parent.parent


def _scope_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        value = value.split(",")
    return sorted({" ".join(str(v).split()).lower() for v in value if str(v).strip()})


def parse_skill_file(path):
    """Split a SKILL.md into (frontmatter dict, body). Flat key: value only."""
    text = Path(path).read_text(encoding="utf-8")
    meta = {}
    body = text
    if text.startswith("---"):
        lines = text.splitlines()
        end = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break
        if end is not None:
            for line in lines[1:end]:
                if ":" in line and not line.startswith((" ", "\t")):
                    key, value = line.split(":", 1)
                    meta[key.strip().lower()] = value.strip()
            body = "\n".join(lines[end + 1:])
    return meta, body.strip()


def _read_catalog(root):
    """Read one catalog. Returns (entries, problems); a missing catalog is empty."""
    root = Path(root)
    catalog_path = root / "skills" / CATALOG_NAME
    if not catalog_path.is_file():
        return [], []
    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"{catalog_path}: unreadable catalog: {exc}"]
    raw = data.get("skills") if isinstance(data, dict) else None
    if not isinstance(raw, list):
        return [], [f"{catalog_path}: catalog must be an object with a skills list"]
    entries, problems, seen = [], [], set()
    for item in raw:
        if not isinstance(item, dict) or not str(item.get("id", "")).strip():
            problems.append(f"{catalog_path}: every skill needs an id")
            continue
        sid = str(item["id"]).strip()
        if sid in seen:
            problems.append(f"{catalog_path}: duplicate skill id {sid}")
            continue
        seen.add(sid)
        rel = str(item.get("path") or f"skills/{sid}/SKILL.md")
        skill_path = (root / rel).resolve()
        try:
            skill_path.relative_to(root.resolve())
        except ValueError:
            problems.append(f"{sid}: path leaves the catalog root: {rel}")
            continue
        if not skill_path.is_file():
            problems.append(f"{sid}: skill file not found: {rel}")
            continue
        meta, body = parse_skill_file(skill_path)
        if not body:
            problems.append(f"{sid}: skill body is empty")
            continue
        if len(body) > MAX_SKILL_CHARS:
            problems.append(f"{sid}: skill body is {len(body)} chars, over the {MAX_SKILL_CHARS} cap")
            continue
        stations = _scope_list(item.get("stations"))
        if not stations:
            problems.append(f"{sid}: a skill must name at least one station")
            continue
        if not str(item.get("source", "")).strip():
            problems.append(f"{sid}: a curated skill must record its source")
            continue
        entries.append({
            "id": sid,
            "name": meta.get("name") or sid,
            "description": meta.get("description", ""),
            "domain": str(item.get("domain", "")).strip().lower(),
            "stations": stations,
            "surfaces": _scope_list(item.get("surfaces")),
            "product_types": _scope_list(item.get("product_types")),
            "kinds": _scope_list(item.get("kinds")),
            "source": str(item.get("source")).strip(),
            "license": str(item.get("license", "")).strip(),
            "path": rel,
            "origin": "",
            "body": body,
        })
    return entries, problems


def load_catalog(project=None, root=None):
    """The composed catalog: factory entries, then project entries by id.

    Returns (entries ordered by id, problems). Malformed entries are
    reported and never resolve.
    """
    base = Path(root) if root is not None else factory_root()
    entries, problems = _read_catalog(base)
    by_id = {}
    for e in entries:
        e["origin"] = "factory"
        by_id[e["id"]] = e
    if project is not None and Path(project).resolve() != base.resolve():
        extra, extra_problems = _read_catalog(project)
        problems += extra_problems
        for e in extra:
            e["origin"] = "project"
            by_id[e["id"]] = e
    return [by_id[k] for k in sorted(by_id)], problems


def check_skills(project=None, root=None):
    """Catalog problems as a list of strings; empty means the catalog is sound."""
    return load_catalog(project, root)[1]


def _matches(entry, signals):
    """Conjunctive across dimensions, disjunctive within, empty unrestricted."""
    for dim in SCOPE_DIMENSIONS:
        wanted = entry.get(dim) or []
        if wanted and not set(wanted) & set(signals.get(dim) or []):
            return False
    return True


def skill_signals(project, work_order):
    """The work order signals skills match on, besides the station.

    Product type: a declaration (in the work order or by the project)
    always counts. Loose keywords in the description count only when the
    work is on the ui surface, where an undeclared type means interface.
    A long backend order that mentions a dashboard is not interface work.
    """
    from .quality import detect_product_type
    surfaces = _scope_list(getattr(work_order, "surfaces", None) or [])
    product_type = detect_product_type(work_order, project, keywords=False)
    if product_type is None and "ui" in surfaces:
        product_type = detect_product_type(work_order, project) or "interface"
    return {
        "surfaces": surfaces,
        "product_types": [product_type] if product_type else [],
        "kinds": _scope_list([getattr(work_order, "kind", "") or ""]),
    }


def resolve_skills(project, work_order, station_ids, config=None, root=None):
    """The skills each station of a work order receives.

    Returns {"resolved": {station: [ids]}, "disabled": [ids],
    "catalog_count": n, "signals": {...}, "problems": [...]}.
    """
    config = config or {}
    entries, problems = load_catalog(project, root)
    overrides = config.get("skill_overrides") or []
    if isinstance(overrides, str):
        overrides = [overrides]
    overrides = {str(s).strip() for s in overrides if str(s).strip()}
    disabled = sorted(e["id"] for e in entries if e["id"] in overrides)
    candidates = [e for e in entries if e["id"] not in overrides]
    base_signals = skill_signals(project, work_order)
    resolved = {}
    for station in station_ids:
        signals = dict(base_signals, stations=[str(station).lower()])
        resolved[station] = [e["id"] for e in candidates if _matches(e, signals)]
    return {"resolved": resolved, "disabled": disabled, "catalog_count": len(entries),
            "signals": base_signals, "problems": problems}


def skills_by_id(project=None, root=None):
    return {e["id"]: e for e in load_catalog(project, root)[0]}


def packet_skills_section(resolution, station_id, entries):
    """The Craft skills section for one station, or "" when none resolved."""
    ids = (resolution or {}).get("resolved", {}).get(station_id, [])
    chosen = [entries[i] for i in ids if i in entries]
    if not chosen:
        return ""
    lines = ["## Craft skills", "", AUTHORITY_NOTE, ""]
    for e in chosen:
        lines.append(f"### Skill: {e['name']}")
        lines.append("")
        lines.append(e["body"])
        lines.append("")
    return "\n".join(lines).rstrip()


def public_resolution(resolution):
    """The resolution as recorded in report.json and the routing record."""
    resolution = resolution or {}
    return {"resolved": dict(resolution.get("resolved", {})),
            "disabled": list(resolution.get("disabled", [])),
            "catalog_count": int(resolution.get("catalog_count", 0)),
            "signals": dict(resolution.get("signals", {}))}
