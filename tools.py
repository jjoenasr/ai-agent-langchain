import requests
import os
from langchain_core.tools import tool
import wikipedia
from langchain_community.tools.tavily_search import TavilySearchResults

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
        movies = data['results']
        movie_list = []
        for movie in movies[:5]:
            movie_info = {
                'title': movie['title'],
                'release_date': movie['release_date'],
                'overview': movie['overview'],
                'poster_path': movie['poster_path'],
            }
            movie_list.append(str(movie_info))
        return "\n".join(movie_list)
    except Exception as e:
        return f"Couldnt find the movies. Error: {e}"

@tool
def search_web(query: str) -> str:
    """Search the web for information"""
    search = TavilySearchResults(max_results=2)
    return search.invoke(query)

#print(get_weather.invoke("London"))
#print(wiki_search.invoke("Viola Davis"))
