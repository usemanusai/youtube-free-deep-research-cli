#!/usr/bin/env node

/**
 * JAEGIS YouTube Chat CLI - Model Context Protocol (MCP) Server
 *
 * This MCP server exposes all YouTube Chat CLI commands as tools for AI assistants.
 * It provides comprehensive functionality for YouTube video analysis, content processing,
 * podcast generation, channel monitoring, and more.
 */

import { spawn } from 'child_process';

// Simple MCP server implementation
const server = {
  name: 'jaegis-youtube-chat-mcp',
  version: '1.0.0',
  tools: [
    {
      name: 'jaegis_set_source',
      description: 'Set the active source URL and process its content',
      inputSchema: {
        type: 'object',
        properties: {
          url: { type: 'string', description: 'YouTube video URL or other content source URL' }
        },
        required: ['url']
      }
    },
    {
      name: 'jaegis_podcast_generate',
      description: 'Generate a podcast from YouTube video',
      inputSchema: {
        type: 'object',
        properties: {
          video_url: { type: 'string', description: 'YouTube video URL' },
          style: { type: 'string', default: 'conversational', description: 'Podcast style' },
          voice: { type: 'string', default: 'alloy', description: 'TTS voice' }
        },
        required: []
      }
    },
    {
      name: 'jaegis_ask',
      description: 'Ask a question to the n8n RAG workflow',
      inputSchema: {
        type: 'object',
        properties: {
          question: { type: 'string', description: 'Question to ask' }
        },
        required: ['question']
      }
    },
    {
      name: 'jaegis_channel_add',
      description: 'Add a YouTube channel for monitoring',
      inputSchema: {
        type: 'object',
        properties: {
          channel_url: { type: 'string', description: 'YouTube channel URL' },
          check_interval: { type: 'number', default: 24, description: 'Check interval in hours' }
        },
        required: ['channel_url']
      }
    },
    {
      name: 'jaegis_stats',
      description: 'Show monitoring and import statistics',
      inputSchema: {
        type: 'object',
        properties: {},
        required: []
      }
    }
  ]
};

// Execute CLI command
async function executeCLI(command: string, args: string[] = []): Promise<{ success: boolean; output: string; error: string | null }> {
  return new Promise((resolve) => {
    const child = spawn('youtube-chat', [command, ...args], { stdio: 'pipe' });

    let stdout = '';
    let stderr = '';

    child.stdout?.on('data', (data) => stdout += data.toString());
    child.stderr?.on('data', (data) => stderr += data.toString());

    child.on('close', (code) => {
      resolve({
        success: code === 0,
        output: stdout,
        error: code !== 0 ? stderr : null
      });
    });

    child.on('error', (error) => {
      resolve({
        success: false,
        output: '',
        error: error.message
      });
    });
  });
}

// Handle tool execution
async function handleToolCall(toolName: string, args: any) {
  try {
    let result;

    switch (toolName) {
      case 'jaegis_set_source':
        result = await executeCLI('set-source', [args.url]);
        break;
      case 'jaegis_podcast_generate':
        const podcastArgs = [];
        if (args.video_url) podcastArgs.push(args.video_url);
        if (args.style) podcastArgs.push('--style', args.style);
        if (args.voice) podcastArgs.push('--voice', args.voice);
        result = await executeCLI('podcast', podcastArgs);
        break;
      case 'jaegis_ask':
        result = await executeCLI('ask', [args.question]);
        break;
      case 'jaegis_channel_add':
        const channelArgs = [args.channel_url];
        if (args.check_interval) channelArgs.push('--check-interval', args.check_interval.toString());
        result = await executeCLI('channel', ['add', ...channelArgs]);
        break;
      case 'jaegis_stats':
        result = await executeCLI('stats');
        break;
      default:
        throw new Error(`Unknown tool: ${toolName}`);
    }

    return {
      content: [{
        type: 'text',
        text: result.success ? `✅ ${result.output}` : `❌ ${result.error || 'Command failed'}`
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: `❌ Error: ${error instanceof Error ? error.message : String(error)}`
      }]
    };
  }
}

// Simple stdio-based MCP server
function startServer() {
  console.error('🎙️ JAEGIS YouTube Chat MCP Server started');

  process.stdin.on('data', async (data) => {
    try {
      const request = JSON.parse(data.toString());
      let response;

      if (request.method === 'tools/list') {
        response = {
          jsonrpc: '2.0',
          id: request.id,
          result: { tools: server.tools }
        };
      } else if (request.method === 'tools/call') {
        const { name, arguments: args } = request.params;
        const result = await handleToolCall(name, args || {});
        response = {
          jsonrpc: '2.0',
          id: request.id,
          result
        };
      } else {
        response = {
          jsonrpc: '2.0',
          id: request.id,
          error: { code: -32601, message: 'Method not found' }
        };
      }

      process.stdout.write(JSON.stringify(response) + '\n');
    } catch (error) {
      const response = {
        jsonrpc: '2.0',
        id: null,
        error: { code: -32700, message: 'Parse error' }
      };
      process.stdout.write(JSON.stringify(response) + '\n');
    }
  });
}

// Start the server
startServer();

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.error('\n👋 JAEGIS YouTube Chat MCP Server shutting down...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.error('\n👋 JAEGIS YouTube Chat MCP Server shutting down...');
  process.exit(0);
});
