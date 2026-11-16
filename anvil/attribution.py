"""ANVIL attribution: the default wording and the deterministic deliverable check.

Spec: .openspec/specs/attribution-default/spec.md (R1, R4). Decision:
brain/decisions/0012-anvil-attribution-default.md. This module is the one
source of the default line; scaffold, onboard and the checks gate read it here.
"""
import re
from html.parser import HTMLParser
from pathlib import Path

DEFAULT_LINE = "Made with ANVIL, an open source software factory."
LANDING_URL = "https://anvil-landing-7x1.pages.dev"
EXCEPTION_PREFIX = "Attribution exception: approved by "
_EXCEPTION_RE = re.compile(r"^Attribution exception: approved by (\S.*?) on (\d{4}-\d{2}-\d{2}): (\S.*)$")

# A bespoke credit counts only when the sentence says ANVIL built or made the
# project ("built end to end by ANVIL", "Made with ANVIL", "ANVIL built this").
_VERBS = r"(?:built|made|designed|created|developed|produced|crafted|generated|shipped)"
_CREDIT_RES = (
    re.compile(rf"\b{_VERBS}\b[^.!?]{{0,80}}?\b(?:by|with|using)\s+ANVIL\b", re.IGNORECASE),
    re.compile(rf"\bANVIL\s+(?:has\s+)?{_VERBS}\b", re.IGNORECASE),
)
# Candidate deliverable directories in layout order; the first that holds HTML is checked.
_DELIVERABLE_DIRS = ("public", "dist", ".")

REQUIREMENT_TEXT = (
    "## ANVIL attribution\n"
    "Every page this project ships carries a visible ANVIL attribution by default, "
    "placed in the page footer or an equivalent visible spot. On a game surface it sits "
    "in a credits or footer element outside the canvas and the input handling region, so "
    "it never breaks gameplay. Default text, exact:\n\n"
    f"    {DEFAULT_LINE}\n\n"
    f"linked to the ANVIL landing {LANDING_URL} (the factory repository link is an "
    "accepted alternative target). A bespoke credit that names ANVIL as the builder is "
    "compliant and is kept, never replaced by the default line. The only way to ship "
    "without it is an owner approved exception recorded in the project spec as a line "
    f"of the form `{EXCEPTION_PREFIX}<owner> on <YYYY-MM-DD>: <reason>`. The factory "
    "checks gate fails a web deliverable that carries no attribution naming ANVIL.\n"
)


class _VisibleText(HTMLParser):
    """Collects text nodes, skipping script, style and template content.

    Comments and attribute values never reach handle_data, so they do not count.
    """
    _HIDDEN = {"script", "style", "template", "noscript"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self._hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._HIDDEN:
            self._hidden_depth += 1

    def handle_endtag(self, tag):
        if tag in self._HIDDEN and self._hidden_depth:
            self._hidden_depth -= 1

    def handle_data(self, data):
        if not self._hidden_depth:
            self.parts.append(data)


def visible_text(html):
    parser = _VisibleText()
    parser.feed(html)
    parser.close()
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def carries_attribution(html):
    """True when the visible text holds the default line or a credit naming ANVIL as builder."""
    text = visible_text(html)
    if DEFAULT_LINE in text:
        return True
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if "ANVIL" in sentence and any(r.search(sentence) for r in _CREDIT_RES):
            return True
    return False


def find_deliverable(project_dir):
    """Return the HTML files of the web deliverable to check, or [] when there is none.

    The index page of the first layout directory that has one is the page
    checked. A public/ or dist/ directory without an index contributes its
    top level HTML files; the project root counts only through index.html.
    """
    root = Path(project_dir)
    for rel in _DELIVERABLE_DIRS:
        base = root / rel
        if not base.is_dir():
            continue
        index = base / "index.html"
        if index.is_file():
            return [index]
        if rel != ".":
            pages = sorted(p for p in base.glob("*.html") if p.is_file())
            if pages:
                return pages
    return []


def find_exception(project_dir, config=None):
    """Return the recorded owner exception line, or None.

    Honoured sources: a line in any .openspec/specs/*/spec.md that matches the
    exact exception form, or the attribution_exception value of the project
    configuration in the same form. Anything looser is not an exception.
    """
    configured = (config or {}).get("attribution_exception")
    if isinstance(configured, str) and _EXCEPTION_RE.match(configured.strip()):
        return configured.strip()
    specs = Path(project_dir) / ".openspec" / "specs"
    if specs.is_dir():
        for spec in sorted(specs.glob("*/spec.md")):
            try:
                lines = spec.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            for line in lines:
                if _EXCEPTION_RE.match(line.strip()):
                    return line.strip()
    return None


def check_attribution(project_dir, config=None):
    """Deterministic attribution check for a web deliverable (spec R4).

    Returns None when the project has no HTML deliverable (the check does not
    apply), else {"verdict": "pass"|"fail", "lines": [str]} for the gate output.
    """
    pages = find_deliverable(project_dir)
    if not pages:
        return None
    root = Path(project_dir)
    rels = [p.relative_to(root).as_posix() for p in pages]
    for page, rel in zip(pages, rels):
        try:
            html = page.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return {"verdict": "fail", "lines": [f"Attribution check failed: {rel} could not be read: {exc}."]}
        if carries_attribution(html):
            return {"verdict": "pass", "lines": [f"Attribution check passed: {rel} carries an attribution naming ANVIL."]}
    exception = find_exception(project_dir, config)
    if exception:
        return {"verdict": "pass", "lines": [
            f"Attribution check passed by recorded owner exception: {exception}",
            f"Checked without attribution: {', '.join(rels)}."]}
    return {"verdict": "fail", "lines": [
        f"Attribution check failed: missing ANVIL attribution in {', '.join(rels)}.",
        f"Add \"{DEFAULT_LINE}\" linked to {LANDING_URL} in the page footer, keep a bespoke "
        "credit naming ANVIL as the builder, or record an owner approved exception in the project spec."]}
