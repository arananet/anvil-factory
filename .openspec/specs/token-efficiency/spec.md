# Token efficiency and project usage pages

Status: proposed
Slug: token-efficiency

## Purpose

The command runtime currently discards usage. Owners cannot see how many
tokens a project consumed, including retries and failed calls, or control
how much context and work each station uses. Make consumption visible and
bounded without weakening the spec, tests, reviewer contracts or approval gates.

## Requirements

R1. Capture runtime evidence. Claude stations use JSON results and Codex
stations use JSONL events. Record input, output, cached input, cache creation,
reasoning and total tokens when reported. Cached and reasoning tokens are
subsets, never added twice. Missing or malformed usage is unknown, not zero.

R2. Every attempt counts. Write a separate, versioned usage artifact for each
station invocation, containing one scalar-only record per attempt, including
corrections, runtime failures and timeouts. Preserve usage on executor errors.
Never recover a review from the free transcript or copy configured model
labels into executed-model evidence. Never publish prompts, credentials,
environment variables or raw runtime events as telemetry.

R3. Aggregate honestly. Reports and pages include measured token totals,
measurement coverage, attempts, retries and breakdowns by station and model.
Partial totals are labeled partial. Historical reports remain usable and
unmeasured historical spend is explicitly unknown. Cost requires a recorded
price source or is labeled as a runtime estimate, never as an invoice.
Rerunning a work order preserves earlier reports in the project totals.

R4. Reduce consumption. Apply configured packet limits to every agent station,
omit interface design context for nonvisual work, bound runtime turns where
supported and bound retained Codex tool output. A configurable run token
threshold and agent-call limit stop subsequent calls with a recorded budget
outcome. These thresholds act between calls; a running call may overshoot.
Required spec and review contracts are never silently truncated. Record
unmeasured calls and support refusing further calls when usage is required.

R5. Project pages. Every new project gets a static usage/status page. Executed
runs refresh it after writing their report. Include project totals, per-run
totals, per-station input/output/cache details, and expandable attempt records.
Distinguish initial packet estimates from runtime consumption. Keep lifecycle
information and existing anchor links. Use escaped HTML and accessible,
responsive, self-contained pages.

R6. Factory portfolio. The status-page command accepts additional project
roots, emits one page per project and links their totals from the factory
page. Do not publish local absolute paths. Project slugs cannot escape the
output directory or collide. Generation needs no model calls or network.
Project URLs remain stable when the checkout moves between local and CI paths.

R7. Public explanation. Update the ANVIL landing page, status-page docs,
configuration documentation and changelog to explain consumption controls,
measurement coverage, and the difference between measured and unknown usage.
Do not claim measured savings without a controlled comparison.

## Scenarios

S1. Claude cache reads/writes and Codex cached input normalize without double
counting. Empty, incomplete and negative usage do not become free calls.
S2. A reviewer requiring correction contributes both attempts; a failed CLI
with a usage result contributes its consumed tokens despite the failure.
S3. A command executor cannot reuse a stale usage artifact and transports
fresh usage through both success and ExecutorError paths.
S4. A run stops before another model call when its token or call threshold
is reached, preserves the report and page, and never reports approval.
S5. Backend packets omit design context; oversized packets fail visibly
without a model invocation; runtime flags bound supported turn/tool output.
S6. Measured, partial, zero and historical unknown reports render distinct
totals. Attempts, models, retries and failure status remain inspectable.
S7. Newly scaffolded projects have a usage page, executed runs refresh it,
and a factory portfolio links multiple projects without exposing paths.
S8. Malicious names and model labels are escaped, duplicate project names
cannot overwrite one another, and pages fit mobile and desktop viewports.

## Scope limits

Python standard library runtime. Existing local curated-skills work remains
in place. No automatic merge, model migration or review bypass. Public
deployment follows the existing owner authorization and credential workflow.
