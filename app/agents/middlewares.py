from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    ModelRequest
)
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.runtime import Runtime
from langchain_core.messages import trim_messages, RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from app.utils import remove_incomplete_tool_calls
from app.core.logger_config import logger
from app.core.config import settings
from typing import Any

class TrimMessagesMiddleware(AgentMiddleware):
    def _apply_trimming(self, messages, max_count: int, is_for_llm=False):
        """
        Unified trimming logic. 
        - If is_for_llm=True: Strict rules to ensure the LLM doesn't hallucinate or crash.
        - If is_for_llm=False: Lazy rules just to keep the DB size in check & preserve instructions.
        """
        kwargs = {
            "token_counter": len,
            "strategy": "last",
            "max_tokens": max_count,
            "include_system": True,
        }
        
        if is_for_llm:
            # LLM needs a valid conversation start (Human) and end (Human/Tool)
            kwargs.update({
                "start_on": "human",
                "end_on": ("human", "tool")
            })

        trimmed = trim_messages(messages, **kwargs)
        
        # Always clean up orphaned tool calls/responses to prevent state corruption
        return remove_incomplete_tool_calls(trimmed)
    
    def _prune_stored_messages(self, messages):
        """Keeps the state messages clean for the UI."""
        if len(messages) > settings.max_stored_messages:
            # PRUNE FOR DB: Keep more messages, no strict start/end rules
            kept_messages = self._apply_trimming(messages, settings.max_stored_messages, is_for_llm=False)
            return {"messages": [
                RemoveMessage(id=REMOVE_ALL_MESSAGES),
                *kept_messages
            ]}
        return None

    def after_agent(self, state: AgentState, runtime: Runtime):
        return self._prune_stored_messages(state["messages"])
    
    async def aafter_agent(self, state: AgentState, runtime: Runtime):
        return self._prune_stored_messages(state["messages"])

    def wrap_model_call(self, request: ModelRequest, handler):
        # TRIM FOR LLM: Small context window, strict start/end rules
        trimmed = self._apply_trimming(request.messages, settings.max_llm_input_messages, is_for_llm=True)
        return handler(request.override(messages=trimmed))

    async def awrap_model_call(self, request: ModelRequest, handler):
        trimmed = self._apply_trimming(request.messages, settings.max_llm_input_messages, is_for_llm=True)
        return await handler(request.override(messages=trimmed))

class LoggingMiddleware(AgentMiddleware):
    def _log_model_response(self, state: AgentState) -> None:
        if state["messages"]:
            last_msg = state["messages"][-1].content
            if isinstance(last_msg, str) and last_msg != "":
                logger.info(f"New AI Message: {repr(last_msg[:50])}...")
    
    def _log_tool_call(self, request: ToolCallRequest) -> None:
        logger.info(f"New Tool Call: '{request.tool_call['name']}' with args {request.tool_call['args']}...")

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        self._log_model_response(state)
        return None

    async def aafter_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        self._log_model_response(state)
        return None

    def wrap_tool_call(self, request: ToolCallRequest, handler):
        self._log_tool_call(request)
        result = handler(request)
        return result

    async def awrap_tool_call(self, request: ToolCallRequest, handler):
        self._log_tool_call(request)
        result = await handler(request)
        return result