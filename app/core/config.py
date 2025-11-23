from pydantic_settings import BaseSettings
from pydantic import BaseModel, model_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "JobMet ApplyMet Backend"
    API_V1_PREFIX: str = "/api/v1"
    SQLALCHEMY_DATABASE_URI: str = "postgresql://user:password@localhost/dbname"
    OPENAI_API_KEY: str | None = None
    SECRET_KEY: str = "your-secret-key-here"
    DATABASE_URL: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"

    @model_validator(mode='after')
    def set_database_uri(self):
        if self.DATABASE_URL:
            self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL
        return self

settings = Settings()
