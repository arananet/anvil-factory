"""Live progress sinks: the github-project sink (spec: live-progress-sinks, wo-gh-47, R3).

Scripted sdlc-default runs through the real runner, with GITHUB_GRAPHQL_URL and
GITHUB_API_URL pointed at a local collector that plays a GitHub Projects v2 board.

Interface these tests pin where the spec leaves names to the builder:
  requests are GraphQL POSTs of {"query": ..., "variables": {...}};
  a request whose text holds "addProjectV2ItemById" adds the issue,
  "updateProjectV2ItemFieldValue" sets the status (the option id appears in the
  query or its variables), and any other mutation is a change to the project's
  shape, which the sink must never send;
  every other request is a lookup, answered with one document that carries the
  common Projects v2 lookups at once: user/organization.projectV2 (id, title,
  field(name:), fields.nodes, items.nodes with content), and
  repository.issue (id, number, projectItems.nodes with project.id).

Scenario map:
  S5  (test e)  test_s5_status_changes_only_when_the_phase_changes
  S6  (test e)  test_s6_missing_option_names_it_and_goes_inactive,
                test_s6_missing_project_names_it_and_goes_inactive
  S16           test_s16_unset_projects_token_makes_no_call
                test_s16_projects_token_never_written
"""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_live_progress_sinks import REPO, Collector, github_env, make_project, run_line  # noqa: E402

PROJECT_ID = "PVT_project_3"
ISSUE_ID = "I_issue_904"
ITEM_ID = "PVTI_item_1"
FIELD_ID = "PVTSSF_status"
DEFAULT_OPTIONS = ["Intake", "Spec", "Build", "Checks", "Review", "Needs human", "Done", "Failed"]
TOKEN_ENV = "ANVIL_PROJECTS_TOKEN"
SINK = {"type": "github-project", "owner": "acme", "number": 3, "token_env": TOKEN_ENV}


def option_id(name):
    return "OPT_" + str(DEFAULT_OPTIONS.index(name) + 1) if name in DEFAULT_OPTIONS else "OPT_x"


class Board:
    """A Projects v2 board behind a fake GraphQL endpoint."""

    def __init__(self, options=DEFAULT_OPTIONS, exists=True, issue_in_project=False):
        self.options = list(options)
        self.exists = exists
        self.in_project = issue_in_project
        self.requests = []

    def field(self):
        return {"__typename": "ProjectV2SingleSelectField", "id": FIELD_ID, "name": "Status",
                "dataType": "SINGLE_SELECT",
                "options": [{"id": option_id(name), "name": name} for name in self.options]}

    def item(self):
        return {"id": ITEM_ID, "project": {"id": PROJECT_ID, "number": 3},
                "content": {"__typename": "Issue", "id": ISSUE_ID, "number": 904}}

    def answer(self, request):
        text = json.dumps(request)
        self.requests.append(request)
        if "addProjectV2ItemById" in text:
            self.in_project = True
            return {"data": {"addProjectV2ItemById": {"item": {"id": ITEM_ID}}}}
        if "updateProjectV2ItemFieldValue" in text:
            return {"data": {"updateProjectV2ItemFieldValue": {"projectV2Item": {"id": ITEM_ID}}}}
        if re.search(r"\bmutation\b", str(request.get("query", ""))):
            return {"errors": [{"message": "this board does not accept that mutation"}]}
        items = [self.item()] if self.in_project else []
        project = None
        if self.exists:
            project = {"id": PROJECT_ID, "number": 3, "title": "Line board", "field": self.field(),
                       "fields": {"nodes": [{"__typename": "ProjectV2Field", "id": "PVTF_title", "name": "Title"},
                                            self.field()], "pageInfo": {"hasNextPage": False}},
                       "items": {"nodes": items, "pageInfo": {"hasNextPage": False}}}
        owner = {"id": "U_acme", "login": "acme", "projectV2": project}
        return {"data": {"user": owner, "organization": owner, "repositoryOwner": owner,
                         "repository": {"id": "R_demo", "issue": {
                             "id": ISSUE_ID, "number": 904,
                             "projectItems": {"nodes": items, "pageInfo": {"hasNextPage": False}}}}}}

    # views
    def kinds(self):
        out = []
        for request in self.requests:
            text = json.dumps(request)
            if "addProjectV2ItemById" in text:
                out.append("add")
            elif "updateProjectV2ItemFieldValue" in text:
                out.append("update")
            elif re.search(r"\bmutation\b", str(request.get("query", ""))):
                out.append("other-mutation")
            else:
                out.append("lookup")
        return out

    def status_options(self):
        names = {option_id(name): name for name in DEFAULT_OPTIONS}
        out = []
        for request in self.requests:
            text = json.dumps(request)
            if "updateProjectV2ItemFieldValue" in text:
                ids = set(re.findall(r"OPT_\d+", text))
                out.append(names.get(ids.pop()) if len(ids) == 1 else sorted(ids))
        return out


def project_run(tmp, board, wo_id="wo-gh-904", token="ghp_projects_token_47", verdicts=None,
                max_loopbacks=0, name="proj"):
    with Collector(project=board) as api:
        project = make_project(tmp, sinks=[SINK], env_deny=[TOKEN_ENV], name=name)
        with github_env(GITHUB_REPOSITORY=REPO, GITHUB_API_URL=api.url, GITHUB_GRAPHQL_URL=api.url + "/graphql",
                        **{TOKEN_ENV: token}):
            run = run_line(project, wo_id, verdicts=verdicts if verdicts is not None else {"reviewer-spec": "fail"},
                           max_loopbacks=max_loopbacks, counter=lambda: len(api.requests))
        return run, api


class ProjectSink(unittest.TestCase):
    def test_s5_status_changes_only_when_the_phase_changes(self):
        """S5 (test e): adds the missing item once, then one status change per phase change, in order"""
        with tempfile.TemporaryDirectory() as tmp:
            board = Board()
            run, api = project_run(tmp, board)
            self.assertTrue(run.report["human_required"])
            self.assertTrue(all(path.split("?")[0] == "/graphql" for _, path, _, _ in api.requests),
                            [p for _, p, _, _ in api.requests])
            kinds = board.kinds()
            self.assertEqual(kinds.count("add"), 1)
            self.assertNotIn("other-mutation", kinds)
            self.assertLess(kinds.index("add"), kinds.index("update"), "the item is added before its first status")
            self.assertIn(ISSUE_ID, json.dumps(board.requests[kinds.index("add")]))
            self.assertEqual(board.status_options(), ["Intake", "Spec", "Build", "Checks", "Review", "Needs human"])
            self.assertGreater(len(run.writes), len(board.status_options()), "no status sent without a change")
            final = run.state()
            self.assertEqual(final["export_errors"], [])
            self.assertEqual(final["sinks"], [{"type": "github-project", "active": True, "reason": None}])
            for _, _, headers, _ in api.requests:
                lowered = {k.lower(): v for k, v in headers.items()}
                self.assertEqual(lowered.get("authorization"), "Bearer ghp_projects_token_47")

    def test_s5_item_already_in_project_is_not_added_again(self):
        """S5 (R3.4): an issue already on the board is not added; an approved run ends on Done"""
        with tempfile.TemporaryDirectory() as tmp:
            board = Board(issue_in_project=True)
            run, _ = project_run(tmp, board, verdicts={}, max_loopbacks=2)
            self.assertEqual(run.report["verdict"], "approved")
            self.assertNotIn("add", board.kinds())
            self.assertEqual(board.status_options(),
                             ["Intake", "Spec", "Build", "Checks", "Review", "Needs human", "Done"])

    def test_s6_missing_option_names_it_and_goes_inactive(self):
        """S6 (test e): no Review option: named in export_errors, no further request, shape untouched"""
        with tempfile.TemporaryDirectory() as tmp:
            full_run, _ = project_run(tmp, Board(), name="full")
            board = Board(options=[o for o in DEFAULT_OPTIONS if o != "Review"])
            run, api = project_run(tmp, board, name="noreview")
            note = "github-project: option Review not found in Status"
            final = run.state()
            self.assertIn(note, final["export_errors"])
            self.assertEqual(final["sinks"], [{"type": "github-project", "active": False, "reason": note}])
            self.assertNotIn("other-mutation", board.kinds())
            self.assertEqual(board.status_options(), ["Intake", "Spec", "Build", "Checks"])
            first = next(i for i, (record, _) in enumerate(run.writes) if note in record.get("export_errors", []))
            self.assertEqual(run.writes[first][0]["current_station"], "reviewer-spec")
            # the request count no longer moves after the write that recorded the missing option
            self.assertEqual(set(run.counts[first:]), {len(api.requests)}, run.counts)
            self.assertEqual(run.report["verdict"], full_run.report["verdict"])
            self.assertEqual(run.report["human_required"], full_run.report["human_required"])

    def test_s6_missing_project_names_it_and_goes_inactive(self):
        """S6 (R3.5): a project that does not exist is named, and the sink sends nothing after the lookup"""
        with tempfile.TemporaryDirectory() as tmp:
            board = Board(exists=False)
            run, _ = project_run(tmp, board)
            note = "github-project: project acme/3 not found"
            final = run.state()
            self.assertIn(note, final["export_errors"])
            self.assertEqual(final["sinks"], [{"type": "github-project", "active": False, "reason": note}])
            self.assertEqual(set(board.kinds()), {"lookup"})
            self.assertLessEqual(len(board.requests), 3, "lookups only, at the first call")

    def test_s16_unset_projects_token_makes_no_call(self):
        """S16 (R3.6, R1.6): token_env unset: zero GraphQL requests, the reason names the variable"""
        with tempfile.TemporaryDirectory() as tmp:
            board = Board()
            run, api = project_run(tmp, board, token=None)
            self.assertEqual(api.requests, [])
            final = run.state()
            self.assertEqual(final["sinks"],
                             [{"type": "github-project", "active": False, "reason": f"{TOKEN_ENV} is not set"}])
            self.assertEqual(final["export_errors"], [])

    def test_s16_projects_token_never_written(self):
        """S16 (R5.2): the Projects token is in no GraphQL body and no run file"""
        sentinel = "ghp_SENTINEL_PROJECTS_47_abcdef"
        with tempfile.TemporaryDirectory() as tmp:
            board = Board()
            run, api = project_run(tmp, board, token=sentinel)
            self.assertTrue(api.requests)
            for _, _, _, body in api.requests:
                self.assertNotIn(sentinel, body)
            for path in (p for p in run.run_dir.rglob("*") if p.is_file()):
                self.assertNotIn(sentinel.encode(), path.read_bytes(), str(path))


if __name__ == "__main__":
    unittest.main()
