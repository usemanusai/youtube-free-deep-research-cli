# Voice Cloning Dashboard

A modern Next.js dashboard for voice cloning with E2-F5-TTS. Create professional-quality speech with your own voice.

## Features

- 🎤 **Voice Upload** - Upload reference audio files (WAV, MP3, FLAC)
- 🎙️ **Voice Recording** - Record reference audio directly in the browser
- 🔊 **Speech Generation** - Generate speech with cloned voices
- 📊 **Voice Management** - List, preview, and delete cloned voices
- ⚡ **Real-time Validation** - Validate audio quality before uploading
- 🎨 **Modern UI** - Beautiful dark theme with Tailwind CSS

## Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Configuration

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main page with tabs
│   ├── providers.tsx       # React Query & Toast providers
│   └── globals.css         # Global styles
├── components/
│   ├── VoiceUpload.tsx     # Upload reference audio
│   ├── AudioRecorder.tsx   # Record reference audio
│   ├── VoiceList.tsx       # List and manage voices
│   └── SpeechGenerator.tsx # Generate speech
├── hooks/
│   └── useVoiceCloning.ts  # Custom React Query hooks
└── lib/
    └── api-client.ts       # API client
```

## API Integration

The dashboard communicates with the backend API at `/api/v1/voice-clone`:

- `POST /upload-reference` - Upload reference audio
- `GET /voices` - List all voices
- `POST /generate` - Generate speech
- `DELETE /voices/{id}` - Delete voice
- `POST /validate-audio` - Validate audio
- `GET /settings` - Get settings

## Building for Production

```bash
# Build
npm run build

# Start production server
npm run start
```

## Technologies

- **Next.js 15** - React framework
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Query** - Data fetching
- **Axios** - HTTP client
- **React Hot Toast** - Notifications

## License

MIT

