# Risk and Surface Routing

Status: draft
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
- The factory's model routing policy is the ceiling. The policy (recorded in the project design system spec) assigns the design model to UI and design stations, the strong builder model to the non-UI builder, and the standard reviewer model to reviewers and writers. A project may override the policy ceiling by providing a `policy_ceilings` section in its configuration; when absent, the factory defaults apply. Routing may reduce a panel or choose a cheaper configured model below that ceiling; it may never assign a model above the policy for a station kind.
- Configuration validation happens at load time. When routing configuration is loaded, every model assignment in the merged configuration (factory defaults plus project overrides) is validated against the policy ceiling. A configuration that assigns a model above the policy for a station kind fails to load with an error naming the station kind, the configured model and the policy model it exceeds. The reviewer lists (`reduced_panel_reviewers` and `full_panel_reviewers`) are validated to contain only valid reviewer station identifiers, and every model referenced in the configuration must exist in the model hierarchy. Invalid references fail at load with the offending value named.
- Routing trusts the intake outcomes as authoritative. The risk rating and surfaces list stamped on the work order by intake are consumed as produced. This is an accepted design choice: intake owns rating work, routing owns panel selection given that rating. Unrated work (null risk) defaults to the full panel at policy models as a safe fallback.
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
- S1: Given a work order rated low risk with no ui and no security surface, when routing runs, then the selected reviewer set is the reduced set from the routing table (reviewer-spec and reviewer-tests), the selected reviewer model is the cheaper configured model, and the routing record names the low risk rule as the reason.

### Scenario: A security surface always keeps the security reviewer at the strong model
- S2: Given a work order with a security surface at any risk level, when routing runs, then reviewer-security is in the selected set at the strong configured reviewer model, and the routing record names the security rule.

### Scenario: Full panel routing for default and unrated cases
- S3: Given a work order with a null risk rating, when routing runs, then the selected set is the pipeline's full reviewer panel, the selected models are the policy models, and the routing record states that the default applied because the work was unrated. Given a work order with a ui surface, when routing runs, then reviewer-design is in the selected set whenever the pipeline has it. Given a work order rated medium risk, when routing runs, then the selected set is the full panel at the policy models. Given a work order rated high risk, when routing runs, then the selected set is the full panel at the policy models and the routing record explicitly states that no reduction applied.

### Scenario: Configuration validation enforces policy ceiling at load time
- S4: Given a project routing configuration that assigns a station kind a model above the recorded policy, when the configuration is loaded, then loading fails with an error naming the station kind, the configured model and the policy model it exceeds. Given a routing configuration with an invalid reviewer station identifier in a panel list, when the configuration is loaded, then loading fails with an error naming the invalid identifier. Given a routing configuration that references a model not in the model hierarchy, when the configuration is loaded, then loading fails with an error naming the invalid model reference.

### Scenario: Routed out reviewers are expected absences, not failures
- S5: Given a run where routing removed a reviewer, when the approver aggregates, then its review count names the expected count after routing, the verdict is computed from the reviews that ran, and the report lists the removed reviewer as routed out with its rule, never as failed or missing.

### Scenario: Every routing decision is in the report with reasons
- S6: Given any completed run, when its report is read, then it contains a routing section listing the selected set, the selected models and the reason for each reduction or assignment, and the swimlane carries the one line summary of that decision.

### Scenario: Project configuration can override policy ceilings
- S7: Given a project configuration that provides a `policy_ceilings` section, when routing configuration is loaded, then the project's policy ceilings are used for validation instead of the factory defaults. Given a project configuration with no `policy_ceilings` section, when routing configuration is loaded, then the factory default policy ceilings apply.
