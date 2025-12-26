import asyncio
import gradio as gr
from app.gradio.views.tutor import create_tutor_agent_view
from app.gradio.views.travel import create_travel_agent_view
from app.gradio.views.data_analyst import create_data_analyst_agent_view
from app.core.logger_config import logger

async def main():
    logger.info("Launching Gradio Multi-Agent Interface...")

    tutor_ui = await create_tutor_agent_view()
    travel_ui = await create_travel_agent_view()
    data_analyst_ui = await create_data_analyst_agent_view()

    # Use Tabs to separate agents
    with gr.Blocks() as demo:
        with gr.Tabs():
            with gr.TabItem("Tutor"):
                tutor_ui.render()
            with gr.TabItem("Travel"):
                travel_ui.render()
            with gr.TabItem("Data Analyst"):
                data_analyst_ui.render()

    demo.launch()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program interrupted, shutting down gracefully...")
