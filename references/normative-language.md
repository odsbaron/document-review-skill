# Normative Language Rules

Use this reference when a decision document contains strong wording, operating principles, commitments, defaults, exceptions, governance, or policy-like statements.

## Force Ladder

| Wording | Use when | Required support |
| --- | --- | --- |
| `must` / `必须` | A hard constraint exists: legal, security, operational, contractual, irreversible, or executive decision. | Authority, scope, exception path, consequence. |
| `must not` / `不得` | A prohibited action creates unacceptable risk or violates a constraint. | Boundary, rationale, exception owner, violation consequence. |
| `should` / `应该` | Strong default with meaningful but overridable benefits. | Criteria, tradeoff, override condition. |
| `recommend` / `建议` | Evidence supports a direction but uncertainty remains. | Evidence, assumptions, next validation step. |
| `may` / `可以` | Optional path, permission, or capability. | Owner decides when to use it; limits are clear. |
| `default` / `默认` | Standard path unless an explicit condition holds. | Default reason, exception condition, approval path. |
| `principle` / `原则` | Reusable judgment rule across cases. | Scope, priority when principles conflict, examples. |

## Mandatory Checks

For every strong normative phrase, answer:

1. What is the source of authority?
2. What is the scope: team, product, customer segment, launch phase, market, or time window?
3. What is the exception condition?
4. Who can approve the exception?
5. What happens if the rule is violated?
6. Is the wording stronger than the evidence supports?

## Claim-Strength Mismatches

- "Can" to "should": capability is not a recommendation.
- "Should" to "must": preference is not a constraint.
- "Users asked for it" to "we must build it": demand signal is not prioritization proof.
- "Competitors do it" to "we are behind": market observation is not strategic necessity.
- "Risk exists" to "we cannot proceed": risk identification is not a veto unless thresholds are defined.

## Rewrite Patterns

Overstated:

```text
We must launch this in Q3.
```

Calibrated:

```text
We should target Q3 if the onboarding error rate falls below 3% by August 15; otherwise we should narrow scope to the admin beta.
```

Ambiguous:

```text
Engineering should own reliability.
```

Calibrated:

```text
Engineering owns service-level reliability metrics; Product owns customer-facing degradation policy and launch-risk tradeoffs.
```

Policy-like:

```text
Enterprise customers cannot access the beta.
```

Calibrated:

```text
Enterprise customers must not access the beta unless Legal approves the DPA addendum and Support confirms named-account coverage.
```
