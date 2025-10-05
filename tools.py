from langchain_core.tools import tool
from duckduckgo_search import DDGS
from typing import Annotated, Literal, Optional
from langchain_community.tools import ArxivQueryRun
from logger_config import logger
from retriever import RAGManager
import wikipedia
import requests
import duckdb
from google import genai
from google.genai import types
from typing import Annotated
import pandas as pd
import os
import json

# RAG Manager
rag_manager = RAGManager()
# Gemini multimodal client
gemini_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@tool
def visit_web_page(url: str, query: str, section_position: Optional[Literal["start", "middle", "end"]] = None) -> str:
    """
    Visits a webpage at the given url, reads its content as markdown and return relevant sections based on query.
    A section_position relative to the document (start, middle, end) can be added if needed.
    """
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()  # Raise an exception for bad status codes
        html = response.text

        # Optional: Section bias toward start, middle, or end
        if section_position:
            return rag_manager.retrieve_html_section(html , section_position)

        # Ingest documents into vector store
        rag_manager.ingest_documents_from_html(html)
        # Retrieve most similar documents
        return rag_manager.retrieve_documents(query)
    
    except Exception as e:
        logger.error(f"Web Visiting tool error: {str(e)}")
        return f"Could not access the website. Error: {str(e)[:100]}..."

@tool
def web_search(query: str) -> str:
    """Search the web for information"""
    try:
        results = DDGS().text(query, max_results=8)
        if len(results) == 0:
            raise ValueError("No results found! Try a less restrictive/shorter query.")
        postprocessed_results = [f"[{result['title']}]({result['href']})\n{result['body']}" for result in results]
        return "## Search Results\n\n" + "\n\n".join(postprocessed_results)
    except Exception as e:
        logger.error(f"Web search tool error: {e}")
        return f"Error searching the web: {str(e)[:100]}..."
    
@tool
def academic_search(query: str) -> str:
    """Search for arXiv academic papers related to the given query"""
    try:
        search = ArxivQueryRun()
        return search.invoke(query)
    except Exception as e:
        logger.error(f"Academic search tool error: {e}")
        return f"Error searching the web: {str(e)[:100]}..."

@tool
def get_weather(location: Annotated[str, "City Name"]) -> str:
    """Get the current weather for a given location"""
    api_key = os.getenv('OPEN_WEATHER_MAP')
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        main_weather = data["weather"][0]["description"]
        temperature = data["main"]["temp"] - 273.15  # Convert from Kelvin to Celsius
        return f"The weather in {location} is currently {main_weather} with a temperature of {temperature:.2f}°C."
    except Exception as e:
        logger.error(f"Weather tool error: {e}")
        return f"Sorry, I couldn't get the weather information at the moment. Error: {str(e)[:100]}..."


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
        response.raise_for_status()
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
        logger.error(f"Movie tool error: {e}")
        return f"Couldnt find the movies. Error: {str(e)[:100]}..."

@tool
def wiki_search(query: str) -> str:
    """Searches Wikipedia and returns a summary of the top results"""
    try:
        search_results = wikipedia.search(query, results=3)
        if not search_results:
            raise ValueError("No results found on Wikipedia for that query.")
        docs = []
        for res in search_results:
            try:
                page = wikipedia.page(res)
                docs.append(f"**Wikipedia Page:** {page.title}\n**Summary:** {wikipedia.summary(page.title, sentences=1)}\n**Read more:** {page.url}")
            except Exception as e:
                continue
        return "\n\n".join(docs)
    except Exception as e:
        logger.error(f"Wikipedia tool error: {e}")
        return "Could not find wikipedia article for that query"

@tool
def calculator(expression: str) -> str:
    """
    Evaluate an arithmetic expression with + - * / % ** and ().
    """
    return str(eval(expression, {"__builtins__": None}, {}))

@tool
def text_analysis(filepath: str) -> str:
    """
    Use this tool to get the text content of a file.
    Supported file types: .txt, .md, .csv, .json, .py, .xlsx
    """
    ext = os.path.splitext(filepath)[1].lower()

    try:
        if ext == '.txt' or ext == '.md':
            # For .txt and .md files, simply read the text
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()

        elif ext == '.csv':
            # For CSV, return a summary
            df = pd.read_csv(filepath)
            summary = f"""
            CSV file loaded with {df.shape[0]} rows and {df.shape[1]} columns.
            Columns: {', '.join(df.columns)}
            Summary statistics:
            {str(df.describe())}
            """
            return summary

        elif ext == '.json':
            # For JSON, load and return the content as a string
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return json.dumps(data, indent=4)  # Return pretty-printed JSON

        elif ext == '.py':
            # For Python files, just read the text
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()

        elif ext == '.xlsx':
            # For Excel files, use pandas to read the sheet and return as a string
            df = pd.read_excel(filepath)
            summary = f"""
            Excel file loaded with {df.shape[0]} rows and {df.shape[1]} columns.
            Columns: {', '.join(df.columns)}
            Summary statistics:
            {str(df.describe())}
            """
            return summary

        else:
            raise ValueError(f"Unsupported file type: {ext}")

    except Exception as e:
        logger.error(f"Text Analysis tool error: {e}")
        return f"Error reading file {filepath}: {str(e)[:100]}..." 

@tool
def sql_file_analysis(filepath: str, query: Annotated[str, "SQL query"]) -> str:
    """
    Use this tool to run SQL queries on a CSV or Excel file using DuckDB.
    Use 'df' as the table name.
    Example: SELECT * FROM df WHERE column_name = 'value'
    """
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == '.csv':
            df = pd.read_csv(filepath)
        elif ext == '.xlsx':
            df = pd.read_excel(filepath)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        # Validate query
        if not query.strip().lower().startswith("select"):
            raise ValueError("Only SELECT queries are supported.")
        
        # Run the query using DuckDB
        result = duckdb.query_df(df, 'df', query).to_df()
        return result.to_string()
        
    except Exception as e:
        logger.error(f"SQL Analysis tool error: {e}")
        return f"Error running SQL query on file {filepath}: {str(e)[:100]}..."   

@tool
def multimodal_analysis(filepath: str, prompt: str) -> str:
    """
    Send a prompt and a file (image, audio or video) to LLM for multimodal analysis
    Supported file types to analyze: .png, .jpg, .mp3
    """
    try:
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".png":
            mime_type = "image/png"
        elif ext == ".jpg":
            mime_type = "image/jpeg"
        elif ext == ".mp3":
            mime_type = "audio/mp3"
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        with open(filepath, "rb") as f:
            file_bytes = f.read()
        
        response = gemini_client.models.generate_content(
            model='models/gemini-2.5-pro-exp-03-25',
            contents=[
            types.Part.from_bytes(
                data=file_bytes,
                mime_type=mime_type,
            ),
            prompt
            ]
        )
        return response.text
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {str(e)}")
        return f"Error reading file {filepath}: {str(e)[:100]}..."

@tool
def youtube_analysis(url: Annotated[str, "Youtube URL"], prompt: str) -> str:
    """
    Send a youtube url and a prompt to LLM for multimodal processing
    """
    try:
        response = gemini_client.models.generate_content(
            model='models/gemini-2.5-pro-exp-03-25',
            contents=types.Content(
                parts=[
                    types.Part(
                        file_data=types.FileData(file_uri=url)
                    ),
                    types.Part(text=prompt)
                ]
            )
        )
        return response.text
    except Exception as e:
        logger.error(f"Error reading ytb video: {str(e)}")
        return f"Error reading ytb video: {str(e)[:100]}..."

