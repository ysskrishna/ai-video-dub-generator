import os
import logging
import shutil
import asyncio
import yt_dlp
import moviepy as mp
from moviepy import AudioFileClip
from deepgram import DeepgramClient
from openai import AsyncOpenAI
from elevenlabs import AsyncElevenLabs, VoiceSettings
from datetime import datetime

from core.config import settings
from core.dbutils import SessionLocal
from models.models import Job
from models.enums import JobStatus, JobErrorCode
from models.exceptions import JobProcessingException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

deepgram = DeepgramClient(api_key=settings.DEEPGRAM_API_KEY)
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
elevenlabs = AsyncElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

async def download_youtube_video(url, output_dir):
    try:
        ydl_opts = {
            'format': 'best[height<=720]/best',
            'outtmpl': f'{output_dir}/video.%(ext)s',
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            ext = info.get('ext', 'mp4')
            video_path = f"{output_dir}/video.{ext}"
            audio_path = f"{output_dir}/audio.wav"
            video_clip = mp.VideoFileClip(video_path)
            video_clip.audio.write_audiofile(audio_path)
            video_clip.close()
            return video_path, audio_path
    except Exception as e:
        logger.exception(f"Error downloading YouTube video", extra={"error_code": JobErrorCode.VIDEO_DOWNLOAD_FAILED})
        raise JobProcessingException(JobErrorCode.VIDEO_DOWNLOAD_FAILED)

async def transcribe_audio(audio_path):
    try:
        with open(audio_path, "rb") as audio:
            return deepgram.listen.v1.media.transcribe_file(
                request=audio.read(),
                model="nova-2",
                detect_language=True,
                smart_format=True,
                punctuate=True,
                utterances=True,
            )
    except Exception:
        logger.exception(f"Error transcribing audio", extra={"error_code": JobErrorCode.AUDIO_TRANSCRIPTION_FAILED})
        raise JobProcessingException(JobErrorCode.AUDIO_TRANSCRIPTION_FAILED)

def extract_audio_segments(transcribed_response):
    print(transcribed_response)
    segments = []
    try:
        if hasattr(transcribed_response, 'results') and transcribed_response.results:
            if hasattr(transcribed_response.results, 'utterances') and transcribed_response.results.utterances:
                for utterance in transcribed_response.results.utterances:
                    segments.append({
                        "start": utterance.start,
                        "end": utterance.end,
                        "transcript": utterance.transcript,
                        "confidence": utterance.confidence
                    })
                return segments
            
        logger.exception("No speech segments found in transcription response", extra={"error_code": JobErrorCode.AUDIO_SEGMENTS_NOT_FOUND})
        raise JobProcessingException(JobErrorCode.AUDIO_SEGMENTS_NOT_FOUND)
    except Exception as e:
        logger.exception(f"Error extracting audio segments", extra={"error_code": JobErrorCode.AUDIO_SEGEMENTS_EXTRACTION_FAILED})
        raise JobProcessingException(JobErrorCode.AUDIO_SEGEMENTS_EXTRACTION_FAILED)

def extract_source_language(transcribed_response):
    try:
        if transcribed_response.results and transcribed_response.results.channels:
            return transcribed_response.results.channels[0].language_code
        
        logger.warning(f"No source language found in transcription response, defaulting to {settings.DEFAULT_SOURCE_LANGUAGE}")
        return settings.DEFAULT_SOURCE_LANGUAGE
    except Exception as e:
        logger.exception(f"Error extracting source language. defaulting to {settings.DEFAULT_SOURCE_LANGUAGE}")
        return settings.DEFAULT_SOURCE_LANGUAGE

async def translate_segments(segments, source_lang="en", target_lang="es"):
    translated_segments = []
    for seg in segments:
        prompt = f"Translate the following text from {source_lang} to {target_lang}, keeping it natural and concise: '{seg['transcript']}'"
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        translated_text = response.choices[0].message.content.strip()
        translated_segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "transcript": translated_text,
            "duration": seg["end"] - seg["start"]
        })
    return translated_segments

async def synthesize_audio_segments(segments, voice_id="pNInz6obpgDQGcFmaJgB", target_lang="es"):
    audio_segments = []
    temp_dir = os.path.join(settings.TEMP_DIR, f"synthesis_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}")
    os.makedirs(temp_dir, exist_ok=True)
    
    for i, seg in enumerate(segments):
        audio = await elevenlabs.generate(
            text=seg["transcript"],
            voice=voice_id,
            model="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True,
            )
        )
        seg_path = f"{temp_dir}/seg_{i}.mp3"
        with open(seg_path, "wb") as f:
            f.write(audio)
        seg_clip = AudioFileClip(seg_path)
        target_duration = seg["duration"]
        if seg_clip.duration > target_duration * 1.1:
            seg_clip = seg_clip.speedx(target_duration / seg_clip.duration)
        elif seg_clip.duration < target_duration * 0.9:
            seg_clip = seg_clip.speedx(target_duration / seg_clip.duration)
        audio_segments.append(seg_clip)
        seg_clip.close()
    return audio_segments, temp_dir

def combine_audio_segments(audio_segments, total_duration):
    dubbed_audio = mp.concatenate_audioclips(audio_segments)
    if dubbed_audio.duration < total_duration:
        silence = mp.AudioClip(lambda t: [0]*dubbed_audio.nchannels, duration=total_duration - dubbed_audio.duration)
        dubbed_audio = mp.CompositeAudioClip([dubbed_audio, silence.set_start(dubbed_audio.duration)])
    elif dubbed_audio.duration > total_duration:
        dubbed_audio = dubbed_audio.subclip(0, total_duration)
    return dubbed_audio

def create_dubbed_video(original_video_path, dubbed_audio_path, output_path):
    video_clip = mp.VideoFileClip(original_video_path)
    audio_clip = mp.AudioFileClip(dubbed_audio_path)
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    video_clip.close()
    audio_clip.close()
    final_clip.close()

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
        
        # # Create output directory in temp storage
        # output_dir = os.path.join(settings.TEMP_DIR, f"job_{job_id}")
        # os.makedirs(output_dir, exist_ok=True)
        
        # # Step 1: Download video
        # logger.info("Step 1/6: Downloading video...")
        # video_path, audio_path = await download_youtube_video(job.video_url, output_dir)
        
        # Step 2: Transcribe audio        
        logger.info("Step 2/6: Transcribing audio...", extra={"audio_path": audio_path})
        transcribed_response = await transcribe_audio(audio_path)
        segments = extract_audio_segments(transcribed_response)
        source_language = extract_source_language(transcribed_response)
        logger.info(f"Extracted segments", extra={"segments": segments})
        logger.info(f"Detected Source language", extra={"source_language": source_language})
        
        # Step 3: Translate segments
        logger.info("Step 3/6: Translating segments...", extra={"source_language": source_language, "target_language": job.target_language})
        translated_segments = await translate_segments(segments, source_language, job.target_language)
        print(translated_segments)
        logger.info(f"Translated segments", extra={"translated_segments": translated_segments})
        
        # Step 4: Synthesize dubbed audio
        logger.info("Step 4/6: Synthesizing dubbed audio...")
        audio_segments, temp_dir = await synthesize_audio_segments(translated_segments, target_lang=job.target_language)
        
        # Get original audio duration
        original_audio = AudioFileClip(audio_path)
        total_duration = original_audio.duration
        original_audio.close()
        
        # Step 5: Combine audio segments
        logger.info("Step 5/6: Combining audio segments...")
        dubbed_audio = combine_audio_segments(audio_segments, total_duration)
        
        dubbed_audio_path = f"{output_dir}/dubbed_audio.wav"
        dubbed_audio.write_audiofile(dubbed_audio_path, verbose=False, logger=None)
        dubbed_audio.close()
        
        # Clean up audio segments
        for seg in audio_segments:
            seg.close()
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        # Step 6: Create final dubbed video
        output_video = f"{output_dir}/dubbed_video_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
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
        logger.error(f"Error processing job {job_id}: {str(e)}", exc_info=True)
        
        # Update job status to failed
        if job:
            try:
                job.status = JobStatus.FAILED.value
                job.error_message = f"Processing error: {str(e)}"
                job.updated_at = datetime.now()
                db.commit()
            except Exception as db_error:
                logger.error(f"Error updating job status: {str(db_error)}")
        
        return None
        
    finally:
        # Clean up temporary files and close database connection
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary files for job {job_id}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory: {e}")
        
        db.close()


def process_video_dubbing(job_id: int):
    return asyncio.run(process_video_dubbing_sync(job_id))
