from __future__ import annotations

from dataclasses import dataclass, field


SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}


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
