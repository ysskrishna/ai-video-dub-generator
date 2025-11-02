# AI Video Dub Generator - Backend

AI-powered backend service for automatic video dubbing from one language to another using speech recognition, translation, and text-to-speech technologies. Powered by Deepgram for speech recognition, OpenAI for translation, and ElevenLabs for lifelike voiceovers.

## Features

- **Automatic Video Dubbing**: Convert YouTube videos from one language to another
- **Real-time Job Processing**: Background task processing with status tracking
- **Multiple Language Support**: Support for 30+ languages
- **High-Quality Audio**: Advanced TTS engines for natural-sounding voice synthesis
- **RESTful API**: FastAPI-based API with automatic documentation
- **Job Management**: Track and manage dubbing jobs with status updates

## Technology Stack

- **Framework**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Video Processing**: MoviePy for video manipulation
- **AI Services**: 
  - [Deepgram](https://deepgram.com) for speech-to-text transcription
  - [OpenAI](https://openai.com) for translation
  - [ElevenLabs](https://elevenlabs.io) for text-to-speech synthesis
- **Video Download**: yt-dlp for YouTube video processing
- **Package Management**: UV

## Prerequisites

- Python 3.11 or higher
- [UV](https://github.com/astral-sh/uv) package manager
- API Keys:
  - Deepgram API Key
  - OpenAI API Key
  - ElevenLabs API Key

## Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Environment Configuration

Create a `.env` file in the `backend` directory with the following variables:

```env
DATABASE_URL=sqlite:///./audio_dub_generator.db
DEEPGRAM_API_KEY=your_deepgram_api_key
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
DEFAULT_SOURCE_LANGUAGE=en
```

### 3. Run the Server

```bash
uv run python main.py
```

The API server will start on `http://localhost:8085`

## Project Structure

```
backend/
├── core/              # Core configuration and utilities
│   ├── config.py      # Application settings
│   ├── dbutils.py     # Database utilities
│   └── logging.py     # Logging configuration
├── models/            # Database models and schemas
│   ├── models.py      # SQLAlchemy models
│   ├── schemas.py     # Pydantic schemas
│   └── enums.py       # Enum definitions
├── routers/           # API route handlers
│   └── video.py       # Video dubbing routes
├── services/          # Business logic
│   ├── video_processor.py      # Main video processing service
│   └── video_processor_utils.py # Video processing utilities
├── storage/           # Temporary file storage
│   └── temp/          # Per-job temporary files
├── main.py            # FastAPI application entry point
└── pyproject.toml     # Project dependencies
```

## API Documentation

Once the server is running, interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8085/docs`
- **ReDoc**: `http://localhost:8085/redoc`


## License

MIT License - see the [LICENSE](../LICENSE) file for details.

## Author

**Y. Siva Sai Krishna** ([@ysskrishna](https://github.com/ysskrishna))
