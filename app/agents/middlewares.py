from langchain_core.messages import trim_messages, RemoveMessage
from langgraph.runtime import Runtime
from app.core.config import settings
from langchain.agents import AgentState
from langchain.agents.middleware import before_model
from typing import Any

@before_model
def trim_messages_before_model(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    messages = state["messages"]
    trimmed_messages = trim_messages(messages,
                                    token_counter=len,
                                    strategy="last",
                                    max_tokens=settings.max_llm_input_messages,
                                    start_on="human",
                                    end_on=("human", "tool")
                                    )
    if len(messages) > settings.max_stored_messages:
        return {"llm_input_messages": trimmed_messages, "messages": [RemoveMessage(id=m.id) for m in messages[:-settings.max_stored_messages]]}
    return {"llm_input_messages": trimmed_messages}