# LangChain Agent with Gradio Interface

A powerful conversational AI agent built with LangChain, Google's Gemini LLM, and Gradio interface. The agent can perform multiple tasks including weather checks, movie information retrieval, web searches, and more.

## Features

- 🤖 Interactive chat interface using Gradio
- 🛠️ Multiple tool integration:
  - Weather information retrieval
  - Now playing movies in theaters
  - Web search using DuckDuckGo
  - Hugging Face Hub model statistics
  - Guest information retrieval using semantic vector similarity
- 📝 Real-time streaming responses
- 🔍 Transparent tool usage display
- 💾 Memory management for conversation context

## Prerequisites

Make sure you have Python installed and the following API keys:
- Google API key (for Gemini LLM)
- OpenWeatherMap API key
- TMDB API key (for movie information)
- Tavily API key (for web searches)

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
TAVILY_API_KEY=your_tavily_key
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

1. **Weather Information** (`get_weather`):
   - Retrieves current weather conditions for any location
   - Provides temperature in Celsius and weather description

2. **Wikipedia Search** (`wiki_search`):
   - Fetches concise summaries from Wikipedia articles
   - Returns 3-sentence summaries for quick information

3. **Now Playing Movies** (`get_now_playing_movies`):
   - Lists currently playing movies in theaters
   - Includes movie titles, release dates, and overviews

4. **Web Search** (`search_web`):
   - Performs web searches using DuckDuckGo
   - Returns relevant search results

5. **Hugging Face Hub Stats** (`get_hub_stats`):
   - Retrieves statistics for Hugging Face model authors
   - Shows most downloaded model and download count

6. **Guest Information** (`guest_info_retriever`):
   - Retrieves detailed information about gala guests
   - Searches by name or relation using vector similarity

## Project Structure

- `app.py`: Main application file with Gradio interface and agent setup
- `tools.py`: Contains tool implementations for weather, movies, web search, and hub stats
- `retriever.py`: Handles guest information vector storage and retrieval
- `.env`: Environment variables and API keys

## Contributing

Feel free to open issues or submit pull requests to improve the project.
