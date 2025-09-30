# YouTube Chat CLI - Comprehensive Features Guide

This guide covers all the enhanced features of the YouTube Chat CLI, including multi-source content processing, advanced podcast generation, blueprint creation, workflow management, and interactive chat.

## Table of Contents

1. [Enhanced Podcast Styles and Formats](#enhanced-podcast-styles-and-formats)
2. [Multi-Source Content Processing](#multi-source-content-processing)
3. [Blueprint Generation](#blueprint-generation)
4. [Multi-Source Podcast Generation](#multi-source-podcast-generation)
5. [Workflow Management](#workflow-management)
6. [Interactive Chat Interface](#interactive-chat-interface)
7. [Advanced Settings and Configuration](#advanced-settings-and-configuration)

## Enhanced Podcast Styles and Formats

### Available Podcast Styles

The YouTube Chat CLI now supports 14 different podcast styles:

#### 1. **Summary** (Default)
- **Purpose**: Quick overview of main points
- **Length**: 3-5 minutes (short) to 30 minutes (extended)
- **Best for**: Daily updates, quick insights
- **Voice roles**: Single narrator

#### 2. **Interview**
- **Purpose**: Conversational format between host and expert
- **Length**: 5-45 minutes
- **Best for**: Educational content, expert insights
- **Voice roles**: Host + Expert

#### 3. **Debate**
- **Purpose**: Multiple perspectives on controversial topics
- **Length**: 7-60 minutes
- **Best for**: Complex issues with multiple viewpoints
- **Voice roles**: Moderator + Advocate + Critic

#### 4. **News Report**
- **Purpose**: Journalistic coverage style
- **Length**: 4-36 minutes
- **Best for**: Current events, breaking news
- **Voice roles**: Anchor + Reporter

#### 5. **Educational Lecture**
- **Purpose**: Teaching-focused presentation
- **Length**: 6-54 minutes
- **Best for**: Learning content, tutorials
- **Voice roles**: Instructor

#### 6. **Storytelling Narrative**
- **Purpose**: Story-driven content
- **Length**: 7-63 minutes
- **Best for**: Case studies, narratives
- **Voice roles**: Narrator

#### 7. **Panel Discussion**
- **Purpose**: Multiple speakers discussing topics
- **Length**: 8-72 minutes
- **Best for**: Roundtable discussions
- **Voice roles**: Moderator + 3 Panelists

#### 8. **Documentary**
- **Purpose**: In-depth investigative format
- **Length**: 10-90 minutes
- **Best for**: Deep investigations, research
- **Voice roles**: Documentary narrator

#### 9. **Quick Tips**
- **Purpose**: Short, actionable advice
- **Length**: 2-18 minutes
- **Best for**: How-to content, tips
- **Voice roles**: Tips host

#### 10. **Deep Dive**
- **Purpose**: Extended technical analysis
- **Length**: 15-120 minutes
- **Best for**: Technical content, research
- **Voice roles**: Technical analyst

#### 11. **Roundup**
- **Purpose**: Compilation of multiple sources
- **Length**: 8-72 minutes
- **Best for**: Weekly summaries, compilations
- **Voice roles**: Roundup host

### Podcast Length Categories

- **Short**: 2-8 minutes - Quick updates and tips
- **Medium**: 6-24 minutes - Standard podcast episodes
- **Long**: 12-48 minutes - In-depth discussions
- **Extended**: 18-120 minutes - Comprehensive analysis

### Podcast Tone Options

- **Professional**: Formal, business-appropriate
- **Casual**: Relaxed, conversational
- **Enthusiastic**: Energetic, exciting
- **Educational**: Teaching-focused, clear
- **Conversational**: Natural, friendly
- **Authoritative**: Expert, confident
- **Friendly**: Warm, approachable
- **Dramatic**: Engaging, compelling

### Usage Examples

```bash
# Basic podcast with new styles
youtube-chat podcast --style interview --length long --tone conversational VIDEO_URL

# Multi-voice debate format
youtube-chat podcast --style debate --length extended --tone professional VIDEO_URL

# Quick tips format
youtube-chat podcast --style quick_tips --length short --tone enthusiastic VIDEO_URL

# Documentary style deep dive
youtube-chat podcast --style documentary --length extended --tone authoritative VIDEO_URL
```

## Multi-Source Content Processing

### Supported Source Types

#### Documents
- **PDF**: Research papers, reports, books
- **DOCX/DOC**: Word documents, articles
- **TXT**: Plain text files, notes
- **MD**: Markdown documentation
- **RTF**: Rich text format files
- **ODT**: OpenDocument text files

#### Spreadsheets
- **CSV**: Data files, lists
- **XLSX/XLS**: Excel spreadsheets
- **ODS**: OpenDocument spreadsheets

#### Audio & Video
- **Audio**: MP3, WAV, M4A, FLAC, OGG (with transcription)
- **Video**: MP4, AVI, MOV, MKV, WebM (with transcription)

#### Web Content
- **URLs**: Website scraping
- **HTML**: Local HTML files

#### YouTube Content
- **Videos**: Individual video links
- **Playlists**: Complete playlist processing
- **Channels**: Channel content analysis

#### Presentations
- **PPTX/PPT**: PowerPoint presentations
- **ODP**: OpenDocument presentations

#### Code Files
- **PY, JS, JSON, YAML, XML**: Source code analysis

#### Images
- **PNG, JPG**: OCR text extraction

### Source Management

#### Adding Sources

```bash
# Add individual file
youtube-chat source add /path/to/document.pdf

# Add entire directory
youtube-chat source add-directory /path/to/documents/

# Add with tags
youtube-chat source add /path/to/file.pdf --tags research,important

# Add remote URL
youtube-chat source add https://example.com/article --location web
```

#### Filtering Sources

```bash
# Filter by date range
youtube-chat source list --days 7  # Last 7 days

# Filter by file type
youtube-chat source list --types pdf,docx

# Filter by tags
youtube-chat source list --tags research

# Filter by size
youtube-chat source list --min-size 1MB --max-size 10MB
```

#### Source Processing

```bash
# Process all sources
youtube-chat source process-all

# Process specific source
youtube-chat source process SOURCE_ID

# Batch process with filter
youtube-chat source process --days 30 --types pdf,docx
```

## Blueprint Generation

Blueprints are comprehensive documentation generated from multiple sources, perfect for creating reports, summaries, and knowledge bases.

### Blueprint Styles

#### 1. **Comprehensive** (Default)
- Executive summary, overview, key findings, detailed analysis, recommendations, conclusion
- Best for: Complete project documentation

#### 2. **Executive**
- Executive summary, key points, strategic implications, next steps
- Best for: Leadership presentations

#### 3. **Technical**
- Technical overview, architecture, implementation details, performance analysis, best practices
- Best for: Technical documentation

#### 4. **Educational**
- Learning objectives, prerequisites, core concepts, step-by-step guide, examples, exercises
- Best for: Training materials

#### 5. **Reference**
- Quick reference, commands/APIs, configuration, troubleshooting, FAQ
- Best for: Quick reference guides

### Blueprint Formats

- **Markdown**: Standard markdown format
- **PDF**: Professional PDF documents
- **HTML**: Web-ready HTML pages
- **DOCX**: Microsoft Word documents
- **JSON**: Structured data format

### Creating Blueprints

```bash
# Basic blueprint creation
youtube-chat blueprint-create --sources /path/to/documents --title "Project Overview"

# Comprehensive blueprint with RAG enhancement
youtube-chat blueprint-create \
  --sources /path/to/research \
  --title "Research Analysis" \
  --style comprehensive \
  --format pdf \
  --use-rag

# Executive summary blueprint
youtube-chat blueprint-create \
  --sources /path/to/reports \
  --title "Q4 Summary" \
  --style executive \
  --format docx \
  --days 90

# Technical documentation
youtube-chat blueprint-create \
  --sources /path/to/code \
  --title "API Documentation" \
  --style technical \
  --format html
```

### Blueprint Management

```bash
# List generated blueprints
youtube-chat blueprint-list

# Export blueprint
youtube-chat blueprint export BLUEPRINT_ID --format pdf

# Share blueprint
youtube-chat blueprint share BLUEPRINT_ID --email user@example.com
```

## Multi-Source Podcast Generation

Generate podcasts from hundreds of sources with intelligent content synthesis.

### Features

- **Batch Processing**: Handle hundreds of sources efficiently
- **Intelligent Prioritization**: AI selects most relevant content
- **Automatic Chunking**: Split long content into manageable segments
- **Smooth Transitions**: Professional audio transitions between segments
- **Episode Metadata**: Timestamps, chapters, show notes
- **RSS Feed Generation**: Create podcast series feeds

### Usage

```bash
# Basic multi-source podcast
youtube-chat podcast-create-multi \
  --sources /path/to/content \
  --title "Weekly Roundup" \
  --style roundup \
  --length medium

# Advanced multi-source with chunking
youtube-chat podcast-create-multi \
  --sources /path/to/research \
  --title "Research Deep Dive" \
  --style deep_dive \
  --length extended \
  --chunk-size 600 \
  --tone professional

# Filtered multi-source podcast
youtube-chat podcast-create-multi \
  --sources /path/to/documents \
  --title "Recent Updates" \
  --style summary \
  --days 7 \
  --file-types pdf,docx,md \
  --use-rag
```

### Chunking and Merging

For long podcasts, the system automatically:

1. **Estimates Duration**: Based on content length and speaking rate
2. **Creates Chunks**: Splits content into specified chunk sizes
3. **Adds Transitions**: Smooth audio transitions between chunks
4. **Merges Audio**: Combines chunks into final podcast
5. **Generates Metadata**: Creates chapter markers and timestamps

## Workflow Management

Manage multiple n8n RAG workflows for different use cases.

### Workflow Commands

```bash
# Add new workflow
youtube-chat workflow add \
  --name "research-workflow" \
  --url "http://localhost:5678/workflow/ABC123" \
  --description "Research-focused RAG workflow"

# List all workflows
youtube-chat workflow list

# Test workflow connection
youtube-chat workflow test research-workflow

# Set default workflow
youtube-chat workflow set-default research-workflow

# Remove workflow
youtube-chat workflow remove old-workflow
```

### Workflow Configuration

Each workflow can have:
- **Custom URL**: Different n8n workflow endpoints
- **Specialized Purpose**: Research, customer support, content creation
- **Different Models**: Various AI models and configurations
- **Custom Prompts**: Tailored prompt engineering

### Workflow Testing

```bash
# Test specific workflow
youtube-chat workflow test my-workflow

# Test all workflows
youtube-chat workflow test

# Get workflow status
youtube-chat workflow status
```

## Interactive Chat Interface

Beautiful terminal-based chat interface with rich formatting and features.

### Starting Chat

```bash
# Basic chat
youtube-chat chat

# Chat with specific session
youtube-chat chat --session my-session

# Chat with specific workflow
youtube-chat chat --workflow research-workflow

# Resume previous session
youtube-chat chat --session previous-session-id
```

### Chat Features

#### Rich Formatting
- **Syntax Highlighting**: Code blocks with language detection
- **Tables**: Automatic table formatting
- **Markdown**: Rich text rendering
- **Colors**: Syntax highlighting and themes

#### Session Management
- **Save/Load**: Persistent chat sessions
- **Export**: JSON and Markdown export
- **History**: Full conversation history
- **Search**: Search through chat history

#### Chat Commands

```
/help              - Show available commands
/quit, /exit       - Exit chat
/clear             - Clear screen
/history [limit]   - Show chat history
/save              - Save current session
/load <session>    - Load saved session
/sessions          - List all sessions
/new [session]     - Start new session
/workflow <name>   - Change workflow
/workflows         - List workflows
/export <format>   - Export session
/status            - Show session status
```

### One-off Questions

```bash
# Ask single question
youtube-chat ask "What are the main trends in AI research?"

# Ask with specific workflow
youtube-chat ask --workflow research-workflow "Summarize recent papers"
```

## Advanced Settings and Configuration

### Environment Configuration

```bash
# Core settings
YOUTUBE_API_KEY="your_api_key"
N8N_WEBHOOK_URL="http://localhost:5678/workflow/ID"
OPENROUTER_API_KEY="your_openrouter_key"

# Podcast settings
DEFAULT_PODCAST_STYLE="summary"
DEFAULT_PODCAST_LENGTH="medium"
DEFAULT_PODCAST_TONE="professional"
ENABLE_RAG_BY_DEFAULT=true

# TTS settings
DEFAULT_TTS_VOICE="en-US-AriaNeural"
DEFAULT_TTS_LIBRARY="edge-tts"

# Processing settings
MAX_SOURCES_PER_BATCH=100
CHUNK_SIZE_SECONDS=600
ENABLE_PARALLEL_PROCESSING=true
```

### Backup and Export Settings

```bash
# Auto-backup configuration
AUTO_BACKUP_ENABLED=true
BACKUP_DIRECTORY="/path/to/backups"
BACKUP_RETENTION_DAYS=30

# Export settings
DEFAULT_EXPORT_FORMAT="markdown"
INCLUDE_METADATA=true
COMPRESS_EXPORTS=true
```

### Performance Tuning

```bash
# Processing settings
MAX_CONCURRENT_SOURCES=5
PROCESSING_TIMEOUT_SECONDS=300
ENABLE_CACHING=true
CACHE_EXPIRY_HOURS=24

# Memory settings
MAX_CONTENT_LENGTH=50000
CHUNK_OVERLAP_WORDS=100
ENABLE_CONTENT_COMPRESSION=true
```

## Integration Examples

### Daily News Roundup

```bash
# 1. Add news sources
youtube-chat source add-directory /path/to/news --tags daily,news

# 2. Generate daily podcast
youtube-chat podcast-create-multi \
  --sources /path/to/news \
  --title "Daily News Roundup" \
  --style news_report \
  --length short \
  --days 1 \
  --tone professional

# 3. Create daily blueprint
youtube-chat blueprint-create \
  --sources /path/to/news \
  --title "Daily News Summary" \
  --style executive \
  --days 1
```

### Research Project Documentation

```bash
# 1. Add research materials
youtube-chat source add-directory /path/to/research --tags research,project

# 2. Generate comprehensive blueprint
youtube-chat blueprint-create \
  --sources /path/to/research \
  --title "Research Project Analysis" \
  --style comprehensive \
  --format pdf \
  --use-rag

# 3. Create research podcast series
youtube-chat podcast-create-multi \
  --sources /path/to/research \
  --title "Research Deep Dive" \
  --style deep_dive \
  --length extended \
  --chunk-size 900
```

### Weekly Team Updates

```bash
# 1. Process team documents
youtube-chat source add-directory /path/to/team-docs --tags team,weekly

# 2. Generate team podcast
youtube-chat podcast-create-multi \
  --sources /path/to/team-docs \
  --title "Weekly Team Update" \
  --style panel \
  --length medium \
  --days 7 \
  --tone conversational

# 3. Create executive summary
youtube-chat blueprint-create \
  --sources /path/to/team-docs \
  --title "Weekly Executive Summary" \
  --style executive \
  --days 7
```

## Best Practices

### Content Organization
1. **Use consistent tagging** for easy filtering
2. **Organize sources by project** or topic
3. **Regular cleanup** of outdated sources
4. **Backup important content** regularly

### Podcast Production
1. **Choose appropriate styles** for content type
2. **Use consistent voice settings** for series
3. **Test different tones** for audience engagement
4. **Monitor audio quality** and adjust settings

### Blueprint Creation
1. **Use descriptive titles** for easy identification
2. **Choose appropriate styles** for audience
3. **Include relevant metadata** for context
4. **Regular updates** for living documents

### Workflow Management
1. **Test workflows regularly** to ensure connectivity
2. **Use descriptive names** for different purposes
3. **Document workflow purposes** and configurations
4. **Monitor performance** and optimize as needed

This comprehensive guide covers all the enhanced features of the YouTube Chat CLI. Each feature is designed to work together, creating a powerful content processing and generation ecosystem.
