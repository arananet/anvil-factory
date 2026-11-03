# Risk and Surface Routing

## Purpose

Every run pays for the full reviewer panel at the policy models by default, whether the change is a one-line fix or a payments migration. Routing adds a deterministic step between intake and the reviewer stages: it reads the risk rating and surfaces intake stamped on the work order and selects, from project configuration, which reviewers run and which model each station uses.

Routing is a table and a function, not a model's mood: the same inputs always produce the same panel, and every decision is written into the run report with its reasons.

## When routing runs

Routing executes automatically after the intake station completes and before any reviewer stations run. It consumes:
- **risk**: low, medium, high, or null (unrated)
- **surfaces**: list of surfaces the work touches (ui, security, data, payments, deploy, content, api)

Both fields are stamped on the work order by the intake station during intake outcomes processing.

## Routing rules

The factory ships a default routing table. Projects may override these rules in `.anvil/routing.json`.

### Default rules

| Condition | Selected panel | Model selection |
|-----------|---------------|-----------------|
| Low risk + no UI + no security | Reduced panel (reviewer-spec, reviewer-tests) | Cheaper model (`review-cheap`) |
| Security surface (any risk) | Always includes reviewer-security | Strong model (`review-strong`) for security reviewer |
| UI surface (any risk) | Always includes reviewer-design | Standard model (`review-balanced`) |
| Medium risk | Full panel | Policy models (standard) |
| High risk | Full panel | Policy models (standard) with explicit "no reduction" |
| Null risk (unrated) | Full panel | Policy models (standard) with "default for unrated" note |

### Surface-specific overrides

- **Security surface**: reviewer-security is always in the selected set at the strong configured model, regardless of risk level
- **UI surface**: reviewer-design is kept in the set whenever the pipeline includes it

## Model policy ceiling

The model routing policy is a ceiling. The policy assigns:
- Standard reviewer model (`review-balanced`) to most reviewers
- Strong model (`review-strong`) to reviewer-security
- Design model to UI and design stations
- Strong builder model to non-UI builders

**Routing may reduce a panel or choose a cheaper model below that ceiling; it may never assign a model above the policy for a station kind.**

Any configuration that tries to assign a model above the policy ceiling is rejected at config load with the violation named:

```
Station 'reviewer-spec' configured with model 'review-strong' 
exceeds policy ceiling 'review-balanced' for reviewer stations
```

## Routed out reviewers

A reviewer removed by routing is recorded as **routed out**, not failed or missing:

- The routing record includes each routed out reviewer with the rule that removed it
- The approver's aggregation treats routed out reviewers as not expected
- Review counts in the verdict rule name the expected count **after routing**
- Routed out reviewers are never rendered as failed or missing reviews

Example routing record:
```json
{
  "selected_reviewers": ["reviewer-spec", "reviewer-tests"],
  "routed_out": [
    {
      "reviewer": "reviewer-security",
      "reason": "Routed out by low risk rule (not in reduced panel)"
    },
    {
      "reviewer": "reviewer-architecture", 
      "reason": "Routed out by low risk rule (not in reduced panel)"
    }
  ],
  "selected_models": {
    "reviewer-spec": "review-cheap",
    "reviewer-tests": "review-cheap"
  },
  "reason": "Low risk with no UI and no security surface: reduced panel at cheaper model"
}
```

## Routing in reports

The routing record appears in two places:

### 1. Run report (`report.md`)

A dedicated routing section lists:
- The routing decision reason
- Selected reviewers with their assigned models
- Routed out reviewers with the rule that removed each one

```markdown
## Routing

**Decision**: Low risk with no UI and no security surface: reduced panel at cheaper model

**Selected reviewers** (2):
- reviewer-spec (model: review-cheap)
- reviewer-tests (model: review-cheap)

**Routed out** (3):
- reviewer-security: Routed out by low risk rule (not in reduced panel)
- reviewer-architecture: Routed out by low risk rule (not in reduced panel)
- reviewer-design: Routed out by low risk rule (not in reduced panel)
```

### 2. Swimlane (`swimlane.md`)

A one-line summary shows the panel size and any reductions:

```
Routing: 2 reviewers (reduced panel, 3 routed out)
```

## What routing never changes

Routing affects **only** reviewer selection and model assignment. It never touches:

- The checks gate: always runs as configured
- The scenario-to-test gates: always validate as before
- The builder's obligation: still implements the full spec
- Gate failures: still trigger loopback as before

## Project configuration

Projects can override the default routing table by creating `.anvil/routing.json`:

```json
{
  "reduced_panel_reviewers": ["reviewer-spec", "reviewer-tests"],
  "full_panel_reviewers": [
    "reviewer-spec",
    "reviewer-security", 
    "reviewer-tests",
    "reviewer-architecture",
    "reviewer-design"
  ],
  "models": {
    "reduced": "review-cheap",
    "standard": "review-balanced",
    "strong": "review-strong"
  },
  "policy_ceilings": {
    "reviewer": "review-balanced",
    "reviewer-security": "review-strong"
  }
}
```

**Configuration validation**: Any model assignment that exceeds the policy ceiling for a station kind will cause config loading to fail with a clear error naming the violation.

## Observability

Every routing decision is fully traced:

1. **Routing record file**: `runs/<work-order-id>/routing.json` with complete decision data
2. **Report section**: Dedicated routing section in `report.md`
3. **Swimlane summary**: One-line panel summary in `swimlane.md`
4. **Approver rule**: States expected review count after routing

This ensures readers can see the shape of the run and understand why certain reviewers ran or didn't run, without opening JSON files.

## Spec reference

Full specification: `.openspec/specs/risk-routing/spec.md`

Test coverage: `tests/test_risk_routing.py` (16 tests covering scenarios S1-S6)
