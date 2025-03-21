# LangChain Agent with Gradio Interface

A powerful conversational AI agent built with LangChain, Google's Gemini LLM, and Gradio interface. The agent can perform multiple tasks including weather checks, Wikipedia searches, movie information retrieval, and web searches.

## Features

- 🤖 Interactive chat interface using Gradio
- 🛠️ Multiple tool integration:
  - Weather information retrieval
  - Wikipedia article summaries
  - Now playing movies in theaters
  - Web search capabilities
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
   - Performs web searches using Tavily
   - Returns relevant search results

## Project Structure

- `app.py`: Main application file with Gradio interface and agent setup
- `tools.py`: Contains all tool implementations
- `.env`: Environment variables and API keys

## Contributing

Feel free to open issues or submit pull requests to improve the project.
