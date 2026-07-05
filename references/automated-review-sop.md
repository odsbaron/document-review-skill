# Automated Review SOP

Use this reference when running or interpreting the bundled `scripts/review_document.py` scanner.

## Purpose

The scanner provides a repeatable first pass over Markdown, text, PDF, and DOCX files. It does not replace judgment. Use it to surface candidate findings, then synthesize them through the decision-document audit workflow.

## Inputs

- Document: `.md`, `.txt`, `.pdf`, or `.docx`.
- Public context: optional public references allowed for verification.
- Sensitive list: optional internal terms, client names, unpublished metrics, private fields, credentials, or disclosure rules.
- Agent list: optional subset of `logic`, `inside`, `data`, `reader`, `decision`, `normative`, `operating`.

## Agents

| Agent | Checks |
| --- | --- |
| `logic` | Contradictions, unsupported conclusions, circular reasoning, causal jumps, timeline conflicts, undefined concepts. |
| `inside` | Hidden premises, internal codenames, unpublished data, customer details, security details, credentials, private metrics. |
| `data` | Figures, percentages, dates, units, denominators, formulas, table/body consistency, missing sources. |
| `reader` | Whether an external reader can understand and verify the document from the text and public context. |
| `decision` | Decision ask, owner, timing, real alternatives, criteria, recommendation support, success metrics. |
| `normative` | `must`, `should`, `may`, `recommend`, `default`, `principle`, `exception`, `owner`, and Chinese equivalents. |
| `operating` | Fact discipline, tool-to-problem fit, reusable assets, mechanism value, collaboration boundaries, AI accountability. |

## Command Pattern

Inspect extraction and chunking first:

```bash
python scripts/review_document.py inspect path/to/document.md
```

Run a trial on one chunk:

```bash
python scripts/review_document.py review path/to/document.md --max-chunks 1 --out review_report.md
```

Run selected agents:

```bash
python scripts/review_document.py review path/to/document.md \
  --agent logic \
  --agent decision \
  --agent normative \
  --agent operating \
  --out review_report.md
```

Run with public context and sensitive terms:

```bash
python scripts/review_document.py review path/to/document.md \
  --public-source path/to/public_context.md \
  --sensitive-list path/to/sensitive_terms.txt \
  --out review_report.md
```

## Credential Rules

Use one of these approaches:

- Environment: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`.
- AIHubMix-compatible environment: `AIHUBMIX_API_KEY`, `AIHUBMIX_BASE_URL`, `AIHUBMIX_MODEL`.
- Keyring: `python scripts/review_document.py store-key`.

Avoid `--api-key` except when the user explicitly requests it. Command history can leak secrets.

## Synthesis Rules

- Treat scanner output as candidate findings, not final truth.
- Merge duplicates across agents.
- Promote an issue only when it affects decision quality, reader trust, sensitive disclosure, or execution safety.
- Mark uncertain sensitive disclosures for human review.
- If the script finds no issues, still perform a short manual pass for decision ask, alternatives, claim strength, and operating principles.
- Preserve exact excerpts when quoting findings, but keep quotes short.

## Required Final Judgment

After reading the script report, answer:

1. Can this document support the requested decision?
2. What are the highest-severity blockers or major risks?
3. Which findings are likely false positives?
4. Which wording should be downgraded, strengthened, or bounded?
5. What rewrite or next action would most improve decision quality?
