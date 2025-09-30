# 🎙️ JAEGIS YouTube Chat MCP Server

[![npm version](https://badge.fury.io/js/jaegis-youtube-chat-mcp.svg)](https://badge.fury.io/js/jaegis-youtube-chat-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen.svg)](https://nodejs.org/)

**JAEGIS YouTube Chat MCP Server** is a Model Context Protocol (MCP) server that exposes all YouTube Chat CLI commands as tools for AI assistants. This enables seamless integration of YouTube video analysis, podcast generation, channel monitoring, and content processing capabilities into any MCP-compatible AI system.

## 🚀 Quick Start

### Installation

```bash
# Install globally via npm
npm install -g jaegis-youtube-chat-mcp

# Or run directly with npx (recommended)
npx jaegis-youtube-chat-mcp
```

### Prerequisites

The MCP server requires the YouTube Chat CLI to be installed:

```bash
# Install the YouTube Chat CLI
pip install youtube-chat-cli

# Verify installation
youtube-chat --version
```

### Usage

```bash
# Start the MCP server
jaegis-youtube-chat-mcp

# Or with npx
npx jaegis-youtube-chat-mcp
```

The server will start and listen for MCP connections via stdio.

## 🛠️ Available Tools

The MCP server exposes **35+ tools** organized into the following categories:

### 📋 Session Management
- `jaegis_session_view` - View current session information
- `jaegis_session_clear_history` - Clear chat history
- `jaegis_session_clear_all` - Clear all session data
- `jaegis_session_new_id` - Generate new session ID

### 📄 Content Processing
- `jaegis_set_source` - Set active source URL and process content
- `jaegis_print_text` - Print processed text content
- `jaegis_summarize` - Generate AI summary
- `jaegis_faq` - Generate FAQ document
- `jaegis_toc` - Generate table of contents
- `jaegis_chat` - Start interactive chat session
- `jaegis_ask` - Ask single question to n8n RAG

### 🎙️ Podcast Generation
- `jaegis_podcast_generate` - Generate podcast from video (14 styles)
- `jaegis_podcast_list` - List generated podcasts
- `jaegis_podcast_create_multi` - Create podcast from multiple sources

### 🔊 Text-to-Speech Management
- `jaegis_tts_list` - List available TTS libraries
- `jaegis_tts_info` - Show TTS library details
- `jaegis_tts_install` - Install TTS library
- `jaegis_tts_install_all` - Install all TTS libraries
- `jaegis_tts_uninstall` - Uninstall TTS library
- `jaegis_tts_test` - Test TTS library
- `jaegis_tts_set_default` - Set default TTS library
- `jaegis_tts_status` - Show TTS status
- `jaegis_tts_configure` - Configure TTS library

### 📺 Channel Monitoring
- `jaegis_channel_add` - Add channel for monitoring
- `jaegis_channel_list` - List monitored channels
- `jaegis_channel_remove` - Remove channel
- `jaegis_channel_update` - Update channel settings
- `jaegis_channel_scan` - Manually scan channels

### 📥 Bulk Import
- `jaegis_import_channel` - Import videos from channel
- `jaegis_import_playlist` - Import videos from playlist
- `jaegis_import_urls` - Import videos from URL file

### ⚙️ Service Management
- `jaegis_service_start` - Start background service
- `jaegis_service_stop` - Stop background service
- `jaegis_service_status` - Check service status
- `jaegis_service_logs` - View service logs

### 🔄 Workflow Management
- `jaegis_workflow_add` - Add n8n workflow
- `jaegis_workflow_remove` - Remove workflow
- `jaegis_workflow_list` - List workflows
- `jaegis_workflow_test` - Test workflow connections
- `jaegis_workflow_set_default` - Set default workflow

### 🔗 n8n Integration
- `jaegis_n8n_configure` - Configure n8n settings
- `jaegis_n8n_send` - Send video to n8n workflow

### 📊 Utilities
- `jaegis_stats` - Show statistics
- `jaegis_history` - View import history
- `jaegis_verify_connections` - Verify service connections
- `jaegis_blueprint_create` - Create documentation blueprint
- `jaegis_blueprint_list` - List blueprints

## 🎯 Key Features

### 🎙️ Advanced Podcast Generation
- **14 Podcast Styles**: Conversational, interview, narrative, educational, news, comedy, documentary, debate, monologue, panel, storytelling, technical, casual, formal
- **Multiple Voices**: Support for various TTS engines and voices
- **RAG Enhancement**: Optional n8n RAG integration for enhanced content
- **Multi-source**: Generate podcasts from multiple content sources

### 📺 Intelligent Channel Monitoring
- **Automated Scanning**: Background service for continuous monitoring
- **Advanced Filtering**: Keywords, duration, content type filters
- **Rate Limiting**: Intelligent rate limiting to respect API limits
- **Bulk Operations**: Import entire channels, playlists, or URL lists

### 🤖 AI Integration
- **n8n RAG Workflows**: Seamless integration with n8n for RAG processing
- **Multiple Workflows**: Support for multiple AI workflows
- **Session Management**: Persistent sessions for context continuity
- **Interactive Chat**: Real-time chat with AI agents

### 🔊 Comprehensive TTS Support
- **Multiple Libraries**: OpenAI, ElevenLabs, Edge TTS, Google TTS, and more
- **Easy Management**: Install, configure, and test TTS libraries
- **Voice Selection**: Wide variety of voices and languages
- **Quality Control**: Test and validate TTS output

## 🔧 Configuration

### Environment Variables

The MCP server uses the same configuration as YouTube Chat CLI:

```bash
# Required for YouTube API access
YOUTUBE_API_KEY=your_youtube_api_key

# Required for AI features
OPENROUTER_API_KEY=your_openrouter_api_key

# Optional: n8n integration
N8N_WEBHOOK_URL=your_n8n_webhook_url

# Optional: TTS API keys
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

### MCP Client Configuration

To use with an MCP client, add the server to your configuration:

```json
{
  "mcpServers": {
    "jaegis-youtube-chat": {
      "command": "npx",
      "args": ["jaegis-youtube-chat-mcp"]
    }
  }
}
```

## 📖 Usage Examples

### Generate a Podcast
```javascript
// Using the MCP tool
await callTool('jaegis_podcast_generate', {
  video_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
  style: 'conversational',
  voice: 'alloy',
  use_rag: true
});
```

### Monitor a YouTube Channel
```javascript
// Add channel for monitoring
await callTool('jaegis_channel_add', {
  channel_url: 'https://www.youtube.com/@channelname',
  check_interval: 24,
  no_shorts: true,
  include_keywords: ['AI', 'technology']
});
```

### Create Documentation Blueprint
```javascript
// Generate comprehensive documentation
await callTool('jaegis_blueprint_create', {
  sources: '/path/to/content',
  title: 'Project Documentation',
  style: 'comprehensive',
  format: 'markdown',
  use_rag: true
});
```

## 🔍 Troubleshooting

### Common Issues

1. **"YouTube Chat CLI not found"**
   ```bash
   pip install youtube-chat-cli
   ```

2. **"Permission denied"**
   ```bash
   chmod +x node_modules/.bin/jaegis-youtube-chat-mcp
   ```

3. **"API key not configured"**
   - Set required environment variables
   - Check `.env` file configuration

### Debug Mode

Run with debug output:
```bash
DEBUG=* npx jaegis-youtube-chat-mcp
```

## 🤝 Contributing

Contributions are welcome! Please see the [main repository](https://github.com/usemanusai/youtube-free-deep-research-cli) for contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [YouTube Chat CLI](https://pypi.org/project/youtube-chat-cli/) - The underlying Python CLI
- [Model Context Protocol](https://modelcontextprotocol.io/) - The MCP specification

## 📞 Support

- 🐛 [Report Issues](https://github.com/usemanusai/youtube-free-deep-research-cli/issues)
- 💬 [Discussions](https://github.com/usemanusai/youtube-free-deep-research-cli/discussions)
- 📧 Email: use.manus.ai@gmail.com

---

**Made with ❤️ by the JAEGIS Team**
