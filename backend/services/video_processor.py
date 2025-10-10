import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_video_dubbing_sync(job_id: int):
    logger.info(f"Processing video dubbing for job {job_id}")
