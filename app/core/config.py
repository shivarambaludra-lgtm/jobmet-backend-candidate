from pydantic_settings import BaseSettings
from pydantic import BaseModel


class Settings(BaseSettings):
    PROJECT_NAME: str = "JobMet ApplyMet Backend"
    API_V1_PREFIX: str = "/api/v1"
    SQLALCHEMY_DATABASE_URI: str = "postgresql://user:password@localhost/dbname"

    class Config:
        env_file = ".env"

settings = Settings()
