import os
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk, trim_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.mongodb import AsyncMongoDBSaver
from pymongo import AsyncMongoClient
from langgraph.prebuilt import create_react_agent
from tools import web_search, visit_web_page, wiki_search, academic_search, calculator, text_analysis, multimodal_analysis, youtube_analysis
from typing import AsyncGenerator, Optional
from logger_config import logger
import shutil
import tempfile
from uuid import uuid4
import gradio as gr

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

# Method to keep the last 5 messages and remove the oldest ones
def pre_model_hook(state):
    trimmed_messages = trim_messages(state["messages"],
                                    token_counter=len,
                                    strategy="last",
                                    max_tokens=5,
                                    start_on="human",
                                    end_on=("human", "tool"),
                                    include_system=True)
    return {"llm_input_messages": trimmed_messages}

class ReActAgent:
    def __init__(self, user_id: str ="user-xxx", thread_id: str = "my-langchain-agent"):
        logger.info("AI Agent initialized.")
        if not os.getenv('GOOGLE_API_KEY'):
            logger.error("Missing Google API Key")
            raise ValueError("Missing Google API Key")
        self.config = {"configurable": {"user_id": user_id, "thread_id": thread_id}}
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
        self.tools = [web_search, visit_web_page, wiki_search, academic_search, calculator]
        self.checkpointer = None
        self.agent = None
    
    async def initialize_agent(self):
        self.checkpointer = await setup_persistence()
        self.agent = create_react_agent(self.llm, self.tools, checkpointer=self.checkpointer, pre_model_hook=pre_model_hook)
    
    def download_file(self, uploaded_file: tempfile._TemporaryFileWrapper) -> str:
        """Process uploaded file from Gradio interface and save it locally"""
        file_path = os.path.join("temp", uploaded_file.name)

        # Check if file already exists
        if os.path.exists(file_path):
            return file_path
        
        try:
            # Save the uploaded file locally
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                # Use shutil.copyfileobj to copy the file content to the destination
                shutil.copyfileobj(uploaded_file, f)
            logger.info(f"File uploaded and saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving uploaded file: {e}")
        
        return file_path

    async def stream_answer(self, query: str, file: Optional[tempfile._TemporaryFileWrapper], hist: list) -> AsyncGenerator[tuple[str, Optional[tempfile._TemporaryFileWrapper], list],  None]:
        try:
            if not query.strip():
                hist.append(gr.ChatMessage(role="assistant", content="you can't send an empty message"))
                yield "", None, hist
            else:
                hist.append(gr.ChatMessage(role="user", content=query))
                hist.append(gr.ChatMessage(role="user", content=file))
                logger.info(f"User Message: {query}")
                if file is not None:
                    hist.append(gr.ChatMessage(role="user", content=file))
                    file_path = self.download_file(file)
                    if file_path:
                        logger.info(f"Downloaded user file at: {file_path}")
                        query += f"\nThe file is attached and available at filepath: {file_path}"
                yield "", None,  hist
                buffer = ""
                async for chunk, _ in self.agent.astream({"messages": [HumanMessage(content=query)]}, config=self.config, stream_mode="messages"):
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
                                yield "", None, hist
                        else:
                            buffer += chunk.content
                            msg = gr.ChatMessage(role="assistant", content=buffer)
                            yield "", None, hist + [msg]
                hist.append(gr.ChatMessage(role="assistant", content=buffer))
                logger.info(f"AI response from assistant: {buffer[:50]}...")
                yield "", None, hist
        except Exception as e:
            logger.error(f"Error in chat function: {e}")
            yield "", None, hist
            return
    
    async def answer(self, question: str) -> str:
        if not question.strip():
            return "You can't send an empty message"
        logger.info(f"Agent received question (first 50 chars): {question[:50]}...")
        llm_output: AIMessage = self.agent.invoke({"messages": [HumanMessage(content=question)]}, config=self.config)['messages'][-1]
        logger.info(f"Agent answers: {llm_output.content}")
        return llm_output