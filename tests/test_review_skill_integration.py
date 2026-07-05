import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class FakeLLMClient:
    def __init__(self):
        self.calls = []

    def complete_json(self, messages):
        self.calls.append(messages)
        return json.dumps({"findings": []})


class ReviewSkillIntegrationTests(unittest.TestCase):
    def test_decision_review_agents_are_available(self):
        from doc_review_agent.reviewer import DEFAULT_AGENTS
        from doc_review_agent.prompts import AGENT_PROMPTS

        for agent_name in ("logic", "inside", "data", "reader", "decision", "normative", "operating"):
            self.assertIn(agent_name, DEFAULT_AGENTS)
            self.assertIn(agent_name, AGENT_PROMPTS)

    def test_reviewer_runs_decision_normative_and_operating_agents(self):
        from doc_review_agent.reviewer import DocumentReviewAgent

        with tempfile.TemporaryDirectory() as tmp:
            document_path = Path(tmp) / "proposal.md"
            document_path.write_text(
                "# Launch proposal\n\n"
                "We must launch next week because AI can automate the workflow. "
                "The team should align on the new process.",
                encoding="utf-8",
            )

            fake_client = FakeLLMClient()
            reviewer = DocumentReviewAgent(fake_client, max_chunk_chars=2000)
            result = reviewer.review(
                document_path,
                agents=("decision", "normative", "operating"),
                max_chunks=1,
            )

        self.assertEqual(len(fake_client.calls), 3)
        self.assertIn("No logic", result.summary)
        system_prompts = [call[0]["content"] for call in fake_client.calls]
        self.assertTrue(any("decision" in prompt.lower() for prompt in system_prompts))
        self.assertTrue(any("normative" in prompt.lower() for prompt in system_prompts))
        self.assertTrue(any("operating" in prompt.lower() for prompt in system_prompts))


if __name__ == "__main__":
    unittest.main()
