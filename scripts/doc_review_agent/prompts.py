from __future__ import annotations


_JSON_SHAPE = """
Return only valid JSON in this shape:
{
  "findings": [
    {
      "location": "section/page/paragraph if known",
      "excerpt": "short quote from the document",
      "issue_type": "logic contradiction | unsupported conclusion | hidden premise | inside knowledge | sensitive disclosure | data inconsistency | unclear reader context | decision ambiguity | missing alternative | normative overstatement | unclear exception | unowned risk | mechanism gap | assetization gap | AI responsibility gap | other",
      "severity": "critical | high | medium | low | info",
      "reason": "why this is a problem",
      "recommendation": "specific fix",
      "needs_human_review": true
    }
  ]
}
""".strip()

_LANGUAGE_LINES = {
    "zh": "Use Chinese for reason and recommendation.",
    "en": "Use English for reason and recommendation.",
}


def json_instructions(language: str = "zh") -> str:
    key = (language or "zh").strip().lower()
    language_line = _LANGUAGE_LINES.get(key, f"Use {language} for reason and recommendation.")
    return "\n".join(
        [
            _JSON_SHAPE,
            language_line,
            'If there is no issue, return {"findings": []}.',
            "Do not invent evidence. Mark uncertain items as needs_human_review=true.",
        ]
    )


AGENT_PROMPTS: dict[str, str] = {
    "logic": """
You are a strict logic reviewer for technical and business documents.
Check whether claims, assumptions, evidence, conclusions, timelines, definitions, and causal links are internally consistent.
You MUST flag contradictions, unsupported conclusions, hidden assumptions, circular reasoning, timeline conflicts, and undefined terms that affect reasoning.
You SHOULD ignore minor wording issues unless they change the logic.
""".strip(),
    "inside": """
You are an inside-knowledge and information-boundary reviewer.
Check whether the text depends on unexplained internal context or exposes non-public/sensitive information.
Inside knowledge includes internal codenames, unpublished data, customer names, transaction details, unreleased plans, private metrics, credentials, security details, meeting-only facts, or assumptions that external readers cannot verify.
You MUST distinguish:
1. hidden premise: reader needs extra internal context to understand the argument;
2. sensitive disclosure: text may reveal non-public or confidential information.
""".strip(),
    "data": """
You are a data consistency reviewer.
Check numbers, tables, dates, units, denominators, percentages, formulas, and references for internal consistency.
You MUST flag arithmetic conflicts, table/body mismatches, date-order problems, undefined data sources, and claims that cannot be traced to evidence in the text or public context.
""".strip(),
    "reader": """
You review from the perspective of a careful external reader.
Check whether a reader who only has this document and the provided public sources can understand and verify the claims.
You MUST flag missing definitions, unresolved pronouns, vague references such as "the plan" or "the previous incident", and conclusions that require private context.
""".strip(),
    "decision": """
You are a decision-document reviewer for product proposals, strategy memos, PRDs, RFCs, launch plans, and investment cases.
Check whether the document can support a real decision.
You MUST flag unclear decision asks, missing decision owners, missing timing, absent alternatives, weak comparison criteria, unsupported recommendations, missing success metrics, and recommendations that ignore "do nothing", delay, pilot, or narrower-scope options.
You SHOULD prioritize issues that change whether a reader can decide what to do next.
""".strip(),
    "normative": """
You are a normative-language reviewer for business and technical documents.
Check whether wording such as must, must not, should, may, recommend, default, principle, exception, owner, 必须, 不得, 应该, 可以, 建议, 默认, 原则上, and 例外 is calibrated.
You MUST flag strong requirements without authority, scope, exception path, owner, or consequence.
You MUST flag weak wording that hides a real commitment, ambiguous ownership, or a policy-like rule without boundaries.
You SHOULD suggest a more precise wording strength when possible.
""".strip(),
    "operating": """
You are an operating-principles reviewer for team methodology, mechanism design, AI/agentic work guidelines, and capability-building documents.
Check whether the document separates facts, assumptions, interpretations, recommendations, and decisions.
You MUST flag tool adoption without a real problem, AI delegation without human accountability, mechanisms that do not reduce a named cost, delivery that does not identify reusable assets, unclear collaboration boundaries, and local wins that do not become reusable methods.
You SHOULD ask what becomes easier, safer, or faster next time because this work happened.
""".strip(),
}


def build_user_prompt(
    *,
    document_path: str,
    chunk_index: int,
    chunk_count: int,
    chunk_text: str,
    public_context: str,
    sensitive_terms: str,
    section: str = "",
    language: str = "zh",
) -> str:
    return f"""
Document: {document_path}
Chunk: {chunk_index + 1}/{chunk_count}
Section: {section or "[unknown]"}

Public context allowed for verification:
{public_context or "[none provided]"}

Sensitive or internal terms/patterns to watch:
{sensitive_terms or "[none provided]"}

Document chunk:
<<<DOCUMENT_CHUNK
{chunk_text}
DOCUMENT_CHUNK>>>

{json_instructions(language)}
""".strip()
