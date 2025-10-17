import { NextRequest, NextResponse } from 'next/server'
import ZAI from 'z-ai-web-dev-sdk'

// Natural language to command mapping patterns
const commandPatterns: Array<{
  pattern: RegExp
  command: string
  description: string
}> = [
  {
    pattern: /(?:add|upload|ingest).*?(?:pdf|document|file)/i,
    command: 'jaegis add-file',
    description: 'Add file to knowledge base',
  },
  {
    pattern: /(?:sync|synchronize).*(?:google|drive|gdrive)/i,
    command: 'jaegis gdrive-sync',
    description: 'Sync Google Drive folder',
  },
  {
    pattern: /(?:search|find|look for).*(?:document|file|info)/i,
    command: 'jaegis search',
    description: 'Search documents',
  },
  {
    pattern: /(?:list|show).*(?:document|file)/i,
    command: 'jaegis list-documents',
    description: 'List all documents',
  },
  {
    pattern: /(?:chat|talk|ask|question)/i,
    command: 'jaegis chat',
    description: 'Start interactive chat',
  },
  {
    pattern: /(?:status|health|check)/i,
    command: 'jaegis status',
    description: 'Show system status',
  },
  {
    pattern: /(?:summarize|summary).*(?:document|file)/i,
    command: 'jaegis summarize',
    description: 'Generate document summary',
  },
  {
    pattern: /(?:blueprint|outline|structure)/i,
    command: 'jaegis blueprint-create',
    description: 'Generate structured blueprint',
  },
  {
    pattern: /(?:podcast|audio)/i,
    command: 'jaegis podcast-create',
    description: 'Create podcast from content',
  },
  {
    pattern: /(?:config|configuration|settings)/i,
    command: 'jaegis config',
    description: 'Show configuration',
  },
  {
    pattern: /(?:logs|log)/i,
    command: 'jaegis logs',
    description: 'Show system logs',
  },
  {
    pattern: /(?:restart|reboot)/i,
    command: 'jaegis restart',
    description: 'Restart background service',
  },
  {
    pattern: /(?:help|commands|what can i do)/i,
    command: 'help',
    description: 'Show available commands',
  },
  {
    pattern: /(?:clear|clean)/i,
    command: 'clear',
    description: 'Clear terminal',
  },
]

export async function POST(request: NextRequest) {
  try {
    const { input } = await request.json()

    if (!input) {
      return NextResponse.json(
        { error: 'Input is required' },
        { status: 400 }
      )
    }

    // First try pattern matching for common commands
    for (const { pattern, command, description } of commandPatterns) {
      if (pattern.test(input)) {
        // Extract any additional parameters from the input
        let finalCommand = command
        
        // Handle specific parameter extraction
        if (command === 'jaegis add-file') {
          const fileMatch = input.match(/(?:add|upload|ingest)\s+(?:the\s+)?(?:file\s+)?["']?([^"'\s]+)["']?/i)
          if (fileMatch) {
            finalCommand += ` ${fileMatch[1]}`
          }
        }
        
        if (command === 'jaegis search') {
          const searchMatch = input.match(/(?:search|find|look for)\s+(?:for\s+)?(?:documents?\s+)?(?:about\s+)?["']?([^"'\.]+)["']?/i)
          if (searchMatch) {
            finalCommand += ` ${searchMatch[1]}`
          }
        }
        
        if (command === 'jaegis summarize') {
          const fileMatch = input.match(/(?:summarize|summary)\s+(?:the\s+)?(?:file\s+)?["']?([^"'\s]+)["']?/i)
          if (fileMatch) {
            finalCommand += ` ${fileMatch[1]}`
          }
        }

        return NextResponse.json({
          success: true,
          command: finalCommand,
          description,
          method: 'pattern-match',
        })
      }
    }

    // If no pattern matches, use AI to convert
    try {
      const zai = await ZAI.create()
      
      const completion = await zai.chat.completions.create({
        messages: [
          {
            role: 'system',
            content: `You are a command converter for JAEGIS NexusSync CLI. Convert natural language input into specific CLI commands.

Available commands:
- jaegis chat: Start interactive RAG chat session
- jaegis add-file [path]: Add file to knowledge base
- jaegis gdrive-sync: Sync Google Drive folder
- jaegis list-documents: List all documents in knowledge base
- jaegis search [query]: Search documents
- jaegis blueprint-create: Generate structured blueprint
- jaegis podcast-create: Create podcast from content
- jaegis summarize [path]: Generate document summary
- jaegis status: Show system status
- jaegis config: Show configuration
- jaegis logs: Show system logs
- jaegis restart: Restart background service
- help: Show available commands
- clear: Clear terminal

Rules:
1. Only return the command, nothing else
2. If the input doesn't match any available command, return "help"
3. Extract file paths or search queries when mentioned
4. Be conservative - if unsure, default to "help"

Examples:
Input: "I want to add a PDF file"
Output: "jaegis add-file"

Input: "sync my google drive"
Output: "jaegis gdrive-sync"

Input: "search for documents about AI"
Output: "jaegis search AI"

Input: "what's the system status"
Output: "jaegis status"`
          },
          {
            role: 'user',
            content: input
          }
        ],
        temperature: 0.1,
        max_tokens: 50,
      })

      const suggestedCommand = completion.choices[0]?.message?.content?.trim()
      
      if (suggestedCommand) {
        return NextResponse.json({
          success: true,
          command: suggestedCommand,
          description: getCommandDescription(suggestedCommand),
          method: 'ai-conversion',
        })
      }
    } catch (aiError) {
      console.error('AI conversion failed:', aiError)
    }

    // Fallback to help if no conversion found
    return NextResponse.json({
      success: true,
      command: 'help',
      description: 'Show available commands',
      method: 'fallback',
    })

  } catch (error) {
    console.error('Natural language conversion error:', error)
    return NextResponse.json(
      { error: 'Failed to convert natural language to command' },
      { status: 500 }
    )
  }
}

function getCommandDescription(command: string): string {
  const descriptions: Record<string, string> = {
    'jaegis chat': 'Start interactive RAG chat session',
    'jaegis add-file': 'Add file to knowledge base',
    'jaegis gdrive-sync': 'Sync Google Drive folder',
    'jaegis list-documents': 'List all documents in knowledge base',
    'jaegis search': 'Search documents',
    'jaegis blueprint-create': 'Generate structured blueprint',
    'jaegis podcast-create': 'Create podcast from content',
    'jaegis summarize': 'Generate document summary',
    'jaegis status': 'Show system status',
    'jaegis config': 'Show configuration',
    'jaegis logs': 'Show system logs',
    'jaegis restart': 'Restart background service',
    'help': 'Show available commands',
    'clear': 'Clear terminal',
  }
  
  return descriptions[command] || 'Execute command'
}