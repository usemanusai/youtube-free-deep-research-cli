'use client'

import { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { MessageSquare, Send, Loader2, Globe, RefreshCw, User, Bot, FileText } from 'lucide-react'
import { useChatQuery, useCreateChatSession } from '@/hooks/use-api'
import { toast } from 'sonner'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  metadata?: {
    web_search_used?: boolean
    transform_count?: number
    documents?: Array<{
      content: string
      metadata: Record<string, any>
      score?: number
    }>
  }
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your JAEGIS NexusSync RAG assistant. Ask me anything about your knowledge base!',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const chatQuery = useChatQuery()
  const createSession = useCreateChatSession()

  useEffect(() => {
    // Create a new chat session on mount
    createSession.mutate(undefined, {
      onSuccess: (data) => {
        setSessionId(data.session_id)
      },
    })
  }, [])

  useEffect(() => {
    // Auto-scroll to bottom when new messages are added
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || chatQuery.isPending) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')

    // Query the RAG engine
    chatQuery.mutate(
      {
        question: userMessage.content,
        session_id: sessionId || undefined,
      },
      {
        onSuccess: (data) => {
          const assistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: data.answer,
            timestamp: new Date(),
            metadata: {
              web_search_used: data.web_search_used,
              transform_count: data.transform_count,
              documents: data.documents,
            },
          }
          setMessages(prev => [...prev, assistantMessage])
        },
        onError: (error: any) => {
          const errorMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: `Sorry, I encountered an error: ${error.response?.data?.detail || error.message}`,
            timestamp: new Date(),
          }
          setMessages(prev => [...prev, errorMessage])
        },
      }
    )
  }

  const handleNewSession = () => {
    createSession.mutate(undefined, {
      onSuccess: (data) => {
        setSessionId(data.session_id)
        setMessages([
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: 'New session started! How can I help you?',
            timestamp: new Date(),
          },
        ])
        toast.success('New chat session created')
      },
    })
  }

  return (
    <Card className="h-[calc(100vh-12rem)]">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              RAG Chat
            </CardTitle>
            <CardDescription>
              Ask questions and get answers from your knowledge base
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleNewSession}
            disabled={createSession.isPending}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${createSession.isPending ? 'animate-spin' : ''}`} />
            New Session
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex flex-col h-[calc(100%-5rem)]">
        {/* Messages Area */}
        <ScrollArea className="flex-1 pr-4" ref={scrollAreaRef}>
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                  </div>
                )}
                
                <div
                  className={`flex flex-col gap-2 max-w-[80%] ${
                    message.role === 'user' ? 'items-end' : 'items-start'
                  }`}
                >
                  <div
                    className={`rounded-lg px-4 py-2 ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>
                  
                  {/* Metadata badges */}
                  {message.metadata && (
                    <div className="flex gap-2 flex-wrap">
                      {message.metadata.web_search_used && (
                        <Badge variant="secondary" className="text-xs">
                          <Globe className="h-3 w-3 mr-1" />
                          Web Search
                        </Badge>
                      )}
                      {message.metadata.transform_count && message.metadata.transform_count > 0 && (
                        <Badge variant="secondary" className="text-xs">
                          <RefreshCw className="h-3 w-3 mr-1" />
                          Query Transformed {message.metadata.transform_count}x
                        </Badge>
                      )}
                      {message.metadata.documents && message.metadata.documents.length > 0 && (
                        <Badge variant="secondary" className="text-xs">
                          <FileText className="h-3 w-3 mr-1" />
                          {message.metadata.documents.length} Sources
                        </Badge>
                      )}
                    </div>
                  )}
                  
                  <span className="text-xs text-muted-foreground">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                </div>

                {message.role === 'user' && (
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                      <User className="h-4 w-4 text-primary-foreground" />
                    </div>
                  </div>
                )}
              </div>
            ))}
            
            {/* Loading indicator */}
            {chatQuery.isPending && (
              <div className="flex gap-3 justify-start">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                </div>
                <div className="bg-muted rounded-lg px-4 py-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <Separator className="my-4" />

        {/* Input Area */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={chatQuery.isPending}
            className="flex-1"
          />
          <Button
            type="submit"
            disabled={!input.trim() || chatQuery.isPending}
            size="icon"
          >
            {chatQuery.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

