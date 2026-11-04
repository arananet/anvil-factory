# Task packet: reviewer-spec

## Station prompt

# Reviewer Spec

## Role
Check the implementation against the spec, nothing else.

## Inputs
- spec
- code change

## Outputs
- review

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.

## Output Format

Return a JSON object with this structure:

{
  "station": "reviewer-spec",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-spec", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.


## Work order

- id: wo-gh-9
- kind: feature
- title: Rendered design review: reviewer-design judges screenshots of the built page
- source: github-issue
- description: Implement the spec in .openspec/specs/rendered-design-review/spec.md in the factory.

Build, per the spec scenarios:

S1: a project can declare a servable web page in its configuration (serve command or static root, page path, breakpoints; defaults 390x844 and 1440x900). After the builder and before reviewer-design's packet is built, the runner serves the project locally, captures one PNG per breakpoint into the run's evidence directory named by dimensions, and the run report lists the captures as evidence.

S2: reviewer-design's packet gains a Rendered evidence section when captures exist, naming the screenshots and instructing that layout, scale and spacing findings cite the rendered evidence. With no captures configured, no section and the report records that no rendered evidence was configured.

S3: when serving or capture is attempted and fails, the run completes, reviewer-design's recorded review states that rendered evidence could not be captured, gives the reason, and says it judged source only; the report claims no screenshot evidence.

S4: demonstrate the capability on the factory's own status page (the servable static page this repo already ships): declare it servable in the factory project config, and hold a demonstration run whose evidence directory contains the breakpoint screenshots referenced from its report. The executed-run workflow wiring pattern gains the matching serve plus headless capture step so executed runs produce the same evidence.

Keep capture out of the unit suite's critical path: unit tests cover the packet section, the evidence listing and the failure record with the capture tool behind an injectable seam, in the factory suite style. Docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/9

GATE LOOPBACK 1 (after run 41741068693's successor run 41747657375, verdict rejected, reviews counted 5 of 5). Round 1 state, read from the run artifact (the run's commit-back was rejected, so round 1's implementation tree was lost with the run workspace and this round rebuilds it): reviewer-security returned fail, reviewer-spec changes_requested, reviewer-tests, reviewer-architecture and reviewer-design pass. Rebuild the full item (capture module, configuration, design packet evidence section, runner integration, anvil.yaml servable configuration, docs, CHANGELOG, tests) with the findings below as design constraints from the start.

Why the commit-back failed, and the standing rule it creates: round 1's builder modified .github/workflows/anvil-execute-rendered-design-review.yml, and the Actions token cannot push workflow changes (remote rejected: refusing to allow a GitHub App to create or update workflow without workflows permission). The builder must not create or modify anything under .github/workflows/ in this or any later round. The operator has preinstalled Playwright and Chromium in the workflow before the line step; any status page generation the demonstration needs happens in factory code or the capture module, never in workflow steps.

Security findings from reviewer-security (fail), all in the new anvil/capture.py, verbatim in substance:
1. CRITICAL, command injection: the serve_command from anvil.yaml is executed with shell=True via subprocess.Popen without validation. Fix: shell=False, split the command with shlex.split, or use an allowlist of permitted serve commands.
2. CRITICAL, path traversal: the static_root configuration value is used directly in Path(project_dir) / static_root without validation, so a value like ../../../etc escapes the project. Fix: resolve the path and require it to stay within project_dir.
3. HIGH, URL path injection: page_path from configuration is concatenated to base_url without validation. Fix: require page_path to start with '/' and contain no '..' sequences.
4. MEDIUM, hardcoded port: the static server port 8765 is hardcoded and can collide. Fix: dynamic port allocation or configurable port with fallback.
5. MEDIUM, unvalidated breakpoint dimensions: width and height from configuration are used unchecked; extreme values can exhaust memory. Fix: validate bounds (width 1 to 7680, height 1 to 4320).
6. MEDIUM, subprocess cleanup: terminate then kill leaves spawned children behind. Fix: terminate the process group (os.killpg) so children are cleaned up.
7. LOW, evidence directory permissions: create the evidence directory with owner-only permissions (0o700).

Spec finding (reviewer-spec, echoed by reviewer-tests): S4's demonstration must exist from this run, not be deferred. The run's evidence directory runs/wo-gh-9/evidence/ must contain the breakpoint screenshots of the served factory status page, referenced from the run report, produced by the capture step inside the line using the preinstalled Playwright and Chromium.

Discipline: test changes are written by the test-writer station; the builder must not modify tests/, anvil.json, pipelines/ or .github/workflows/. Keep the whole suite green and every pipeline valid. Update CHANGELOG Unreleased.
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: passed

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-9/reviewer-spec.review.json. The free output transcript stays as provenance and is never parsed for a review.
