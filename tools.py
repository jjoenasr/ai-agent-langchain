import requests
import os
import json
from langchain_core.tools import tool
import wikipedia
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import DuckDuckGoSearchRun
from huggingface_hub import list_models

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a given location"""
    api_key = os.getenv('OPEN_WEATHER_MAP')
    url = "http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("cod") != 200:
            return "Sorry, I couldn't get the weather information at the moment."
        main_weather = data["weather"][0]["description"]
        temperature = data["main"]["temp"] - 273.15  # Convert from Kelvin to Celsius
        return f"The weather in {location} is currently {main_weather} with a temperature of {temperature:.2f}°C."
    except Exception as e:
        return f"Sorry, I couldn't get the weather information at the moment. Error: {e}"


@tool
def wiki_search(query: str) -> str:
    """Searches Wikipedia and returns a summary"""
    try:
        return wikipedia.summary(query, sentences=3)
    except:
        return "Could not find Wikipedia article"

@tool
def get_now_playing_movies() -> str:
    """Get the movies that are now playing in cinema"""
    url = "https://api.themoviedb.org/3/movie/now_playing"
    params={
        "api_key": os.getenv("TMDB_API_KEY"),
        "language": "en-US",
        "page": 1
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return "Sorry, I couldn't get the now playing movies"
        data = response.json()
        movies = data['results'][:5]
        movie_list = [
            {
                'title': movie['title'],
                'release_date': movie['release_date'],
                'overview': movie['overview'],
            }
            for movie in movies
        ]
        return json.dumps(movie_list, indent=2)
    except Exception as e:
        return f"Couldnt find the movies. Error: {e}"

@tool
def search_web(query: str) -> str:
    """Search the web for information"""
    try:
        # search = TavilySearchResults(max_results=2)
        search = DuckDuckGoSearchRun(max_results=2)
        return search.invoke(query)
    except Exception as e:
        return f"Error searching the web: {str(e)}"


@tool
def get_hub_stats(author: str) -> str:
    """Fetches the most downloaded model from a specific author on the Hugging Face Hub."""
    try:
        # List models from the specified author, sorted by downloads
        models = list(list_models(author=author, sort="downloads", direction=-1, limit=1))

        if models:
            model = models[0]
            return f"The most downloaded model by {author} is {model.id} with {model.downloads:,} downloads."
        else:
            return f"No models found for author {author}."
    except Exception as e:
        return f"Error fetching models for {author}: {str(e)}"

#print(get_weather.invoke("London"))
#print(wiki_search.invoke("Viola Davis"))
