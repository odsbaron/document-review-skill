import json

import pytest

from doc_review_agent.models import Finding, normalize_severity
from doc_review_agent.reviewer import (
    DEFAULT_AGENTS,
    DocumentReviewAgent,
    _dedupe_findings,
    _extract_json_object,
)


class ScriptedClient:
    """Returns scripted responses in call order; raises entries that are exceptions."""

    def __init__(self, responses):
        self.calls = []
        self._responses = responses

    def complete_json(self, messages):
        self.calls.append(messages)
        response = self._responses[len(self.calls) - 1]
        if isinstance(response, Exception):
            raise response
        return response


def _write_doc(tmp_path):
    document_path = tmp_path / "proposal.md"
    document_path.write_text(
        "# Launch proposal\n\n"
        "We must launch next week because AI can automate the workflow. "
        "The team should align on the new process.",
        encoding="utf-8",
    )
    return document_path


def _finding_payload(severity="high", excerpt="We must launch next week"):
    return json.dumps(
        {
            "findings": [
                {
                    "location": "para 1",
                    "excerpt": excerpt,
                    "issue_type": "normative overstatement",
                    "severity": severity,
                    "reason": "缺少授权来源",
                    "recommendation": "补充授权、范围与例外",
                }
            ]
        }
    )


def test_review_collects_and_normalizes_findings(tmp_path):
    client = ScriptedClient([_finding_payload(severity="严重")])
    reviewer = DocumentReviewAgent(client, max_chunk_chars=2000, max_workers=1)

    result = reviewer.review(_write_doc(tmp_path), agents=("normative",))

    assert len(result.findings) == 1
    assert result.findings[0].severity == "critical"
    assert result.agents == ("normative",)
    assert "normative" in result.summary


def test_malformed_json_becomes_parse_error_finding(tmp_path):
    client = ScriptedClient(["this is not json at all", _finding_payload()])
    reviewer = DocumentReviewAgent(client, max_chunk_chars=2000, max_workers=1)

    result = reviewer.review(_write_doc(tmp_path), agents=("logic", "normative"))

    issue_types = {finding.issue_type for finding in result.findings}
    assert "parse_error" in issue_types
    # The valid response from the second agent still lands in the result.
    assert "normative overstatement" in issue_types
    assert len(client.calls) == 2


def test_agent_exception_becomes_agent_error_finding(tmp_path):
    client = ScriptedClient([RuntimeError("boom"), _finding_payload()])
    reviewer = DocumentReviewAgent(client, max_chunk_chars=2000, max_workers=1)

    result = reviewer.review(_write_doc(tmp_path), agents=("logic", "normative"))

    errors = [finding for finding in result.findings if finding.issue_type == "agent_error"]
    assert len(errors) == 1
    assert "boom" in errors[0].reason
    assert any(finding.issue_type == "normative overstatement" for finding in result.findings)


def test_unknown_agent_raises(tmp_path):
    reviewer = DocumentReviewAgent(ScriptedClient([]), max_workers=1)
    with pytest.raises(ValueError):
        reviewer.review(_write_doc(tmp_path), agents=("nonexistent",))


def test_default_agents_have_prompts():
    from doc_review_agent.prompts import AGENT_PROMPTS

    for agent_name in ("logic", "inside", "data", "reader", "decision", "normative", "operating"):
        assert agent_name in DEFAULT_AGENTS
        assert agent_name in AGENT_PROMPTS


def test_prompt_includes_section_and_language(tmp_path):
    client = ScriptedClient([json.dumps({"findings": []})])
    reviewer = DocumentReviewAgent(client, max_chunk_chars=2000, max_workers=1, language="zh")

    reviewer.review(_write_doc(tmp_path), agents=("decision",))

    user_prompt = client.calls[0][1]["content"]
    assert "Section: Launch proposal" in user_prompt
    assert "Use Chinese for reason and recommendation." in user_prompt


def test_dedupe_ignores_reason_wording():
    base = dict(
        agent="logic",
        location="chunk 1/2",
        excerpt="We must launch next week",
        issue_type="normative overstatement",
        severity="high",
        recommendation="fix",
    )
    findings = [
        Finding(reason="缺少授权来源", **base),
        Finding(reason="没有说明授权来源与范围", **{**base, "location": "chunk 2/2"}),
    ]
    assert len(_dedupe_findings(findings)) == 1


def test_dedupe_keeps_distinct_findings_without_excerpt():
    base = dict(
        agent="logic",
        location="chunk 1/1",
        excerpt="",
        issue_type="other",
        severity="low",
        recommendation="fix",
    )
    findings = [
        Finding(reason="first issue", **base),
        Finding(reason="second issue", **base),
    ]
    assert len(_dedupe_findings(findings)) == 2


@pytest.mark.parametrize(
    ("raw", "expected_substring"),
    [
        ('{"findings": []}', '"findings"'),
        ('```json\n{"findings": []}\n```', '"findings"'),
        ('Noise before {"findings": []} noise after', '"findings"'),
    ],
)
def test_extract_json_object_variants(raw, expected_substring):
    assert expected_substring in _extract_json_object(raw)


def test_extract_json_object_rejects_non_json():
    with pytest.raises(ValueError):
        _extract_json_object("no braces here")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("critical", "critical"),
        ("High ", "high"),
        ("严重", "critical"),
        ("中等", "medium"),
        ("提示", "info"),
        ("unknown-label", "medium"),
        (None, "medium"),
    ],
)
def test_normalize_severity(value, expected):
    assert normalize_severity(value) == expected
