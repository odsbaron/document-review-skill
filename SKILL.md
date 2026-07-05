---
name: decision-document-auditor
description: Use when reviewing, drafting, rewriting, or stress-testing decision-oriented documents — product proposals, strategy memos, PRDs, RFCs, launch plans, roadmap recommendations, investment cases, or team operating principles — for decision clarity, alternatives, evidence strength, risks, normative wording, and reusable structure. Also covers running the bundled multi-agent automated review over local .md/.txt/.pdf/.docx files.
---

# Decision Document Auditor

## Overview

Audit decision-oriented documents so they help a reader decide what to do, why now, and under what conditions the recommendation should change.

The core standard: separate facts, judgments, recommendations, and decisions. Do not let polished prose hide weak reasoning.

## Audit Workflow

1. Identify the decision ask: who must decide, by when, and what decision is requested.
2. Classify the document: product proposal, strategy memo, PRD/RFC, roadmap recommendation, launch plan, investment case, or operating principle.
3. Map the argument: problem, options, recommendation, evidence, tradeoffs, risks, assumptions, metrics, next steps.
4. Check options: include at least one real alternative and usually an explicit "do nothing / delay / narrow scope" path.
5. Check evidence bridge: verify that evidence supports the claim strength instead of merely making the recommendation feel plausible.
6. Check normative wording: calibrate "must", "should", "may", "recommend", "principle", "default", "exception", and "owner".
7. Check operating principles: facts before judgment, boundaries before mandates, real problems before tools, delivery with assetization, mechanisms that reduce noise, AI delegation with human responsibility.
8. Check risk integrity: name triggers, monitoring signals, reversibility, blast radius, and exit criteria.
9. When a local document path is available and the user wants a full sweep, run the bundled automated review script before synthesis.
10. Produce a review that prioritizes material decision risks over copy edits.

## Automated Review Script

Use the bundled script for long or file-based reviews where chunking, PDF/DOCX extraction, data checks, information-boundary checks, or repeatable findings matter.

Inspect without API calls:

```bash
python scripts/review_document.py inspect path/to/document.md
```

Install script dependencies when needed:

```bash
python -m pip install -r scripts/requirements.txt
```

Run the full review when an OpenAI-compatible API key is available through environment variables (see `.env.example`) or keyring:

```bash
python scripts/review_document.py review path/to/document.md \
  --public-source path/to/public_context.md \
  --sensitive-list path/to/sensitive_terms.txt \
  --out review_report.md
```

Supported agents: `logic`, `inside`, `data`, `reader`, `decision`, `normative`, `operating`.

Useful flags: `--agent` to select a subset (repeatable), `--max-chunks` for trial runs, `--lang` for findings language (default zh), `--workers` for concurrency, `--raw-out` to save raw agent outputs for debugging.

Failed or unparsable agent calls do not abort the run; they appear as `agent_error` / `parse_error` findings and should be treated as coverage gaps, not document issues.

Prefer environment variables or keyring for credentials. Do not put API keys in the command line unless the user explicitly asks; command history can leak secrets.

After the script runs, synthesize its findings with the manual audit workflow. Do not return only the raw report unless the user asks for raw findings.

## Load References

- For creating or restructuring a document, read `references/decision-document-template.md`.
- For strong wording, obligations, principles, defaults, exceptions, or commitments, read `references/normative-language.md`.
- For argument quality, hidden assumptions, decision traps, and memo failure modes, read `references/logic-flaws.md`.
- For team methodology, mechanism design, assetization, quality semantics, AI/agentic responsibility, or "how we work" principles, read `references/operating-principles.md`.
- For the bundled multi-agent scanner, local file review, public context, sensitive-term lists, or report synthesis, read `references/automated-review-sop.md`.

## Output Contract

When auditing, use this structure unless the user asks for another format:

```markdown
## Decision Clarity
- Decision ask:
- Decision owner:
- Deadline / timing:
- Missing clarity:

## Material Issues
1. [Severity] Issue
   Why it matters:
   How to fix:

## Automated Findings
- Script used:
- Agents run:
- Finding count:
- Highest severity:
- Findings to merge into final judgment:

## Normative Language
- Overstated:
- Understated:
- Ambiguous:
- Suggested rewrites:

## Risks, Assumptions, and Tradeoffs
- Key assumption:
- Failure signal:
- Tradeoff not owned:
- Reversibility:

## Operating Principles
- Fact discipline:
- Boundary clarity:
- Tool-to-problem fit:
- Assetization / reuse:
- Mechanism value:
- AI responsibility:

## Recommended Rewrite
[Rewrite the highest-leverage section or sentence.]
```

If the document is already strong, say so directly and focus on the few remaining decision risks. Omit the Automated Findings section when the script was not run.

## Review Standards

- Be charitable to intent and strict about reasoning.
- Prefer "what would make this decision safer?" over "what sounds smarter?"
- Flag missing alternatives before debating wording.
- Treat "we should" without owner, timing, and success criteria as incomplete.
- Treat "must" without source of authority, scope, exception, and consequence as suspect.
- Treat evidence that supports a weaker claim as a claim-strength mismatch, not as no evidence.
- Treat principles that do not change a decision, habit, metric, or mechanism as decorative until operationalized.
- Do not manufacture objections. If a choice is well supported, name why it is strong.
