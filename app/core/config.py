from pydantic_settings import BaseSettings
from pydantic import model_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "JobMet Backend"
    API_V1_PREFIX: str = "/api/v1"
    SQLALCHEMY_DATABASE_URI: str
    
    # Auth settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    GOOGLE_CLIENT_ID: str = ""
    
    # Week 3-4: Agentic RAG settings
    OPENAI_API_KEY: str = ""
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "jobmet123"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    class Config:
        env_file = ".env"

settings = Settings()
