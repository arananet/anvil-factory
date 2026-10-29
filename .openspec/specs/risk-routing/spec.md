# Risk and Surface Routing

Status: approved
Slug: risk-routing

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
Every run today pays for the full reviewer panel at the policy models, whether the change is a one line fix or a payments migration. This spec adds a deterministic routing step between intake and the reviewer stages: it reads the risk rating and surfaces intake stamped on the work order and selects, from project configuration, which reviewers run and which model each station uses. Routing is a table and a function, not a model's mood: the same inputs always produce the same panel, and every decision is written into the run report with its reasons.

## Requirements
- Routing consumes the work order's risk (low, medium, high, or null) and surfaces list as produced by the intake outcomes capability. It runs after intake and before the reviewer stage, and its output is a routing record: the selected reviewer set, the model selected for each station in the run, and the reasons for each reduction or assignment.
- Routing rules are configuration, held in the project config alongside the station table: a routing table mapping risk levels and surface conditions to reviewer set reductions and per-station model choices. The factory ships a default table; a project may override it in its own config.
- The factory's model routing policy is the ceiling. The policy (recorded in the project design system spec) assigns the design model to UI and design stations, the strong builder model to the non-UI builder, and the standard reviewer model to reviewers and writers. Routing may reduce a panel or choose a cheaper configured model below that ceiling; it may never assign a model above the policy for a station kind, and any configuration that tries to is rejected at config load with the violation named.
- Rules of the default table:
  - Low risk and no ui surface and no security surface: a reduced reviewer set (reviewer-spec and reviewer-tests) at the cheaper configured reviewer model.
  - A security surface, at any risk level: reviewer-security is always in the set, at the strong configured model for reviewers.
  - A ui surface: reviewer-design is in the set whenever the pipeline has it.
  - Medium risk: the full panel at the policy models.
  - High risk: the full panel at the policy models, and routing records that no reduction applied.
  - Null risk (intake did not rate the work): the full panel at the policy models, and the routing record states the default applied because the work was unrated.
- A reviewer removed by routing is recorded in the run report as routed out, with the rule that removed it. The approver's aggregation treats a routed out reviewer as not expected: it neither counts for nor against the verdict, and the review count the approver reports names how many reviews were expected after routing. A routed out reviewer is never rendered as a failed or missing review.
- The routing record lands in the run report as its own section, and the swimlane shows the routing decision in one line (panel size and any model changes), so a reader sees the shape of the run without opening JSON.
- Routing never touches the builder's obligation or the gates: the checks gate and the scenario-to-test gates run as before regardless of the selected panel.

## Scenarios

### Scenario: Low risk work runs a reduced panel at cheaper models
- S1: Given a work order rated low risk with no ui and no security surface, when routing runs, then the selected reviewer set is the reduced set from the routing table, the selected reviewer model is the cheaper configured model, and the routing record names the low risk rule as the reason.

### Scenario: A security surface always keeps the security reviewer at the strong model
- S2: Given a work order with a security surface at any risk level, when routing runs, then reviewer-security is in the selected set at the strong configured reviewer model, and the routing record names the security rule.

### Scenario: Unrated work defaults to the full panel at the policy models
- S3: Given a work order with a null risk rating, when routing runs, then the selected set is the pipeline's full reviewer panel, the selected models are the policy models, and the routing record states that the default applied because the work was unrated.

### Scenario: Routing may never exceed the policy ceiling
- S4: Given a project routing configuration that assigns a station kind a model above the recorded policy, when the configuration is loaded, then loading fails with an error naming the station kind, the configured model and the policy model it exceeds.

### Scenario: Routed out reviewers are expected absences, not failures
- S5: Given a run where routing removed a reviewer, when the approver aggregates, then its review count names the expected count after routing, the verdict is computed from the reviews that ran, and the report lists the removed reviewer as routed out with its rule, never as failed or missing.

### Scenario: Every routing decision is in the report with reasons
- S6: Given any completed run, when its report is read, then it contains a routing section listing the selected set, the selected models and the reason for each reduction or assignment, and the swimlane carries the one line summary of that decision.
