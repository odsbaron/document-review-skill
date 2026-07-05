from __future__ import annotations

from dataclasses import dataclass, field


SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}

_SEVERITY_ALIASES = {
    "critical": "critical",
    "blocker": "critical",
    "致命": "critical",
    "严重": "critical",
    "阻断": "critical",
    "high": "high",
    "major": "high",
    "高": "high",
    "重大": "high",
    "medium": "medium",
    "moderate": "medium",
    "中": "medium",
    "中等": "medium",
    "low": "low",
    "minor": "low",
    "低": "low",
    "轻微": "low",
    "info": "info",
    "informational": "info",
    "hint": "info",
    "信息": "info",
    "提示": "info",
}


def normalize_severity(value: object, default: str = "medium") -> str:
    """Map free-form severity labels (including Chinese variants) to the canonical enum."""
    key = str(value or "").strip().lower()
    return _SEVERITY_ALIASES.get(key, default)


@dataclass(frozen=True)
class Finding:
    agent: str
    location: str
    excerpt: str
    issue_type: str
    severity: str
    reason: str
    recommendation: str
    needs_human_review: bool = True

    def sort_key(self) -> tuple[int, str]:
        return (SEVERITY_ORDER.get(self.severity.lower(), 99), self.location)


@dataclass(frozen=True)
class ReviewResult:
    document_path: str
    summary: str
    findings: list[Finding] = field(default_factory=list)
    raw_agent_outputs: list[str] = field(default_factory=list)
    agents: tuple[str, ...] = ()
