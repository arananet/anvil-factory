# Rendered Design Review

Status: approved
Slug: rendered-design-review

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
reviewer-design judges interface work by reading source, and source does not show what a page actually looks like: spacing collapses, type scales and layout breaks are invisible in markup. This spec makes design review evidence based for web projects: the run serves the built project, captures screenshots at defined breakpoints, stores them as run evidence, and puts them in reviewer-design's packet so its findings cite the rendered page. When the page cannot be served or captured, the review says so plainly and falls back to source; it never pretends to have seen a render it did not see.

## Requirements
- A project declares a servable web page in its configuration: a serve command (or a static root to serve), the page path to capture, and capture breakpoints (viewport width and height pairs). Defaults when breakpoints are not declared: a phone viewport (390 by 844) and a desktop viewport (1440 by 900).
- The capture step belongs to the runner and station contract: after the builder completes and before reviewer-design's packet is built, the runner starts the project's server on a local port, waits for the page to answer, captures one screenshot per breakpoint with a headless browser, and stops the server. Captures land in the run's evidence directory as PNG files named by breakpoint (for example screenshot-390x844.png), and the run report lists them as evidence with their paths.
- reviewer-design's packet gains a Rendered evidence section when captures exist: the screenshot file names and their evidence paths, and the instruction that findings about layout, scale and spacing must cite the rendered evidence where it applies. In runtimes whose packets can carry images, the images themselves are attached; where the packet is text only, the paths are the citation targets and the executing runtime is expected to open them.
- The capability is scoped to projects that declare a servable page. A project with no serve declaration gets no capture step and reviewer-design proceeds as today; the report records that no rendered evidence was configured.
- When serving or capture is attempted and fails (the server does not answer, the capture tool errors, a breakpoint fails), reviewer-design's recorded review carries an explicit note that rendered evidence could not be captured and the review judged source only, with the failure reason. The run does not fail for a capture failure, and no screenshot evidence is claimed in the report for captures that did not happen.
- Executed runs in GitHub Actions follow the same contract through the project workflow wiring pattern: Playwright and Chromium are preinstalled in the workflow by the operator (the builder must not modify files under .github/workflows/). The serve and capture step runs in factory code or the capture module, and the evidence exists in the run's committed evidence exactly as a local capture would produce it.
- Demonstration: the capability is demonstrated on the factory's own status page (the servable static page this repo ships at status/index.html). The demonstration run's evidence directory must contain the captured screenshots of the served status page, referenced from that run's report. This demonstration is completed in the current run, not deferred.

### Security
The implementation must enforce these security constraints:
- **Command injection prevention**: serve_command configuration values must be executed without shell expansion. Use subprocess with shell=False and split the command with shlex.split, or maintain an allowlist of permitted serve commands. Never pass serve_command to shell=True.
- **Path traversal prevention**: static_root configuration values must be validated to remain within the project directory. Resolve the path and verify it does not escape project_dir boundaries. Reject values like ../../../etc that attempt directory traversal.
- **URL path injection prevention**: page_path configuration values must be validated before concatenation to base URLs. Require page_path to start with '/' and contain no '..' sequences.
- **Port collision prevention**: do not hardcode server ports. Use dynamic port allocation or a configurable port with automatic fallback to prevent collisions when multiple captures run concurrently.
- **Dimension validation**: breakpoint width and height values must be bounded. Validate that width is between 1 and 7680 pixels, and height is between 1 and 4320 pixels, to prevent memory exhaustion from extreme values.
- **Subprocess cleanup**: when terminating a server process, clean up the entire process group with os.killpg to ensure spawned child processes do not remain behind.
- **Evidence directory permissions**: create evidence directories with owner-only permissions (0o700) to protect captured screenshots.

### Testing discipline
The capture module must have a testable seam: tests must import the capture module and packet functions, call validation functions with inputs that must raise and inputs that must pass, call packet_rendered_evidence_section with real capture result objects and assert the markdown lists the screenshots with their citations, and drive capture_breakpoints through the injectable seam with mock serve and capture functions, asserting the mocks were called and that server-never-answers and capture-error configurations record the failure notes this spec requires. Tests stay deterministic and browser-free through the seam, following the factory suite style. Tests do not run the actual capture in the critical path. The test-writer station writes test changes; the builder does not modify tests/, anvil.json, pipelines/ or .github/workflows/.

## Scenarios

### Scenario: A servable project produces screenshot evidence at the defined breakpoints
- S1: Given a project that declares a serve command, a page path and two breakpoints, when a run reaches design review, then the evidence directory holds one PNG per breakpoint named by its dimensions, and the run report lists both as evidence.

### Scenario: reviewer-design's packet carries the rendered evidence
- S2: Given captures exist for a run, when reviewer-design's packet is built, then it contains a Rendered evidence section naming the screenshots and instructing that layout findings cite them; and given no captures exist because none were configured, then the packet contains no such section and the report records that no rendered evidence was configured.

### Scenario: Capture failure is recorded and the review falls back to source
- S3: Given a project whose server never answers, when capture is attempted, then the run completes, reviewer-design's recorded review states that rendered evidence could not be captured with the reason and that it judged source only, and the report claims no screenshot evidence.

### Scenario: The demonstration run holds real screenshots
- S4: Given the factory status page (status/index.html) declared servable in anvil.yaml, when the current demonstration run completes, then the run's evidence directory at runs/wo-gh-9/evidence/ contains the breakpoint screenshots of the served factory status page, and the run report references them as evidence.
