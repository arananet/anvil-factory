# I stopped prompting agents one chat at a time, and built a factory instead

[IMAGE: cover.png]

Here is the honest version of how my work with coding agents looked a few months ago.

I opened a chat. I explained the project, again. I pasted context, again. The agent wrote something plausible, I reviewed it line by line, found the part where it had invented an API, fixed the prompt, and started over. For a small change, fine. For anything that mattered, I had quietly become two things I did not want to be: the bottleneck and the quality gate.

The agent was not the problem. The way I was using it was. One chat is a conversation. What I needed was a process that runs the same way every time, whether I am watching it or not.

So I built ANVIL.

ANVIL stands for Agentic Network for Verified Implementation Lifecycle. It is an open source framework, Apache 2.0, that treats software work the way a factory treats production. Work does not wander through chats. It moves down a line.

It runs on two pieces of technology I already trust, and nothing exotic. GitHub holds the code, the issues that become work orders, and the automation that runs the line. Cloudflare provides the edge: the intake that receives work runs as a Worker, and anything the factory publishes or serves can live there too. No new platform to learn, no vendor invented for the occasion.

## The line

[IMAGE: diagram-1-the-line.png]

Everything enters ANVIL as a work order. That can be an idea, a feature, a bug, an incident, a plain task, or a piece of content. The work order is the unit of work, and it moves through stations.

A spec writer turns it into an OpenSpec spec, with requirements and numbered scenarios. A test writer turns those scenarios into tests before any implementation exists. A builder writes the code that makes the tests pass. Then four reviewers look at the result in parallel, each with a different job: one checks the work against the spec, one checks security, one checks the tests, one checks the architecture.

An approver aggregates the four reviews into a single verdict. It does not fix anything and it does not review its own side of the line. If the verdict is no, the work loops back to the builder or to the spec writer with the findings attached. If the work touches something risky, a separate triage station decides whether a human has to look before it ships. Auth, payments, data deletion, production deploys, secrets: those always need a human. No exceptions configured away in a settings file.

After shipping, an observer station closes the loop and the run leaves a report behind: what each station did, how long it took, and what it produced.

## Agents propose, code disposes

The part that changed my thinking is what is not an agent.

The pipeline engine is deterministic code. The gates are deterministic code. The check that every scenario in a spec has a matching test is code, and it fails the run if the mapping is missing. The approver aggregation is code. The risk triage is code.

That split is deliberate. Models are rented. You do not own them, their prices change, their behavior drifts between versions. Code is the opposite: it costs almost nothing to run, it does the same thing every time, and you own it outright. So ANVIL puts the validating in code and the creating in agents. Anything a machine can check mechanically should never consume a model's attention, and should never depend on a model remembering to check it.

The agent stations still matter, obviously. Writing a good spec, building an implementation, reviewing for security: that is judgment work, and that is what models are for. They just do it inside a structure that verifies what they produce.

## Composable stations, and the Core Four

[IMAGE: diagram-3-station.png]

A station in ANVIL is a small thing: a manifest, a prompt, and a contract about what it takes in and what it produces. There are 24 of them in one catalog, and a pipeline is just a JSON file that lists stations in order, with the parallel ones grouped. Eight pipelines ship with it. The default is the full SDLC line. There are shorter ones for a hotfix, for docs only, for a read only scouting pass, and for content.

Every station is configured through four things: its context, its model, its prompt, and its tools. Those four live in one file per project, anvil.yaml, so tuning the whole roster is editing one place. It also means the model question stops being which single model is best. Different stations get different models: a strong reasoning model for the spec writer, a fast one for the builder, a balanced one for reviewers. It is a model stack, assigned per role, and changing it is a config edit, not a rewrite.

And one rule is baked into every station contract: a station never approves its own work. The builder does not get a vote on whether the build is good. That sounds obvious. In agent systems it is surprisingly easy to end up with exactly that, one agent generating, checking and approving its own output in a single pass, which is not quality control. It is self approval with extra steps.

## Build from zero, or start from what exists

Most factory talk assumes a greenfield that does not exist. ANVIL has a greenfield mode for the cases where it does: an idea enters as a work order, a blueprint station picks a starting shape from a small catalog, and a single command scaffolds the whole project, brain, specs and pipelines included.

The other mode is the one most of us actually live in. Existing projects get onboarded, not rewritten. The onboard command analyzes a codebase read only, adds only the factory files that are missing, and never overwrites anything. It drafts a baseline spec that describes the project as it was found, marked as a draft, because a description of what exists is not the same thing as an intent. The gaps it finds, no tests, no CI, no specs, come back as suggested first work orders.

## One core, software and content

[IMAGE: diagram-2-domains-modes.png]

Halfway through building this I noticed the line did not actually care what it was producing.

So the same core also runs a content factory. The stations change: a brief writer instead of a spec writer, a researcher who builds a source pack, a writer, a media producer, and four different reviewers working in parallel, checking facts against sources, voice, platform fit and brand risk. The brief replaces the spec. The source pack replaces the test base. The failure modes rhyme: software fails when code drifts from a spec, content fails when a draft drifts from its sources.

One rule I care about personally made it into the triage list. Publishing is treated as a risk, in the same set as payments and data deletion. A content work order always stops at the human gate before the publisher station. The factory can prepare and check everything. What goes out under my name is still my decision.

## Memory that has to earn trust, and evolution with a constitution

Two recent additions came from reading research on evolving agent teams, and disagreeing with half of it.

The research is right that a fixed team can plateau: the roles a task needs change as the work changes. It is also, in my view, careless about the other half: its teams write what they learn into a shared record, and the next team trusts it, with no check on whether the lesson was ever true. One confident, wrong observation, recorded early, becomes doctrine. I work on exactly that failure mode in my own research, so ANVIL now treats memory the way it treats code.

Learnings proposed by agents land in an inbox, quarantined. A learning is promoted into the project brain only when it carries provenance that verifies: the run it came from, the artifact, and the evidence, checked against the actual run report. A claim that cites a run that rejected the work does not get promoted, and the refusal says why. Station packets read only verified learnings. Memory in ANVIL is not a diary. It is a gated store.

And the team can evolve, within limits. A supervisor station watches for stalls, the same reviewer failing across runs, loopbacks exhausted, a deploy that failed verification, and proposes a recomposition of the line. But it may only compose from the existing station catalog, the proposal must pass the pipeline validator, and a constitution it cannot amend protects the core: intake, the approver and the human triage are always present, and the reviewer set can grow but never shrink. Proposals are filed with their reasoning and evidence. Nothing applies itself; a human points a run at a proposal, or it stays a proposal. Evolution, yes. Self-modifying governance, no.

## The honest limits

I would rather state these plainly than let the diagrams oversell it.

The deterministic spine runs for real: the engine, the gates, the approver, the triage, the scaffolding, the onboarding, the run reports. The agent stations start as contracts plus task packets, and there is now an execution mode that sends those packets to a runtime you configure yourself: a command template for an agent CLI, Claude Code or Codex style, or an HTTP endpoint in the OpenAI shape. Reviewer output is parsed back into reviews, the approver only counts reviews produced in that same run, and every step records which model was configured for it and, when it executed, which model actually ran, because a result you cannot attribute to a model is a result you cannot reproduce. The run report records what actually executed. ANVIL ships no model of its own, and your keys stay in your environment, never in the config file.

What is not proven yet is the last mile: a full run where a real model does the building and the reviewing on a real change, end to end. The public examples are honest about which parts used packets and which used a small stand-in executor, and they are labeled that way in the repos. That full model run is the next job, and now it is a small one: pick a runtime, point the config at it, open an issue.

## What the examples prove

Talk is cheap, so both repos carry their evidence.

The example project, Taskline, is a small task API built from zero on the line. Its repo contains the whole trail: the original work order, the approved spec with six scenarios, the tests written first, the saved output of those tests failing before any implementation existed, the implementation, the output of the same tests passing, the four reviews, and the run report. Nothing in that chain is a screenshot or a claim. It is files you can open.

The content example is smaller and, to me, more telling. Its demo run went down the content line, produced its packets, and stopped at the human gate, because publishing requires a human. The factory refusing to finish the job on its own is not a bug in the demo. It is the demo.

The trigger is live, too. Open an issue on the example repo, label it anvil, and a GitHub Actions workflow runs the line on it and posts the run report back as a comment on the issue. You can watch it happen on a real one: a test coverage gap I filed as issue 3. Its verdict reads no_reviews, because in that run the reviewer stations produced packets and no runtime executed them, and the report says so instead of borrowing the reviews from an earlier build. A separate demonstration run goes further: executed stations, an automatic deploy, and a verification pass against the deployed copy, ending in the state the factory calls deployed_verified. Every run of the example is on a public status page, generated from the run reports themselves: https://anvil-status.pages.dev

The front door is a Cloudflare Worker: it receives GitHub webhooks, verifies their signatures, and turns issues into normalized work orders, so the line starts from a real event and not just a command line.

## Where to look

ANVIL is Apache 2.0 and open source:

Factory: github.com/arananet/anvil-factory
Example: github.com/arananet/anvil-example-taskline
Live run status: https://anvil-status.pages.dev

Eighty nine tests cover the factory itself, six cover the example, nine cover the intake worker, and every gate I described is exercised by test suites and gate checks you can reproduce locally. If you build agent workflows, I would genuinely like to hear where this design breaks for you: which station is missing, which gate you would never accept, which part you think should be an agent and I made code, or the reverse. That feedback is worth more to me than a star.

## Credit where it is due

The factory idea is not mine, and I would rather point at my sources than pretend otherwise. Two videos explain the same concept, from different starting points, and ANVIL is what I built after watching both and deciding to answer them with my own design, my own wording and my own stack:

"Programming with AI agents is no longer enough: build your own Software Factory", by Eric Risco: https://youtu.be/p6nnqerea7w

"My Super Simple Software Factory (For Agentic Engineers)", by Dan (disler): https://youtu.be/haUfb1ievTE

If the concept is new to you, watch those first. They explain it better than a summary would. What I took from them is the shape of the idea. Everything in ANVIL itself, the stations, the gates, the config, the code, is my own build.

That's where I stand today. I reserve the right to change my mind tomorrow. In AI, that's not flip-flopping, it's keeping up. 🥤
