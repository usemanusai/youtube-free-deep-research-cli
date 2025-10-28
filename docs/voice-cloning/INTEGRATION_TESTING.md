# Voice Cloning Integration Testing Guide

Comprehensive testing guide for CLI commands and Dashboard UI integration.

## Test Environment Setup

### 1. Start Backend Services

```bash
cd youtube_chat_cli_main
python api_server.py
```

Verify: `curl http://localhost:8000/api/v1/health`

### 2. Start Dashboard

```bash
cd dashboard
npm run dev
```

Open: `http://localhost:3000`

### 3. Prepare Test Audio

Create a test audio file (10-30 seconds):
```bash
# Using ffmpeg
ffmpeg -f lavfi -i sine=f=440:d=15 -q:a 9 -acodec libmp3lame test_audio.mp3
```

## CLI Testing

### Test 1: Create Voice from File

```bash
youtube-chat voice-clone create \
  --reference test_audio.mp3 \
  --name "Test Voice CLI"
```

**Expected Output:**
```
✅ Voice created successfully!
   Voice ID: 1
   Name: Test Voice CLI
   Created: 2025-10-27T...
```

### Test 2: List Voices

```bash
youtube-chat voice-clone list
```

**Expected Output:**
```
Found 1 voice(s):

  ID: 1
  Name: Test Voice CLI
  Created: 2025-10-27
  Usage count: 0
```

### Test 3: Generate Speech

```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello from the CLI" \
  --output cli_output.wav \
  --quality balanced
```

**Expected Output:**
```
✅ Speech generated successfully!
   Output: cli_output.wav
```

### Test 4: Delete Voice

```bash
youtube-chat voice-clone delete --voice-id 1
```

**Expected Output:**
```
✅ Voice deleted successfully!
```

## Dashboard Testing

### Test 1: Upload Voice

1. Navigate to "Upload Voice" tab
2. Enter voice name: "Test Voice Dashboard"
3. Drag-and-drop test_audio.mp3
4. Click "Validate Audio"
5. Verify validation results
6. Click "Create Voice"
7. Verify success message

**Expected Results:**
- ✅ Audio validation shows duration, sample rate, SNR
- ✅ Voice created successfully
- ✅ Toast notification appears

### Test 2: Record Voice

1. Navigate to "Record Voice" tab
2. Click "Start Recording"
3. Speak for 10-15 seconds
4. Click "Stop Recording"
5. Preview audio
6. Enter voice name: "Test Voice Recorded"
7. Click "Save Voice"

**Expected Results:**
- ✅ Recording duration displays
- ✅ Audio preview works
- ✅ Voice saved successfully

### Test 3: List Voices

1. Navigate to "My Voices" tab
2. Verify both voices appear
3. Check creation dates and usage counts
4. Click delete on one voice
5. Confirm deletion

**Expected Results:**
- ✅ Both voices listed
- ✅ Metadata displays correctly
- ✅ Voice deleted after confirmation

### Test 4: Generate Speech

1. Navigate to "Generate Speech" tab
2. Select a voice from dropdown
3. Enter text: "This is a test of the voice cloning system"
4. Adjust speed to 1.2x
5. Select "Balanced" quality
6. Click "Generate Speech"
7. Wait for generation
8. Preview generated audio

**Expected Results:**
- ✅ Voice dropdown populated
- ✅ Generation completes in 2-3 seconds
- ✅ Audio preview works
- ✅ Output path displayed

## Integration Tests

### Test 1: CLI to Dashboard Sync

1. Create voice via CLI
2. Refresh dashboard "My Voices" tab
3. Verify voice appears

**Expected:** Voice created via CLI visible in dashboard

### Test 2: Dashboard to CLI Sync

1. Create voice via dashboard
2. Run `youtube-chat voice-clone list` in CLI
3. Verify voice appears

**Expected:** Voice created via dashboard visible in CLI

### Test 3: Cross-Platform Generation

1. Create voice via CLI
2. Generate speech via dashboard using that voice
3. Create voice via dashboard
4. Generate speech via CLI using that voice

**Expected:** Both workflows work seamlessly

### Test 4: Error Handling

**Invalid Audio:**
- Upload audio < 3 seconds
- Expected: Error message "Audio too short"

**Invalid Voice ID:**
- Generate speech with non-existent voice ID
- Expected: Error message "Voice not found"

**Missing Parameters:**
- Try to generate without text
- Expected: Error message "Text required"

## Performance Tests

### Test 1: Voice Generation Speed

```bash
# Measure generation time
time youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Performance test" \
  --quality fast
```

**Expected:** < 2 seconds for "fast" quality

### Test 2: Dashboard Responsiveness

1. Create 10 voices
2. Navigate between tabs
3. Generate multiple speeches
4. Monitor browser performance

**Expected:** Smooth UI, no lag

### Test 3: API Response Times

```bash
# Test list endpoint
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/voice-clone/voices
```

**Expected:** < 200ms response time

## Regression Tests

### Test 1: Existing TTS Engines

Verify other TTS engines still work:

```bash
youtube-chat podcast generate --url "https://youtube.com/watch?v=..." --engine melotts
```

**Expected:** MeloTTS generation works normally

### Test 2: Database Integrity

```bash
# Check database
python -c "from youtube_chat_cli_main.core.database import get_database; db = get_database(); print(db.execute('SELECT COUNT(*) FROM cloned_voices').fetchone())"
```

**Expected:** Correct voice count

### Test 3: API Health

```bash
curl http://localhost:8000/api/v1/health
```

**Expected:** 200 OK response

## Test Results Template

```
Date: 2025-10-27
Tester: [Name]
Environment: Windows/macOS/Linux

CLI Tests:
- [ ] Create voice
- [ ] List voices
- [ ] Generate speech
- [ ] Delete voice

Dashboard Tests:
- [ ] Upload voice
- [ ] Record voice
- [ ] List voices
- [ ] Generate speech

Integration Tests:
- [ ] CLI to Dashboard sync
- [ ] Dashboard to CLI sync
- [ ] Cross-platform generation
- [ ] Error handling

Performance Tests:
- [ ] Generation speed
- [ ] Dashboard responsiveness
- [ ] API response times

Regression Tests:
- [ ] Existing TTS engines
- [ ] Database integrity
- [ ] API health

Issues Found:
[List any issues]

Notes:
[Additional observations]
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Voice Cloning Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Python dependencies
        run: pip install -r requirements.txt
      
      - name: Install Node dependencies
        run: cd dashboard && npm install
      
      - name: Run tests
        run: pytest tests/test_voice_cloning.py -v
```

## Success Criteria

✅ All CLI commands work correctly
✅ Dashboard UI is responsive
✅ API endpoints return correct responses
✅ No regressions in existing features
✅ Error handling works as expected
✅ Performance meets targets
✅ Cross-platform compatibility verified

