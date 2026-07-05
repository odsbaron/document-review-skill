from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Iterable

from .chunking import Chunk, chunk_document
from .document_loader import load_document, load_text_bundle, read_text_best_effort
from .models import Finding, ReviewResult, normalize_severity
from .prompts import AGENT_PROMPTS, build_user_prompt


DEFAULT_AGENTS = ("logic", "inside", "data", "reader", "decision", "normative", "operating")

ProgressCallback = Callable[[str], None]


class DocumentReviewAgent:
    def __init__(
        self,
        llm_client,
        max_chunk_chars: int = 8000,
        max_workers: int = 4,
        language: str = "zh",
        progress: ProgressCallback | None = None,
    ):
        self.llm_client = llm_client
        self.max_chunk_chars = max_chunk_chars
        self.max_workers = max(1, max_workers)
        self.language = language
        self.progress = progress

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
        chunks = chunk_document(document.text, max_chars=self.max_chunk_chars)
        if max_chunks is not None:
            chunks = chunks[:max_chunks]

        selected_agents = _validate_agents(tuple(agents))
        tasks = [
            (chunk_index, chunk, agent_name)
            for chunk_index, chunk in enumerate(chunks)
            for agent_name in selected_agents
        ]
        self._report_progress(
            f"Reviewing {len(chunks)} chunk(s) x {len(selected_agents)} agent(s) "
            f"= {len(tasks)} call(s), {self.max_workers} worker(s)."
        )

        def run(task: tuple[int, Chunk, str]) -> tuple[str, list[Finding]]:
            chunk_index, chunk, agent_name = task
            return self._run_task(
                document_path=str(document.path),
                chunk_index=chunk_index,
                chunk_count=len(chunks),
                chunk=chunk,
                agent_name=agent_name,
                public_context=public_context,
                sensitive_terms=sensitive_terms,
            )

        findings: list[Finding] = []
        raw_outputs: list[str] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for index, (raw, task_findings) in enumerate(executor.map(run, tasks), start=1):
                raw_outputs.append(raw)
                findings.extend(task_findings)
                self._report_progress(f"[{index}/{len(tasks)}] completed")

        findings = sorted(_dedupe_findings(findings), key=lambda item: item.sort_key())
        return ReviewResult(
            document_path=str(document.path),
            summary=_build_summary(findings, selected_agents),
            findings=findings,
            raw_agent_outputs=raw_outputs,
            agents=selected_agents,
        )

    def _run_task(
        self,
        *,
        document_path: str,
        chunk_index: int,
        chunk_count: int,
        chunk: Chunk,
        agent_name: str,
        public_context: str,
        sensitive_terms: str,
    ) -> tuple[str, list[Finding]]:
        location = f"chunk {chunk_index + 1}/{chunk_count}"
        if chunk.section:
            location += f" ({chunk.section})"

        try:
            raw = self._run_agent(
                agent_name=agent_name,
                document_path=document_path,
                chunk_index=chunk_index,
                chunk_count=chunk_count,
                chunk=chunk,
                public_context=public_context,
                sensitive_terms=sensitive_terms,
            )
        except Exception as exc:  # noqa: BLE001 - keep the sweep alive when one call fails
            message = f"{type(exc).__name__}: {exc}"
            finding = _operational_finding(
                agent=agent_name,
                location=location,
                issue_type="agent_error",
                reason=f"Agent call failed after retries: {message}",
                recommendation="Re-run this agent on this chunk, or check API credentials, model, and rate limits.",
            )
            return f"[agent_error] {message}", [finding]

        return raw, _parse_findings(raw, agent_name=agent_name, fallback_location=location)

    def _run_agent(
        self,
        *,
        agent_name: str,
        document_path: str,
        chunk_index: int,
        chunk_count: int,
        chunk: Chunk,
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
                    chunk_text=chunk.text,
                    public_context=public_context,
                    sensitive_terms=sensitive_terms,
                    section=chunk.section,
                    language=self.language,
                ),
            },
        ]
        return self.llm_client.complete_json(messages)

    def _report_progress(self, message: str) -> None:
        if self.progress is not None:
            self.progress(message)


def _load_optional_text(path: str | Path | None) -> str:
    if path is None:
        return ""
    return read_text_best_effort(path).strip()


def _validate_agents(agent_names: tuple[str, ...]) -> tuple[str, ...]:
    unknown = [name for name in agent_names if name not in AGENT_PROMPTS]
    if unknown:
        raise ValueError(f"Unknown agent(s): {', '.join(unknown)}")
    return agent_names


def _operational_finding(
    *,
    agent: str,
    location: str,
    issue_type: str,
    reason: str,
    recommendation: str,
) -> Finding:
    return Finding(
        agent=agent,
        location=location,
        excerpt="",
        issue_type=issue_type,
        severity="info",
        reason=reason,
        recommendation=recommendation,
        needs_human_review=True,
    )


def _parse_findings(raw: str, *, agent_name: str, fallback_location: str) -> list[Finding]:
    try:
        data = json.loads(_extract_json_object(raw))
    except (ValueError, json.JSONDecodeError):
        return [
            _operational_finding(
                agent=agent_name,
                location=fallback_location,
                issue_type="parse_error",
                reason=f"Agent response was not valid JSON: {raw[:160]!r}",
                recommendation="Re-run this agent on this chunk, or inspect the raw output via --raw-out.",
            )
        ]

    items = data.get("findings", [])
    if not isinstance(items, list):
        items = []

    findings: list[Finding] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        findings.append(
            Finding(
                agent=agent_name,
                location=str(item.get("location") or fallback_location),
                excerpt=str(item.get("excerpt") or "").strip(),
                issue_type=str(item.get("issue_type") or "other").strip(),
                severity=normalize_severity(item.get("severity")),
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
    """Merge duplicates across agents and overlapping chunks.

    The key intentionally excludes ``reason``: the same issue reported from two
    overlapping chunks usually shares the excerpt but not the exact wording of
    the reason. Findings without an excerpt fall back to the reason text.
    """
    seen: set[tuple[str, str]] = set()
    deduped: list[Finding] = []
    for finding in findings:
        excerpt_key = finding.excerpt[:120].lower()
        key = (finding.issue_type.lower(), excerpt_key or finding.reason[:120].lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    return deduped


def _build_summary(findings: list[Finding], agents: tuple[str, ...]) -> str:
    agent_list = ", ".join(agents)
    if not findings:
        return f"No issues reported by the selected agents ({agent_list})."

    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    parts = [f"{severity}: {count}" for severity, count in sorted(counts.items())]
    return (
        f"Found {len(findings)} issue(s) from agents ({agent_list}). "
        "Severity counts: " + ", ".join(parts) + "."
    )
