# Enterprise port: secret hygiene, Copilot telemetry and operator guide, reconciled to the single-runtime design

## Problem

A body of factory work exists only as a patch produced outside this
repository (the order's source artifact,
work-orders/artifacts/issue-44-anvil-enterprise-port.patch, supplied by the
owner on 2026-11-15). It carries four things the factory wants: a hardened
secret hygiene package (factory .gitignore, a project .gitignore template
the scaffold installs, a secret scanning test), Copilot runtime telemetry
(token usage and failure reasons read from the Copilot session output), a
usage sync flag for private repositories, and a consolidated operator
guide. The patch was cut against a divergent base: it does not apply to
current main, its Copilot support arrives as a second station wrapper
(tools/copilot_station.py), and its Copilot model mapping includes
openai/gpt-6.1-sol.

## Decision basis

Owner's order, 2026-11-15: port the patch with corrected scope. The
corrections are decisions, not discoveries for the line to make:

- Decision 0008 stands: one family of models, no OpenAI route.
- Decision 0010 stands: the runtime is selected by ANVIL_RUNTIME
  (claude-gateway default, copilot as the second door to the same models),
  and one wrapper holds the station contract for both runtimes. The port
  strengthens that wrapper; it does not add a parallel one.
- Decision 0012 stands: Anthropic only. Under Copilot the mappable models
  are the Anthropic ids (claude-opus-5-5, claude-sonnet-5-5,
  claude-fable-5-2, in the dotted Copilot form where the runtime requires
  it). Any non-Anthropic model id under any runtime fails loudly.
- Produced files carry no employer or organization names beyond ANVIL and
  arananet. The patch itself is already clean on this point; the port
  keeps it that way.

## Requirements

R1. Secret hygiene. The factory .gitignore gains the patch's secret and
credential rules. templates/project.gitignore is added with the patch's
project rules. anvil/scaffold.py installs that template as a new project's
.gitignore when none exists and never overwrites an existing one. The
patch's greenfield pipeline wording fix in scaffold lands with it.

R2. Secret scanning test. The patch's secret scan arrives as a new test
file (tests/test_secret_scan.py): it scans tracked factory files for the
credential patterns it names (cloud keys, private keys, tokens) and fails
naming the file and pattern. It must pass on the ported tree.

R3. Copilot telemetry inside the single wrapper. anvil/telemetry.py gains
the patch's Copilot parsing: token usage from the session's accounting
snapshot (modelMetrics) and the failure reason from its session.error
event. The parsing is wired into the existing runtime path
(tools/claude_station.py and tools/copilot_runtime.py per decision 0010),
so a failed or completed Copilot station records the same usage and
failure evidence the gateway path records. No new station wrapper file is
created; tools/copilot_station.py from the patch is not ported as a file.

R4. Anthropic-only Copilot mapping. Wherever the Copilot runtime maps
ANVIL model ids to Copilot ids, the map contains only the Anthropic
models named in the decision basis. A configured non-Anthropic model
under the copilot runtime fails loudly with no fallback, matching the
gateway path's behaviour. The patch's dispatch changes are ported only
where they serve the existing runtime selection (decision 0010); dispatch
behaviour for the default gateway runtime is unchanged.

R5. Usage sync. tools/sync_project_usage.py gains the patch's
--allow-private flag: private and internal repositories are refused
unless the flag is passed. Its behaviour without the flag is unchanged.

R6. Operator documentation. docs/OPERATOR-GUIDE.md is added, ported from
the patch and corrected where the patch describes its divergent design:
one wrapper, runtime selection by ANVIL_RUNTIME, Anthropic-only model
mapping, gateway as default. docs/EXECUTION.md gains the patch's runtime
section in the same corrected form. README.md and CHANGELOG.md gain the
patch's entries, adjusted to the same corrections.

R7. Tests. The patch's new tests arrive as new files, adapted to the
single-wrapper design: tests/test_secret_scan.py (R2),
tests/test_sync_project_usage.py (R5), and the Copilot runtime tests
covering R3 and R4 (usage parsing, failure reason, Anthropic-only map,
loud failure on a non-Anthropic id). Existing test files at the base ref
are not modified. The full factory suite passes and check-skills passes.

## Scenarios

S1. Scaffolding a new project produces a .gitignore identical to
templates/project.gitignore; scaffolding over a folder that already has a
.gitignore leaves that file byte-identical.

S2. The secret scan test fails on a fixture file containing a planted
credential pattern and passes on the ported tree.

S3. A Copilot session fixture with an accounting snapshot records token
usage in the run's telemetry; a fixture with a session.error event
records its message as the station's failure reason.

S4. Configuring openai/gpt-6.1-sol for a station under ANVIL_RUNTIME=copilot
fails loudly before any model call; the same station on claude-opus-5-5
dispatches normally.

S5. sync_project_usage without --allow-private refuses a private
repository; with the flag it imports it.
