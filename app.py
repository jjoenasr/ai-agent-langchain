import os
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, AIMessageChunk
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from tools import get_weather, get_now_playing_movies, search_web, get_hub_stats
from retriever import load_guest_dataset
import gradio as gr
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.4, streaming=True)
memory = MemorySaver()
guest_tool = load_guest_dataset()
tools = [get_weather, get_now_playing_movies, search_web, get_hub_stats, guest_tool]

agent = create_react_agent(llm, tools, checkpointer=memory)
config = {"configurable": {"thread_id": "my-langchain-agent"}}

async def chat(query: str, hist: list):
    try:
        if not query.strip():
            hist.append(gr.ChatMessage(role="assistant", content="you can't send an empty message"))
            yield "", hist
        else:
            hist.append(gr.ChatMessage(role="user", content=query))
            yield "", hist
            buffer = ""
            async for chunk, _ in agent.astream({"messages": [HumanMessage(content=query)]}, config, stream_mode="messages"):
                if isinstance(chunk, AIMessageChunk):
                    if chunk.tool_calls:
                        for tool_call in chunk.tool_calls:
                            tool_name = tool_call.get('name', 'Unknown Tool')
                            tool_args = tool_call.get('args', 'no args')
                            
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
            yield "", hist
    except Exception as e:
        logger.error(f"Error in chat function: {e}")
        yield "", hist


with gr.Blocks() as demo:
    gr.Markdown("# Chat with your agent and see its thoughts")
    chatbot = gr.Chatbot(label="AI Assistant",
                         type="messages",
                         placeholder="What can i help you with?",
                         show_copy_button=True)
    msg = gr.Textbox(placeholder="Enter a message", show_label=False, submit_btn=True)
    clear = gr.ClearButton([msg, chatbot])
    msg.submit(chat, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch()




