import os
import logging
import shutil
import asyncio
from moviepy import AudioFileClip
from datetime import datetime

from core.config import settings
from core.dbutils import SessionLocal
from models.models import Job
from models.enums import JobStatus
from services.video_processor_utils import (
    download_youtube_video, 
    transcribe_audio, 
    extract_audio_segments, 
    extract_source_language, 
    translate_segments, 
    synthesize_audio_segments, 
    combine_audio_segments, 
    create_dubbed_video, 
    extract_audio_duration
)

logger = logging.getLogger(__name__)

async def process_video_dubbing_sync(job_id: int):
    db = SessionLocal()
    job = None
    temp_dir = None
    
    try:
        # Get the job from database
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found in database")
            return None
        
        logger.info(f"Processing video dubbing for job {job_id}", extra={"video_url": job.video_url, "target_language": job.target_language})
        
        # Update status to processing
        job.status = JobStatus.PROCESSING.value
        job.error_message = None
        job.updated_at = datetime.now()
        db.commit()

        # hardcoded for now
        output_dir = os.path.join(settings.TEMP_DIR, f"job_14") 
        video_path = os.path.join(output_dir, "video.mp4")
        audio_path = os.path.join(output_dir, "audio.wav")
        

        # # # Create output directory in temp storage
        # output_dir = os.path.join(settings.TEMP_DIR, f"job_{job_id}")
        # os.makedirs(output_dir, exist_ok=True)
        
        # # Step 1: Download video
        # logger.info("Step 1/6: Downloading video...")
        # video_path, audio_path = await download_youtube_video(job.video_url, output_dir)
        
        # # Step 2: Transcribe audio        
        # logger.info("Step 2/6: Transcribing audio...", extra={"audio_path": audio_path})
        # transcribed_response = await transcribe_audio(audio_path)
        # segments = extract_audio_segments(transcribed_response)
        # source_language = extract_source_language(transcribed_response)
        # logger.info(f"Extracted segments", extra={"segments": segments})
        # logger.info(f"Detected Source language", extra={"source_language": source_language})
        
        # # Step 3: Translate segments
        # logger.info("Step 3/6: Translating segments...", extra={"source_language": source_language, "target_language": job.target_language})
        # translated_segments = await translate_segments(segments, source_language, job.target_language)
        # print(translated_segments)
        # logger.info(f"Translated segments", extra={"translated_segments": translated_segments})

        translated_segments = [
            {'start': 8.559999, 'end': 13.935, 'transcript': "'तुम्हारी ढेरों में भरा हुआ। बेसी पीछे है, भाई। मैं तुम्हारी मां को ऐसा पॉट बनाना चाहता हूं। तुम्हें कुछ दूं।'", 'duration': 5.375001000000001}, 
            {'start': 19.535, 'end': 20.435001, 'transcript': '"क्या? ओह।"', 'duration': 0.9000009999999996}
        ]
        
        # Step 4: Synthesize dubbed audio
        logger.info("Step 4/6: Synthesizing dubbed audio...")
        audio_segments, temp_dir = synthesize_audio_segments(translated_segments)
        
        # Get total duration of the audio
        total_duration = extract_audio_duration(audio_path)
        
        # Step 5: Combine audio segments
        logger.info("Step 5/6: Combining audio segments...")
        dubbed_audio = combine_audio_segments(audio_segments, total_duration)
        
        logger.info(f"Dubbed audio", extra={"duration": dubbed_audio.duration, "total_duration": total_duration})
        dubbed_audio_path = f"{output_dir}/dubbed_audio.wav"
        dubbed_audio.write_audiofile(dubbed_audio_path)
        dubbed_audio.close()
        
        # Clean up audio segments
        for seg in audio_segments:
            seg.close()
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        # Step 6: Create final dubbed video
        output_video = f"{output_dir}/dubbed_video.mp4"
        logger.info("Step 6/6: Creating final dubbed video...")
        create_dubbed_video(video_path, dubbed_audio_path, output_video)
        
        # Update job as completed
        job.status = JobStatus.COMPLETED.value
        job.output_video_path = output_video
        job.error_message = None
        job.updated_at = datetime.now()
        db.commit()
        
        logger.info(f"Job {job_id} completed successfully! Output: {output_video}")
        
        # Clean up temporary audio file
        if os.path.exists(dubbed_audio_path):
            os.remove(dubbed_audio_path)
        
        return output_video
        
    except Exception as e:
        logger.exception(f"Error processing job {job_id}")
        
        # Update job status to failed
        if job:
            try:
                job.status = JobStatus.FAILED.value
                job.error_message = f"{str(e)}"
                job.updated_at = datetime.now()
                db.commit()
            except Exception as db_error:
                logger.error(f"Error updating job status: {str(db_error)}")
        
        return None
        
    finally:
        # # Clean up temporary files and close database connection
        # if temp_dir and os.path.exists(temp_dir):
        #     try:
        #         shutil.rmtree(temp_dir)
        #         logger.info(f"Cleaned up temporary files for job {job_id}")
        #     except Exception:
        #         logger.exception(f"Failed to clean up temp directory")
        
        db.close()


def process_video_dubbing(job_id: int):
    return asyncio.run(process_video_dubbing_sync(job_id))
