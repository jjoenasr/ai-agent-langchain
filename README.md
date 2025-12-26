# Multi-Agent AI with LangGraph and Gradio

This project showcases a sophisticated multi-agent conversational AI system built with LangGraph, LangChain, and Google's Gemini LLM. It features a modular architecture that allows for the easy creation and management of distinct AI agent "profiles," each with its own unique personality, tools, and purpose. The user interface is powered by Gradio, providing a clean, tab-based layout to interact with the different agents.

## Features

- 🤖 **Multi-Agent Architecture**: Easily define and switch between different agent profiles (e.g., Data Analyst, Travel Agent, Tutor).  
- ⚙️ **LangGraph Backend**: Built on LangGraph for robust, stateful, and observable agent execution.  
- 🎨 **Configurable Agent Profiles**: Each agent is defined by a profile specifying its system prompt, tools, and middleware.  
- 💾 **Persistent Conversations**: Chat history is saved using MongoDB or in-memory checkpointers, allowing sessions to be resumed.  
- ⚡ **Real-time Streaming**: Responses and tool usage are streamed in real-time for a dynamic user experience.  
- 🛠️ **Comprehensive Tool Integration**:
  - **Data Analysis**: Execute SQL queries directly on uploaded CSV and Excel files.  
  - **Web Intelligence**: Perform web searches and conduct RAG-powered analysis of webpage content.  
  - **Academic Research**: Search for papers on ArXiv.  
  - **Real-world Info**: Get current weather and movie information.  
  - **Utilities**: Wikipedia search and a calculator.  
  - **Multimodal Analysis**: Analyze images, audio, and YouTube videos.  
- 🧠 **Context Management**: Automatically trims message history to fit within the LLM's context window while preserving long-term memory.

## Prerequisites

Make sure you have Python installed and the following API keys:  
- Google API key (for Gemini LLM or adequate one based on your prefered provider)  
- OpenWeatherMap API key  
- TMDB API key (for movie information)  
- (Optional) LangSmith API key for tracing

## Installation

1. Clone the repository.  
2. Install the required packages:

```bash
uv sync --locked
# or pip install -r requirements.txt
```

3. Create a .env file in the root directory and add your API keys. You can use .env.example as a template:
```bash
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
OPEN_WEATHER_MAP=your_openweathermap_key
TMDB_API_KEY=your_tmdb_key
LANGSMITH_API_KEY=your_langsmith_api_key
MONGODB_URI=mongodb://localhost:27017
```

## Usage

Run the Gradio application:

```bash
uv run python -m app.gradio.app
# python -m app.gradio.app
```

The Gradio interface will launch in your web browser, presenting each available agent in its own tab.

## Project Architecture

The project follows a modular structure to separate concerns and make it easy to extend.

- `app/gradio/app.py`: The main entry point that launches the Gradio multi-tab interface.

- `app/gradio/views/`: Contains the UI definitions for each agent tab (e.g., data_analyst.py, travel.py).

- `app/agents/base.py`: Defines the core `AIAgent` class, which orchestrates agent creation, stream handling, and state management.

- `app/agents/profiles.py`: Contains `AgentProfile` definitions, specifying the unique prompt, tools, and configuration for each agent persona.

- `app/agents/tools.py`: Implements all tools available to the agents (e.g., web_search, sql_file_analysis).

- `app/agents/persistence.py`: Manages conversation persistence using LangGraph checkpointers (MongoDB or in-memory).

- `app/agents/middlewares.py`: Houses LangGraph middleware, such as the message trimming logic.

- `app/agents/retriever.py`: Implements the `RAGManager` for efficient document retrieval from web pages.

- `app/core/config.py`: Centralized application configuration using Pydantic.

- `app/core/logger_config.py`: Logging setup for the application.

## Agent Profiles

This system is built around the concept of "Agent Profiles," which are Python objects that define an agent's behavior and capabilities. The currently implemented profiles are:

- **Data Analyst**: A professional data analyst that can perform SQL queries on uploaded files (CSV, XLSX), compute statistics, and explain insights.

- **Travel Assistant**: Helps users plan trips, find attractions, and check weather and logistics.

- **Tutor**: A patient tutor that can explain concepts step-by-step and use a calculator for math problems.

- **Research Assistant**: Uses academic and web sources to find information and provide citations.

- **Movie Recommender**: Recommends movies based on user preferences by searching the web and movie databases.

## Available Tools

- `sql_file_analysis`: Runs SQL queries on CSV or Excel files using DuckDB.

- `text_analysis`: Extracts and summarizes content from various file types (.txt, .md, .csv, .json, .py, .xlsx).

- `multimodal_analysis`: Performs analysis on image (.png, .jpg) and audio (.mp3) files.

- `youtube_analysis`: Analyzes content from a YouTube video URL.

- `visit_web_page`: Visits a URL, ingests its content into a RAG pipeline, and returns sections relevant to a query.

- `web_search`: Searches the web using DuckDuckGo.

- `academic_search`: Searches for academic papers on ArXiv.

- `get_weather`: Retrieves current weather information from OpenWeatherMap.

- `get_now_playing_movies`: Fetches a list of movies currently in theaters from TMDB.

- `wiki_search`: Searches Wikipedia for article summaries.

- `calculator`: Evaluates basic arithmetic expressions.
