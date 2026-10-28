import argparse, json, sys
from pathlib import Path
from .pipeline import load_pipeline
from .stations import load_registry
from .gates import spec_gate, tdd_gate, review_gate, brief_gate, disclosure_gate
from .scaffold import init_project, scaffold_spec, new_project
from .onboard import onboard_project
from .blueprints import get_blueprint
from .model import WorkOrder
from .runner import run_pipeline
from .config import load_anvil_config, apply_overrides, runtime_config, deploy_config
from .executor import create_executor
from .statuspage import generate_status_page
from .brain import check_brain, promote_learning, demote_learning
from .supervisor import supervise

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
    p = sub.add_parser("new-project"); p.add_argument("path"); p.add_argument("--name", required=True); p.add_argument("--blueprint", required=True); p.add_argument("--idea", default="")
    p = sub.add_parser("onboard"); p.add_argument("path"); p.add_argument("--name", default=None)
    p = sub.add_parser("new-spec"); p.add_argument("project"); p.add_argument("slug"); p.add_argument("--title", required=True)
    p = sub.add_parser("validate-pipeline"); p.add_argument("file")
    p = sub.add_parser("check"); p.add_argument("project"); p.add_argument("--slug", required=True)
    p = sub.add_parser("check-content"); p.add_argument("project"); p.add_argument("--slug", required=True)
    p = sub.add_parser("run"); p.add_argument("project"); p.add_argument("--pipeline", required=True); p.add_argument("--work-order", required=True); p.add_argument("--execute", action="store_true")
    p = sub.add_parser("status-page"); p.add_argument("project"); p.add_argument("--out", default=None)
    p = sub.add_parser("check-brain"); p.add_argument("project")
    p = sub.add_parser("promote-learning"); p.add_argument("project"); p.add_argument("inbox_file")
    p = sub.add_parser("demote-learning"); p.add_argument("project"); p.add_argument("entry_id"); p.add_argument("--reason", required=True)
    p = sub.add_parser("supervise"); p.add_argument("project"); p.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    if args.cmd == "init":
        init_project(args.path, args.name); print(f"Created project at {args.path}"); return 0
    if args.cmd == "new-project":
        bp = get_blueprint(_factory_root() / "blueprints", args.blueprint)
        new_project(args.path, args.name, bp, idea=args.idea); print(f"Created greenfield project at {args.path} from blueprint {bp['id']}"); return 0
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
    if args.cmd == "run":
        reg = _registry(args.project)
        pipe = load_pipeline(args.pipeline, known_stations=set(reg.ids()))
        data = json.loads(Path(args.work_order).read_text(encoding="utf-8"))
        wo = WorkOrder.from_dict(data)
        executor = None
        deploy_cfg = None
        if args.execute:
            cfg = load_anvil_config(Path(args.project) / "anvil.yaml")
            runtime = runtime_config(cfg)
            if runtime is None:
                print("--execute needs a runtime object in the project anvil.yaml", file=sys.stderr)
                return 2
            executor = create_executor(runtime)
            deploy_cfg = deploy_config(cfg)
        report = run_pipeline(args.project, pipe, wo, registry=reg, executor=executor, deploy_cfg=deploy_cfg)
        print(json.dumps(report.to_dict(), indent=2))
        print(f"Report: {Path(args.project) / 'runs' / wo.id / 'report.json'}")
        return 0
    if args.cmd == "status-page":
        summary = generate_status_page(args.project, args.out)
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
        print(f"brain: {'PASS' if result['ok'] else 'FAIL'} - "
              f"{len(result['entries'])} verified entries, {len(result['quarantined'])} quarantined proposals")
        return 0 if result["ok"] else 1
    if args.cmd == "promote-learning":
        try:
            entry_id = promote_learning(args.project, args.inbox_file)
        except ValueError as exc:
            print(f"Promotion refused: {exc}")
            return 1
        print(f"Promoted {args.inbox_file} as {entry_id} in brain/learnings.md")
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
