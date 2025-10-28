# Voice Cloning Dashboard Setup Guide

Complete guide for setting up and running the Next.js dashboard for voice cloning.

## Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running (see Backend Setup below)
- Python 3.13+ with voice cloning service

## Backend Setup

### 1. Start the FastAPI Backend

```bash
cd youtube_chat_cli_main
python api_server.py
```

The API will be available at `http://localhost:8000`

Verify with:
```bash
curl http://localhost:8000/api/v1/health
```

### 2. Verify Voice Cloning Endpoints

```bash
curl http://localhost:8000/api/v1/voice-clone/voices
```

Should return:
```json
{
  "voices": [],
  "total": 0
}
```

## Dashboard Setup

### 1. Install Dependencies

```bash
cd dashboard
npm install
```

### 2. Configure Environment

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Features

### 1. Upload Voice Tab

- Drag-and-drop audio file upload
- Automatic audio validation
- Support for WAV, MP3, FLAC formats
- Real-time file size display

**Workflow:**
1. Enter voice name
2. Upload reference audio (3-300 seconds)
3. Click "Validate Audio" to check quality
4. Click "Create Voice" to save

### 2. Record Voice Tab

- Browser-based audio recording
- Real-time duration display
- Audio preview before saving
- Automatic WAV encoding

**Workflow:**
1. Click "Start Recording"
2. Speak into microphone
3. Click "Stop Recording"
4. Preview audio
5. Enter voice name
6. Click "Save Voice"

### 3. My Voices Tab

- List all created voices
- View creation date and usage count
- Delete voices with confirmation
- Last used timestamp

### 4. Generate Speech Tab

- Select cloned voice
- Enter text to synthesize
- Adjust speed (0.5x - 2.0x)
- Choose quality preset (fast/balanced/high)
- Preview generated audio

## API Integration

The dashboard uses these endpoints:

### Upload Reference Audio
```
POST /api/v1/voice-clone/upload-reference
Content-Type: multipart/form-data

Parameters:
- name: string (voice name)
- file: File (audio file)
- consent_ip: string (optional)
```

### List Voices
```
GET /api/v1/voice-clone/voices

Response:
{
  "voices": [
    {
      "id": 1,
      "name": "My Voice",
      "created_at": "2025-10-27T...",
      "usage_count": 5,
      "last_used": "2025-10-27T..."
    }
  ],
  "total": 1
}
```

### Generate Speech
```
POST /api/v1/voice-clone/generate

Body:
{
  "voice_id": 1,
  "text": "Hello world",
  "speed": 1.0,
  "quality": "balanced"
}

Response:
{
  "success": true,
  "output_path": "/path/to/audio.wav",
  "duration": 2.5
}
```

### Delete Voice
```
DELETE /api/v1/voice-clone/voices/{voice_id}

Response:
{
  "success": true
}
```

### Validate Audio
```
POST /api/v1/voice-clone/validate-audio
Content-Type: multipart/form-data

Parameters:
- file: File (audio file)

Response:
{
  "valid": true,
  "duration": 15.5,
  "sample_rate": 24000,
  "snr_db": 25.3,
  "issues": []
}
```

## Troubleshooting

### API Connection Error

**Problem:** "Failed to connect to API"

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/api/v1/health`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Ensure CORS is enabled in backend

### Audio Upload Fails

**Problem:** "Invalid audio" error

**Solution:**
1. Check audio format (WAV, MP3, FLAC)
2. Verify duration (3-300 seconds)
3. Check sample rate (≥22kHz)
4. Validate SNR (>20dB recommended)

### Recording Not Working

**Problem:** Microphone access denied

**Solution:**
1. Check browser permissions
2. Ensure HTTPS in production
3. Allow microphone access when prompted

## Production Deployment

### Build for Production

```bash
npm run build
npm run start
```

### Docker Deployment

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY .next ./.next
COPY public ./public

EXPOSE 3000

CMD ["npm", "start"]
```

### Environment Variables

```env
NEXT_PUBLIC_API_URL=https://api.example.com
NODE_ENV=production
```

## Performance Optimization

- React Query caching (5-10 minute stale time)
- Lazy loading of components
- Audio compression before upload
- Optimized bundle size (~150KB gzipped)

## Security Considerations

- HTTPS required in production
- CORS properly configured
- Input validation on client and server
- Consent tracking for voice data
- Audio file size limits (100MB max)

## Support

For issues or questions:
1. Check logs: `npm run dev` output
2. Verify API connectivity
3. Check browser console for errors
4. Review backend logs

## Next Steps

1. ✅ Dashboard setup complete
2. Create your first voice
3. Generate speech samples
4. Integrate with your application
5. Deploy to production

