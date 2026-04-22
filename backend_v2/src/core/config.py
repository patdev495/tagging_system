import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_PORT: int = 8001
    
    class Config:
        env_file = ".env"

settings = Settings()
