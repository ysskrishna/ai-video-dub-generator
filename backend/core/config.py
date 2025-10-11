from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    DEEPGRAM_API_KEY: str
    OPENAI_API_KEY: str
    ELEVENLABS_API_KEY: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8" 

settings = Settings()