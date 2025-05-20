import os
from dotenv import load_dotenv
from agent import ReActAgent
import gradio as gr
from logger_config import logger
from uuid import uuid4
import asyncio

load_dotenv()

async def main():
    print("\n" + "-"*30 + " App Starting " + "-"*30)
    # Initialize agent and tools
    agent = ReActAgent()
    await agent.initialize_agent()
    print("-"*(60 + len(" App Starting ")) + "\n")

    # Gradio UI    
    with gr.Blocks() as demo:
        gr.Markdown("# Chat with your agent and see its thoughts")
        # State variables per user/session
        thread_id = gr.State(uuid4().hex)
        hist = gr.State([])
        
        # Load previous messages on session start
        demo.load(agent.load_prev_messages, [thread_id], [hist])
    

        chatbot = gr.Chatbot(value=hist.value,
                            label="AI Assistant",
                            type="messages",
                            placeholder="What can i help you with?",
                            show_copy_button=True)
        msg = gr.MultimodalTextbox(placeholder="Ask anything",
                                   file_types=[".txt", ".csv", ".md", ".json", ".py", ".xlsx", ".png", ".jpg", ".mp3"],
                                   show_label=False,
                                   submit_btn=True)
    
        clear = gr.ClearButton([msg, chatbot])
        msg.submit(agent.stream_answer, [thread_id, msg, chatbot], [msg, chatbot])
    logger.info("Launching Gradio Interface for Basic Agent Evaluation...")
    demo.launch()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program interrupted, shutting down gracefully...")




