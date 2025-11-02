# AI Video Dub Generator - Frontend

An innovative AI-driven platform that seamlessly dubs videos across languages. Powered by Deepgram for speech recognition, OpenAI for translation, and ElevenLabs for lifelike voiceovers, this frontend application helps content creators, educators, and businesses reach global audiences effortlessly.

## 🚀 Features

- **Video URL Processing**: Submit YouTube video URLs for dubbing
- **Language Selection**: Choose from multiple target languages
- **Real-time Job Monitoring**: Track video dubbing progress with live status updates
- **Job History**: View all past and current dubbing jobs
- **Download Videos**: Download completed dubbed videos
- **Modern UI**: Clean, responsive interface built with React and TypeScript
- **Dark Mode Support**: Built-in theme switching with next-themes

## 🛠️ Technology Stack

- **Framework**: [React](https://react.dev/) 18.3+
- **Language**: [TypeScript](https://www.typescriptlang.org/) 5.8+
- **Build Tool**: [Vite](https://vitejs.dev/) 5.4+
- **UI Components**: [shadcn/ui](https://ui.shadcn.com/) (Radix UI primitives)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) 3.4+

## 📋 Prerequisites

- **Node.js**: v18 or higher
- **npm**: v9 or higher (or yarn/pnpm)

## 🏃 Quick Start

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server
npm run dev
```

The application will be available at `http://localhost:5173` (or the next available port).

Make sure the backend API is running at `http://localhost:8085` (or update the API_BASE_URL in `src/lib/api.ts`).

### Build

```bash
# Build for production
npm run build

# Build for development
npm run build:dev
```

The production build will be created in the `dist` directory.

### Preview Production Build

```bash
# Preview the production build locally
npm run preview
```

### Linting

```bash
# Run ESLint
npm run lint
```

## 📁 Project Structure

```
client/
├── src/
│   ├── components/      # React components
│   │   ├── ui/          # shadcn/ui components
│   │   ├── Header.tsx   # Header component
│   │   ├── Footer.tsx   # Footer component
│   │   ├── JobCard.tsx  # Job card component for displaying job status
│   │   └── Layout.tsx   # Main layout wrapper
│   ├── pages/           # Page components
│   │   ├── Home.tsx     # Main page with job creation and history
│   │   └── NotFound.tsx # 404 page
│   ├── hooks/           # Custom React hooks
│   │   └── use-toast.ts # Toast notification hook
│   ├── lib/             # Utility functions
│   │   ├── api.ts       # API client with fetch-based calls
│   │   └── utils.ts     # Helper functions (cn utility)
│   ├── assets/          # Static assets (logos, images)
│   ├── App.tsx          # Root component with routing
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── public/              # Public assets
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── tsconfig.json        # TypeScript config
├── vite.config.ts       # Vite configuration
└── tailwind.config.ts   # Tailwind CSS config
```

## 🔌 API Integration

The frontend communicates with the backend API at `http://localhost:8085/api/v1/video`. The API client is implemented in `src/lib/api.ts` using native `fetch` API.

### API Endpoints Used

- `GET /api/v1/video/languages` - Get available target languages
- `POST /api/v1/video/create` - Create a new dubbing job (requires video_url and target_language)
- `GET /api/v1/video/status/{job_id}` - Get status of a specific job
- `GET /api/v1/video/jobs` - Get all jobs
- `GET /api/v1/video/download/{job_id}` - Download completed dubbed video

### How It Works

1. User enters a YouTube video URL and selects a target language
2. Frontend sends a POST request to create a dubbing job
3. Frontend polls the job status every 3 seconds until completion
4. Once completed, user can download the dubbed video


## 📝 Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production (optimized)
- `npm run build:dev` - Build for development (faster, less optimized)
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint to check code quality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 👨‍💻 Author

**Y. Siva Sai Krishna** ([@ysskrishna](https://github.com/ysskrishna))

## 🔗 Links

- [Repository](https://github.com/ysskrishna/ai-video-dub-generator)
- [Issues](https://github.com/ysskrishna/ai-video-dub-generator/issues)
- [Main README](../README.md)
