from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

from .chunking import chunk_document
from .config import (
    DEFAULT_KEYRING_SERVICE,
    DEFAULT_KEYRING_USERNAME,
    ConfigError,
    load_dotenv_file,
    load_llm_config,
)
from .document_loader import load_document
from .llm_client import OpenAICompatibleClient
from .report import render_markdown_report
from .reviewer import DEFAULT_AGENTS, DocumentReviewAgent


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "inspect":
        return _inspect(args)
    if args.command == "store-key":
        return _store_key(args)
    if args.command == "review":
        return _review(args)

    parser.print_help()
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="doc-review-agent",
        description="Review documents for decision quality, logic issues, normative wording, and information-boundary risk.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Parse and chunk a document without API calls.")
    inspect_parser.add_argument("document", help="Path to .md/.txt/.pdf/.docx document.")
    inspect_parser.add_argument("--max-chars", type=int, default=8000, help="Max characters per chunk.")

    key_parser = subparsers.add_parser("store-key", help="Store an OpenAI-compatible API key in system keyring.")
    key_parser.add_argument("--service", default=DEFAULT_KEYRING_SERVICE, help="Keyring service name.")
    key_parser.add_argument("--username", default=DEFAULT_KEYRING_USERNAME, help="Keyring username.")
    key_parser.add_argument("--key", help="API key. If omitted, a hidden prompt is shown.")

    review_parser = subparsers.add_parser("review", help="Run the multi-agent document review.")
    review_parser.add_argument("document", help="Path to .md/.txt/.pdf/.docx document.")
    review_parser.add_argument("--public-source", action="append", default=[], help="Public reference document. Repeatable.")
    review_parser.add_argument("--sensitive-list", help="Text file of sensitive/internal terms or rules.")
    review_parser.add_argument("--agent", action="append", choices=list(DEFAULT_AGENTS), help="Agent to run. Repeatable.")
    review_parser.add_argument("--out", default="review_report.md", help="Markdown report output path.")
    review_parser.add_argument("--raw-out", help="Optional path to save raw agent outputs for debugging.")
    review_parser.add_argument("--lang", help="Language for findings (default: REVIEW_LANGUAGE env or zh).")
    review_parser.add_argument("--workers", type=int, help="Concurrent API calls (default: REVIEW_MAX_WORKERS env or 4).")
    review_parser.add_argument("--env", default=".env", help="Path to .env file.")
    review_parser.add_argument("--api-key", help="Override OPENAI_API_KEY.")
    review_parser.add_argument("--base-url", help="Override OPENAI_BASE_URL.")
    review_parser.add_argument("--model", help="Override OPENAI_MODEL.")
    review_parser.add_argument("--max-chunks", type=int, help="Limit chunks for trial runs.")

    return parser


def _inspect(args: argparse.Namespace) -> int:
    document = load_document(args.document)
    chunks = chunk_document(document.text, max_chars=args.max_chars)
    print(f"Document: {document.path}")
    print(f"Kind: {document.kind}")
    print(f"Characters: {len(document.text)}")
    print(f"Chunks: {len(chunks)}")
    for index, chunk in enumerate(chunks, start=1):
        section = chunk.section or "[no heading]"
        print(f"  chunk {index}: {len(chunk.text)} chars | {section}")
    return 0


def _store_key(args: argparse.Namespace) -> int:
    try:
        import keyring
    except ImportError:
        print("keyring is not installed. Run: pip install keyring")
        return 2

    api_key = args.key or getpass.getpass("OpenAI-compatible API key: ")
    if not api_key.strip():
        print("No API key provided.")
        return 2

    keyring.set_password(args.service, args.username, api_key.strip())
    print(f"Stored API key in keyring service '{args.service}' for username '{args.username}'.")
    return 0


def _review(args: argparse.Namespace) -> int:
    load_dotenv_file(args.env)
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
    if args.base_url:
        os.environ["OPENAI_BASE_URL"] = args.base_url
    if args.model:
        os.environ["OPENAI_MODEL"] = args.model

    try:
        config = load_llm_config()
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        return 2

    client = OpenAICompatibleClient(config)
    reviewer = DocumentReviewAgent(
        client,
        max_chunk_chars=config.max_chunk_chars,
        max_workers=args.workers or config.max_workers,
        language=args.lang or config.language,
        progress=lambda message: print(message, file=sys.stderr),
    )
    result = reviewer.review(
        args.document,
        public_source_paths=args.public_source,
        sensitive_list_path=args.sensitive_list,
        agents=args.agent or DEFAULT_AGENTS,
        max_chunks=args.max_chunks,
    )

    output_path = Path(args.out)
    output_path.write_text(render_markdown_report(result), encoding="utf-8")
    print(f"Report written to {output_path}")

    if args.raw_out:
        raw_path = Path(args.raw_out)
        raw_path.write_text("\n\n---\n\n".join(result.raw_agent_outputs), encoding="utf-8")
        print(f"Raw agent outputs written to {raw_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
