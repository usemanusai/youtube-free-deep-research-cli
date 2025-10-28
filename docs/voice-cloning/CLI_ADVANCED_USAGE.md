# Advanced Voice Cloning CLI Usage Guide

Complete reference for using advanced voice parameters with the CLI.

## Command Structure

```bash
youtube-chat voice-clone generate [OPTIONS]
```

## Required Options

- `--voice-id, -v`: Voice ID to use (integer)
- `--text, -t`: Text to synthesize (string)
- `--output, -o`: Output audio file path (string)

## Basic Voice Parameters

### Speed Control
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello world" \
  --output output.wav \
  --speed 1.2
```

**Range**: 0.5 - 2.0 (default: 1.0)

### Pitch Adjustment
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello world" \
  --output output.wav \
  --pitch 3
```

**Range**: -12 to +12 semitones (default: 0)

### Emotion Selection
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "I'm so happy!" \
  --output output.wav \
  --emotion happy
```

**Options**: neutral, happy, sad, angry, joyful, excited, surprised, curious, confident, empathetic

### Exaggeration Control
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "This is amazing!" \
  --output output.wav \
  --exaggeration 0.8
```

**Range**: 0.25 - 2.0 (default: 0.5)

## Advanced Parameters

### CFG Weight (Rhythm Control)
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello world" \
  --output output.wav \
  --cfg-weight 0.7
```

**Range**: 0.0 - 1.0 (default: 0.5)

### Temperature (Variation Control)
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello world" \
  --output output.wav \
  --temperature 1.1
```

**Range**: 0.0 - 2.0 (default: 0.9)

### Top P (Diversity Control)
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello world" \
  --output output.wav \
  --top-p 0.9
```

**Range**: 0.0 - 1.0 (default: 0.95)

### Min P (Probability Threshold)
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello world" \
  --output output.wav \
  --min-p 0.15
```

**Range**: 0.0 - 1.0 (default: 0.1)

## Emphasis and Timing

### Emphasize Words
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "This is very important" \
  --output output.wav \
  --emphasis "important" \
  --emphasis "very"
```

Multiple `--emphasis` flags for multiple words.

### Pause Before Speech
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello world" \
  --output output.wav \
  --pause-before 500
```

**Range**: 0 - 5000 milliseconds (default: 0)

### Pause After Speech
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello world" \
  --output output.wav \
  --pause-after 300
```

**Range**: 0 - 5000 milliseconds (default: 0)

### Breath Frequency
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "This is a long passage with many words" \
  --output output.wav \
  --breath-frequency 5
```

**Range**: 0 - 20 words (default: 0)

## Reproducibility

### Use Seed for Consistent Results
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello world" \
  --output output.wav \
  --seed 42
```

**Range**: 0 to 2^32-1 (optional)

## Quality Presets

### Fast Quality
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello world" \
  --output output.wav \
  --quality fast
```

### Balanced Quality (Default)
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello world" \
  --output output.wav \
  --quality balanced
```

### High Quality
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello world" \
  --output output.wav \
  --quality high
```

## Complete Examples

### Professional Presentation
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Welcome to our quarterly earnings report" \
  --output presentation.wav \
  --speed 1.0 \
  --pitch 1 \
  --exaggeration 0.5 \
  --emotion confident \
  --emphasis "earnings" "report"
```

### Friendly Podcast
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hey everyone, welcome back to the show!" \
  --output podcast.wav \
  --speed 1.0 \
  --pitch 0 \
  --exaggeration 0.6 \
  --emotion joyful \
  --breath-frequency 8 \
  --pause-before 300
```

### Dramatic Narration
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "In a galaxy far, far away..." \
  --output narration.wav \
  --speed 0.9 \
  --pitch 2 \
  --exaggeration 1.2 \
  --emotion joyful \
  --pause-before 500 \
  --pause-after 300
```

### Calm Meditation
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Take a deep breath and relax" \
  --output meditation.wav \
  --speed 0.8 \
  --pitch -2 \
  --exaggeration 0.4 \
  --emotion empathetic \
  --pause-after 500 \
  --breath-frequency 3
```

### Energetic Announcement
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Get ready for the biggest sale of the year!" \
  --output announcement.wav \
  --speed 1.3 \
  --pitch 3 \
  --exaggeration 0.8 \
  --emotion excited \
  --emphasis "biggest" "sale" \
  --breath-frequency 5
```

### Sad Storytelling
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "It was a dark and stormy night" \
  --output story.wav \
  --speed 0.85 \
  --pitch -1 \
  --exaggeration 0.7 \
  --emotion sad \
  --pause-before 300 \
  --pause-after 200
```

## Viewing Available Presets

```bash
youtube-chat voice-clone presets
```

Shows all available parameter presets with descriptions and recommended use cases.

## Managing Voices

### List All Voices
```bash
youtube-chat voice-clone list
```

### Create New Voice
```bash
youtube-chat voice-clone create \
  --name "My Voice" \
  --reference-audio reference.wav
```

### Delete Voice
```bash
youtube-chat voice-clone delete --voice-id 1
```

## Tips and Tricks

### Batch Processing
Generate multiple variations:
```bash
for emotion in happy sad angry; do
  youtube-chat voice-clone generate \
    --voice-id 1 \
    --text "Hello world" \
    --output "output_${emotion}.wav" \
    --emotion "$emotion"
done
```

### A/B Testing
Compare different parameter sets:
```bash
# Version A
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Test text" \
  --output test_a.wav \
  --speed 1.0 --pitch 0

# Version B
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Test text" \
  --output test_b.wav \
  --speed 1.2 --pitch 2
```

### Reproducible Results
Use seed for consistent output:
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello world" \
  --output output.wav \
  --seed 12345
```

## Troubleshooting

### Command Not Found
Ensure youtube-chat-cli is installed:
```bash
pip install youtube-chat-cli
```

### Invalid Parameter Values
Check parameter ranges in help:
```bash
youtube-chat voice-clone generate --help
```

### Voice Not Found
List available voices:
```bash
youtube-chat voice-clone list
```

### Generation Failed
Check error message and try with simpler parameters:
```bash
youtube-chat voice-clone generate \
  --voice-id 1 \
  --text "Hello" \
  --output output.wav
```

## Performance Notes

- Generation time: 2-5 seconds for 100 words
- Longer text takes proportionally longer
- Complex parameters may increase generation time
- Use `--quality fast` for quick iterations
- Use `--quality high` for final output

