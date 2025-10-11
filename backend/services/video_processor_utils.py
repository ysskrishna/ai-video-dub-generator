import os
import logging
import yt_dlp
import moviepy as mp
from moviepy import AudioFileClip
from deepgram import DeepgramClient
from openai import AsyncOpenAI
from elevenlabs import AsyncElevenLabs, VoiceSettings
from datetime import datetime

from core.config import settings
from models.enums import JobErrorCode
from models.exceptions import JobProcessingException

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

async def synthesize_audio_segments(segments, voice_id="pNInz6obpgDQGcFmaJgB", target_lang="es"):
    try:
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
    except Exception:
        logger.exception(f"Error synthesizing audio segments", extra={"error_code": JobErrorCode.SYNTHESIS_FAILED})
        raise JobProcessingException(JobErrorCode.SYNTHESIS_FAILED)

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
