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
- Executed runs in GitHub Actions follow the same contract through the project workflow wiring pattern: the workflow gains a serve plus headless capture step (installing the headless browser in the workflow, as it installs other runtimes) so the evidence exists in the run's committed evidence exactly as a local capture would produce it.
- Demonstration: the capability is demonstrated on the factory's own status page (a servable static page this repo already ships) or on the example project, and the demonstration run's evidence directory contains the captured screenshots, referenced from that run's report.

## Scenarios

### Scenario: A servable project produces screenshot evidence at the defined breakpoints
- S1: Given a project that declares a serve command, a page path and two breakpoints, when a run reaches design review, then the evidence directory holds one PNG per breakpoint named by its dimensions, and the run report lists both as evidence.

### Scenario: reviewer-design's packet carries the rendered evidence
- S2: Given captures exist for a run, when reviewer-design's packet is built, then it contains a Rendered evidence section naming the screenshots and instructing that layout findings cite them; and given no captures exist because none were configured, then the packet contains no such section and the report records that no rendered evidence was configured.

### Scenario: Capture failure is recorded and the review falls back to source
- S3: Given a project whose server never answers, when capture is attempted, then the run completes, reviewer-design's recorded review states that rendered evidence could not be captured with the reason and that it judged source only, and the report claims no screenshot evidence.

### Scenario: The demonstration run holds real screenshots
- S4: Given the demonstration target (the factory status page or the example project) declared servable, when its demonstration run completes, then its evidence directory contains the breakpoint screenshots and its run report references them.
