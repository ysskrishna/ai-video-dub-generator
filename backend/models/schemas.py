from pydantic import BaseModel, Field, field_validator
import re
from typing import Optional, List, Dict, Union
from models.enums import JobStatus
from datetime import datetime

# Video Dubbing Schemas
class VideoDubCreate(BaseModel):
    video_url: str = Field(..., description="YouTube URL to dub")
    target_language: str = Field(..., description="Target language for dubbing (e.g., 'en', 'es', 'fr')")
    
    @field_validator("video_url")
    def validate_youtube_url(cls, v):
        youtube_patterns = [
            r"https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+",
            r"https?://(?:www\.)?youtu\.be/[\w-]+",
            r"https?://(?:www\.)?youtube\.com/embed/[\w-]+",
            r"https?://(?:www\.)?youtube\.com/shorts/[\w-]+"
        ]
        if not any(re.match(pattern, v) for pattern in youtube_patterns):
            raise ValueError("Invalid YouTube URL format")
        return v

class VideoDubResponse(BaseModel):
    job_id: int
    status: JobStatus
    message: str

class VideoDubStatus(BaseModel):
    job_id: int
    video_url: str
    target_language: str
    status: JobStatus
    error_code: Optional[str] = None
    output_video_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True