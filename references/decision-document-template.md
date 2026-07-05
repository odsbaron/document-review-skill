# Decision Document Template

Use this reference when drafting, restructuring, or rewriting a product proposal, strategy memo, PRD/RFC, roadmap recommendation, launch plan, or investment case.

## Minimal Skeleton

```markdown
# [Decision Object]

## 1. Decision Ask
We need [decision owner] to decide [choice] by [date/context] so that [next action becomes possible].

## 2. Context
What changed? Why now? What constraint, opportunity, risk, or learning makes this decision timely?

## 3. Problem
What is the real problem? Who experiences it? What happens if we do not act?

## 4. Options
- Option A:
- Option B:
- Option C / Delay / Do nothing / Narrow scope:

## 5. Recommendation
Recommend [option] because [criteria and reasoning].

## 6. Evidence
What facts, data, customer signals, market signals, operational constraints, or prior experiments support the recommendation?

## 7. Tradeoffs
What do we give up? Who bears cost? What becomes harder later?

## 8. Risks and Assumptions
What must be true? What could make this wrong? What is the monitoring plan?

## 9. Success Metrics
Leading indicators, lagging indicators, guardrails, and review date.

## 10. Next Steps
Immediate actions, owners, and checkpoints after the decision.
```

## Required Decision Tests

| Test | Pass condition |
| --- | --- |
| Decision ask | A named person or group can say yes/no/defer. |
| Timing | The document explains why the decision is needed now. |
| Options | At least two real paths are compared; "do nothing" is considered when relevant. |
| Criteria | The recommendation is judged against explicit criteria. |
| Evidence | Evidence supports the strength of the claim. |
| Tradeoffs | The document says what gets worse, slower, riskier, or more expensive. |
| Risk plan | Risks have triggers, monitoring signals, owners, and mitigation or exit paths. |
| Metrics | Success and failure can be evaluated after the decision. |

## Common Section Fixes

- If the doc starts with a solution, add a problem statement before the recommendation.
- If options are straw men, strengthen the best alternative before defending the recommendation.
- If metrics are only output metrics, add outcome and guardrail metrics.
- If the recommendation depends on unknowns, state the assumption and the cheapest test.
- If the document asks for alignment, translate it into a concrete decision or next action.
