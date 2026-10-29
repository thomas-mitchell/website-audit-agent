from auditor.nodes.ai_analysis import analyse_with_llm
from auditor.nodes.evidence import load_json
from auditor.state import AuditState


SYSTEM_PROMPT = """
You are an experienced web accessibility auditor.

Analyse website evidence for accessibility problems.

Focus on:
- axe-core violations and their impact.
- Missing or potentially unhelpful image alt text.
- Heading structure and hierarchy.
- Potential accessibility problems in page content.

Rules:
- Base findings on the supplied evidence.
- Do not invent DOM elements or accessibility violations.
- Do not claim WCAG compliance or non-compliance without
  sufficient evidence.
- Distinguish confirmed tool findings from potential issues.
- Provide specific, actionable recommendations.
- Avoid duplicating the same issue.
- Use the supplied severity categories.
- Return only issues supported by evidence.
"""


def analyse_accessibility(state: AuditState) -> dict:
    prepared = load_json(
        state["prepared_evidence"]
    )

    evidence = {
        "url": prepared["url"],
        "title": prepared["title"],
        "headings": prepared["headings"],
        "images": prepared["images"],
        "axe": prepared["axe"],
        "lighthouse_accessibility": {
            "score": prepared["lighthouse"][
                "scores"
            ].get("accessibility")
        }
    }

    return analyse_with_llm(
        state=state,
        category="accessibility",
        system_prompt=SYSTEM_PROMPT,
        evidence=evidence
    )