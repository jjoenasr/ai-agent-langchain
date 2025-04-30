# LangChain Agent with Gradio Interface

A powerful conversational AI agent built with LangChain, Google's Gemini LLM, and Gradio interface. The agent can perform multiple tasks including weather checks, movie information retrieval, web searches, and more.

## Features

- 🤖 Interactive chat interface using Gradio
- 🛠️ Comprehensive tool integration:
  - Web search and webpage analysis
  - Academic paper search via ArXiv
  - Weather information retrieval
  - Movie information from TMDB
  - Wikipedia search
  - Calculator functions
  - File analysis and content extraction
  - Multimodal analysis (images, audio)
  - YouTube video analysis
- 📝 Real-time streaming responses
- 🔍 Transparent tool usage display
- 💾 Memory management with RAG support

## Prerequisites

Make sure you have Python installed and the following API keys:
- Google API key (for Gemini LLM)
- OpenWeatherMap API key
- TMDB API key (for movie information)

## Installation

1. Clone the repository
2. Install the required packages:
```bash
pip install requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```env
GOOGLE_API_KEY=your_google_api_key
OPEN_WEATHER_MAP=your_openweathermap_key
TMDB_API_KEY=your_tmdb_key
LANGSMITH_API_KEY=your_langsmith_api_key
```

## Usage

Run the application:
```bash
python app.py
```

The Gradio interface will launch in your default web browser, allowing you to:
- Chat with the AI agent
- See tool usage in real-time
- Copy conversation messages
- Clear the chat history

## Tools Available

1. **Web Page Analysis** (`visit_web_page`):
   - Visits and analyzes webpage content
   - RAG-optimized content processing

1. **Web Search** (`web_search`):
   - DuckDuckGo-powered web search
   - Returns formatted markdown results

1. **Academic Search** (`academic_search`):
   - ArXiv paper search integration
   - Academic research discovery

1. **Weather Information** (`get_weather`):
   - Current weather conditions
   - Weather description

1. **Movie Information** (`get_now_playing_movies`):
   - Currently playing movies
   - TMDB API integration

1. **Wikipedia Search** (`wiki_search`):
   - Wikipedia article summaries
   - Direct article links

1. **Calculator** (`calculator`):
   - Basic arithmetic operations
   - Supports +, -, *, /, %, ** and ()

1. **Text Analysis** (`text_analysis`):
   - Supports multiple file formats:
     - .txt, .md (plain text)
     - .csv (with statistics)
     - .json (formatted output)
     - .py (source code)
     - .xlsx (spreadsheet data)

1. **Multimodal Analysis** (`multimodal_analysis`):
   - Image analysis (.png, .jpg)
   - Audio processing (.mp3)
   - Gemini-powered insights

1. **YouTube Analysis** (`youtube_analysis`):
    - YouTube video analysis
    - Content understanding
    - Gemini multimodal processing

## Project Structure

- `app.py`: Main application file with Gradio interface and agent setup
- `agent.py`: Agent implementation
- `tools.py`: Tool implementations
- `retriever.py`: RAG Manager implementation
- `logger_config.py`: # Logging configuration
- `.env`: Environment variables and API keys

## Contributing

Feel free to open issues or submit pull requests to improve the project.
