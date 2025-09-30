# YouTube-to-Podcast Generation with n8n RAG Integration

This guide explains how to use the YouTube Chat CLI's enhanced podcast generation feature that integrates with your n8n RAG workflow for intelligent content enhancement.

## Overview

The YouTube Chat CLI can now:
1. **Extract YouTube video content** (transcript, metadata)
2. **Send content to your n8n RAG workflow** for intelligent processing
3. **Generate enhanced podcast scripts** using your knowledge base
4. **Create high-quality audio** using multiple TTS engines
5. **Maintain conversation context** across multiple videos

## Prerequisites

### 1. n8n RAG Workflow Setup
Your n8n workflow should be running at: `http://localhost:5678/workflow/vTN9y2dLXqTiDfPT`

The workflow includes:
- **Qdrant Vector Store** for document embeddings
- **Ollama/OpenRouter LLMs** for content generation
- **PostgreSQL** for conversation memory
- **Google Drive integration** for document processing

### 2. Environment Configuration
Copy `.env.template` to `.env` and configure:

```bash
# Required
YOUTUBE_API_KEY="your_youtube_api_key_here"

# n8n RAG Integration
N8N_WEBHOOK_URL="http://localhost:5678/workflow/vTN9y2dLXqTiDfPT"

# Optional
OPENROUTER_API_KEY="your_openrouter_key_here"
DEFAULT_TTS_VOICE="en-US-AriaNeural"
ENABLE_RAG_BY_DEFAULT=true
```

## Usage Examples

### Basic Podcast Generation

```bash
# Generate a summary-style podcast with RAG enhancement
youtube-chat podcast https://www.youtube.com/watch?v=VIDEO_ID

# Generate without RAG (local processing only)
youtube-chat podcast --no-rag https://www.youtube.com/watch?v=VIDEO_ID
```

### Advanced Podcast Styles

```bash
# Detailed analysis podcast
youtube-chat podcast --style detailed https://www.youtube.com/watch?v=VIDEO_ID

# Q&A style podcast
youtube-chat podcast --style qa --voice en-US-JennyNeural https://www.youtube.com/watch?v=VIDEO_ID

# Expert analysis with custom session
youtube-chat podcast --style analysis --session-id "deep-dive-session" https://www.youtube.com/watch?v=VIDEO_ID
```

### Voice Options

```bash
# Use different TTS voices
youtube-chat podcast --voice en-US-AriaNeural https://www.youtube.com/watch?v=VIDEO_ID
youtube-chat podcast --voice en-US-JennyNeural https://www.youtube.com/watch?v=VIDEO_ID
youtube-chat podcast --voice en-GB-SoniaNeural https://www.youtube.com/watch?v=VIDEO_ID
```

### Managing Generated Podcasts

```bash
# List recent podcasts
youtube-chat podcast-list

# List more podcasts
youtube-chat podcast-list --limit 20
```

## Podcast Styles

### 1. Summary (Default)
- **Purpose**: Quick overview of main points
- **Length**: 3-5 minutes typically
- **Best for**: Daily news, tutorials, quick insights

### 2. Detailed
- **Purpose**: Comprehensive analysis
- **Length**: 10-15 minutes typically
- **Best for**: Educational content, complex topics

### 3. Q&A
- **Purpose**: Question-and-answer format
- **Length**: 5-10 minutes typically
- **Best for**: FAQ-style content, interviews

### 4. Analysis
- **Purpose**: Expert-level critical analysis
- **Length**: 10-20 minutes typically
- **Best for**: Research papers, technical content

## n8n RAG Integration Benefits

When RAG is enabled, your podcasts are enhanced with:

### 1. **Contextual Knowledge**
- Content is enriched with information from your knowledge base
- Related documents and insights are automatically included
- Cross-references to similar topics in your collection

### 2. **Intelligent Summarization**
- AI agents analyze content against your existing knowledge
- Key insights are highlighted based on your document collection
- Connections to broader themes are identified

### 3. **Conversation Memory**
- Session-based context maintains continuity
- Previous podcast topics influence new content
- Building knowledge over time

### 4. **Multi-Modal Processing**
- Text, documents, and video content processed together
- Unified knowledge representation
- Enhanced search and retrieval

## Workflow Integration Details

### How It Works

1. **Video Processing**
   ```
   YouTube URL → Transcript Extraction → Content Analysis
   ```

2. **RAG Enhancement**
   ```
   Content → n8n Workflow → Vector Search → LLM Enhancement → Enhanced Script
   ```

3. **Audio Generation**
   ```
   Enhanced Script → TTS Engine → High-Quality Audio → Saved Podcast
   ```

### n8n Workflow Interaction

The CLI sends structured data to your n8n workflow:

```json
{
  "type": "video_import",
  "video_data": {
    "video_id": "VIDEO_ID",
    "title": "Video Title",
    "channel": "Channel Name",
    "transcript": "Full transcript...",
    "summary": "AI-generated summary...",
    "key_points": ["Point 1", "Point 2"]
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

For chat interactions:
```json
{
  "chatInput": "Generate a detailed analysis of this video content...",
  "sessionId": "podcast_VIDEO_ID_20240101_120000"
}
```

## Output Files

Generated podcasts are saved to: `~/.youtube-chat-cli/podcasts/`

Each podcast includes:
- **Audio file**: `podcast_VIDEO_ID_TIMESTAMP.wav`
- **Metadata**: `podcast_VIDEO_ID_TIMESTAMP.json`
- **Script**: Included in metadata JSON

### Metadata Structure

```json
{
  "video_id": "VIDEO_ID",
  "video_title": "Original Video Title",
  "video_channel": "Channel Name",
  "video_url": "https://youtube.com/watch?v=VIDEO_ID",
  "podcast_style": "summary",
  "audio_file": "/path/to/audio.wav",
  "script_length": 1500,
  "generated_at": "2024-01-01T12:00:00Z",
  "script": "Full podcast script..."
}
```

## Troubleshooting

### n8n Connection Issues

```bash
# Test n8n connection
youtube-chat verify-connections

# Check n8n workflow status
curl -X POST http://localhost:5678/workflow/vTN9y2dLXqTiDfPT \
  -H "Content-Type: application/json" \
  -d '{"chatInput": "test", "sessionId": "test"}'
```

### Common Issues

1. **"n8n webhook failed"**
   - Ensure n8n is running: `docker ps`
   - Check workflow URL in `.env`
   - Verify workflow is active in n8n

2. **"No valid response received"**
   - Check n8n workflow output format
   - Ensure AI models are loaded (Ollama)
   - Verify Qdrant vector store is accessible

3. **TTS Generation Fails**
   - Check available voices: `youtube-chat tts list`
   - Try different voice: `--voice en-US-AriaNeural`
   - Ensure edge-tts is installed

## Advanced Usage

### Batch Processing

```bash
# Process multiple videos with consistent session
SESSION_ID="batch-$(date +%Y%m%d)"

youtube-chat podcast --session-id "$SESSION_ID" --style detailed VIDEO_URL_1
youtube-chat podcast --session-id "$SESSION_ID" --style detailed VIDEO_URL_2
youtube-chat podcast --session-id "$SESSION_ID" --style detailed VIDEO_URL_3
```

### Custom Prompts via n8n

Modify your n8n workflow to handle custom podcast styles by updating the prompt generation logic in the AI Agent node.

### Integration with Other Tools

```bash
# Generate podcast and immediately play
youtube-chat podcast VIDEO_URL && \
  play ~/.youtube-chat-cli/podcasts/podcast_*.wav

# Generate and upload to cloud storage
youtube-chat podcast VIDEO_URL && \
  aws s3 cp ~/.youtube-chat-cli/podcasts/podcast_*.wav s3://my-podcasts/
```

## Best Practices

1. **Use consistent session IDs** for related content
2. **Choose appropriate styles** based on content type
3. **Maintain your n8n knowledge base** with relevant documents
4. **Monitor RAG performance** through n8n workflow logs
5. **Backup generated podcasts** regularly

## Next Steps

- Explore different TTS voices and styles
- Customize n8n workflow prompts for your use case
- Build automated podcast generation pipelines
- Integrate with podcast hosting platforms
