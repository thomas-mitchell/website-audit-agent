import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from auditor.models.investigation import (
    InvestigationRequest,
    InvestigationResult,
    ScreenshotEvidence,
    InvestigationConclusion,
)
from auditor.tools.langchain_browser import create_browser_tools
from auditor.tools.session import BrowserSession


INVESTIGATOR_PROMPT = """
You are a website quality assurance investigator.

Your job is to answer a specific investigation question using
browser inspection tools.

RULES:
- Use the available tools to gather evidence.
- Do not assume an issue exists simply because it was reported.
- Distinguish observed facts from interpretations.
- Do not invent browser interactions or test results.
- Do not claim to have visually inspected an image when you
  have only inspected its HTML attributes.
- If the available tools cannot answer the question, set
  resolved to false and explain what additional testing is needed.
- Set resolved to true only when the evidence answers the
  original investigation question.
- Include concrete observations in the evidence list.
- Keep your investigation focused on the supplied question.
- Report observed accessibility roles and names, but do not
  determine whether they constitute an accessibility violation.
  That decision belongs to the reviewer.

You are investigating a finding, not deciding its severity
or whether it should appear in the final report.

ACCESSIBILITY VERIFICATION:
- DOM elements and accessibility landmarks are not equivalent.
- Do not infer accessibility-tree roles solely from HTML tag names.
- A footer element does not always expose a contentinfo landmark.
- Multiple elements with the same semantic role do not automatically
  constitute an accessibility violation.
- Do not claim to have verified screen-reader behaviour without
  appropriate testing.
- If the investigation requires accessibility-tree inspection and
  no suitable tool is available, set resolved to false.

SELECTOR USAGE:
- Browser tools accept Playwright selectors, not jQuery selectors.
- Use :has-text("text") instead of :contains("text").
- Prefer stable IDs, attributes and semantic selectors.
- For text searches, use Playwright's :has-text() or text= syntax.
- If a tool reports an invalid selector, correct it and retry.
- A failed tool call is not evidence that an element is absent.
- Do not mark an investigation unresolved solely because a selector
  failed if alternative selectors can answer the question.

VISUAL INVESTIGATION:
- You can capture screenshots using capture_screenshot.
- You can visually inspect captured screenshots using analyse_screenshot.
- To investigate visual content:
  1. Identify the relevant element using DOM inspection.
  2. Capture a screenshot of that element.
  3. Pass the screenshot path to analyse_screenshot with a
     specific question.
  4. Combine the visual observations with DOM and accessibility
     evidence when answering the investigation question.

- Prefer element screenshots over full-page screenshots when
  investigating a specific image or component.
- A screenshot path alone is not visual evidence.
- Do not describe screenshot contents unless analyse_screenshot
  has successfully examined them.
- Distinguish visual observations from interpretations.
- Visual appearance does not establish accessibility-tree behaviour.
- When deciding whether an image is decorative or informative,
  consider both its visible content and surrounding page context.
- Do not assume that every photograph requires descriptive alt text.
- If visual analysis fails or remains inconclusive, report the
  limitation rather than inventing a conclusion.

INVESTIGATION EFFICIENCY AND STOPPING:

- Your goal is to answer the investigation question, not to
  exhaustively inspect every matching element on the page.
- Before each additional tool call, consider whether the
  available evidence is already sufficient to answer the question.
- Stop investigating once sufficient evidence has been collected.
- Prefer a small number of well-chosen observations over broad
  searches returning dozens of unrelated elements.
- Do not repeat a tool call with the same arguments unless the
  page state has changed or there is a specific reason to retry.
- Do not repeat screenshot analysis when the previous analysis
  already answered the visual question.
- If further inspection is unlikely to change the conclusion,
  produce the InvestigationResult immediately.
- If the question cannot be answered with the available tools,
  report the limitation and finish rather than searching indefinitely.
- Do not attempt to inspect every image on a page unless the
  investigation explicitly requires an exhaustive inventory.
- Distinguish evidence sufficient to answer the question from
  evidence sufficient to confirm a particular accessibility defect.

INVESTIGATION CONCLUSIONS:
- A successful investigation does not necessarily confirm a defect.
- An investigation may resolve a question by disproving its premise.
- When a reported element or link is absent, report that observation
  without assuming the corresponding feature is broken.
- Do not infer JavaScript behaviour solely from DOM inspection.
- Do not infer the purpose of hidden or animated elements without
  supporting evidence.
- Use resolved=true when sufficient evidence answers the specific
  question, even if the original finding is unsupported.
- Clearly distinguish "not found in the inspected page state"
  from "does not exist anywhere on the website".

EVIDENCE AND CERTAINTY:
- Distinguish three levels of evidence:
  OBSERVED: Directly established by a browser tool.
  INFERRED: A reasonable interpretation of observed evidence.
  UNVERIFIED: A claim requiring testing that has not been performed.

- Clearly identify which conclusions are observations and which
  are interpretations.
- Never present an inference as a directly observed fact.
- Browser accessibility snapshots show accessible roles, names,
  and structure. They do not prove how a particular screen reader
  will announce or navigate the content.
- An image's filename, dimensions, position, surrounding text,
  or HTML attributes do not establish its visual contents.
- Do not claim that an image contains a logo, person, product,
  or other meaningful content without visual evidence.
- An image with alt="" is generally treated as decorative by
  assistive technologies. The absence of aria-hidden does not
  automatically make it an accessibility violation.
- When visual inspection is required but unavailable, explain
  what could be established through DOM inspection and what
  remains unverified.
- Do not set resolved=true when the investigation question
  requires evidence that the available tools cannot obtain.
- Include relevant limitations in the answer field.
"""


MAX_TOOL_CALLS = 10
MAX_MODEL_CALLS = 12


async def investigate(
    url: str,
    request: InvestigationRequest,
    output_dir: Path | None = None,
) -> InvestigationResult:

    load_dotenv()

    model = init_chat_model(
        os.getenv("AUDITOR_MODEL", "anthropic:claude-sonnet-4-6")
    )

    messages = [
        SystemMessage(content=INVESTIGATOR_PROMPT),
        HumanMessage(
            content=json.dumps({
                "url": url,
                "investigation": request.model_dump(mode="json"),
            })
        ),
    ]

    screenshots: dict[str, ScreenshotEvidence] = {}

    async with BrowserSession(
        url,
        output_dir=output_dir,
    ) as session:
        tools = create_browser_tools(session)
        tools_by_name = {tool.name: tool for tool in tools}

        tool_model = model.bind_tools(tools)

        tool_calls_used = 0

        for _ in range(MAX_MODEL_CALLS):
            remaining = MAX_TOOL_CALLS - tool_calls_used

            if remaining <= 0:
                break

            response = await tool_model.ainvoke(messages)

            if not response.tool_calls:
                messages.append(response)
                break

            # Avoid partially executing a batch of tool calls.
            if len(response.tool_calls) > remaining:
                print(
                    "[Investigator] Insufficient budget for "
                    "the next tool-call batch."
                )
                break

            messages.append(response)

            for tool_call in response.tool_calls:
                name = tool_call["name"]
                args = tool_call["args"]

                print(f"[Investigator] Calling {name}: {args}")

                tool_calls_used += 1

                try:
                    tool = tools_by_name[name]
                    result = await tool.ainvoke(args)

                    if name == "capture_screenshot" and result.get("success"):
                        screenshot_path = Path(result["path"]).resolve()

                        screenshots[str(screenshot_path)] = ScreenshotEvidence(
                            path=Path(result["path"]).as_posix(),
                            capture_type=result["capture_type"],
                            selector=result.get("selector"),
                        )

                    elif name == "analyse_screenshot" and result.get("success"):
                        screenshot_path = str(Path(result["path"]).resolve())

                        screenshot = screenshots.get(screenshot_path)

                        if screenshot:
                            screenshot.analysed = True
                            screenshot.analysis_question = result["question"]
                            screenshot.analysis_answer = result["answer"]

                except Exception as exc:
                    result = {
                        "success": False,
                        "error": str(exc),
                    }

                print(
                    f"[Investigator] Result: {str(result)[:500]}"
                )

                messages.append(
                    ToolMessage(
                        content=json.dumps(result, default=str),
                        tool_call_id=tool_call["id"],
                    )
                )

        print(
            "[Investigator] Evidence collection complete. "
            f"Tool calls used: {tool_calls_used}/{MAX_TOOL_CALLS}"
        )

        # The conclusion phase has no tools.
        conclusion_model = model.with_structured_output(
            InvestigationConclusion
        )

        conclusion_messages = [
            *messages,
            HumanMessage(
                content=(
                    "Evidence collection is complete. "
                    "Do not request additional tools. "
                    "Produce the final InvestigationResult using "
                    "only the evidence collected above. "
                    "Answer the original investigation question. "
                    "If the evidence is insufficient, explain the "
                    "limitations and set resolved=false. "
                    "Do not invent observations or test results."
                )
            ),
        ]

        conclusion = await conclusion_model.ainvoke(
            conclusion_messages
        )

        return InvestigationResult(
            **conclusion.model_dump(),
            finding_id=request.finding_id,
            screenshots=list(screenshots.values()),
        )