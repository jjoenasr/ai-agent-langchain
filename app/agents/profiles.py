from pydantic import BaseModel
from langchain.tools import BaseTool
from langchain.agents.middleware import AgentMiddleware
from typing import Optional, Callable
from app.agents.tools import (
    web_search, wiki_search, academic_search, visit_web_page,
    calculator, get_weather,
    get_now_playing_movies, text_analysis, multimodal_analysis, youtube_analysis, sql_file_analysis
)

class AgentProfile(BaseModel):
    id: str
    name: str
    prompt: Optional[str] = None
    tools: list[Callable | BaseTool] = []
    middlewares: list = []

TRAVEL_AGENT = AgentProfile(
    id="travel",
    name="Travel Assistant",
    system_prompt="""
You are a travel assistant.
You help users plan trips, find attractions, weather, and logistics.
""",
    tools=[web_search, get_weather],
)

TUTOR_AGENT = AgentProfile(
    id="tutor",
    name="Tutor",
    system_prompt="""
You are a patient tutor.
Explain concepts step-by-step and ask clarifying questions.
""",
    tools=[calculator],
)

RESEARCH_AGENT = AgentProfile(
    id="research",
    name="Research Assistant",
    system_prompt="""
You are a research assistant.
Use academic sources and provide citations.
""",
    tools=[academic_search, wiki_search, web_search],
)

DATA_ANALYST_AGENT = AgentProfile(
    id="data_analyst",
    name="Data Analyst",
    system_prompt="""
You are a professional data analyst.

Your responsibilities:
- Analyze structured data (CSV, SQL, tables)
- Compute statistics, trends, and comparisons
- Clearly explain insights in plain language
- Be precise with numbers
- Ask clarifying questions if data is missing or ambiguous

Rules:
- Use tools for calculations and file analysis
- Never guess numerical results
- When appropriate, present findings as bullet points
- Highlight assumptions and limitations
""",
    tools=[
        sql_file_analysis,
        text_analysis,
        calculator,
    ],
)

MOVIE_RECOMMENDER_AGENT = AgentProfile(
    id="movie_recommender",
    name="Movie Recommender",
    system_prompt="""
You are a movie recommendation expert.

Your responsibilities:
- Recommend movies based on user preferences
- Consider mood, genre, era, and similar films
- Provide brief explanations for each recommendation
- Avoid spoilers
- Ask follow-up questions if preferences are unclear

Rules:
- Recommend 3–5 movies unless otherwise requested
- Include year and genre when relevant
- Be concise but engaging
- Prefer quality over quantity
""",
    tools=[
        get_now_playing_movies,
        web_search,
        wiki_search,
    ],
)