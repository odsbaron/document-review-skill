from __future__ import annotations

from .models import ReviewResult


def render_markdown_report(result: ReviewResult) -> str:
    lines = [
        "# Document Review Report",
        "",
        f"- Document: `{result.document_path}`",
        f"- Agents: {', '.join(result.agents) if result.agents else '[unknown]'}",
        f"- Summary: {result.summary}",
        "",
        "## Findings",
        "",
    ]

    if not result.findings:
        lines.append("No findings.")
        return "\n".join(lines).rstrip() + "\n"

    for index, finding in enumerate(result.findings, start=1):
        human_review = "yes" if finding.needs_human_review else "no"
        lines.extend(
            [
                f"### {index}. {finding.severity.upper()} - {finding.issue_type}",
                "",
                f"- Agent: `{finding.agent}`",
                f"- Location: {finding.location}",
                f"- Needs human review: {human_review}",
                f"- Excerpt: {finding.excerpt or '[not provided]'}",
                f"- Reason: {finding.reason or '[not provided]'}",
                f"- Recommendation: {finding.recommendation or '[not provided]'}",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"
