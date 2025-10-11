import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    DEEPGRAM_API_KEY: str
    OPENAI_API_KEY: str
    ELEVENLABS_API_KEY: str
    DEFAULT_SOURCE_LANGUAGE: str = "en"
    
    # Storage paths
    STORAGE_ROOT: str = str(Path(__file__).parent.parent / "storage")
    TEMP_DIR: str = str(Path(__file__).parent.parent / "storage" / "temp")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **data):
        super().__init__(**data)
        # Ensure directories exist
        os.makedirs(self.STORAGE_ROOT, exist_ok=True)
        os.makedirs(self.TEMP_DIR, exist_ok=True)

settings = Settings()