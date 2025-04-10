import os
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk, trim_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.mongodb import AsyncMongoDBSaver
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from tools import get_weather, get_now_playing_movies, search_web, get_hub_stats
from retriever import guest_info_tool
from pymongo import AsyncMongoClient
import gradio as gr
import logging
import asyncio

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(filename='agent.log', encoding='utf-8', mode='a')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

# Persistence layer
async def setup_persistence():
    try:
        host = os.getenv('MONGODB_URI')
        if not host:
            raise ValueError("MONGODB_URI environment variable not set")
        mongodb_client = AsyncMongoClient(host)
        await mongodb_client.server_info()  # Check if the connection is successful
        logger.info("Connected to MongoDB successfully")
        checkpointer = AsyncMongoDBSaver(mongodb_client)
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        logger.info("Falling back to MemorySaver")
        checkpointer = MemorySaver()
    return checkpointer

def pre_model_hook(state):
    # Keep the last 5 messages and remove the oldest ones
    trimmed_messages = trim_messages(state["messages"],
                                    token_counter=len,
                                    strategy="last",
                                    max_tokens=5,
                                    start_on="human",
                                    end_on=("human", "tool"),
                                    include_system=True)
    return {"llm_input_messages": trimmed_messages}

async def main():
    # Initialize agent and tools
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2, streaming=True)
    tools = [get_weather, get_now_playing_movies, search_web, get_hub_stats, guest_info_tool]
    checkpointer = await setup_persistence()
    agent = create_react_agent(llm, tools, checkpointer=checkpointer, pre_model_hook=pre_model_hook)
    config = {"configurable": {"user_id": "user-xxx", "thread_id": "my-langchain-agent"}}

    async def chat(query: str, hist: list):
        try:
            if not query.strip():
                hist.append(gr.ChatMessage(role="assistant", content="you can't send an empty message"))
                yield "", hist
            else:
                hist.append(gr.ChatMessage(role="user", content=query))
                logger.info(f"User Message: {query}")
                yield "", hist
                buffer = ""
                async for chunk, _ in agent.astream({"messages": [HumanMessage(content=query)]}, config, stream_mode="messages"):
                    if isinstance(chunk, AIMessageChunk):
                        if chunk.tool_calls:
                            for tool_call in chunk.tool_calls:
                                tool_name = tool_call.get('name', 'Unknown Tool')
                                tool_args = tool_call.get('args', 'no args')
                                logger.info(f"Invoking tool: {tool_name} with arguments: {tool_args}")
                                
                                # Format the tool call and arguments
                                hist.append(gr.ChatMessage(role="assistant",
                                                        content=f"Invoking {tool_name} with {tool_args}",
                                                        metadata={"title": f"🛠️ Used tool {tool_name}"}))
                                yield "", hist
                        else:
                            buffer += chunk.content
                            msg = gr.ChatMessage(role="assistant", content=buffer)
                            yield "", hist + [msg]
                hist.append(gr.ChatMessage(role="assistant", content=buffer))
                logger.info(f"AI response from assistant: {buffer[:50]}...")
                yield "", hist
        except Exception as e:
            logger.error(f"Error in chat function: {e}")
            yield "", hist

    # Gradio UI
    with gr.Blocks() as demo:
        gr.Markdown("# Chat with your agent and see its thoughts")
        chatbot = gr.Chatbot(label="AI Assistant",
                            type="messages",
                            placeholder="What can i help you with?",
                            show_copy_button=True)
        msg = gr.Textbox(placeholder="Enter a message", show_label=False, submit_btn=True)
        clear = gr.ClearButton([msg, chatbot])
        msg.submit(chat, [msg, chatbot], [msg, chatbot])

    demo.launch()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program interrupted, shutting down gracefully...")




