# Reviewer UX: The Experience Lens

Status: approved
Slug: reviewer-ux

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
The factory's design review has one lens: reviewer-design judges visual compliance against the project's design system, and it is good at exactly that: tokens honored, type scale respected, spacing on rhythm, palette in bounds. None of that says whether a person can actually use the page. This spec adds the second lens as its own station: reviewer-ux judges the experience itself, how a user moves through the page, whether the primary task can be completed, whether the interface follows basic usability and accessibility practice, and whether its words say what they mean. The lenses stay separate on purpose: a page can be perfectly on-system and still be unusable, and each failure deserves its own name.

## Requirements
- reviewer-ux is a station in the catalog (stations/reviewer-ux/, agent kind) answering in the standard review format (station, verdict, findings). Its contract judges four things: user flows and task completion (can the page's primary task be started, followed and finished from what the interface presents), usability heuristics (visibility of state, match with the real world, user control, consistency, error prevention and recovery, recognition over recall, in the plain vocabulary of the contract), accessibility basics (labeled controls, focus visibility, contrast against the design system's own tokens, text alternatives for meaningful images, keyboard reachability of interactive elements), and clarity of the interface copy (labels, buttons and messages that name what they do).
- reviewer-ux belongs to the UX module: its catalog entry carries the same guided design station designation as the other design stations, naming the design model from the recorded routing policy as its designated model.
- Its packet is informed by two evidence sources beyond the change itself: the UX rules slice of the design knowledge base (the guidelines matched to the project's product type, by the design knowledge mechanism), and, where the run produced rendered screenshots, the screenshots rather than source alone. Where no screenshots exist for the run, the review records that it judged from source and the knowledge slice, and it does not claim rendered evidence it did not see.
- Presence is routed, not static: reviewer-ux is a member of the reviewer group of the pipelines that serve web UI work (sdlc-default, content-default, content-short, the same pipelines reviewer-design serves), and the routing step activates it only when the work order carries a ui surface. On work without a ui surface it is routed out before execution, recorded as routed out with the surface rule named, and the approver treats it as not expected, exactly as routing already treats any routed out reviewer. Non-UI work never pays for this lens.
- The two lenses never merge: the run report lists reviewer-design and reviewer-ux as separate review entries with their own verdicts and findings, the swimlane shows them as separate steps, and the approver aggregates both as independent reviews. reviewer-ux never issues findings about tokens, type scale or palette compliance (that is reviewer-design's lens), and its contract says so; its findings cite the flow, heuristic, accessibility or copy evidence behind them.

## Scenarios

### Scenario: The station exists with an experience contract
- S1: Given the station catalog as shipped by this change, when stations/reviewer-ux/ is read, then it exists as an agent station whose contract names the four judgment areas (flows and task completion, usability heuristics, accessibility basics, copy clarity), excludes visual system compliance as another station's lens, and carries the guided design station designation.

### Scenario: A UI surface activates the lens
- S2: Given a work order with a ui surface on a pipeline whose reviewer group includes reviewer-ux, when routing runs, then reviewer-ux is in the selected reviewer set, its packet carries the knowledge base guidelines slice for the project's product type, and where the run produced rendered screenshots its packet carries the rendered evidence as well.

### Scenario: No UI surface, no lens, no cost
- S3: Given a work order with no ui surface, when routing runs, then reviewer-ux is not in the selected set, it is recorded in the report as routed out with the surface rule named, the approver's expected review count excludes it, and no reviewer-ux step executes.

### Scenario: The two lenses report separately
- S4: Given a completed run where both design lenses executed, when the run report and swimlane are read, then reviewer-design and reviewer-ux appear as separate entries with independent verdicts and findings, and neither entry's text attributes the other's judgment to it.

### Scenario: Missing screenshots are declared, not papered over
- S5: Given a run with a ui surface but no rendered screenshots, when reviewer-ux's review is recorded, then it states that it judged from source and the knowledge slice without rendered evidence.
