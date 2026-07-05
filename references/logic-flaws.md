# Decision Document Logic Flaws

Use this reference when auditing argument quality in product proposals, strategy memos, decision docs, PRDs, RFCs, roadmap recommendations, launch plans, and investment cases.

## High-Risk Flaws

| Flaw | Symptom | Fix |
| --- | --- | --- |
| Solution-first reasoning | The doc opens with what to build before proving the problem. | Add problem, user, cost of inaction, and alternatives. |
| False binary | Only "do it" vs "do not do it" appears. | Add delay, pilot, narrow scope, partner, manual process, or reversible test. |
| Weak alternative | Alternatives are obviously worse. | Steelman the strongest rejected path. |
| Evidence overreach | Anecdote, sales request, or competitor feature becomes strategy. | Downgrade claim or add corroborating evidence. |
| Metric drift | The metric is easy to move but not the real objective. | Add outcome metric and guardrail. |
| Hidden opportunity cost | The doc lists benefits but not what the team stops doing. | Name displaced roadmap items, maintenance cost, and coordination cost. |
| Risk theater | Risks are listed but have no trigger, owner, or response. | Add threshold, monitoring signal, mitigation, and exit criteria. |
| Assumption laundering | A major premise is written as a fact. | Label it as an assumption and define validation. |
| Urgency without proof | "Window is closing" appears without timing evidence. | Provide deadline source or remove urgency. |
| Irreversibility error | A hard-to-reverse decision is treated like an experiment. | Add reversibility, rollback cost, blast radius, and decision gate. |
| Ownership gap | Many teams are mentioned but no accountable owner exists. | Assign owner for decision, execution, metric, and exception. |
| Stakeholder absence | Affected users, teams, or opponents are not represented. | Add impact map and likely objections. |

## Audit Heuristics

- If the recommendation would be the same under any evidence, the reasoning is decorative.
- If the strongest alternative is not tempting, the options section is probably weak.
- If a risk has no threshold, it cannot guide action.
- If a metric has no decision attached, it is dashboard decoration.
- If the doc says "align", ask what decision alignment enables.
- If a statement sounds obvious, ask what would make it false.

## Severity Labels

- `Blocker`: The document cannot support a decision until fixed.
- `Major`: The recommendation may be right, but the reasoning has a material gap.
- `Medium`: The decision is understandable, but risk or wording could mislead execution.
- `Minor`: Clarity or polish issue that does not change the decision.

## Review Priorities

1. Decision ask and owner.
2. Options and tradeoffs.
3. Evidence-to-claim strength.
4. Risks, assumptions, and reversibility.
5. Normative wording.
6. Copy clarity.
