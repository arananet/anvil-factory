# Status Page

Status: approved
Slug: status-page

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
Give anyone a single page that shows the actual status of every step of every ANVIL run in a project, generated from the run reports on disk and publishable on any static host.

## Requirements
- The generator is `anvil status-page <project> [--out DIR]` and writes a single self contained index.html with inline CSS and no external assets, so the same file works on Cloudflare Pages, GitHub Pages or any static host unchanged.
- Style follows the Arananet palette: dark background #0C0C0C, panels #1E1E1E, one orange accent #FF5C00, status expressed with white, orange and gray only, monospace labels.
- No data is invented: cost stays null, and any missing field renders as a dash.
- Each run section shows why the run ended as it did: when the report carries a decision object, the page renders the runner's own approver and human gate rule sentences; when an older report has no decision object, the page derives a minimal explanation from the recorded verdict, the human_required flag and the executed reviewer steps, and labels it derived from the run record so nobody mistakes it for the runner's own words.

## Scenarios

### Scenario: One page renders every readable run
- S1: Given a project with several runs/<id>/report.json files, when the generator runs, then the output index.html contains one section per run report, newest work order ids included alongside older ones.

### Scenario: Run header shows the run facts
- S2: Given a run report, when its section renders, then it shows the work order id, the work order title, the pipeline name, the approver verdict, the human_required flag, and the deployment status when the report carries one, or a dash when it does not.

### Scenario: Per station table shows each step as it ran
- S3: Given a run report with steps in mixed statuses (completed, packet_ready, executed, failed), when the section renders, then a table lists every station with its status, its duration and its artifacts.

### Scenario: The page is honest about being a snapshot
- S4: Given a generated page, when it renders, then it states its generation timestamp and that it is a snapshot generated from the run reports on disk, not a live feed.

### Scenario: Unreadable runs are skipped and noted
- S5: Given a run folder whose report.json is missing or corrupt, when the generator runs, then that run is skipped, the page still renders the readable runs, and the footer notes each skipped run folder.

### Scenario: The page shows the decision reasoning, recorded or derived
- S6: Given one run report that carries a decision object and one older report without one, when the page renders, then the first section shows the recorded approver and human gate rule sentences, and the second section shows a minimal explanation derived from its recorded fields and labeled derived from the run record.
