'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Terminal, Send, Sparkles, Command as CommandIcon, Loader2, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface TerminalMessage {
  id: string
  type: 'input' | 'output' | 'error' | 'success' | 'info'
  content: string
  timestamp: Date
  command?: string
}

interface CommandSuggestion {
  command: string
  description: string
  category: string
}

export function TerminalComponent() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<TerminalMessage[]>([
    {
      id: '1',
      type: 'info',
      content: 'JAEGIS NexusSync Terminal v1.0.0',
      timestamp: new Date(),
    },
    {
      id: '2',
      type: 'info',
      content: 'Type "help" for available commands or use natural language to describe what you want to do.',
      timestamp: new Date(),
    },
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [suggestions, setSuggestions] = useState<CommandSuggestion[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const { toast } = useToast()

  const availableCommands: CommandSuggestion[] = [
    { command: 'jaegis chat', description: 'Start interactive RAG chat session', category: 'Core' },
    { command: 'jaegis add-file [path]', description: 'Add file to knowledge base', category: 'Core' },
    { command: 'jaegis gdrive-sync', description: 'Sync Google Drive folder', category: 'Core' },
    { command: 'jaegis list-documents', description: 'List all documents in knowledge base', category: 'Core' },
    { command: 'jaegis search [query]', description: 'Search documents', category: 'Core' },
    { command: 'jaegis blueprint-create', description: 'Generate structured blueprint', category: 'Generation' },
    { command: 'jaegis podcast-create', description: 'Create podcast from content', category: 'Generation' },
    { command: 'jaegis summarize [path]', description: 'Generate document summary', category: 'Generation' },
    { command: 'jaegis status', description: 'Show system status', category: 'System' },
    { command: 'jaegis config', description: 'Show configuration', category: 'System' },
    { command: 'jaegis logs', description: 'Show system logs', category: 'System' },
    { command: 'jaegis restart', description: 'Restart background service', category: 'System' },
    { command: 'help', description: 'Show available commands', category: 'Help' },
    { command: 'clear', description: 'Clear terminal', category: 'Help' },
  ]

  useEffect(() => {
    // Auto-scroll to bottom when new messages are added
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  useEffect(() => {
    // Focus input when component mounts
    inputRef.current?.focus()
  }, [])

  const addMessage = (type: TerminalMessage['type'], content: string, command?: string) => {
    const newMessage: TerminalMessage = {
      id: Date.now().toString(),
      type,
      content,
      timestamp: new Date(),
      command,
    }
    setMessages(prev => [...prev, newMessage])
  }

  const executeCommand = async (command: string) => {
    setIsLoading(true)
    addMessage('input', `$ ${command}`, command)

    try {
      const response = await fetch('/api/terminal/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command }),
      })

      const result = await response.json()

      if (result.success) {
        addMessage('success', result.output || 'Command executed successfully')
      } else {
        addMessage('error', result.error || 'Command failed')
      }
    } catch (error) {
      addMessage('error', 'Failed to execute command. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const convertNaturalLanguage = async (input: string) => {
    setIsLoading(true)
    addMessage('input', `> ${input}`)

    try {
      const response = await fetch('/api/terminal/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input }),
      })

      const result = await response.json()

      if (result.success && result.command) {
        addMessage('info', `🤖 Converting: "${input}"`)
        addMessage('info', `📝 Suggested command: ${result.command}`)
        
        // Auto-execute the converted command
        await executeCommand(result.command)
      } else {
        addMessage('error', 'Failed to convert natural language to command')
      }
    } catch (error) {
      addMessage('error', 'Failed to process natural language input')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const trimmedInput = input.trim()
    setInput('')
    setShowSuggestions(false)

    // Check if it's a direct command or natural language
    if (trimmedInput.startsWith('jaegis ') || trimmedInput === 'help' || trimmedInput === 'clear') {
      await executeCommand(trimmedInput)
    } else {
      await convertNaturalLanguage(trimmedInput)
    }
  }

  const handleInputChange = (value: string) => {
    setInput(value)
    
    // Filter suggestions based on input
    if (value.length > 0) {
      const filtered = availableCommands.filter(cmd =>
        cmd.command.includes(value.toLowerCase()) ||
        cmd.description.toLowerCase().includes(value.toLowerCase())
      )
      setSuggestions(filtered.slice(0, 5))
      setShowSuggestions(true)
    } else {
      setShowSuggestions(false)
    }
  }

  const handleSuggestionClick = (suggestion: CommandSuggestion) => {
    setInput(suggestion.command)
    setShowSuggestions(false)
    inputRef.current?.focus()
  }

  const clearTerminal = () => {
    setMessages([
      {
        id: '1',
        type: 'info',
        content: 'Terminal cleared.',
        timestamp: new Date(),
      },
    ])
  }

  const getMessageIcon = (type: TerminalMessage['type']) => {
    switch (type) {
      case 'input':
        return <Terminal className="h-4 w-4" />
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'info':
        return <AlertCircle className="h-4 w-4 text-blue-500" />
      default:
        return null
    }
  }

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  }

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center">
            <Terminal className="h-5 w-5 mr-2" />
            JAEGIS Terminal
          </CardTitle>
          <div className="flex items-center space-x-2">
            <Badge variant="secondary" className="text-xs">
              Natural Language Enabled
            </Badge>
            <Button variant="outline" size="sm" onClick={clearTerminal}>
              Clear
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0">
        <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
          <div className="space-y-2 font-mono text-sm">
            {messages.map((message) => (
              <div key={message.id} className="flex items-start space-x-2">
                <div className="flex-shrink-0 mt-0.5">
                  {getMessageIcon(message.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-muted-foreground">
                      {formatTimestamp(message.timestamp)}
                    </span>
                    {message.command && (
                      <Badge variant="outline" className="text-xs">
                        {message.command}
                      </Badge>
                    )}
                  </div>
                  <div className={`mt-1 ${
                    message.type === 'error' ? 'text-red-500' :
                    message.type === 'success' ? 'text-green-500' :
                    message.type === 'info' ? 'text-blue-500' :
                    'text-foreground'
                  }`}>
                    {message.content}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex items-center space-x-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-muted-foreground">Processing...</span>
              </div>
            )}
          </div>
        </ScrollArea>

        <Separator />

        <div className="p-4">
          <form onSubmit={handleSubmit} className="relative">
            <div className="flex items-center space-x-2">
              <div className="relative flex-1">
                <Input
                  ref={inputRef}
                  value={input}
                  onChange={(e) => handleInputChange(e.target.value)}
                  placeholder="Enter command or describe what you want to do..."
                  className="font-mono"
                  disabled={isLoading}
                />
                
                {/* Suggestions dropdown */}
                {showSuggestions && suggestions.length > 0 && (
                  <div className="absolute top-full left-0 right-0 mt-1 bg-background border rounded-md shadow-lg z-10">
                    <div className="p-1">
                      {suggestions.map((suggestion, index) => (
                        <button
                          key={index}
                          type="button"
                          onClick={() => handleSuggestionClick(suggestion)}
                          className="w-full text-left px-3 py-2 hover:bg-muted rounded-sm text-sm"
                        >
                          <div className="font-mono">{suggestion.command}</div>
                          <div className="text-xs text-muted-foreground">{suggestion.description}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
            
            <div className="flex items-center space-x-2 mt-2">
              <Sparkles className="h-3 w-3 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">
                Try: "add the PDF file to my knowledge base" or "sync my Google Drive"
              </span>
            </div>
          </form>
        </div>
      </CardContent>
    </Card>
  )
}