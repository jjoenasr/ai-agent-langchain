import os
from dotenv import load_dotenv
from agent import ReActAgent
import gradio as gr
from logger_config import logger
import asyncio

load_dotenv()

async def main():
    # Initialize agent and tools
    agent = ReActAgent()
    await agent.initialize_agent()

    # Gradio UI
    with gr.Blocks() as demo:
        gr.Markdown("# Chat with your agent and see its thoughts")
        chatbot = gr.Chatbot(label="AI Assistant",
                            type="messages",
                            placeholder="What can i help you with?",
                            show_copy_button=True)
    
        with gr.Row():
            msg = gr.Textbox(placeholder="Enter a message",
                            show_label=False,
                            submit_btn=True,
                            scale=4)
            file = gr.UploadButton(file_types=[".txt", ".csv", ".md", ".json", ".py", ".xlsx", ".png", ".jpg", ".mp3"], scale=1)
            send_btn = gr.Button("Send", scale=1)
        clear = gr.ClearButton([msg, chatbot])
        msg.submit(agent.stream_answer, [msg, file, chatbot], [msg, file, chatbot])

    demo.launch()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program interrupted, shutting down gracefully...")




