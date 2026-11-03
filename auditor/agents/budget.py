from langchain.agents.middleware import AgentMiddleware


class InvestigationBudget(AgentMiddleware):
    def __init__(self, max_tool_calls: int = 10):
        self.max_tool_calls = max_tool_calls
        self.calls = 0

    async def awrap_tool_call(self, request, handler):
        if self.calls >= self.max_tool_calls:
            return (
                "INVESTIGATION BUDGET EXHAUSTED. "
                "Do not call any more tools. "
                "Produce your final conclusion using existing evidence."
            )

        self.calls += 1
        return await handler(request)