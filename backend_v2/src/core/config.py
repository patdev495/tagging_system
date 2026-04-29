import os
import sys
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_PORT: int = 8000
    DB_SERVER: str = ""
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASS: str = ""
    PDF_EXPORT_DIR: str = ""  # Đường dẫn lưu file PDF tạm, nếu rỗng dùng %TEMP%\ny_labels
    
    class Config:
        # Determine .env location
        if getattr(sys, 'frozen', False):
            env_file = os.path.join(os.path.dirname(sys.executable), ".env")
        else:
            env_file = ".env"
        extra = "ignore"

settings = Settings()
