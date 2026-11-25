"""Live progress sinks (spec: live-progress-sinks).

A sink is a consumer of the run state record (schema anvil/run-state@1).
The recorder in anvil/observe.py calls every configured sink once per state
write, before state.json is written, so a run can be watched from outside
while it runs. Two ship:

- github-issue: one comment on the work order's issue, created at the first
  call and edited at every later one, found again by a hidden marker that
  carries the run id.
- github-project: the status of the issue's item on a GitHub Projects (v2)
  board, set when the run's phase changes. It never changes the board's
  shape: a missing project, field or option makes it inactive for the run.

Sinks run in the line process and read their token from its environment at
call time; the token goes into the Authorization header and nowhere else.
A sink failure never decides a run: the caller records a short note
("<type>: <ExceptionClassName>" or "<type>: HTTP <status>") and goes on.
Standard library only.
"""

import json
import os
import re
import urllib.error
import urllib.request

SINK_TYPES = ("github-issue", "github-project")
DEFAULT_TOKEN_ENV = "GH_TOKEN"
# Phase name -> default option name on the project board (R3.2).
PHASES = {"intake": "Intake", "spec": "Spec", "build": "Build", "checks": "Checks", "review": "Review",
          "human": "Needs human", "done": "Done", "failed": "Failed"}
# Keys each sink type accepts besides "type" (R2.1, R3.1); anvil/config.py validates against these.
ALLOWED_KEYS = {
    "github-issue": {"token_env"},
    "github-project": {"owner", "number", "owner_type", "status_field", "token_env", "columns"},
}
REQUIRED_KEYS = {"github-issue": set(), "github-project": {"owner", "number"}}
WO_GH = re.compile(r"^wo-gh-([0-9]+)$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class SinkInactive(Exception):
    """The sink cannot serve this run; the message is its fixed reason."""


class GraphQLError(Exception):
    """A GraphQL response carried errors and no usable data."""


def api_base():
    return (os.environ.get("GITHUB_API_URL") or "https://api.github.com").rstrip("/")


def note_for(sink_type, exc):
    """The export error text for a failed call: never a message, URL or body."""
    if isinstance(exc, urllib.error.HTTPError):
        return f"{sink_type}: HTTP {exc.code}"
    return f"{sink_type}: {type(exc).__name__}"


def issue_target(work_order_id, token_env):
    """(repository, issue number) or SinkInactive with the R2.2 reason, checked in order."""
    match = WO_GH.match(str(work_order_id or ""))
    if not match:
        raise SinkInactive("work order id is not wo-gh-<number>")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not REPOSITORY.match(repo):
        raise SinkInactive("GITHUB_REPOSITORY is not set")
    if not os.environ.get(token_env):
        raise SinkInactive(f"{token_env} is not set")
    return repo, int(match.group(1))


class Sink:
    """One configured sink: activation at its first call, then one delivery per state write."""

    type = ""

    def __init__(self, entry, timeout):
        self.entry = entry
        self.timeout = timeout
        self.token_env = str(entry.get("token_env") or DEFAULT_TOKEN_ENV)
        self.active = True
        self.reason = None
        self.started = False

    def status(self):
        return {"type": self.type, "active": self.active, "reason": self.reason}

    def call(self, record):
        """Deliver one state record; returns a note to record, or None. Raises on a failed request."""
        if not self.active:
            return
        if not self.started:
            try:
                self.start(record)
            except SinkInactive as exc:
                self.active, self.reason = False, str(exc)
                return
            self.started = True
        return self.deliver(record)

    def deactivate(self, note):
        """Stop for the rest of the run with a reason that is also an export error (R3.5)."""
        self.active, self.reason = False, note
        return note

    # http -------------------------------------------------------------
    def request(self, method, url, payload=None, accept="application/vnd.github+json"):
        """One HTTP request with the token in the Authorization header. Returns (json, headers)."""
        if not url.lower().startswith(("https://", "http://")):
            raise ValueError("sink url must be http or https")
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {os.environ.get(self.token_env, '')}")
        req.add_header("Accept", accept)
        req.add_header("User-Agent", "anvil-progress")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            response = urllib.request.urlopen(req, timeout=self.timeout)
        except urllib.error.HTTPError as exc:
            # An HTTPError holds the open response; close it so a failing API does not
            # leak one socket per state write. The caller records only the status (R1.5).
            exc.close()
            raise
        with response:
            raw = response.read()
            return (json.loads(raw.decode("utf-8")) if raw else None), response.headers


# -- github-issue -------------------------------------------------------------

def _station_rows(record):
    """One (station, status, attempt, tokens) row per station in pipeline order (R2.5)."""
    running = record.get("state") == "running"
    steps = [s for s in record.get("steps") or [] if isinstance(s, dict)]
    rows = []
    for station in record.get("stations") or []:
        own = [s for s in steps if s.get("station") == station]
        settled = [s for s in own if s.get("status") != "loopback"]
        if running and station == record.get("current_station"):
            status = "running"
        elif settled:
            raw = str(settled[-1].get("status"))
            status = {"executed": "done", "not_run": "not run"}.get(raw, raw)
        else:
            status = "pending" if running else "not run"
        # The runner stamps attempt only from the second attempt on: an unstamped step is attempt 1.
        attempts = [s["attempt"] if isinstance(s.get("attempt"), int) else 1 for s in settled]
        tokens = [s["total_tokens"] for s in own if isinstance(s.get("total_tokens"), int)]
        rows.append((station, status, str(max(attempts)) if attempts else "-",
                     str(sum(tokens)) if tokens else "-"))
    return rows


def render_issue_comment(record):
    """The comment body for a state record: scalar facts only (R2.5, R2.6)."""
    lines = [f"<!-- anvil-progress run_id={record.get('run_id')} -->",
             f"### ANVIL progress: {record.get('work_order_id')}", "",
             f"Pipeline: {record.get('pipeline')}", "", f"State: {record.get('state')}", ""]
    if record.get("verdict") is not None:
        lines += [f"Verdict: {record.get('verdict')}", ""]
    if record.get("exit_status") is not None:
        lines += [f"Exit status: {record.get('exit_status')}", ""]
    lines += ["| Station | Status | Attempt | Tokens |", "| --- | --- | --- | --- |"]
    lines += [f"| {station} | {status} | {attempt} | {tokens} |"
              for station, status, attempt, tokens in _station_rows(record)]
    usage = record.get("token_usage") or {}
    total = usage.get("total_tokens")
    cost = record.get("cost")
    estimate = record.get("runtime_cost_estimate_usd")
    if isinstance(cost, (int, float)):
        cost_line = f"Cost: ${cost:.4f}"
    elif isinstance(estimate, (int, float)):
        cost_line = f"Cost: about ${estimate:.2f} (the runtime's own estimate, not an invoice)"
    else:
        cost_line = "Cost: not priced"
    budget = usage.get("budget_tokens")
    lines += ["", f"Loopbacks: {record.get('loopbacks') or 0}", "",
              f"Tokens: {total if isinstance(total, int) else 'unmeasured'}", ""]
    if isinstance(budget, int):
        lines += [f"Budget tokens: {budget} (cache reads weighed down, the figure the limits read)", ""]
    lines += [cost_line, "", f"Updated: {record.get('updated_at')}"]
    run_id = os.environ.get("GITHUB_RUN_ID")
    if run_id:
        server = (os.environ.get("GITHUB_SERVER_URL") or "https://github.com").rstrip("/")
        lines += ["", f"Workflow run: {server}/{os.environ.get('GITHUB_REPOSITORY')}/actions/runs/{run_id}"]
    return "\n".join(lines) + "\n"


def _next_link(headers):
    for part in (headers.get("Link") or "").split(","):
        match = re.match(r'\s*<([^>]+)>\s*;\s*rel="next"', part)
        if match:
            return match.group(1)
    return None


class GitHubIssueSink(Sink):
    """One live comment on the work order's issue (R2)."""

    type = "github-issue"

    def start(self, record):
        self.repo, self.number = issue_target(record.get("work_order_id"), self.token_env)
        self.comment_id = None

    def deliver(self, record):
        base = api_base()
        body = render_issue_comment(record)
        if self.comment_id is None:
            self.comment_id = self._find_comment(base, f"<!-- anvil-progress run_id={record.get('run_id')} -->")
        if self.comment_id is None:
            created, _ = self.request("POST", f"{base}/repos/{self.repo}/issues/{self.number}/comments",
                                      {"body": body})
            comment_id = (created or {}).get("id")
            if not isinstance(comment_id, int):
                raise ValueError("comment creation returned no id")
            self.comment_id = comment_id
            return
        self.request("PATCH", f"{base}/repos/{self.repo}/issues/comments/{self.comment_id}", {"body": body})

    def _find_comment(self, base, marker):
        """The id of the first comment carrying this run's marker, across every page."""
        url = f"{base}/repos/{self.repo}/issues/{self.number}/comments?per_page=100"
        while url:
            page, headers = self.request("GET", url)
            for comment in page if isinstance(page, list) else []:
                if isinstance(comment, dict) and marker in str(comment.get("body") or ""):
                    return comment.get("id")
            url = _next_link(headers)
            if url and not url.startswith(base + "/"):
                break  # the token only goes to the configured API host
        return None


# -- github-project -----------------------------------------------------------

def station_phase(station, previous):
    if station == "intake":
        return "intake"
    if station == "spec-writer":
        return "spec"
    if station in ("test-writer", "builder"):
        return "build"
    if station == "checks-gate":
        return "checks"
    if station == "approver" or str(station).startswith("reviewer-"):
        return "review"
    if station == "triage-human":
        return "human"
    if station in ("deployer", "observer"):
        return previous
    return "build"


def record_phase(record, previous=None):
    """The board phase a state record stands for (R3.3)."""
    if record.get("state") == "running":
        station = record.get("current_station")
        if station is None:
            steps = record.get("steps") or []
            if not steps:
                return "intake"
            station = steps[-1].get("station")
        return station_phase(station, previous) or "build"
    exit_status = record.get("exit_status")
    if record.get("state") in ("crashed", "stalled") or (exit_status is not None and exit_status != "completed"):
        return "failed"
    if record.get("human_required") is True:
        return "human"
    if record.get("verdict") == "approved":
        return "done"
    return "failed"


PROJECT_QUERY = """query($owner: String!, $number: Int!, $field: String!) {
  %s(login: $owner) {
    projectV2(number: $number) {
      id
      field(name: $field) { ... on ProjectV2SingleSelectField { id name options { id name } } }
    }
  }
}"""
ISSUE_QUERY = """query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    issue(number: $number) { id projectItems(first: 100) { nodes { id project { id } } } }
  }
}"""
ADD_ITEM = """mutation($project: ID!, $content: ID!) {
  addProjectV2ItemById(input: {projectId: $project, contentId: $content}) { item { id } }
}"""
SET_STATUS = """mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
  updateProjectV2ItemFieldValue(input: {projectId: $project, itemId: $item, fieldId: $field,
    value: {singleSelectOptionId: $option}}) { projectV2Item { id } }
}"""


class GitHubProjectSink(Sink):
    """The status of the issue's item on a Projects v2 board (R3)."""

    type = "github-project"

    def __init__(self, entry, timeout):
        super().__init__(entry, timeout)
        self.owner = str(entry.get("owner"))
        self.project_number = int(entry.get("number"))
        self.owner_type = "organization" if entry.get("owner_type") == "organization" else "user"
        self.status_field = str(entry.get("status_field") or "Status")
        self.columns = dict(PHASES, **(entry.get("columns") or {}))
        self.phase = None
        self.board = None  # {"project", "field", "options", "item"} once looked up

    def start(self, record):
        self.repo, self.number = issue_target(record.get("work_order_id"), self.token_env)

    def graphql(self, query, variables):
        url = os.environ.get("GITHUB_GRAPHQL_URL") or f"{api_base()}/graphql"
        answer, _ = self.request("POST", url, {"query": query, "variables": variables},
                                 accept="application/json")
        answer = answer if isinstance(answer, dict) else {}
        return answer.get("data") if isinstance(answer.get("data"), dict) else {}

    def deliver(self, record):
        phase = record_phase(record, self.phase)
        if phase == self.phase:
            return None
        if self.board is None:
            note = self._look_up()
            if note:
                return note
        option = self.columns[phase]
        option_id = self.board["options"].get(option)
        if option_id is None:
            return self.deactivate(f"{self.type}: option {option} not found in {self.status_field}")
        if self.board["item"] is None:
            data = self.graphql(ADD_ITEM, {"project": self.board["project"], "content": self.board["issue"]})
            item = ((data.get("addProjectV2ItemById") or {}).get("item") or {}).get("id")
            if not item:
                raise GraphQLError()
            self.board["item"] = item
        data = self.graphql(SET_STATUS, {"project": self.board["project"], "item": self.board["item"],
                                                 "field": self.board["field"], "option": option_id})
        if not data.get("updateProjectV2ItemFieldValue"):
            raise GraphQLError()
        self.phase = phase
        return None

    def _look_up(self):
        """Find the project, its status field, the issue and its item. A note when something is missing."""
        data = self.graphql(PROJECT_QUERY % self.owner_type,
                                    {"owner": self.owner, "number": self.project_number, "field": self.status_field})
        project = (data.get(self.owner_type) or {}).get("projectV2")
        if not isinstance(project, dict) or not project.get("id"):
            return self.deactivate(f"{self.type}: project {self.owner}/{self.project_number} not found")
        field = project.get("field")
        if not isinstance(field, dict) or not field.get("id") or not isinstance(field.get("options"), list):
            return self.deactivate(f"{self.type}: field {self.status_field} not found")
        owner, repo = self.repo.split("/", 1)
        data = self.graphql(ISSUE_QUERY, {"owner": owner, "repo": repo, "number": self.number})
        issue = (data.get("repository") or {}).get("issue")
        if not isinstance(issue, dict) or not issue.get("id"):
            raise GraphQLError()
        nodes = ((issue.get("projectItems") or {}).get("nodes")) or []
        item = next((n.get("id") for n in nodes if isinstance(n, dict)
                     and (n.get("project") or {}).get("id") == project["id"]), None)
        self.board = {"project": project["id"], "field": field["id"], "issue": issue["id"], "item": item,
                      "options": {str(o.get("name")): o.get("id") for o in field["options"] if isinstance(o, dict)}}
        return None


SINK_CLASSES = {"github-issue": GitHubIssueSink, "github-project": GitHubProjectSink}


class SinkSet:
    """The configured sinks of one run, called in list order at every state write."""

    def __init__(self, entries, timeout):
        self.sinks = [SINK_CLASSES[e["type"]](e, timeout) for e in entries or []
                      if isinstance(e, dict) and e.get("type") in SINK_CLASSES]

    def deliver(self, record, export_errors):
        """Call every sink with the record; append new notes to export_errors. Returns the sinks field."""
        for sink in self.sinks:
            try:
                note = sink.call(record)
            except Exception as exc:  # a sink never decides a run
                note = note_for(sink.type, exc)
            if note and note not in export_errors:
                export_errors.append(note)
        return [sink.status() for sink in self.sinks]
