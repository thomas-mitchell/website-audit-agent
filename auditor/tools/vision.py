import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage


VISION_PROMPT = """
You are a website quality assurance visual investigator.

Analyse the supplied screenshot and answer the user's question.

RULES:
- Describe only what is visible in the screenshot.
- Distinguish direct visual observations from interpretations.
- Do not invent details that cannot be seen.
- Do not infer DOM attributes, ARIA roles, or accessibility names
  from visual appearance.
- Do not assume an image is informational simply because it is large.
- Explain when the screenshot is insufficient to answer the question.
- Do not determine WCAG compliance from visual appearance alone.
- Keep your response focused on the question.
"""


async def analyse_screenshot(
    path: Path,
    question: str,
) -> str:
    """Ask a vision-capable model to inspect a screenshot."""

    load_dotenv()

    image_data = base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")

    model = init_chat_model(
        os.getenv("AUDITOR_MODEL", "anthropic:claude-sonnet-4-6")
    )

    response = await model.ainvoke([
        SystemMessage(content=VISION_PROMPT),
        HumanMessage(content=[
            {
                "type": "text",
                "text": question,
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_data}"
                },
            },
        ]),
    ])

    return str(response.content)