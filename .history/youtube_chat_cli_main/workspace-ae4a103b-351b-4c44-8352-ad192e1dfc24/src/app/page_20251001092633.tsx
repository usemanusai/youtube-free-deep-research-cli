'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Settings, Terminal, Command, Database, Cloud, FileText, BarChart3, Zap } from 'lucide-react'
import { SettingsPanel } from '@/components/settings-panel'
import { TerminalComponent } from '@/components/terminal'
import { CommandPalette } from '@/components/command-palette'
import { SystemStatus } from '@/components/system-status'

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    const handleNavigate = (event: CustomEvent) => {
      setActiveTab(event.detail)
    }

    window.addEventListener('navigate-to-tab', handleNavigate as EventListener)
    return () => {
      window.removeEventListener('navigate-to-tab', handleNavigate as EventListener)
    }
  }, [])

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <img
                  src="/jaegis-logo.png"
                  alt="JAEGIS NexusSync"
                  className="h-8 w-8 rounded"
                />
                <h1 className="text-2xl font-bold">JAEGIS NexusSync</h1>
              </div>
              <span className="text-sm text-muted-foreground">Adaptive RAG Service Dashboard</span>
            </div>
            <div className="flex items-center space-x-2">
              <CommandPalette />
              <Button variant="outline" size="sm">
                <Command className="h-4 w-4 mr-2" />
                Commands
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="terminal">Terminal</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
            <TabsTrigger value="commands">Commands</TabsTrigger>
            <TabsTrigger value="status">System Status</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Documents Processed</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">1,234</div>
                  <p className="text-xs text-muted-foreground">+12% from last month</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">RAG Queries</CardTitle>
                  <Database className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">5,678</div>
                  <p className="text-xs text-muted-foreground">+23% from last month</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">API Calls</CardTitle>
                  <Cloud className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">89,012</div>
                  <p className="text-xs text-muted-foreground">+8% from last month</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">98.5%</div>
                  <p className="text-xs text-muted-foreground">+2% from last month</p>
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                  <CardDescription>Latest system events and operations</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-4">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">Google Drive sync completed</p>
                        <p className="text-xs text-muted-foreground">2 minutes ago</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">New documents processed</p>
                        <p className="text-xs text-muted-foreground">15 minutes ago</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">RAG pipeline updated</p>
                        <p className="text-xs text-muted-foreground">1 hour ago</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                  <CardDescription>Common tasks and operations</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-2">
                    <Button variant="outline" className="justify-start">
                      <FileText className="h-4 w-4 mr-2" />
                      Add Document to Knowledge Base
                    </Button>
                    <Button variant="outline" className="justify-start">
                      <Database className="h-4 w-4 mr-2" />
                      Run RAG Query
                    </Button>
                    <Button variant="outline" className="justify-start">
                      <Cloud className="h-4 w-4 mr-2" />
                      Sync Google Drive
                    </Button>
                    <Button variant="outline" className="justify-start">
                      <Terminal className="h-4 w-4 mr-2" />
                      Open Terminal
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Terminal Tab */}
          <TabsContent value="terminal">
            <TerminalComponent />
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings">
            <SettingsPanel />
          </TabsContent>

          {/* Commands Tab */}
          <TabsContent value="commands" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Available Commands</CardTitle>
                <CardDescription>Complete list of JAEGIS NexusSync CLI commands</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <h3 className="font-semibold">Core Commands</h3>
                      <div className="space-y-1 text-sm">
                        <div className="p-2 bg-muted rounded">
                          <code className="text-xs">jaegis chat</code>
                          <p className="text-muted-foreground">Start interactive RAG chat session</p>
                        </div>
                        <div className="p-2 bg-muted rounded">
                          <code className="text-xs">jaegis add-file [path]</code>
                          <p className="text-muted-foreground">Add file to knowledge base</p>
                        </div>
                        <div className="p-2 bg-muted rounded">
                          <code className="text-xs">jaegis gdrive-sync</code>
                          <p className="text-muted-foreground">Sync Google Drive folder</p>
                        </div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <h3 className="font-semibold">Content Generation</h3>
                      <div className="space-y-1 text-sm">
                        <div className="p-2 bg-muted rounded">
                          <code className="text-xs">jaegis blueprint-create</code>
                          <p className="text-muted-foreground">Generate structured blueprint</p>
                        </div>
                        <div className="p-2 bg-muted rounded">
                          <code className="text-xs">jaegis podcast-create</code>
                          <p className="text-muted-foreground">Create podcast from content</p>
                        </div>
                        <div className="p-2 bg-muted rounded">
                          <code className="text-xs">jaegis summarize</code>
                          <p className="text-muted-foreground">Generate document summary</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* System Status Tab */}
          <TabsContent value="status">
            <SystemStatus />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}