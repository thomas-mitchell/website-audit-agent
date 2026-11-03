from langchain_core.callbacks import AsyncCallbackHandler


class InvestigatorCallbackHandler(AsyncCallbackHandler):
    async def on_tool_start(
        self,
        serialized: dict,
        input_str: str,
        **kwargs,
    ):
        name = serialized.get("name", "unknown")

        print(f"[Investigator] Calling {name}")
        print(f"  Input: {input_str[:500]}")

    async def on_tool_end(
        self,
        output,
        **kwargs,
    ):
        print("[Investigator] Tool completed")
        print(f"  Output: {str(output)[:500]}")

    async def on_tool_error(
        self,
        error: BaseException,
        **kwargs,
    ):
        print(f"[Investigator] Tool failed: {error}")