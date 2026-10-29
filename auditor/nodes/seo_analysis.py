from auditor.nodes.ai_analysis import analyse_with_llm
from auditor.nodes.evidence import load_json
from auditor.state import AuditState


SYSTEM_PROMPT = """
You are an experienced SEO and website content auditor.

Analyse the supplied website evidence.

Focus on:
- Page title and meta description.
- Heading structure.
- Content clarity and organization.
- Readability and usefulness.
- Internal linking and navigation labels.
- Canonical and robots metadata.
- Relevant Lighthouse SEO findings.

Rules:
- Base findings on the supplied evidence.
- Do not invent search rankings or traffic data.
- Do not assume a target keyword unless supplied.
- Distinguish confirmed technical issues from
  subjective content recommendations.
- Provide specific, actionable recommendations.
- Avoid duplicate findings.
- Return only issues supported by evidence.
"""


def analyse_seo(state: AuditState) -> dict:
    prepared = load_json(
        state["prepared_evidence"]
    )

    lighthouse = prepared["lighthouse"]

    evidence = {
        "url": prepared["url"],
        "title": prepared["title"],
        "description": prepared["description"],
        "canonical": prepared["canonical"],
        "robots": prepared["robots"],
        "headings": prepared["headings"],
        "links": prepared["links"],
        "text": prepared["text"],
        "lighthouse_seo": {
            "score": lighthouse["scores"].get("seo"),
            "issues": [
                issue
                for issue in lighthouse["issues"]
                if issue["id"] in (
                    "document-title",
                    "meta-description",
                    "link-text",
                    "crawlable-anchors",
                    "canonical",
                    "robots-txt",
                    "hreflang",
                    "is-crawlable",
                )
            ]
        }
    }

    return analyse_with_llm(
        state=state,
        category="seo",
        system_prompt=SYSTEM_PROMPT,
        evidence=evidence
    )