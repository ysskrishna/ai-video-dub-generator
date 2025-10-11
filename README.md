# AI Video Dub Generator

An AI-powered application that automatically dubs videos from one language to another using advanced speech recognition, translation, and text-to-speech technologies.

![Demo](media/demo.png)

## Features

- **Automatic Video Dubbing**: Convert videos from one language to another
- **Real-time Processing**: Monitor job progress with live status updates
- **Multiple Language Support**: Support various target languages
- **High-Quality Audio**: Uses advanced TTS engines for natural-sounding voice synthesis
- **Web Interface**: Clean, modern UI for easy video upload and management

## Example Output

Check out the example dubbed video in the `media/examples/` directory:
- `youtubeid_JcfOdtBk55Y_en_to_hi_dub.mp4` - English to Hindi dubbing example

## Architecture

This project consists of two main components:

### Frontend (`/client`)
- **Technology Stack**: React, TypeScript, Vite
- **UI Framework**: shadcn/ui components with Tailwind CSS
- **State Management**: TanStack Query for server state
- **Routing**: React Router DOM

### Backend (`/backend`)
- **Framework**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Video Processing**: MoviePy for video manipulation
- **AI Services**: 
  - Deepgram for speech-to-text
  - OpenAI for translation
  - ElevenLabs for text-to-speech
- **Video Download**: yt-dlp for YouTube video processing

## Quick Start

### Prerequisites
- Node.js (v18 or higher)
- Python 3.11+
- UV package manager

### Backend Setup
```bash
cd backend
uv sync
uv run python main.py
```

### Frontend Setup
```bash
cd client
npm install
npm run dev
```

## API Endpoints

- `POST /api/video/upload` - Upload video for dubbing
- `GET /api/video/jobs` - List all dubbing jobs
- `GET /api/video/jobs/{job_id}` - Get specific job details
- `GET /api/video/jobs/{job_id}/download` - Download completed dubbed video


## 👨‍💻 Author

**Y. Siva Sai Krishna** ([@ysskrishna](https://github.com/ysskrishna))