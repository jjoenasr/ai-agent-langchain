from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    debug: bool = True
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_ttl_seconds: int = 604800
    llm_provider: str = "google_genai"
    llm_model: str = "gemini-2.5-flash"
    llm_temperature: float = 0.2
    max_llm_input_messages: int = 15
    max_stored_messages: int = 50

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()