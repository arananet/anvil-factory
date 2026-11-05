# Rendered Design Review

## Purpose

reviewer-design judges interface work by reading source, and source does not show what a page actually looks like: spacing collapses, type scales and layout breaks are invisible in markup. Rendered design review makes design review evidence-based for web projects: the run serves the built project, captures screenshots at defined breakpoints, stores them as run evidence, and puts them in reviewer-design's packet so its findings cite the rendered page.

When the page cannot be served or captured, the review says so plainly and falls back to source; it never pretends to have seen a render it did not see.

## Configuration

Projects declare a servable web page in `anvil.yaml`:

```json
{
  "version": 1,
  "servable": {
    "static_root": "dist",
    "page_path": "/index.html",
    "breakpoints": [
      {"width": 390, "height": 844},
      {"width": 1440, "height": 900}
    ]
  }
}
```

### Configuration fields

- **serve_command** (optional): Shell command to start the server. Use `{port}` as a placeholder for the dynamically allocated port. Example: `"npm start -- --port {port}"`
- **static_root** (optional): Directory to serve as a static site. Either `serve_command` or `static_root` must be specified.
- **page_path** (required): URL path to capture, e.g. `"/index.html"`. Must start with `/` and contain no `..` sequences.
- **breakpoints** (optional): List of viewport dimensions. Each breakpoint is `{"width": <int>, "height": <int>}`. Defaults to phone (390x844) and desktop (1440x900).

### Security constraints

The implementation enforces these security constraints:

- **Command injection prevention**: `serve_command` values are executed without shell expansion using `shell=False` and `shlex.split()`
- **Path traversal prevention**: `static_root` values are validated to remain within the project directory
- **URL path injection prevention**: `page_path` must start with `/` and contain no `..` sequences
- **Port collision prevention**: Ports are dynamically allocated, not hardcoded
- **Dimension validation**: Breakpoint dimensions are bounded (width 1-7680, height 1-4320)
- **Subprocess cleanup**: Server processes are terminated with `os.killpg` to clean up entire process groups
- **Evidence directory permissions**: Evidence directories are created with owner-only permissions (0o700)

## Capture workflow

1. After the builder station completes successfully in execute mode, the runner checks for servable configuration in `anvil.yaml`
2. If no servable configuration exists, capture is skipped and no evidence is produced
3. If servable is configured:
   - The runner finds a free port dynamically
   - Starts the server (static HTTP server or custom serve command)
   - Waits for the server to respond (10 second timeout)
   - Captures one PNG screenshot per breakpoint using Playwright/Chromium
   - Stops the server and cleans up all processes
   - Stores screenshots in `runs/<work-order-id>/evidence/` named `screenshot-<width>x<height>.png`
4. Capture results are recorded in the run report's `evidence` field

## reviewer-design packet

When screenshots exist for a run, reviewer-design's packet includes a "Rendered evidence" section:

```markdown
## Rendered evidence

This run captured screenshots of the served project at the following breakpoints:

- `screenshot-390x844.png` at `runs/wo-123/evidence/screenshot-390x844.png`
- `screenshot-1440x900.png` at `runs/wo-123/evidence/screenshot-1440x900.png`

**Design review instruction:** When judging layout, scale, spacing, 
or visual hierarchy findings, cite the rendered evidence screenshots 
where applicable. The screenshots show what the page actually looks like 
at each breakpoint, not just what the source implies.
```

When capture is attempted but fails, the packet documents the failure:

```markdown
## Rendered evidence

**Note:** Rendered evidence could not be captured for this run. 
Reason: server did not answer within timeout. 
This review judged source only.
```

When no servable is configured, no rendered evidence section appears in the packet.

## Run report evidence

Successfully captured screenshots are listed in the run report's `evidence` field:

```json
{
  "work_order_id": "wo-123",
  "evidence": [
    {
      "type": "screenshot",
      "breakpoint": "390x844",
      "path": "runs/wo-123/evidence/screenshot-390x844.png",
      "width": 390,
      "height": 844
    },
    {
      "type": "screenshot",
      "breakpoint": "1440x900",
      "path": "runs/wo-123/evidence/screenshot-1440x900.png",
      "width": 1440,
      "height": 1440
    }
  ]
}
```

## Testing

The capture module has injectable seams for testing. Unit tests cover:

- Configuration validation (security constraints)
- Packet section generation with and without captures
- Failure recording and handling
- Evidence listing in reports

Real browser capture happens only in integration scenarios, not in the unit test critical path.

## Example: Factory's own status page

The factory itself demonstrates rendered design review on its own status page. See `anvil.yaml`:

```json
{
  "servable": {
    "static_root": "status",
    "page_path": "/index.html"
  }
}
```

The status page at `status/index.html` is generated by `anvil status-page .` and served during runs. Screenshots of the factory's own run status page are captured as evidence.

## Dependencies

Rendered design review requires Playwright and Chromium:

```bash
pip install playwright
playwright install chromium
```

In GitHub Actions workflows, these are preinstalled by the operator before the run step.
