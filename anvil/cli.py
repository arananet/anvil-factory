import argparse, json, sys
from pathlib import Path
from .pipeline import load_pipeline
from .stations import load_registry
from .gates import spec_gate, tdd_gate, review_gate, brief_gate, disclosure_gate, derive_base_ref
from .scaffold import init_project, scaffold_spec, new_project
from .onboard import onboard_project
from .blueprints import get_blueprint
from .model import WorkOrder
from .runner import run_pipeline
from .config import load_anvil_config, apply_overrides, runtime_config, deploy_config, health_config
from .executor import create_executor
from .statuspage import generate_status_page
from .brain import check_brain, promote_learning, demote_learning, propose_practice, promote_practice
from .supervisor import supervise
from . import line

# Alias for test compatibility
new_project_command = new_project

def _factory_root():
    return Path(__file__).resolve().parent.parent

def _registry(project=None):
    # Prefer project stations if present, else factory stations
    candidates = []
    if project:
        candidates.append(Path(project) / "stations")
    candidates.append(_factory_root() / "stations")
    for c in candidates:
        if c.is_dir():
            reg = load_registry(c)
            # Core Four overrides from the project anvil.yaml
            if project:
                cfg_path = Path(project) / "anvil.yaml"
                if cfg_path.exists():
                    apply_overrides(reg, load_anvil_config(cfg_path))
            return reg
    raise SystemExit("No stations directory found")

def main(argv=None):
    parser = argparse.ArgumentParser(prog="anvil")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("path"); p.add_argument("--name", required=True)
    p = sub.add_parser("new-project"); p.add_argument("path"); p.add_argument("--name", required=True); p.add_argument("--blueprint", required=True); p.add_argument("--idea", default=""); p.add_argument("--deploy-target", default=None, choices=["cloudflare", "github"], help="Write deploy, preview and provision config for this platform into anvil.yaml")
    p = sub.add_parser("onboard"); p.add_argument("path"); p.add_argument("--name", default=None)
    p = sub.add_parser("new-spec"); p.add_argument("project"); p.add_argument("slug"); p.add_argument("--title", required=True)
    p = sub.add_parser("validate-pipeline"); p.add_argument("file")
    p = sub.add_parser("check"); p.add_argument("project"); p.add_argument("--slug", required=True)
    p = sub.add_parser("check-content"); p.add_argument("project"); p.add_argument("--slug", required=True)
    p = sub.add_parser("run"); p.add_argument("project"); p.add_argument("--pipeline", required=True); p.add_argument("--work-order", required=True); p.add_argument("--execute", action="store_true"); p.add_argument("--base-ref", default=None, help="Base ref for checks gate (overrides automatic derivation)"); p.add_argument("--isolate", action="store_true", help="Run on branch anvil/<work-order-id> in its own git worktree and commit the result there")
    p = sub.add_parser("resume"); p.add_argument("project"); p.add_argument("work_order_id"); p.add_argument("--pipeline", default=None); p.add_argument("--execute", action="store_true"); p.add_argument("--base-ref", default=None); p.add_argument("--isolate", action="store_true")
    p = sub.add_parser("approve"); p.add_argument("project"); p.add_argument("work_order_id"); p.add_argument("--by", required=True); p.add_argument("--note", default=""); p.add_argument("--override", action="store_true", help="Approve a run the line did not approve; recorded as an override"); p.add_argument("--isolate", action="store_true")
    p = sub.add_parser("runs"); p.add_argument("project"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("preview-cleanup"); p.add_argument("project"); p.add_argument("work_order_id")
    p = sub.add_parser("provision"); p.add_argument("project")
    p = sub.add_parser("work-order-from-issue"); p.add_argument("issue_json", help="Path to a GitHub issue JSON object, or to an event payload with an issue key"); p.add_argument("--out-dir", default="work-orders")
    p = sub.add_parser("status-page"); p.add_argument("project"); p.add_argument("--out", default=None); p.add_argument("--include-project", action="append", default=None)
    p = sub.add_parser("check-brain"); p.add_argument("project")
    p = sub.add_parser("promote-learning"); p.add_argument("project"); p.add_argument("inbox_file")
    p = sub.add_parser("demote-learning"); p.add_argument("project"); p.add_argument("entry_id"); p.add_argument("--reason", required=True)
    p = sub.add_parser("propose-practice"); p.add_argument("project"); p.add_argument("--topic", required=True); p.add_argument("--rule", required=True); p.add_argument("--enforcement", default="prompt"); p.add_argument("--languages", default=""); p.add_argument("--surfaces", default=""); p.add_argument("--stations", default=""); p.add_argument("--source", required=True); p.add_argument("--supersedes", default=None)
    p = sub.add_parser("promote-practice"); p.add_argument("project"); p.add_argument("inbox_file")
    p = sub.add_parser("check-skills"); p.add_argument("project"); p.add_argument("--work-order", default=None); p.add_argument("--pipeline", default=None)
    p = sub.add_parser("supervise"); p.add_argument("project"); p.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    # Deploy and preview commands may call the factory's own tools.
    import os
    os.environ.setdefault("ANVIL_FACTORY_ROOT", str(_factory_root()))
    if args.cmd == "init":
        init_project(args.path, args.name); print(f"Created project at {args.path}"); return 0
    if args.cmd == "new-project":
        bp = get_blueprint(_factory_root() / "blueprints", args.blueprint)
        try:
            new_project(args.path, args.name, bp, idea=args.idea, deploy_target=args.deploy_target)
        except ValueError as exc:
            print(f"Cannot create the project: {exc}", file=sys.stderr); return 2
        print(f"Created greenfield project at {args.path} from blueprint {bp['id']}"); return 0
    if args.cmd == "onboard":
        try:
            result = onboard_project(args.path, name=args.name)
        except ValueError as exc:
            print(f"Cannot onboard: {exc}"); return 1
        print(f"Onboarded {args.path}: created {len(result['created'])} files, kept {len(result['kept'])}, gaps {len(result['gaps'])}")
        for s in result["suggested_work_orders"]:
            print(f"Suggested: {s}")
        return 0
    if args.cmd == "new-spec":
        f = scaffold_spec(args.project, args.slug, args.title); print(f"Created spec at {f}"); return 0
    if args.cmd == "validate-pipeline":
        reg = _registry()
        pipe = load_pipeline(args.file, known_stations=set(reg.ids()))
        print(f"Pipeline {pipe.name} valid: {', '.join(pipe.topological_order())}"); return 0
    if args.cmd == "check":
        gates = [("spec", spec_gate(args.project, args.slug)), ("tdd", tdd_gate(args.project, args.slug)), ("review", review_gate(args.project, args.slug))]
        ok = True
        for name, (passed, detail) in gates:
            print(f"{name}: {'PASS' if passed else 'FAIL'} - {detail}")
            ok = ok and passed
        return 0 if ok else 1
    if args.cmd == "check-content":
        gates = [("brief", brief_gate(args.project, args.slug)), ("disclosure", disclosure_gate(args.project, args.slug))]
        ok = True
        for name, (passed, detail) in gates:
            print(f"{name}: {'PASS' if passed else 'FAIL'} - {detail}")
            ok = ok and passed
        return 0 if ok else 1
    if args.cmd == "runs":
        from .observe import fleet_summary, run_states
        summary = fleet_summary(args.project)
        states = run_states(args.project)
        if args.json:
            print(json.dumps({"summary": summary, "runs": states}, indent=2))
            return 0
        for st in states:
            tokens = (st.get("token_usage") or {}).get("total_tokens")
            print(f"{st['work_order_id']}: {st['state']}"
                  + (f" at {st['current_station']}" if st["state"] != "finished" and st.get("current_station") else "")
                  + f", verdict {st.get('verdict') or 'none'}, loopbacks {st.get('loopbacks', 0)}"
                  + f", tokens {tokens if tokens is not None else 'unmeasured'}"
                  + (f", cost {st['cost']}" if st.get("cost") is not None else ""))
        for name, group in sorted(summary["by_pipeline"].items()):
            print(f"pipeline {name}: {group['runs']} runs, approval rate {group['approval_rate']}, loopbacks {group['loopbacks']}")
        print(f"runs: {summary['runs']} reported, {len(summary['in_progress'])} in progress, "
              f"{len(summary['interrupted'])} interrupted")
        return 0
    if args.cmd in {"preview-cleanup", "provision"}:
        deploy = deploy_config(load_anvil_config(Path(args.project) / "anvil.yaml")) or {}
        if args.cmd == "preview-cleanup":
            preview = deploy.get("preview") if isinstance(deploy.get("preview"), dict) else {}
            if not preview.get("cleanup"):
                print("No preview cleanup command is configured; nothing to do.")
                return 0
            try:
                result = line.run_preview(args.project, preview, args.work_order_id, action="cleanup")
            except ValueError as exc:
                print(f"Cannot clean up: {exc}", file=sys.stderr)
                return 2
            print(result["detail"])
            if not result["ok"]:
                print(result["output"], file=sys.stderr)
            return 0 if result["ok"] else 1
        commands = [str(c) for c in deploy.get("provision") or []]
        if not commands:
            print("No provision commands are configured; nothing to do.")
            return 0
        import subprocess
        for command in commands:
            print(f"$ {command}")
            code = subprocess.run(command, shell=True, cwd=str(args.project)).returncode
            if code != 0:
                print(f"Provision stopped: exit code {code}", file=sys.stderr)
                return 1
        print(f"Provisioned: {len(commands)} commands ran.")
        return 0
    if args.cmd == "work-order-from-issue":
        try:
            payload = json.loads(Path(args.issue_json).read_text(encoding="utf-8"))
            issue = payload.get("issue", payload) if isinstance(payload, dict) else payload
            data, pipeline_name = line.work_order_from_issue(issue)
            WorkOrder.from_dict(data)
        except (OSError, ValueError) as exc:
            print(f"Cannot build a work order: {exc}", file=sys.stderr)
            return 2
        out = Path(args.out_dir) / f"issue-{issue['number']}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"work_order": str(out), "id": data["id"], "pipeline": pipeline_name}))
        return 0
    if args.cmd == "approve":
        project = args.project
        try:
            if args.isolate:
                project, branch = line.isolate(args.project, args.work_order_id)
            # The policy is read from the checkout the operator controls, never
            # from the run's worktree, which the builder can edit.
            policy = load_anvil_config(Path(args.project) / "anvil.yaml").get("approvals")
            record = line.record_approval(project, args.work_order_id, args.by, note=args.note,
                                          override=args.override, policy=policy)
            if args.isolate:
                line.commit_run(project, args.work_order_id, f"Record human approval for {args.work_order_id} by {record['approved_by']}")
        except ValueError as exc:
            print(f"Approval refused: {exc}", file=sys.stderr)
            return 1
        print(f"Approved run {record['run_id']} of {args.work_order_id} by {record['approved_by']}"
              f"{' (override)' if record['override'] else ''}. Continue with: anvil resume {args.project} {args.work_order_id} --execute")
        return 0
    if args.cmd in {"run", "resume"}:
        project = args.project
        branch = None
        resume_state = None
        try:
            if args.cmd == "run":
                data = json.loads(Path(args.work_order).read_text(encoding="utf-8"))
                wo = WorkOrder.from_dict(data)
                pipeline_path = args.pipeline
            if args.isolate:
                project, branch = line.isolate(args.project, args.work_order_id if args.cmd == "resume" else wo.id)
            if args.cmd == "resume":
                resume_state = line.load_resume(project, args.work_order_id)
                wo_file = Path(project) / "work_orders" / f"{args.work_order_id}.json"
                if wo_file.is_file():
                    wo = WorkOrder.from_dict(json.loads(wo_file.read_text(encoding="utf-8")))
                else:
                    prev = resume_state["report"]
                    wo = WorkOrder(id=args.work_order_id, kind=prev.get("kind") or "task",
                                   title=prev.get("title") or args.work_order_id,
                                   risk_hints=list(prev.get("risk_hints") or []))
                pipeline_path = args.pipeline
                if pipeline_path is None:
                    name = resume_state["report"].get("pipeline")
                    candidates = [Path(project) / "pipelines" / f"{name}.json", _factory_root() / "pipelines" / f"{name}.json"]
                    pipeline_path = next((c for c in candidates if c.is_file()), None)
                    if pipeline_path is None:
                        raise ValueError(f"pipeline {name} not found; pass --pipeline")
        except ValueError as exc:
            print(f"Cannot {args.cmd}: {exc}", file=sys.stderr)
            return 2
        reg = _registry(project)
        pipe = load_pipeline(pipeline_path, known_stations=set(reg.ids()))
        executor = None
        deploy_cfg = None
        health_cfg = None
        if args.execute:
            cfg = load_anvil_config(Path(project) / "anvil.yaml")
            runtime = runtime_config(cfg)
            if runtime is None:
                print("--execute needs a runtime object in the project anvil.yaml", file=sys.stderr)
                return 2
            executor = create_executor(runtime)
            deploy_cfg = deploy_config(cfg)
            health_cfg = health_config(cfg)

        # Loopback round 3: Derive base ref from git when in a repository
        base_ref = args.base_ref
        if base_ref is None:
            # Load project config to check for base_branch setting
            project_config_path = Path(project) / "anvil.json"
            base_branch = None
            if project_config_path.exists():
                try:
                    project_config = json.loads(project_config_path.read_text(encoding="utf-8"))
                    base_branch = project_config.get("base_branch")
                except (json.JSONDecodeError, OSError):
                    pass

            # Derive base ref from git merge-base
            base_ref = derive_base_ref(project, base_branch=base_branch)

        try:
            report = run_pipeline(project, pipe, wo, registry=reg, executor=executor, deploy_cfg=deploy_cfg,
                                  health_cfg=health_cfg, base_ref=base_ref, resume=resume_state)
        except ValueError as exc:
            if resume_state is None:
                raise
            print(f"Cannot resume: {exc}", file=sys.stderr)
            return 2
        result = report.to_dict()
        print(json.dumps(result, indent=2))
        print(f"Report: {Path(project) / 'runs' / wo.id / 'report.json'}")
        code = line.exit_code(result, executed=args.execute, work_order_status=wo.status)
        if branch:
            verb = "resume" if resume_state else "run"
            commit = line.commit_run(project, wo.id, f"ANVIL {verb} {wo.id}: verdict {result['verdict']}")
            print(f"Branch: {branch} at {commit or 'no changes'} (worktree {project})")
        if code == line.EXIT_HUMAN_GATE:
            print(f"Human gate: approve with `anvil approve {args.project} {wo.id} --by <name>`, "
                  f"then `anvil resume {args.project} {wo.id} --execute`.", file=sys.stderr)
        return code
    if args.cmd == "status-page":
        summary = generate_status_page(args.project, args.out, projects=args.include_project)
        print(f"Status page: {summary['path']} ({summary['runs']} runs, skipped: {', '.join(summary['skipped']) or 'none'})")
        return 0
    if args.cmd == "check-brain":
        result = check_brain(args.project)
        for entry in result["entries"]:
            print(f"{entry['id']}: {'PASS' if entry['ok'] else 'FAIL'}")
        for problem in result["problems"]:
            print(f"brain: FAIL - {problem}")
        for name in result["quarantined"]:
            print(f"quarantined (inbox, not verified): {name}")
        practices = result.get("practices", {})
        print(f"brain: {'PASS' if result['ok'] else 'FAIL'} - "
              f"{len(result['entries'])} verified entries, {len(result['quarantined'])} quarantined proposals, "
              f"{practices.get('active', 0)} active practices")
        return 0 if result["ok"] else 1
    if args.cmd == "check-skills":
        from .skills import load_catalog, resolve_skills
        entries, problems = load_catalog(args.project)
        for e in entries:
            scope = "; ".join(f"{dim}: {', '.join(e[dim])}" for dim in ("stations", "surfaces", "product_types", "kinds") if e[dim])
            print(f"{e['id']} [{e['domain'] or 'general'}, {e['origin']}] {scope}")
        for problem in problems:
            print(f"skills: FAIL - {problem}")
        if args.work_order and args.pipeline:
            wo = WorkOrder.from_dict(json.loads(Path(args.work_order).read_text(encoding="utf-8")))
            order = load_pipeline(args.pipeline).topological_order()
            config = load_anvil_config(Path(args.project) / "anvil.yaml")
            resolution = resolve_skills(args.project, wo, order, config)
            print(f"signals: {json.dumps(resolution['signals'])}")
            for station in order:
                if resolution["resolved"].get(station):
                    print(f"{station}: {', '.join(resolution['resolved'][station])}")
        print(f"skills: {'PASS' if not problems else 'FAIL'} - {len(entries)} curated skills in the catalog")
        return 0 if not problems else 1
    if args.cmd == "promote-learning":
        try:
            entry_id = promote_learning(args.project, args.inbox_file)
        except ValueError as exc:
            print(f"Promotion refused: {exc}")
            return 1
        print(f"Promoted {args.inbox_file} as {entry_id} in brain/learnings.md")
        return 0
    if args.cmd == "propose-practice":
        name = propose_practice(args.project, args.topic, args.rule, enforcement=args.enforcement,
                                languages=args.languages, surfaces=args.surfaces,
                                stations=args.stations, source=args.source,
                                supersedes=args.supersedes)
        print(f"Proposed practice quarantined at brain/inbox/{name}")
        return 0
    if args.cmd == "promote-practice":
        try:
            pid = promote_practice(args.project, args.inbox_file)
        except ValueError as exc:
            print(f"Promotion refused: {exc}")
            return 1
        print(f"Promoted {args.inbox_file} as {pid} in brain/practices.md")
        return 0
    if args.cmd == "demote-learning":
        try:
            record = demote_learning(args.project, args.entry_id, args.reason)
        except ValueError as exc:
            print(f"Demotion refused: {exc}")
            return 1
        print(f"Demoted {args.entry_id}; decision recorded at {record}")
        return 0
    if args.cmd == "supervise":
        reg = _registry(args.project)
        executor = None
        if args.execute:
            cfg = load_anvil_config(Path(args.project) / "anvil.yaml")
            runtime = runtime_config(cfg)
            if runtime is None:
                print("--execute needs a runtime object in the project anvil.yaml", file=sys.stderr)
                return 2
            executor = create_executor(runtime)
        result = supervise(args.project, reg, executor=executor)
        if not result["signals"]:
            print("no stalls detected")
            return 0
        for signal in result["signals"]:
            print(f"Signal: {signal['kind']} - {signal['detail']} (evidence: {', '.join(signal['evidence'])})")
        if result["action"] == "packet":
            print(f"Supervisor packet: {result['packet']}")
            print(f"Proposal work order: {result['work_order']}")
        elif result["action"] == "accepted":
            print(f"Proposal accepted: {result['proposal']} (see {result['proposal_doc']}). Nothing auto applies.")
        elif result["action"] == "rejected":
            print(f"Proposal rejected: {result['proposal']} (see {result['rejection']})")
            for failure in result["failures"]:
                print(f"Failed check: {failure}")
        elif result["action"] == "no_proposal":
            print(f"Runtime output carried no JSON proposal: {result['output']}")
        elif result["action"] == "execute_failed":
            print(f"Executor failed: {result['error']}")
            return 1
        return 0
    return 2

if __name__ == "__main__":
    sys.exit(main())
