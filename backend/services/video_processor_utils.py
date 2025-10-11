import os
import logging
import yt_dlp
import moviepy as mp
from moviepy import AudioFileClip
from deepgram import DeepgramClient
from openai import AsyncOpenAI
from elevenlabs import ElevenLabs, VoiceSettings
from datetime import datetime

from core.config import settings
from models.enums import JobErrorCode
from models.exceptions import JobProcessingException

logger = logging.getLogger(__name__)

deepgram = DeepgramClient(api_key=settings.DEEPGRAM_API_KEY)
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
elevenlabs = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

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
    except Exception:
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
    except Exception:
        logger.exception(f"Error extracting audio segments", extra={"error_code": JobErrorCode.AUDIO_SEGEMENTS_EXTRACTION_FAILED})
        raise JobProcessingException(JobErrorCode.AUDIO_SEGEMENTS_EXTRACTION_FAILED)

def extract_source_language(transcribed_response):
    try:
        if transcribed_response.results and transcribed_response.results.channels:
            return transcribed_response.results.channels[0].language_code
        
        logger.warning(f"No source language found in transcription response, defaulting to {settings.DEFAULT_SOURCE_LANGUAGE}")
        return settings.DEFAULT_SOURCE_LANGUAGE
    except Exception:
        logger.exception(f"Error extracting source language. defaulting to {settings.DEFAULT_SOURCE_LANGUAGE}")
        return settings.DEFAULT_SOURCE_LANGUAGE

async def translate_segments(segments, source_lang, target_lang):
    try:
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
    except Exception:
        logger.exception(f"Error translating segments", extra={"error_code": JobErrorCode.TRANSLATION_FAILED})
        raise JobProcessingException(JobErrorCode.TRANSLATION_FAILED)

def synthesize_audio_segments(temp_dir, segments, voice_id="pNInz6obpgDQGcFmaJgB"):
    try:
        audio_segments = []
        for i, seg in enumerate(segments):
            audio_generator = elevenlabs.text_to_speech.convert(
                voice_id=voice_id,
                text=seg["transcript"],
                model_id="eleven_multilingual_v2",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True,
                )
            )

            # Convert the generator to bytes
            audio_bytes = b"".join(chunk for chunk in audio_generator)
            seg_path = f"{temp_dir}/seg_{i}.mp3"
            with open(seg_path, "wb") as f:
                f.write(audio_bytes)

            seg_clip = AudioFileClip(seg_path)
            target_duration = seg["duration"]
            if seg_clip.duration > target_duration * 1.1:
                seg_clip = seg_clip.with_speed_scaled(target_duration / seg_clip.duration)
            # elif seg_clip.duration < target_duration * 0.9:
            #     seg_clip = seg_clip.with_speed_scaled(target_duration / seg_clip.duration)

            seg_clip = seg_clip.with_start(seg["start"])
            audio_segments.append(seg_clip)
        return audio_segments
    except Exception:
        logger.exception(f"Error synthesizing audio segments", extra={"error_code": JobErrorCode.SYNTHESIS_FAILED})
        raise JobProcessingException(JobErrorCode.SYNTHESIS_FAILED)

def combine_audio_segments(audio_segments, total_duration):
    try:
        # Create a silence track for the full duration (stereo)
        silence = mp.AudioClip(lambda t: [0]*2, duration=total_duration)
        audio_clips = [silence, *audio_segments]
        
        dubbed_audio = mp.CompositeAudioClip(audio_clips)
        if dubbed_audio.duration > total_duration:
            dubbed_audio = dubbed_audio.subclipped(0, total_duration)
        return dubbed_audio
    except Exception:
        logger.exception(f"Error combining audio segments", extra={"error_code": JobErrorCode.COMBINATION_FAILED})
        raise JobProcessingException(JobErrorCode.COMBINATION_FAILED)

def create_dubbed_video(original_video_path, dubbed_audio_path, output_path):
    try:
        video_clip = mp.VideoFileClip(original_video_path)
        audio_clip = mp.AudioFileClip(dubbed_audio_path)
        final_clip = video_clip.with_audio(audio_clip)
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        video_clip.close()
        audio_clip.close()
        final_clip.close()
    except Exception:
        logger.exception(f"Error creating dubbed video", extra={"error_code": JobErrorCode.VIDEO_CREATION_FAILED})
        raise JobProcessingException(JobErrorCode.VIDEO_CREATION_FAILED)

def extract_audio_duration(audio_path):
    try:
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        audio_clip.close()
        return duration
    except Exception:
        logger.exception(f"Error extracting audio duration", extra={"error_code": JobErrorCode.AUDIO_DURATION_EXTRACTION_FAILED})
        raise JobProcessingException(JobErrorCode.AUDIO_DURATION_EXTRACTION_FAILED)