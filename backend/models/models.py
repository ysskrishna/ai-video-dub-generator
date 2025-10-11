from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from core.dbutils import Base
from sqlalchemy.orm import declarative_mixin
from datetime import datetime
from models.enums import JobStatus

@declarative_mixin
class Timestamp:
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

# Job model
class Job(Timestamp, Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, autoincrement=True)
    video_url = Column(String)
    target_language = Column(String)
    status = Column(String, default=JobStatus.PENDING.value)
    error_code = Column(String, nullable=True)
    output_video_path = Column(String, nullable=True)
