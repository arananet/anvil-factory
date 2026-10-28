import json, re
from pathlib import Path

REVIEWER_STATIONS = ["reviewer-spec", "reviewer-security", "reviewer-tests", "reviewer-architecture"]
RISK_HINTS = {"auth", "payments", "data-deletion", "production-deploy", "secrets", "publishing"}

def spec_gate(project_dir, slug):
    spec = Path(project_dir) / ".openspec" / "specs" / slug / "spec.md"
    if not spec.exists():
        return (False, f"Spec not found: {spec}")
    text = spec.read_text(encoding="utf-8")
    if "Scenario:" not in text:
        return (False, "Spec has no Scenario: line")
    if "Status:" not in text:
        return (False, "Spec has no Status line")
    return (True, "Spec present with scenarios and status")

def scenario_ids(project_dir, slug):
    spec = Path(project_dir) / ".openspec" / "specs" / slug / "spec.md"
    if not spec.exists():
        return []
    text = spec.read_text(encoding="utf-8")
    ids = []
    for m in re.finditer(r"\b(S\d+)\b", text):
        if m.group(1) not in ids:
            ids.append(m.group(1))
    return ids

def tdd_gate(project_dir, slug):
    ids = scenario_ids(project_dir, slug)
    if not ids:
        return (False, "No scenario ids found in spec")
    tests_dir = Path(project_dir) / "tests"
    if not tests_dir.is_dir():
        return (False, "No tests directory")
    combined = ""
    for f in tests_dir.rglob("*"):
        if f.is_file():
            try:
                combined += f.read_text(encoding="utf-8") + "\n"
            except UnicodeDecodeError:
                pass
    missing = [sid for sid in ids if sid not in combined]
    if missing:
        return (False, f"Scenarios without test references: {', '.join(missing)}")
    return (True, f"All {len(ids)} scenarios referenced in tests")

def review_gate(project_dir, slug):
    base = Path(project_dir) / "reviews" / slug
    for station in REVIEWER_STATIONS:
        f = base / f"{station}.json"
        if not f.exists():
            return (False, f"Missing review: {f}")
        data = json.loads(f.read_text(encoding="utf-8"))
        if data.get("verdict") != "pass":
            return (False, f"Review {station} verdict is {data.get('verdict')}, not pass")
    return (True, "All 4 reviews present and passing")

def human_gate(work_order):
    hints = set(getattr(work_order, "risk_hints", []) or [])
    if isinstance(work_order, dict):
        hints = set(work_order.get("risk_hints", []))
    return "required" if hints & RISK_HINTS else "not_required"


def brief_gate(project_dir, slug):
    brief = Path(project_dir) / "content" / slug / "brief.md"
    if not brief.exists():
        return (False, f"Brief not found: {brief}")
    text = brief.read_text(encoding="utf-8")
    for field in ("Audience:", "Angle:", "Claims:"):
        if field not in text:
            return (False, f"Brief is missing {field}")
    return (True, "Brief present with audience, angle and claims")

def disclosure_gate(project_dir, slug):
    draft = Path(project_dir) / "content" / slug / "draft.md"
    if not draft.exists():
        return (False, f"Draft not found: {draft}")
    text = draft.read_text(encoding="utf-8").lower()
    if "ai generated" not in text and "ai-generated" not in text:
        return (False, "Draft has no AI generated disclosure")
    return (True, "Draft carries an AI generated disclosure")
