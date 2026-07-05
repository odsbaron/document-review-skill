"""End-to-end smoke test: reviewer wiring, prompts, and report rendering."""

import json


class FakeLLMClient:
    def __init__(self):
        self.calls = []

    def complete_json(self, messages):
        self.calls.append(messages)
        return json.dumps({"findings": []})


def test_reviewer_runs_selected_agents_and_renders_report(tmp_path):
    from doc_review_agent.report import render_markdown_report
    from doc_review_agent.reviewer import DocumentReviewAgent

    document_path = tmp_path / "proposal.md"
    document_path.write_text(
        "# Launch proposal\n\n"
        "We must launch next week because AI can automate the workflow. "
        "The team should align on the new process.",
        encoding="utf-8",
    )

    fake_client = FakeLLMClient()
    reviewer = DocumentReviewAgent(fake_client, max_chunk_chars=2000, max_workers=1)
    result = reviewer.review(
        document_path,
        agents=("decision", "normative", "operating"),
        max_chunks=1,
    )

    assert len(fake_client.calls) == 3
    assert "No issues reported" in result.summary
    system_prompts = [call[0]["content"] for call in fake_client.calls]
    assert any("decision" in prompt.lower() for prompt in system_prompts)
    assert any("normative" in prompt.lower() for prompt in system_prompts)
    assert any("operating" in prompt.lower() for prompt in system_prompts)

    report = render_markdown_report(result)
    assert "# Document Review Report" in report
    assert "decision, normative, operating" in report
    assert "No findings." in report
