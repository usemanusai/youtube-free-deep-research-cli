'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Command as CommandIcon, Search, FileText, Database, Cloud, Settings, Terminal, Zap } from 'lucide-react'

interface CommandItem {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  action: () => void
  category: string
  shortcut?: string
}

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')

  const commands: CommandItem[] = [
    {
      id: 'terminal',
      title: 'Open Terminal',
      description: 'Launch the command terminal',
      icon: <Terminal className="h-4 w-4" />,
      action: () => {
        // Navigate to terminal tab
        const event = new CustomEvent('navigate-to-tab', { detail: 'terminal' })
        window.dispatchEvent(event)
        setOpen(false)
      },
      category: 'Navigation',
      shortcut: '⌘T',
    },
    {
      id: 'settings',
      title: 'Open Settings',
      description: 'Configure application settings',
      icon: <Settings className="h-4 w-4" />,
      action: () => {
        const event = new CustomEvent('navigate-to-tab', { detail: 'settings' })
        window.dispatchEvent(event)
        setOpen(false)
      },
      category: 'Navigation',
      shortcut: '⌘,',
    },
    {
      id: 'add-file',
      title: 'Add File',
      description: 'Add a file to the knowledge base',
      icon: <FileText className="h-4 w-4" />,
      action: () => {
        // Trigger file add action
        setOpen(false)
      },
      category: 'Actions',
    },
    {
      id: 'sync-gdrive',
      title: 'Sync Google Drive',
      description: 'Synchronize Google Drive folder',
      icon: <Cloud className="h-4 w-4" />,
      action: () => {
        // Trigger sync action
        setOpen(false)
      },
      category: 'Actions',
    },
    {
      id: 'search-docs',
      title: 'Search Documents',
      description: 'Search through your knowledge base',
      icon: <Search className="h-4 w-4" />,
      action: () => {
        // Trigger search action
        setOpen(false)
      },
      category: 'Actions',
    },
    {
      id: 'status',
      title: 'System Status',
      description: 'View system status and metrics',
      icon: <Database className="h-4 w-4" />,
      action: () => {
        const event = new CustomEvent('navigate-to-tab', { detail: 'status' })
        window.dispatchEvent(event)
        setOpen(false)
      },
      category: 'Navigation',
    },
    {
      id: 'chat',
      title: 'Start Chat',
      description: 'Begin a new RAG chat session',
      icon: <Zap className="h-4 w-4" />,
      action: () => {
        // Trigger chat action
        setOpen(false)
      },
      category: 'Actions',
    },
  ]

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }

    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [])

  const filteredCommands = commands.filter(command =>
    command.title.toLowerCase().includes(search.toLowerCase()) ||
    command.description.toLowerCase().includes(search.toLowerCase()) ||
    command.category.toLowerCase().includes(search.toLowerCase())
  )

  const groupedCommands = filteredCommands.reduce((groups, command) => {
    if (!groups[command.category]) {
      groups[command.category] = []
    }
    groups[command.category].push(command)
    return groups
  }, {} as Record<string, CommandItem[]>)

  return (
    <>
      <Button
        variant="outline"
        onClick={() => setOpen(true)}
        className="relative w-full justify-start text-sm text-muted-foreground sm:pr-12 md:w-40 lg:w-64"
      >
        <Search className="mr-2 h-4 w-4" />
        <span className="hidden lg:inline-flex">Search commands...</span>
        <span className="inline-flex lg:hidden">Search...</span>
        <kbd className="pointer-events-none absolute right-1.5 top-2.5 hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex">
          <span className="text-xs">⌘</span>K
        </kbd>
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="p-0">
          <DialogHeader className="border-b px-4 pb-4 pt-5">
            <DialogTitle className="text-left">Command Palette</DialogTitle>
          </DialogHeader>
          <Command className="rounded-lg border shadow-md">
            <div className="flex items-center border-b px-3">
              <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
              <CommandInput
                placeholder="Type a command or search..."
                value={search}
                onValueChange={setSearch}
                className="border-0 focus:ring-0"
              />
            </div>
            <CommandList className="max-h-[450px]">
              <CommandEmpty>No commands found.</CommandEmpty>
              {Object.entries(groupedCommands).map(([category, categoryCommands]) => (
                <CommandGroup key={category} heading={category}>
                  {categoryCommands.map((command) => (
                    <CommandItem
                      key={command.id}
                      onSelect={() => command.action()}
                      className="flex items-center gap-2 px-4 py-2"
                    >
                      {command.icon}
                      <div className="flex-1">
                        <div className="font-medium">{command.title}</div>
                        <div className="text-sm text-muted-foreground">
                          {command.description}
                        </div>
                      </div>
                      {command.shortcut && (
                        <Badge variant="secondary" className="text-xs">
                          {command.shortcut}
                        </Badge>
                      )}
                    </CommandItem>
                  ))}
                </CommandGroup>
              ))}
            </CommandList>
          </Command>
        </DialogContent>
      </Dialog>
    </>
  )
}