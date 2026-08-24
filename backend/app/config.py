from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str          # e.g. postgresql://user:pass@localhost:5432/jobboard
    gemini_api_key: str = ""   # optional here — user supplies their OWN key at chat time
    embedding_model: str = "text-embedding-004"
    llm_model: str = "gemini-3.7-flash"
    fallback_llm_model: str = "gemini-3.5-flash-lite"
    recommendation_mode: str = "keyword"  # set to "rag" when ML dependencies are available
    allowed_origins: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"

    # class Config:
    #     env_file = ".env"
    #     extra = "ignore"

settings = Settings()
