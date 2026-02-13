from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk, ToolMessageChunk, ToolMessage
from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph
from langchain.chat_models import init_chat_model
from typing import AsyncGenerator, Optional, Literal
from app.core.config import settings
from app.core.logger_config import logger
from app.agents.profiles import AgentProfile
from app.agents.persistence import setup_persistence
from app.agents.middlewares import LoggingMiddleware, TrimMessagesMiddleware
from app.gradio.schemas import MultimodalMessage
from app.utils import download_file, try_parse
import gradio as gr
import json

class AIAgent:
    def __init__(self, agent: Optional[CompiledStateGraph] = None, checkpointer_type: Literal["MongoDBSaver", "MemorySaver"] = "MemorySaver"):
        self.agent = agent
        self.checkpointer_type = checkpointer_type
    
    @classmethod
    async def create(cls, profile: AgentProfile) -> "AIAgent":
        llm = init_chat_model(f"{settings.llm_provider}:{settings.llm_model}", temperature=settings.llm_temperature)
        tools = profile.tools
        prompt = profile.prompt
        middlewares = [TrimMessagesMiddleware(), LoggingMiddleware()] + profile.middlewares
        checkpointer_type, checkpointer = await setup_persistence()
        agent = create_agent(llm, tools, checkpointer=checkpointer, system_prompt=prompt, middleware=middlewares)
        logger.info(f"{profile.name} AI Agent initialized.")
        return cls(agent, checkpointer_type)
    
    async def load_prev_messages(self, thread_id: str) -> list:
        """Load agent messages in gradio format"""
        config = {"configurable": {"thread_id": thread_id}}
        logger.info(f"New session started, thread_id: {thread_id}")
        hist = []
        try:
            if self.checkpointer_type == "MongoDBSaver":
                state = await self.agent.aget_state(config)
            else:
                state = self.agent.get_state(config)   
            last_tool_message: gr.ChatMessage = None
            msgs = state.values.get('messages', [])
            for msg in msgs:
                if isinstance(msg, HumanMessage):
                    hist.append(gr.ChatMessage(role='user', content=msg.text))
                    last_tool_message = None
                elif isinstance(msg, AIMessage):
                    if msg.tool_calls:
                        if last_tool_message is None:
                            last_tool_message = gr.ChatMessage(role='assistant', content="")
                            hist.append(last_tool_message)
                        for tool_call in msg.tool_calls:
                            tool_name = tool_call.get('name', 'Unknown Tool')
                            tool_args = tool_call.get('args', 'no args')
                            last_tool_message.content += f"Input: {json.dumps(tool_args, indent=2)}"
                            last_tool_message.metadata = {"title": f"🛠️ Invoking {tool_name}..."}
                    else:
                        hist.append(gr.ChatMessage(role='assistant', content=msg.text))
                elif isinstance(msg, ToolMessage) and last_tool_message is not None:
                    tool_content = try_parse(msg.content)
                    tool_output = tool_content if isinstance(tool_content, str) else json.dumps(tool_content, indent=2)
                    last_tool_message.content += f"\nOutput: {tool_output}"
        except Exception as e:
            logger.error(f"Error loading prev messages: {str(e)}")
        return hist

    async def stream_answer(self, thread_id: str, msg_dict: dict, hist: list) -> AsyncGenerator[tuple[dict, list],  None]:
        """Stream the answer from the agent and update the chat history"""
        try:
            msg = MultimodalMessage(**msg_dict)
            query, files = msg.text, msg.files
            if not query.strip():
                hist.append(gr.ChatMessage(role="assistant", content="you can't send an empty message"))
                yield MultimodalMessage().model_dump(), hist
            else:
                hist.append(gr.ChatMessage(role="user", content=query))
                logger.info(f"User Message: {query}")
                if files:
                    for file in files:
                        hist.append(gr.ChatMessage(role="user", content=gr.File(file)))
                        file_path = download_file(file)
                        if file_path:
                            query += f"\nThe file is attached and available at filepath: {file_path}"
                yield MultimodalMessage().model_dump(),  hist
                buffer = ""
                config = {"configurable": {"thread_id": thread_id}}
                async for chunk, _ in self.agent.astream({"messages": [HumanMessage(content=query)]}, config=config, stream_mode="messages"):
                    if isinstance(chunk, AIMessageChunk):
                        if chunk.tool_calls:
                            for tool_call in chunk.tool_calls:
                                tool_name = tool_call.get('name', 'Unknown Tool')
                                tool_args = tool_call.get('args', 'no args')
                                if isinstance(tool_args, dict) and "runtime" in tool_args:
                                    tool_args = {k: v for k, v in tool_args.items() if k != "runtime"}
                                logger.info(f"Invoking tool: {tool_name} with arguments: {tool_args}")
                                
                                # Format the tool call and arguments
                                hist.append(gr.ChatMessage(role="assistant",
                                                        content=f"Input: {json.dumps(tool_args, indent=2)}",
                                                        metadata={"title": f"🛠️ Invoking {tool_name}...", "status": "pending"}))
                                yield MultimodalMessage().model_dump(), hist
                        else:
                            buffer += chunk.content
                            msg = gr.ChatMessage(role="assistant", content=buffer)
                            yield MultimodalMessage().model_dump(), hist + [msg]
                    elif isinstance(chunk, ToolMessage):
                        output_content = chunk.content
                        last_tool_msg: gr.ChatMessage = hist[-1]
                        last_tool_msg.content += f"\nOutput: {output_content}"
                        last_tool_msg.metadata["status"] = "done"
                        yield MultimodalMessage().model_dump(), hist
                hist.append(gr.ChatMessage(role="assistant", content=buffer))
                logger.info(f"AI response from assistant: {buffer[:50]}...")
                yield MultimodalMessage().model_dump(), hist
        except Exception as e:
            logger.error(f"Error in chat function: {e}")
            yield MultimodalMessage().model_dump(), hist + [gr.ChatMessage(role="assistant", content="Internal error. Try again later ")]
            return
    
    async def answer(self, question: str, thread_id: str) -> str:
        """Answer a question directly using the agent"""
        if not question.strip():
            return "You can't send an empty message"
        try:
            logger.info(f"Agent received question (first 50 chars): {question[:50]}...")
            config = {"configurable": {"user_id": "user-xxx", "thread_id": thread_id}}
            llm_output: AIMessage = await self.agent.ainvoke({"messages": [HumanMessage(content=question)]}, config=config)['messages'][-1]
            logger.info(f"Agent answers: {llm_output.content}")
            return llm_output
        except Exception as e:
            logger.error(f"Error in chat function: {e}")
            return "Internal error. Try again later "