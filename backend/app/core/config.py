from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "GeoSyn"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "geosyn"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # FRED (Federal Reserve) API Key for Macro Data
    FRED_API_KEY: Optional[str] = None

    # Tactical Ingestion Keys
    EVENT_REGISTRY_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"

    def get_db_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        # If Postgres vars are at their defaults, we fallback to SQLite for zero-config local runs
        if self.POSTGRES_SERVER == "localhost" and self.POSTGRES_USER == "postgres" and self.POSTGRES_PASSWORD == "postgres":
            return "sqlite:///./geosyn.db"
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

settings = Settings()
