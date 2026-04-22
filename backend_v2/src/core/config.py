import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_PORT: int = 8000
    DB_SERVER: str = ""
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASS: str = ""
    BARTENDER_WATCH_FOLDER: str = "../print_jobs"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
