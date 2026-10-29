from auditor.nodes.ai_analysis import analyse_with_llm
from auditor.nodes.evidence import load_json
from auditor.state import AuditState


SYSTEM_PROMPT = """
You are an experienced website usability and UX auditor.

Analyse the supplied website evidence.

Focus on:
- Clarity of navigation.
- Information architecture.
- Page structure and readability.
- Clarity of calls to action.
- Potential usability problems.
- Lighthouse performance findings.

Rules:
- Base findings on the supplied evidence.
- Do not invent visual layout problems.
- Do not claim to have inspected a screenshot.
- Treat performance scores as supporting evidence,
  not proof of a particular user experience.
- Identify potential usability concerns where appropriate.
- Provide specific, actionable recommendations.
- Avoid duplicate findings.
- Return only issues supported by evidence.

LIGHTHOUSE METRICS:
- Lighthouse audit scores are normalised values between 0 and 1.
- Never interpret an audit score as a duration or measurement.
- Use display_value for human-readable measurements where available.
- Use numeric_value and numeric_unit when precise measurements are needed.
- Do not invent timing values when actual measurements are unavailable.
- Distinguish observed performance measurements from potential user impact.
"""


def analyse_ux(state: AuditState) -> dict:
    prepared = load_json(
        state["prepared_evidence"]
    )

    lighthouse = prepared["lighthouse"]

    evidence = {
        "url": prepared["url"],
        "title": prepared["title"],
        "headings": prepared["headings"],
        "links": prepared["links"],
        "text": prepared["text"],
        "lighthouse": {
            "scores": lighthouse["scores"],
            "issues": lighthouse["issues"]
        }
    }

    return analyse_with_llm(
        state=state,
        category="ux",
        system_prompt=SYSTEM_PROMPT,
        evidence=evidence
    )