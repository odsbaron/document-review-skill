from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .chunking import chunk_text
from .document_loader import load_document, load_text_bundle
from .models import Finding, ReviewResult
from .prompts import AGENT_PROMPTS, build_user_prompt


DEFAULT_AGENTS = ("logic", "inside", "data", "reader", "decision", "normative", "operating")


class DocumentReviewAgent:
    def __init__(self, llm_client, max_chunk_chars: int = 8000):
        self.llm_client = llm_client
        self.max_chunk_chars = max_chunk_chars

    def review(
        self,
        document_path: str | Path,
        *,
        public_source_paths: list[str | Path] | None = None,
        sensitive_list_path: str | Path | None = None,
        agents: Iterable[str] = DEFAULT_AGENTS,
        max_chunks: int | None = None,
    ) -> ReviewResult:
        document = load_document(document_path)
        public_context = load_text_bundle(public_source_paths or [])
        sensitive_terms = _load_optional_text(sensitive_list_path)
        chunks = chunk_text(document.text, max_chars=self.max_chunk_chars)
        if max_chunks is not None:
            chunks = chunks[:max_chunks]

        findings: list[Finding] = []
        raw_outputs: list[str] = []
        selected_agents = _validate_agents(tuple(agents))

        for chunk_index, text_chunk in enumerate(chunks):
            for agent_name in selected_agents:
                raw = self._run_agent(
                    agent_name=agent_name,
                    document_path=str(document.path),
                    chunk_index=chunk_index,
                    chunk_count=len(chunks),
                    chunk_text=text_chunk,
                    public_context=public_context,
                    sensitive_terms=sensitive_terms,
                )
                raw_outputs.append(raw)
                findings.extend(
                    _parse_findings(
                        raw,
                        agent_name=agent_name,
                        fallback_location=f"chunk {chunk_index + 1}/{len(chunks)}",
                    )
                )

        findings = sorted(_dedupe_findings(findings), key=lambda item: item.sort_key())
        return ReviewResult(
            document_path=str(document.path),
            summary=_build_summary(findings),
            findings=findings,
            raw_agent_outputs=raw_outputs,
        )

    def _run_agent(
        self,
        *,
        agent_name: str,
        document_path: str,
        chunk_index: int,
        chunk_count: int,
        chunk_text: str,
        public_context: str,
        sensitive_terms: str,
    ) -> str:
        messages = [
            {"role": "system", "content": AGENT_PROMPTS[agent_name]},
            {
                "role": "user",
                "content": build_user_prompt(
                    document_path=document_path,
                    chunk_index=chunk_index,
                    chunk_count=chunk_count,
                    chunk_text=chunk_text,
                    public_context=public_context,
                    sensitive_terms=sensitive_terms,
                ),
            },
        ]
        return self.llm_client.complete_json(messages)


def _load_optional_text(path: str | Path | None) -> str:
    if path is None:
        return ""
    return Path(path).read_text(encoding="utf-8").strip()


def _validate_agents(agent_names: tuple[str, ...]) -> tuple[str, ...]:
    unknown = [name for name in agent_names if name not in AGENT_PROMPTS]
    if unknown:
        raise ValueError(f"Unknown agent(s): {', '.join(unknown)}")
    return agent_names


def _parse_findings(raw: str, *, agent_name: str, fallback_location: str) -> list[Finding]:
    data = json.loads(_extract_json_object(raw))
    items = data.get("findings", [])
    findings: list[Finding] = []

    for item in items:
        severity = str(item.get("severity", "medium")).lower()
        findings.append(
            Finding(
                agent=agent_name,
                location=str(item.get("location") or fallback_location),
                excerpt=str(item.get("excerpt") or "").strip(),
                issue_type=str(item.get("issue_type") or "other").strip(),
                severity=severity,
                reason=str(item.get("reason") or "").strip(),
                recommendation=str(item.get("recommendation") or "").strip(),
                needs_human_review=bool(item.get("needs_human_review", True)),
            )
        )
    return findings


def _extract_json_object(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"LLM response did not contain a JSON object: {text[:200]}")
    return stripped[start : end + 1]


def _dedupe_findings(findings: list[Finding]) -> list[Finding]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[Finding] = []
    for finding in findings:
        key = (
            finding.issue_type.lower(),
            finding.excerpt[:120].lower(),
            finding.reason[:120].lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    return deduped


def _build_summary(findings: list[Finding]) -> str:
    if not findings:
        return "No logic, inside-knowledge, or consistency issues were reported by the selected agents."

    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    parts = [f"{severity}: {count}" for severity, count in sorted(counts.items())]
    return f"Found {len(findings)} issue(s). Severity counts: " + ", ".join(parts) + "."
