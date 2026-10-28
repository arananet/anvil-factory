# ANVIL

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue) ![License Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green) ![OpenSpec](https://img.shields.io/badge/OpenSpec-specs-orange) TDD: tests before implementation

> "ANVIL is a composable software factory: spec first, tests first, and no station approves its own work."

Full name: ANVIL, Agentic Network for Verified Implementation Lifecycle.

## What it is
ANVIL is a framework for running software work down a line of stations. Each station has a manifest and a clear contract. Some stations are deterministic code that runs for real: intake, gates, the approver and human triage. Agent stations are explicit contracts, a manifest plus a prompt packet. The runner never pretends a model ran: for an agent station it writes a packet file and marks the step packet_ready.

A project keeps everything in its repo: specs, tests, reviews, run reports, envelopes and a brain folder with context and decisions.

## One core, two domains: software and content
The factory core (work orders, pipelines, gates, envelopes, approver, human triage, brain) does not care what the line produces. Domains are station sets that plug into the same core:

- **Software** is the default domain in this repo: spec-writer, test-writer and builder produce code, and the four software reviewers check it. The spec is the contract and tests are the evidence.
- **Content** ships in the same catalog: brief-writer, researcher, writer and media-producer produce a piece, and four different reviewers check it in parallel (facts against sources, voice, platform fit, brand risk). The brief replaces the spec, the source pack replaces the test base, and two deterministic gates check the brief and the AI generated disclosure on the draft.

Publishing is a risk hint in ANVIL, so a content work order that will be published always stops at the human gate before the publisher station runs. That is deliberate: the factory prepares and checks, a human decides what goes out under their name.

A worked content example with a brief, a draft and a full run lives in examples/content/why-factories. The same composition rule applies both ways: a content series can start greenfield from an idea, and a software team can borrow the researcher or the facts reviewer for a technical article line.

## Two modes: greenfield and brownfield
ANVIL is not only a line for issues on existing code. It has two modes that share the same stations:

- **Greenfield, build from zero.** The entry is an idea, not an issue. `anvil new-project` scaffolds a brand new project from a catalog blueprint (python-service, cloudflare-worker, static-site): repo structure, a brain seeded with the idea, BLUEPRINT.md with the stack and the first specs, and anvil.json pointing at the greenfield pipeline. That pipeline adds one station at the front, blueprint, which turns the idea into a project shape before spec-writer takes over. Taskline, the example repo, is a build from zero: no code existed when its work order was written. Its recorded run used sdlc-default, and the greenfield pipeline formalizes that from zero path with scaffolding and the blueprint station in front.
- **Brownfield, work on what exists.** The entry is a feature, a bug report, a production incident or a task, from a GitHub issue, the intake worker, or a file. The sdlc-default, hotfix, plan-build-test, docs-only and scout pipelines serve this mode.

The modes are a starting point, not a wall: a greenfield project becomes brownfield the day its first version ships, and it keeps the same brain, specs and gates.

## The line

| Station | Kind | What it does |
|---|---|---|
| intake | deterministic | Normalize a work order into the shared shape |
| spec-writer | agent | Write an OpenSpec spec from the work order |
| test-writer | agent | Write tests mapped to spec scenarios |
| builder | agent | Implement the spec so the tests pass |
| reviewer-spec | agent | Check the change against the spec |
| reviewer-security | agent | Check for security risks and unsafe defaults |
| reviewer-tests | agent | Check tests are real, mapped and passing |
| reviewer-architecture | agent | Check fit with structure and decisions |
| approver | deterministic | Aggregate the four reviews into one verdict |
| triage-human | deterministic | Decide if a human must review risky work |
| deployer | agent | Carry out the release step for the project |
| observer | agent | Watch the release and report what happened |
| scout | agent | Read only recon, reports and changes no code |
| blueprint | agent | Greenfield only: turn an idea into a project blueprint, stack, structure and first specs |
| brief-writer | agent | Content: turn an idea or topic into a brief with audience, angle, claims and sources |
| researcher | agent | Content: build the source pack, one primary source per claim |
| writer | agent | Content: write the draft from the brief and the source pack only |
| media-producer | agent | Content: produce images, audio or video and record how each was made |
| reviewer-facts | agent | Content: check every claim against the source pack |
| reviewer-voice | agent | Content: check voice, house rules and the AI generated disclosure |
| reviewer-platform | agent | Content: check format and fit for the target channel |
| reviewer-brand | agent | Content: check brand and policy risks |
| publisher | agent | Content: publish only after approval and the human gate, and record where it went live |

## Composing a pipeline
A pipeline is a small JSON file. Order stations, or group them in parallel. Stations are reused across pipelines, never redefined.

```json
{
  "name": "my-line",
  "stages": [
    {"station": "intake"},
    {"station": "builder"},
    {"parallel": ["reviewer-spec", "reviewer-security"]},
    {"station": "approver"}
  ]
}
```

## Quick start
```bash
python3 -m anvil.cli new-project ../my-new-app --name MyNewApp --blueprint cloudflare-worker --idea "What this app is for"
python3 -m anvil.cli init ../my-project --name MyProject
python3 -m anvil.cli new-spec ../my-project my-feature --title "My Feature"
python3 -m anvil.cli validate-pipeline pipelines/sdlc-default.json
python3 -m anvil.cli run ../my-project --pipeline pipelines/sdlc-default.json --work-order work-order.json
python3 -m anvil.cli check ../my-project --slug my-feature
python3 -m anvil.cli check-content ../my-channel --slug my-post
```
Installed as a package, the same commands are available as `anvil new-project`, `anvil init`, `anvil new-spec`, `anvil validate-pipeline`, `anvil run` and `anvil check`.

Project station settings live in `anvil.yaml` at the project root: context, model, prompt and tools per station. See docs/ARCHITECTURE.md for the Core Four.

## The brain
The brain/ folder holds project.md (what the project is and its principles), glossary.md, decisions/ (numbered decision records) and worklog.md. Stations read the brain as context, so decisions survive beyond a single run.

## Pipelines included
- sdlc-default: the full SDLC line, intake to observer with four parallel reviewers.
- hotfix: a short line for urgent fixes, with spec and security review.
- docs-only: intake, builder, one review and the approver.
- scout: a single read only recon station, no code changes.
- plan-build-test: intake, spec, tests, build, test review and approver.
- greenfield: the from zero line. Intake, blueprint, spec, tests, build, the four parallel reviewers, approver, human triage, deployer and observer.
- content-default: the full content line. Intake, brief, research, writing, media, four parallel content reviewers, approver, human triage, publisher and observer.
- content-short: a short content line for posts. Intake, brief, writing, facts and voice review, approver, human triage and publisher.

## Intake worker
intake-worker/ is a Cloudflare Worker in plain JavaScript with no dependencies. POST /work-orders validates and normalizes a work order and returns 201. GET /health returns ok. Tests run with `node --test "intake-worker/*.test.js"`.

Optional GitHub dispatch: set GITHUB_REPO and GITHUB_TOKEN in the Worker environment to forward work orders to a repository dispatch event in your own deployment code. No secrets live in the repo.

## Contributing
Every change starts with a spec under .openspec/specs/ (OpenSpec). Write the spec, write tests that map to its scenarios, then implement. Keep runtime code on the Python standard library only.

## Documentation

| Document | What it covers |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layers, artifact flow, gates, risk triage, Core Four, model stack, loopback, envelopes, observability |
| [docs/SDLC.md](docs/SDLC.md) | How the default pipeline maps to SDLC phases |
| [brain/project.md](brain/project.md) | Principles and project context |
| [templates/spec.md](templates/spec.md) | The spec template every spec starts from |

## License

[Apache 2.0](LICENSE)

---

## Developer

Eduardo Arana

## Support this with a ko-fi

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/H2H51MPWG)
