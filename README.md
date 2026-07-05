# Decision Document Auditor

A skill + CLI for auditing decision-oriented documents (product proposals, strategy memos, PRDs, RFCs, launch plans, investment cases, operating principles): does the document make clear who must decide what, by when, based on which evidence — and under what conditions the recommendation should change?

## Layout

- `SKILL.md` — the skill definition: manual audit workflow, output contract, review standards.
- `references/` — methodology references (decision template, logic flaws, normative language, operating principles, automated review SOP).
- `scripts/doc_review_agent/` — a multi-agent review CLI that scans `.md/.txt/.pdf/.docx` files with seven reviewer agents: `logic`, `inside`, `data`, `reader`, `decision`, `normative`, `operating`.
- `examples/` — a sample proposal with seeded flaws for trying the tool.
- `tests/` — pytest suite (no API calls required).

## Install

```bash
pip install -e ".[all]"        # CLI + PDF/DOCX/keyring extras
# or minimal:
pip install -e .               # OpenAI SDK only (.md/.txt reviews)
```

## Configure

Copy `.env.example` to `.env` and set `OPENAI_API_KEY` (any OpenAI-compatible endpoint works via `OPENAI_BASE_URL`), or store a key in the system keyring:

```bash
python scripts/review_document.py store-key
```

## Use

```bash
# Parse and chunk without API calls
python scripts/review_document.py inspect examples/sample-proposal.md

# Trial run on one chunk
python scripts/review_document.py review examples/sample-proposal.md --max-chunks 1

# Full review with selected agents, English findings, debug output
python scripts/review_document.py review path/to/doc.md \
  --agent logic --agent decision --lang en --raw-out raw.txt --out review_report.md
```

Useful flags: `--agent` (repeatable subset), `--lang` (findings language, default `zh`), `--workers` (concurrent API calls, default 4), `--max-chunks` (trial runs), `--raw-out` (raw agent outputs for debugging), `--public-source`, `--sensitive-list`.

Failed or unparsable agent calls never abort a run — they are recorded as `agent_error` / `parse_error` findings so the rest of the sweep completes.

## Develop

```bash
pip install -e ".[all,dev]"
ruff check scripts tests
pytest -q
```
