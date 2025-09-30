# 🎙️ YouTube Chat CLI - Professional Podcast Generation Platform

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/usemanusai/youtube-free-deep-research-cli)
[![Version](https://img.shields.io/badge/version-v2.0.0-orange.svg)](https://github.com/usemanusai/youtube-free-deep-research-cli/releases)

A comprehensive command-line platform for transforming YouTube videos and multi-source content into professional podcasts with AI-powered enhancement, multi-source processing, blueprint generation, and interactive n8n RAG workflow integration.

## 🌟 Key Features

### 🎙️ **Advanced Podcast Generation**
- **14 Professional Podcast Styles**: Interview, Debate, News Report, Educational, Storytelling, Panel Discussion, Documentary, Quick Tips, Deep Dive, Roundup, and more
- **Multi-Voice Support**: Different speakers for different roles (host, expert, moderator, panelists)
- **Customizable Length & Tone**: Short (2-8 min) to Extended (30+ min) with 8 different tone options
- **Intelligent Content Synthesis**: AI-powered script generation with n8n RAG integration

### 📚 **Multi-Source Content Processing**
- **20+ File Types**: PDF, DOCX, TXT, MD, CSV, XLSX, MP3, WAV, MP4, AVI, URLs, YouTube videos/playlists/channels, PPTX, code files, images (OCR)
- **Advanced Filtering**: Date range, file type, size, tags, location-based filtering
- **Batch Processing**: Handle hundreds of sources efficiently with parallel processing
- **Smart Content Prioritization**: AI selects most relevant content automatically

### 📋 **Blueprint Generation**
- **5 Blueprint Styles**: Comprehensive, Executive, Technical, Educational, Reference
- **Multiple Output Formats**: Markdown, PDF, HTML, DOCX, JSON
- **Intelligent Documentation**: AI-powered synthesis from multiple sources
- **Structured Output**: Table of contents, citations, metadata, and professional formatting

### 🤖 **Interactive Chat Interface**
- **Rich Terminal UI**: Beautiful formatting with syntax highlighting, tables, and markdown rendering
- **Session Management**: Save, load, resume conversations with full history
- **Real-time Streaming**: Live responses from n8n RAG workflows
- **Export Capabilities**: JSON and Markdown export of chat sessions

### 🔄 **Workflow Management**
- **Multiple n8n Workflows**: Manage different RAG workflows for various use cases
- **Connection Testing**: Automated workflow health checks
- **Default Workflow**: Set preferred workflows for different tasks
- **Import/Export**: Backup and share workflow configurations

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Podcast Styles](#podcast-styles)
- [Multi-Source Processing](#multi-source-processing)
- [Blueprint Generation](#blueprint-generation)
- [Interactive Chat](#interactive-chat)
- [Workflow Management](#workflow-management)
- [CLI Reference](#cli-reference)
- [n8n Integration](#n8n-integration)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### Option 1: Install from PyPI (Recommended)
```bash
pip install youtube-chat-cli
```

### Option 2: Install from Source
```bash
# Clone the repository
git clone https://github.com/usemanusai/youtube-free-deep-research-cli.git
cd youtube-free-deep-research-cli

# Install in development mode
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt
```

### Option 3: Using Docker
```bash
docker pull usemanusai/youtube-chat-cli:latest
docker run -it --env-file .env usemanusai/youtube-chat-cli
```

## ⚡ Quick Start

### 1. Setup Environment
```bash
# Copy environment template
cp .env.template .env

# Edit .env and add your API keys
nano .env
```

### 2. Basic Podcast Generation
```bash
# Generate a summary podcast from YouTube video
youtube-chat podcast https://www.youtube.com/watch?v=VIDEO_ID

# Generate an interview-style podcast with custom voice
youtube-chat podcast --style interview --voice en-US-JennyNeural --length long VIDEO_URL

# Generate a multi-source podcast from documents
youtube-chat podcast-create-multi --sources /path/to/documents --style roundup --length medium
```

### 3. Interactive Chat
```bash
# Start interactive chat with n8n RAG
youtube-chat chat

# Ask a one-off question
youtube-chat ask "What are the main insights from recent videos?"
```

### 4. Blueprint Generation
```bash
# Create comprehensive documentation from sources
youtube-chat blueprint-create --sources /path/to/research --title "Research Analysis" --style comprehensive
```

## ⚙️ Configuration

### Required API Keys

Create a `.env` file with the following configuration:

```env
# Required: YouTube Data API v3 key
YOUTUBE_API_KEY="your_youtube_api_key_here"

# Optional: OpenRouter API key for AI features
OPENROUTER_API_KEY="your_openrouter_key_here"

# Optional: n8n webhook URL for RAG integration
N8N_WEBHOOK_URL="http://localhost:5678/workflow/vTN9y2dLXqTiDfPT"

# TTS Configuration
DEFAULT_TTS_VOICE="en-US-AriaNeural"
DEFAULT_TTS_LIBRARY="edge-tts"

# Podcast Generation Settings
DEFAULT_PODCAST_STYLE="summary"
DEFAULT_PODCAST_LENGTH="medium"
ENABLE_RAG_BY_DEFAULT=true
```

### Getting API Keys

1. **YouTube Data API v3**: 
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Create a new project or select existing
   - Enable YouTube Data API v3
   - Create credentials (API Key)

2. **OpenRouter API** (Optional):
   - Visit [OpenRouter](https://openrouter.ai/keys)
   - Sign up and generate an API key
   - Provides access to multiple AI models

## 🎙️ Podcast Styles

### Available Styles

| Style | Description | Length Range | Voice Roles | Best For |
|-------|-------------|--------------|-------------|----------|
| **Summary** | Quick overview of main points | 3-30 min | Narrator | Daily updates, quick insights |
| **Interview** | Conversational host-expert format | 5-45 min | Host + Expert | Educational content, expert insights |
| **Debate** | Multiple perspectives discussion | 7-60 min | Moderator + Advocates | Controversial topics, analysis |
| **News Report** | Journalistic coverage style | 4-36 min | Anchor + Reporter | Current events, breaking news |
| **Educational** | Teaching-focused presentation | 6-54 min | Instructor | Learning content, tutorials |
| **Storytelling** | Narrative-driven content | 7-63 min | Narrator | Case studies, stories |
| **Panel** | Multiple speakers discussion | 8-72 min | Moderator + Panelists | Roundtable discussions |
| **Documentary** | In-depth investigative format | 10-90 min | Documentary narrator | Deep investigations |
| **Quick Tips** | Short, actionable advice | 2-18 min | Tips host | How-to content |
| **Deep Dive** | Extended technical analysis | 15-120 min | Technical analyst | Technical content, research |
| **Roundup** | Compilation of multiple sources | 8-72 min | Roundup host | Weekly summaries |

### Usage Examples

```bash
# Interview style with custom settings
youtube-chat podcast --style interview --length long --tone conversational VIDEO_URL

# News report with professional tone
youtube-chat podcast --style news_report --length medium --tone professional VIDEO_URL

# Quick tips with enthusiastic delivery
youtube-chat podcast --style quick_tips --length short --tone enthusiastic VIDEO_URL
```

## 📚 Multi-Source Processing

### Supported File Types

#### Documents
- **PDF**: Research papers, reports, books
- **DOCX/DOC**: Word documents, articles
- **TXT**: Plain text files, notes
- **MD**: Markdown documentation
- **RTF**: Rich text format files

#### Spreadsheets & Data
- **CSV**: Data files, lists
- **XLSX/XLS**: Excel spreadsheets
- **ODS**: OpenDocument spreadsheets

#### Media Files
- **Audio**: MP3, WAV, M4A, FLAC, OGG (with transcription)
- **Video**: MP4, AVI, MOV, MKV, WebM (with transcription)

#### Web & Online Content
- **URLs**: Website scraping and analysis
- **HTML**: Local HTML files
- **YouTube**: Videos, playlists, channels

#### Presentations & Code
- **PPTX/PPT**: PowerPoint presentations
- **Code Files**: PY, JS, JSON, YAML, XML
- **Images**: PNG, JPG (with OCR text extraction)

### Multi-Source Commands

```bash
# Process entire directory
youtube-chat podcast-create-multi --sources /path/to/documents --style roundup

# Filter by file types and date
youtube-chat podcast-create-multi \
  --sources /path/to/content \
  --file-types pdf,docx,md \
  --days 30 \
  --style comprehensive

# Create from mixed sources
youtube-chat podcast-create-multi \
  --sources /path/to/research \
  --title "Research Roundup" \
  --style deep_dive \
  --length extended \
  --use-rag
```

## 📋 Blueprint Generation

Create comprehensive documentation from multiple sources with AI-powered synthesis.

### Blueprint Styles

| Style | Purpose | Sections | Best For |
|-------|---------|----------|----------|
| **Comprehensive** | Complete documentation | Executive summary, overview, findings, analysis, recommendations | Project documentation |
| **Executive** | High-level summary | Executive summary, key points, implications, next steps | Leadership presentations |
| **Technical** | Technical documentation | Overview, architecture, implementation, best practices | Technical docs |
| **Educational** | Learning materials | Objectives, concepts, guide, examples, exercises | Training materials |
| **Reference** | Quick reference | Commands, configuration, troubleshooting, FAQ | Reference guides |

### Blueprint Commands

```bash
# Create comprehensive blueprint
youtube-chat blueprint-create \
  --sources /path/to/research \
  --title "Research Analysis" \
  --style comprehensive \
  --format pdf

# Executive summary from recent files
youtube-chat blueprint-create \
  --sources /path/to/reports \
  --title "Q4 Summary" \
  --style executive \
  --days 90 \
  --use-rag

# Technical documentation
youtube-chat blueprint-create \
  --sources /path/to/code \
  --title "API Documentation" \
  --style technical \
  --format html
```

## 🤖 Interactive Chat

Rich terminal-based chat interface with n8n RAG integration.

### Chat Features

- **Rich Formatting**: Syntax highlighting, tables, markdown rendering
- **Session Management**: Save, load, resume conversations
- **Real-time Responses**: Streaming responses from n8n workflows
- **Export Options**: JSON and Markdown export
- **Command System**: Built-in commands for session management

### Chat Commands

```bash
# Start interactive chat
youtube-chat chat

# Resume specific session
youtube-chat chat --session my-research-session

# Use specific workflow
youtube-chat chat --workflow research-workflow

# One-off questions
youtube-chat ask "What are the main trends in AI research?"
```

### In-Chat Commands

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
/export <format>   - Export session (json/markdown)
/status            - Show session status
```

## 🔄 Workflow Management

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

### Workflow Testing

```bash
# Test specific workflow
youtube-chat workflow test my-workflow

# Test all workflows
youtube-chat workflow test

# Get workflow statistics
youtube-chat workflow stats
```

## 📚 CLI Reference

### Core Commands

| Command | Description | Key Options |
|---------|-------------|-------------|
| `podcast` | Generate podcast from YouTube video | `--style`, `--length`, `--tone`, `--voice`, `--use-rag` |
| `podcast-create-multi` | Generate podcast from multiple sources | `--sources`, `--style`, `--days`, `--file-types` |
| `podcast-list` | List generated podcasts | `--limit` |
| `blueprint-create` | Create documentation blueprint | `--sources`, `--title`, `--style`, `--format` |
| `blueprint-list` | List generated blueprints | - |
| `chat` | Start interactive chat | `--session`, `--workflow` |
| `ask` | Ask one-off question | `--workflow` |
| `workflow` | Manage n8n workflows | `add`, `remove`, `list`, `test`, `set-default` |

### Legacy Commands (Backward Compatible)

| Command | Description | Status |
|---------|-------------|--------|
| `set-source` | Set active YouTube video | ✅ Supported |
| `summarize` | Generate content summary | ✅ Supported |
| `faq` | Generate FAQ | ✅ Supported |
| `toc` | Generate table of contents | ✅ Supported |
| `import` | Bulk import videos/channels | ✅ Supported |
| `channel` | Manage channel monitoring | ✅ Supported |
| `service` | Background service management | ✅ Supported |
| `tts` | TTS library management | ✅ Supported |

## 🔗 n8n Integration

### Your n8n RAG Workflow

The CLI integrates seamlessly with your existing n8n RAG workflow:

**Workflow URL**: `http://localhost:5678/workflow/vTN9y2dLXqTiDfPT`

**Features**:
- **Qdrant Vector Store** for document embeddings
- **Ollama/OpenRouter LLMs** for content generation
- **PostgreSQL** for conversation memory
- **Google Drive integration** for document processing

### Integration Benefits

- **Enhanced Content**: RAG-powered podcast scripts with insights from your knowledge base
- **Contextual Responses**: Chat responses informed by your document collection
- **Persistent Memory**: Conversation history maintained across sessions
- **Multi-Modal Processing**: Text, documents, and video content processed together

### Setup Instructions

1. **Ensure n8n is running**: `docker ps` (check for n8n container)
2. **Configure webhook URL**: Already set in `.env.template`
3. **Test connection**: `youtube-chat workflow test default`
4. **Start chatting**: `youtube-chat chat`

## 🏗️ Architecture

```
src/youtube_chat_cli/
├── core/                    # Core functionality
│   ├── youtube_api.py      # YouTube Data API client
│   ├── database.py         # SQLite database management
│   └── config.py           # Configuration management
├── services/               # Service implementations
│   ├── podcast/           # Podcast generation
│   │   ├── generator.py   # Main podcast generator
│   │   └── styles.py      # Style definitions
│   ├── content/           # Multi-source processing
│   │   └── source_manager.py
│   ├── blueprint/         # Documentation generation
│   │   └── generator.py
│   ├── workflow/          # n8n workflow management
│   │   └── manager.py
│   ├── chat/             # Interactive chat interface
│   │   └── interface.py
│   ├── tts/              # Text-to-speech services
│   ├── transcription/    # Content processing
│   ├── monitoring/       # Channel monitoring
│   ├── import_service/   # Bulk import functionality
│   └── n8n/             # n8n integration
├── cli/                  # Command-line interface
├── utils/                # Utility functions
└── models/               # Data models
```

## 🛠️ Development

### Running Tests

```bash
# Basic import tests
python test_basic_imports.py

# Full test suite
pytest tests/

# Test specific functionality
PYTHONPATH=src python -m youtube_chat_cli.cli.main --help
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/usemanusai/youtube-free-deep-research-cli.git
cd youtube-free-deep-research-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Run tests
python test_basic_imports.py
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: 
   ```bash
   pip install -r requirements.txt
   pip install rich  # For interactive chat
   ```

2. **API Key Issues**:
   - Verify YouTube API key is valid
   - Check `.env` file configuration
   - Ensure YouTube Data API v3 is enabled

3. **n8n Connection Issues**:
   ```bash
   # Test n8n connection
   youtube-chat workflow test default
   
   # Check n8n status
   curl -X POST http://localhost:5678/workflow/vTN9y2dLXqTiDfPT
   ```

4. **TTS Issues**:
   ```bash
   # List available voices
   youtube-chat tts list
   
   # Test voice
   youtube-chat tts test en-US-AriaNeural
   ```

### Getting Help

- 📖 Check the [comprehensive features guide](docs/guides/comprehensive-features-guide.md)
- 🎙️ Review [podcast generation guide](docs/guides/podcast-generation-with-n8n-rag.md)
- 🐛 Open an issue on GitHub for bug reports
- 💡 Request features through GitHub issues

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📝 Changelog

### v2.0.0 (Latest) - Comprehensive Enhancement Release

#### 🎉 **Major New Features**
- **14 Professional Podcast Styles**: Interview, Debate, News Report, Educational, Storytelling, Panel Discussion, Documentary, Quick Tips, Deep Dive, Roundup
- **Multi-Source Content Processing**: Support for 20+ file types including documents, audio, video, web content, presentations, and code files
- **Blueprint Generation**: Create comprehensive documentation from multiple sources with 5 different styles
- **Interactive Chat Interface**: Rich terminal UI with syntax highlighting, session management, and export capabilities
- **Workflow Management**: Complete n8n workflow management system with testing and configuration

#### 🚀 **Enhancements**
- **Enhanced Podcast Generation**: Multi-voice support, customizable length and tone, intelligent chunking
- **Advanced Filtering**: Date range, file type, size, and tag-based filtering for source selection
- **Batch Processing**: Efficiently handle hundreds of sources with parallel processing
- **Session Persistence**: Save and resume chat sessions with full history
- **Professional Package Structure**: Modular architecture with proper separation of concerns

#### 🔧 **Technical Improvements**
- **Rich Dependencies**: Beautiful terminal UI with Rich library
- **Comprehensive Error Handling**: Robust error handling and logging throughout
- **Configuration Management**: Enhanced environment variable management
- **Documentation**: Comprehensive guides and API reference

### v1.0.0 - Initial Release
- 🎉 Core YouTube processing functionality
- 🤖 AI-powered content analysis with OpenRouter integration
- 🎙️ Multi-engine TTS support (gTTS, edge-tts, MaryTTS)
- 💬 Interactive chat interface for content Q&A
- 📊 Bulk import and channel monitoring capabilities
- 🔗 n8n workflow integration for automation

## 🙏 Acknowledgments

- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api) for transcript extraction
- [OpenRouter](https://openrouter.ai/) for AI model access
- [n8n](https://n8n.io/) for workflow automation capabilities
- [Edge TTS](https://github.com/rany2/edge-tts) for high-quality text-to-speech
- [Rich](https://github.com/Textualize/rich) for beautiful terminal UI
- [Click](https://click.palletsprojects.com/) for CLI framework

---

**Made with ❤️ for content creators, researchers, and knowledge workers**

Transform your content into professional podcasts with AI-powered intelligence! 🎙️✨
