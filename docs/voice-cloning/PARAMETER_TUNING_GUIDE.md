# Voice Parameter Tuning Guide

Complete guide for tuning advanced voice parameters to achieve desired voice characteristics and emotional expression.

## Parameter Overview

### Speed (0.5 - 2.0, default: 1.0)
Controls the speech rate multiplier.

**Use Cases:**
- **0.5-0.8**: Slow, deliberate speech (audiobooks, meditation, dramatic narration)
- **0.9-1.1**: Natural, conversational speech (podcasts, interviews)
- **1.2-1.5**: Fast, energetic speech (announcements, excitement)
- **1.6-2.0**: Very fast speech (rapid-fire delivery, comedy)

**Tips:**
- Combine with lower pitch for calm, authoritative tone
- Combine with higher pitch for energetic, youthful tone
- Extreme speeds (>1.8) may reduce clarity

### Pitch (-12 to +12 semitones, default: 0)
Adjusts the fundamental frequency of the voice.

**Use Cases:**
- **-12 to -6**: Deep, masculine, authoritative voice
- **-3 to 0**: Natural, neutral voice
- **+3 to +6**: Higher, feminine, youthful voice
- **+9 to +12**: Very high, childlike voice

**Tips:**
- Combine with exaggeration for more dramatic effect
- Extreme pitch shifts may sound unnatural
- Works best with emotion parameter

### Exaggeration (0.25 - 2.0, default: 0.5)
Controls emotional intensity and expression.

**Use Cases:**
- **0.25-0.4**: Subtle, professional delivery
- **0.5-0.7**: Balanced emotional expression
- **0.8-1.2**: Strong emotional delivery
- **1.3-2.0**: Highly exaggerated, theatrical delivery

**Tips:**
- Increase for emotional content (stories, advertisements)
- Decrease for technical/professional content
- Combine with emotion parameter for best results

### CFG Weight (0.0 - 1.0, default: 0.5)
Classifier-free guidance weight for speech rhythm control.

**Use Cases:**
- **0.0-0.3**: More natural, less constrained rhythm
- **0.4-0.6**: Balanced rhythm control
- **0.7-1.0**: Strict rhythm adherence, more robotic

**Tips:**
- Lower values for conversational speech
- Higher values for consistent, predictable rhythm
- Affects prosody consistency

### Temperature (0.0 - 2.0, default: 0.9)
Controls randomness and variation in speech generation.

**Use Cases:**
- **0.0-0.3**: Deterministic, repetitive speech
- **0.4-0.9**: Natural variation with consistency
- **1.0-1.5**: High variation, more expressive
- **1.6-2.0**: Maximum variation, unpredictable

**Tips:**
- Lower for reproducible results
- Higher for more natural, varied speech
- Combine with seed for reproducible variation

### Top P (0.0 - 1.0, default: 0.95)
Nucleus sampling parameter for diversity control.

**Use Cases:**
- **0.0-0.5**: Conservative, focused generation
- **0.6-0.9**: Balanced diversity
- **0.91-1.0**: Maximum diversity

**Tips:**
- Lower for technical/factual content
- Higher for creative/expressive content
- Works with temperature for fine-grained control

### Min P (0.0 - 1.0, default: 0.1)
Minimum probability threshold for token selection.

**Use Cases:**
- **0.0-0.05**: Allow rare tokens
- **0.1-0.2**: Balanced token selection
- **0.3-0.5**: Conservative token selection

**Tips:**
- Lower for creative content
- Higher for technical content
- Prevents very unlikely tokens

### Emotion (neutral, happy, sad, angry, joyful, excited, surprised, curious, confident, empathetic)
Emotional tone of the voice.

**Use Cases:**
- **neutral**: Default, professional tone
- **happy**: Upbeat, positive delivery
- **sad**: Melancholic, sorrowful tone
- **angry**: Intense, forceful delivery
- **joyful**: Celebratory, enthusiastic tone
- **excited**: High energy, enthusiastic
- **surprised**: Shocked, astonished tone
- **curious**: Inquisitive, questioning tone
- **confident**: Assured, authoritative tone
- **empathetic**: Compassionate, understanding tone

**Tips:**
- Combine with pitch and exaggeration for best effect
- Use for emotional content (stories, advertisements)
- Combine with emphasis for targeted emotional delivery

### Emphasis (list of words)
Words to emphasize in the speech.

**Use Cases:**
- Highlight important words
- Create natural stress patterns
- Improve clarity of key terms

**Example:**
```bash
--emphasis "important" "critical" "urgent"
```

**Tips:**
- Use sparingly (2-5 words per sentence)
- Emphasize key terms and important concepts
- Combine with emotion for dramatic effect

### Pause Before / After (0 - 5000ms, default: 0)
Silence before and after the speech.

**Use Cases:**
- **pause_before**: Add intro silence for dramatic effect
- **pause_after**: Add outro silence for emphasis

**Typical Values:**
- **0-200ms**: Minimal pause
- **300-800ms**: Natural pause
- **1000-2000ms**: Dramatic pause
- **2000-5000ms**: Extended silence

**Tips:**
- Use for podcast/audiobook production
- Combine with breath_frequency for natural pacing
- Helps with audio editing and transitions

### Breath Frequency (0 - 20 words, default: 0)
Insert breath sound every N words.

**Use Cases:**
- **0**: No breath sounds
- **5-10**: Natural breathing pattern
- **15-20**: Frequent breathing (for dramatic effect)

**Tips:**
- Use for long passages (>50 words)
- Improves naturalness of long speeches
- Combine with pauses for realistic delivery

### Seed (0 to 2^32-1, optional)
Random seed for reproducible generation.

**Use Cases:**
- Reproduce exact same audio
- Consistent results across runs
- Testing and validation

**Tips:**
- Use same seed with same parameters for identical output
- Useful for A/B testing
- Leave empty for random variation

## Preset Combinations

### Professional Presentation
```bash
--speed 1.0 --pitch 1 --exaggeration 0.5 --emotion confident
```

### Friendly Podcast
```bash
--speed 1.0 --pitch 0 --exaggeration 0.6 --emotion joyful --breath-frequency 8
```

### Dramatic Narration
```bash
--speed 0.9 --pitch 2 --exaggeration 1.2 --emotion joyful --pause-before 500
```

### Calm Meditation
```bash
--speed 0.8 --pitch -2 --exaggeration 0.4 --emotion empathetic --pause-after 300
```

### Energetic Announcement
```bash
--speed 1.3 --pitch 3 --exaggeration 0.8 --emotion excited --breath-frequency 5
```

### Sad Storytelling
```bash
--speed 0.85 --pitch -1 --exaggeration 0.7 --emotion sad --pause-before 300
```

## Tuning Workflow

1. **Start with preset**: Choose closest preset to your use case
2. **Adjust speed**: Fine-tune speech rate for clarity
3. **Adjust pitch**: Set appropriate voice register
4. **Adjust exaggeration**: Control emotional intensity
5. **Add emphasis**: Highlight key words
6. **Add pauses**: Improve pacing and drama
7. **Test and iterate**: Generate samples and refine

## Common Issues and Solutions

### Speech sounds robotic
- Increase temperature (0.9 → 1.2)
- Decrease CFG weight (0.5 → 0.3)
- Add breath frequency (0 → 5)

### Speech sounds unnatural
- Decrease temperature (1.2 → 0.8)
- Increase CFG weight (0.3 → 0.6)
- Adjust pitch to natural range (-3 to +3)

### Words are unclear
- Decrease speed (1.2 → 0.9)
- Increase exaggeration (0.5 → 0.7)
- Add emphasis to unclear words

### Emotion not coming through
- Increase exaggeration (0.5 → 0.8)
- Adjust pitch to match emotion
- Use emphasis on emotional words

### Audio too fast
- Decrease speed (1.2 → 0.8)
- Increase pause_after (0 → 500)
- Add breath_frequency (0 → 5)

### Audio too slow
- Increase speed (0.8 → 1.2)
- Decrease pause_before/after
- Reduce breath_frequency

## Best Practices

1. **Start conservative**: Begin with default values, adjust gradually
2. **Test incrementally**: Change one parameter at a time
3. **Use presets**: Leverage predefined combinations
4. **Consider context**: Match parameters to content type
5. **A/B test**: Compare different parameter sets
6. **Use seed for consistency**: Reproduce good results
7. **Document settings**: Keep track of successful combinations
8. **Listen carefully**: Pay attention to naturalness and clarity

## Advanced Techniques

### Emphasis Patterns
Create natural stress patterns:
```bash
--emphasis "first" "important" "remember"
```

### Emotional Arcs
Build emotional intensity:
```bash
# Start calm
--emotion neutral --exaggeration 0.4

# Build excitement
--emotion excited --exaggeration 0.8

# End with emphasis
--emotion joyful --exaggeration 1.0 --emphasis "amazing"
```

### Pacing Control
Control speech pacing:
```bash
--speed 1.0 --pause-before 300 --pause-after 200 --breath-frequency 5
```

### Voice Characterization
Create distinct voice characters:
```bash
# Deep, authoritative
--pitch -6 --exaggeration 0.5 --emotion confident

# High, energetic
--pitch +6 --exaggeration 0.8 --emotion excited

# Warm, empathetic
--pitch 0 --exaggeration 0.7 --emotion empathetic
```

