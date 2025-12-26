import gradio as gr
from app.agents.base import AIAgent
from app.agents.profiles import TUTOR_AGENT
from uuid import uuid4

async def create_tutor_agent_view():
    agent = await AIAgent.create(TUTOR_AGENT)

    with gr.Blocks() as tutor_demo:
        thread_id = gr.State("")
        hist = gr.State([])

        async def load_session():
            tid = uuid4().hex
            messages = await agent.load_prev_messages(tid)
            return tid, messages

        tutor_demo.load(load_session, outputs=[thread_id, hist])
        gr.Markdown("## Tutor Agent Chat")

        chatbot = gr.Chatbot(value=hist.value, placeholder="Ask anything...", label="Tutor Assistant")
        msg = gr.MultimodalTextbox(
            placeholder="Ask your question",
            file_types=[".txt", ".csv", ".md", ".json", ".py", ".xlsx", ".png", ".jpg", ".mp3"],
            show_label=False,
            submit_btn=True
        )

        msg.submit(agent.stream_answer, [thread_id, msg, chatbot], [msg, chatbot])
        gr.ClearButton([msg, chatbot])

    return tutor_demo
