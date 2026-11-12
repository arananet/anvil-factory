# ANVIL

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue) ![License Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green) ![OpenSpec](https://img.shields.io/badge/OpenSpec-specs-orange) TDD: tests before implementation

> "ANVIL is a composable software factory: spec first, tests first, and no station approves its own work."

Full name: ANVIL, Agentic Network for Verified Implementation Lifecycle.

## See it working

**Landing page**: [anvil-landing-7x1.pages.dev](https://anvil-landing-7x1.pages.dev) explains what ANVIL is: the problem it solves, how the line works, and the proof built on it. The page itself was built by ANVIL under work order wo-gh-35 and went through the same review line as everything else here.

**Real run trail**: [wo-gh-9](runs/wo-gh-9/) shows the complete cycle from work order through five independent reviews to merge. Every station's packet, every review file, and the final report are preserved in the runs/ directory. No mockups - this is what the factory actually produced.

**Live example**: The [Taskline repository](https://github.com/arananet/anvil-example-taskline) is a working task board API built entirely on the ANVIL line from a blank slate, with spec-first, red-green TDD evidence, and all station artifacts committed to its tree.

## Built by ANVIL

Three projects running in production, built on this factory:

- **[Sentia](https://sentia.info-693.workers.dev)** - Full-stack web app with database persistence, built from spec through deployment verification on the greenfield pipeline
- **[Platform25](https://platform25.pages.dev)** - Playable game built through the content pipeline with media production and brand review stations
- **[Status Board](https://anvil-status.pages.dev)** - Live factory run status, generated from run reports and published automatically

Each proves the same line can ship software, content, and infrastructure.

## Quickstart

Clone the Taskline example and see the factory output in under a minute:

```bash
git clone https://github.com/arananet/anvil-example-taskline.git
cd anvil-example-taskline
python3 -m unittest discover -s tests -v
```

You will see 6 passing tests mapped to spec scenarios, a complete run report in runs/, and review files from five independent reviewers. The example completes in ~0.3 seconds.

If ANVIL is useful to you, a star helps other builders find it.

## Why you can trust the output

### 1. No station approves its own work

Every agent station writes to its assigned artifact file (builder writes code, reviewers write review JSON). The approver station reads only the review files - it cannot see station output or logs - and aggregates verdicts using [deterministic parsing that fails closed](stations/approver/station.json). If a review file is malformed or a verdict is missing, the run is rejected, never assumed pass.

Independent review evidence: [runs/wo-gh-9/reviewer-spec.review.json](runs/wo-gh-9/reviewer-spec.review.json), [reviewer-security.review.json](runs/wo-gh-9/reviewer-security.review.json), [reviewer-tests.review.json](runs/wo-gh-9/reviewer-tests.review.json), [reviewer-architecture.review.json](runs/wo-gh-9/reviewer-architecture.review.json), [reviewer-design.review.json](runs/wo-gh-9/reviewer-design.review.json) - five independent reviewers, none of which built the code.

### 2. Memory with provenance

The factory brain learns from run outcomes, but agent-written learnings never reach verified storage directly. New learnings wait in [brain/inbox/](brain/inbox/) (quarantined) until deterministic code verifies their provenance field against an actual run report that produced the claimed outcome. Only verified learnings promote to [brain/learnings.md](brain/learnings.md). This is the project's answer to benign memory contamination (CONTAM-Bench): the brain cannot learn from hallucinated runs.

Provenance gate implementation: [docs/MEMORY-GATE.md](docs/MEMORY-GATE.md)

### 3. Human gate before publishing or production deploys

Any work order with a publishing or production deploy risk hint stops at the [triage-human station](stations/triage-human/station.json) for explicit human approval before the deployer or publisher stations run. The factory prepares and checks, but a human decides what goes out. Runs that reach the deployer without approval are rejected at that gate.

Evidence: [runs/wo-gh-9/report.json](runs/wo-gh-9/report.json) line 147, triage-human station status: "executed", blocking risky work.

## What it is

ANVIL is a framework for running software work down a line of 27 stations. Each station has a manifest and a clear contract. Some stations are deterministic code: intake, gates, the approver and human triage. Agent stations are explicit contracts, a manifest plus a prompt packet. The runner never pretends a model ran: for an agent station it writes a packet file and marks the step packet_ready.

A project keeps everything in its repo: specs, tests, reviews, run reports, envelopes and a brain folder with context and decisions.

The factory ships 8 pipelines and over 500 tests covering the full SDLC, content production, and greenfield builds.

## One core, two domains: software and content

The factory core (work orders, pipelines, gates, envelopes, approver, human triage, brain) does not care what the line produces. Domains are station sets that plug into the same core:

- **Software** is the default domain in this repo: spec-writer, test-writer and builder produce code, and five software reviewers check it. The spec is the contract and tests are the evidence.
- **Content** ships in the same catalog: brief-writer, researcher, writer and media-producer produce a piece, and five different reviewers check it in parallel (facts against sources, voice, platform fit, brand risk, UX). The brief replaces the spec, the source pack replaces the test base, and two deterministic gates check the brief and the AI generated disclosure on the draft.

Publishing is a risk hint in ANVIL, so a content work order that will be published always stops at the human gate before the publisher station runs. That is deliberate: the factory prepares and checks, a human decides what goes out under their name.

A worked content example with a brief, a draft and a full run lives in examples/content/why-factories. The same composition rule applies both ways: a content series can start greenfield from an idea, and a software team can borrow the researcher or the facts reviewer for a technical article line.

## Two modes: greenfield and brownfield

ANVIL is not only a line for issues on existing code. It has two modes that share the same stations:

- **Greenfield, build from zero.** The entry is an idea, not an issue. `anvil new-project` scaffolds a brand new project from a catalog blueprint (python-service, cloudflare-worker, static-site): repo structure, a brain seeded with the idea, BLUEPRINT.md with the stack and the first specs, and anvil.json pointing at the greenfield pipeline. That pipeline adds one station at the front, blueprint, which turns the idea into a project shape before spec-writer takes over. Taskline, the example repo, is a build from zero: no code existed when its work order was written. Its recorded run used sdlc-default, and the greenfield pipeline formalizes that from zero path with scaffolding and the blueprint station in front.
- **Onboarding an existing project.** `anvil onboard <path>` is the brownfield front door: it analyzes the codebase read only (stack, tests, specs, CI), adds only the factory pieces that are missing, never overwrites a file, drafts a baseline spec of the project as found, and writes ONBOARDING.md with the gaps turned into suggested first work orders. A project that already has anvil.json is refused, clearly.
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
| reviewer-design | agent | Check visual output against design system |
| approver | deterministic | Aggregate the five reviews into one verdict |
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
| reviewer-ux | agent | Content: check user experience and interaction patterns |
| publisher | agent | Content: publish only after approval and the human gate, and record where it went live |
| supervisor | agent | Between runs: watch the run record for stalls and propose one bounded pipeline recomposition |
| checks-gate | deterministic | Pre-review gate: verify protected paths, base branch, and S4 conditions before reviews run |

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

## Curated skills

Stations do not start from a bare prompt. A curated catalog of craft skills ([skills/](skills/README.md)) covers architecture, design, web, gaming and content. Before any model runs, the runner resolves which skills match each station, the work order surfaces and the product type, and writes them into that station's packet. A landing page order gives the builder the interface design and web engineering skills; a game order gives it game feel and game engineering; a content order gives the writer the writing skill. Resolution is deterministic code, recorded in report.json, and a project can replace or switch off any skill.

## Token consumption and limits

Each station runtime records input, output, cached input and retry usage in
the run report. Failed calls count too. Project status pages show totals,
measurement coverage and expandable details for every station attempt;
earlier runs remain in the total when a work order is rerun. Missing usage
stays unknown, including historical reports.

New projects include `status/index.html` and consumption controls in
`anvil.yaml`: a 12,000 token packet ceiling, 32 agent calls per run, a 250,000
token run threshold and up to 16 Claude runtime turns. These are adjustable
starting settings. Run thresholds
are checked between calls; a running call can exceed them. An agent call is
one station runtime invocation, which may contain several model/tool turns.

```bash
python3 -m anvil.cli status-page .
python3 -m anvil.cli status-page . --include-project ../my-project
python3 tools/sync_project_usage.py
```

The last command refreshes public report snapshots for Sentia, Platform25
and Taskline and generates their linked pages in the factory status site.
It uses authenticated GitHub CLI reads and makes no model calls.
See [consumption controls](docs/COST-MEASUREMENT.md) and
[project pages](docs/STATUS-PAGE.md).

## Quick start

```bash
python3 -m anvil.cli new-project ../my-new-app --name MyNewApp --blueprint cloudflare-worker --idea "What this app is for"
python3 -m anvil.cli onboard ../my-existing-project
python3 -m anvil.cli init ../my-project --name MyProject
python3 -m anvil.cli new-spec ../my-project my-feature --title "My Feature"
python3 -m anvil.cli validate-pipeline pipelines/sdlc-default.json
python3 -m anvil.cli run ../my-project --pipeline pipelines/sdlc-default.json --work-order work-order.json
python3 -m anvil.cli check ../my-project --slug my-feature
python3 -m anvil.cli check-content ../my-channel --slug my-post
python3 -m anvil.cli check-brain ../my-project
python3 -m anvil.cli check-skills ../my-project
python3 -m anvil.cli supervise ../my-project
python3 -m anvil.cli run ../my-project --pipeline pipelines/sdlc-default.json --work-order work-order.json --execute --isolate
python3 -m anvil.cli approve ../my-project wo-gh-12 --by "Your Name"
python3 -m anvil.cli resume ../my-project wo-gh-12 --execute
python3 -m anvil.cli work-order-from-issue issue.json
```

## From issue to pull request, unattended

One workflow, [.github/workflows/anvil-line.yml](.github/workflows/anvil-line.yml), runs the line for any work order. Label an issue `anvil` and the line runs on its own branch (`anvil/wo-gh-<number>`), corrects itself through real loopbacks (a failed review or a failed checks gate sends the work back to the builder with the findings, up to two times), opens a pull request and reports on the issue. When a human must decide, a maintainer comments `/anvil approve` on the issue: the approval is recorded against that run and the line resumes after the gate to deploy or publish. `anvil run --execute` exits 0 when approved, 1 when not, 3 when a human must act and 4 when intake stopped the order, so any CI can gate on it. See [docs/EXECUTION.md](docs/EXECUTION.md).

Installed as a package, the same commands are available as `anvil new-project`, `anvil onboard`, `anvil init`, `anvil new-spec`, `anvil validate-pipeline`, `anvil run`, `anvil check`, `anvil check-brain` and `anvil supervise`.

Project station settings live in `anvil.yaml` at the project root: context, model, prompt and tools per station. See docs/ARCHITECTURE.md for the Core Four.

The factory's own stations run on Anthropic models, reached one of two ways chosen by the `ANVIL_RUNTIME` variable: Claude Code through the Cloudflare AI Gateway (`claude-gateway`, the default) or GitHub Copilot CLI with a GitHub account (`copilot`).

Agent runtimes are pluggable: add a `runtime` object to anvil.yaml and run with `--execute` to have a command or HTTP executor run the station packets, with reviewer output feeding the approver of the same run. A `deploy` object in the same file lets an approved, unblocked run deploy automatically and pass a deterministic verification gate. Every step records which model was configured and, for executed steps, which model actually ran. See docs/EXECUTION.md.

Memory is gated like code: agent written learnings wait in a quarantined inbox and reach the verified store only when deterministic code verifies their provenance against the run record. See docs/MEMORY-GATE.md.

The supervisor watches run reports between runs and proposes pipeline recompositions built only from the station catalog, under a constitution it cannot amend, and nothing it proposes applies itself. See docs/SUPERVISOR.md.

## The brain

The brain/ folder holds project.md (what the project is and its principles), glossary.md, decisions/ (numbered decision records) and worklog.md. Stations read the brain as context, so decisions survive beyond a single run. Verified learnings live in brain/learnings.md behind the memory gate, with proposals quarantined in brain/inbox/ until their provenance verifies (docs/MEMORY-GATE.md).

## Pipelines included

- sdlc-default: the full SDLC line, intake to observer with five parallel reviewers.
- hotfix: a short line for urgent fixes, with spec and security review.
- docs-only: intake, builder, one review and the approver.
- scout: a single read only recon station, no code changes.
- plan-build-test: intake, spec, tests, build, test review and approver.
- greenfield: the from zero line. Intake, blueprint, spec, tests, build, the five parallel reviewers, approver, human triage, deployer and observer.
- content-default: the full content line. Intake, brief, research, writing, media, five parallel content reviewers, approver, human triage, publisher and observer.
- content-short: a short content line for posts. Intake, brief, writing, facts and voice review, approver, human triage and publisher.

## Intake worker

intake-worker/ is a Cloudflare Worker in plain JavaScript with no dependencies. POST /work-orders validates and normalizes a work order and returns 201. GET /health returns ok. POST /github accepts GitHub webhook deliveries: set GITHUB_WEBHOOK_SECRET on the Worker to require a valid X-Hub-Signature-256 HMAC (invalid signature returns 401), and issues opened, or labeled with the label anvil, are mapped to a work order (kind task when the issue carries the task label) and returned with 202; other events are acknowledged and ignored. Tests run with `node --test "intake-worker/*.test.js"`.

GitHub dispatch: set GITHUB_REPO and GITHUB_TOKEN in the Worker environment and the worker forwards work orders to the line as a repository_dispatch event of type anvil-work-order, which the anvil-line workflow runs. Only a signature verified issue delivery labeled anvil is forwarded, and POST /work-orders forwards only with the INTAKE_TOKEN bearer; the response reports whether the forward happened. No secrets live in the repo.

## Contributing

Every change starts with a spec under .openspec/specs/ (OpenSpec). Write the spec, write tests that map to its scenarios, then implement. Keep runtime code on the Python standard library only.

## Documentation

| Document | What it covers |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layers, artifact flow, gates, risk triage, Core Four, model stack, loopback, envelopes, observability |
| [docs/SDLC.md](docs/SDLC.md) | How the default pipeline maps to SDLC phases |
| [docs/EXECUTION.md](docs/EXECUTION.md) | Agent runtime executors, the runtime contract, automatic deploy and post deploy verification |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Operating the line: live run state and events, export to a webhook or OpenTelemetry, the approvals policy, what a station can reach, and a preview per work order on Cloudflare or GitHub Pages |
| [docs/STATUS-PAGE.md](docs/STATUS-PAGE.md) | The run status page: generation, publishing to Cloudflare Pages or GitHub Pages, and the snapshot note |
| [docs/MEMORY-GATE.md](docs/MEMORY-GATE.md) | Verified learnings: the inbox flow, the provenance format, and why memory writes are gated |
| [docs/SUPERVISOR.md](docs/SUPERVISOR.md) | The bounded supervisor: stall signals, the constitution, the proposal lifecycle, and what it can never do |
| [docs/OPERATOR-REQUIREMENTS.md](docs/OPERATOR-REQUIREMENTS.md) | Operator credentials and permissions: the GitHub PAT, the Cloudflare token and AI Gateway shape, and where each lives in the Secure Vault |
| [brain/project.md](brain/project.md) | Principles and project context |
| [templates/spec.md](templates/spec.md) | The spec template every spec starts from |

## License

[Apache 2.0](LICENSE)

Copyright Eduardo Arana

---

## Developer

Eduardo Arana

## Support this with a ko-fi

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/H2H51MPWG)

---

If ANVIL is useful to you, a star helps other builders find it.

---

## Metadata Update (Operator Step)

This README is ready for merge. The following repository metadata updates are operator steps to be completed after merge via the GitHub web interface:

- **Homepage**: https://anvil-status.pages.dev
- **Topics**: ai-agents, multi-agent-systems, software-factory, sdlc, llm, code-generation, code-review, openspec, spec-driven-development, ai-coding, developer-tools, python
- **Social preview image**: Upload runs/wo-gh-23/evidence/social-preview.png (1280x640) via Settings > General > Social preview
- **Description**: Current repository description is retained. Alternative available in work order if owner approval needed.
