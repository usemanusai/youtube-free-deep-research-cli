'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Save, Download, Upload, Eye, EyeOff, Key, Database, Cloud, Shield } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

export function SettingsPanel() {
  const [showSecrets, setShowSecrets] = useState(false)
  const [settings, setSettings] = useState({
    // API Keys
    openaiApiKey: '',
    googleApiKey: '',
    tavilyApiKey: '',
    ollamaBaseUrl: 'http://localhost:11434',
    
    // Google Drive
    googleDriveClientId: '',
    googleDriveClientSecret: '',
    googleDriveFolderId: '',
    
    // Vector Store
    vectorStore: 'qdrant',
    qdrantUrl: 'http://localhost:6333',
    qdrantApiKey: '',
    chromaPath: './chroma_db',
    
    // LLM Settings
    defaultModel: 'gpt-4',
    temperature: 0.7,
    maxTokens: 4000,
    
    // RAG Settings
    chunkSize: 1000,
    chunkOverlap: 200,
    embeddingModel: 'text-embedding-ada-002',
    
    // Background Service
    enableBackgroundSync: true,
    syncInterval: 300, // seconds
    
    // MCP Settings
    enableMCP: true,
    mcpPort: 3001,
  })

  const { toast } = useToast()

  const handleSave = async () => {
    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      })
      
      if (response.ok) {
        toast({
          title: "Settings saved",
          description: "Your configuration has been updated successfully.",
        })
      } else {
        throw new Error('Failed to save settings')
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save settings. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleExport = () => {
    const dataStr = JSON.stringify(settings, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    const exportFileDefaultName = 'jaegis-settings.json'
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const imported = JSON.parse(e.target?.result as string)
          setSettings({ ...settings, ...imported })
          toast({
            title: "Settings imported",
            description: "Configuration has been imported successfully.",
          })
        } catch (error) {
          toast({
            title: "Import failed",
            description: "Invalid settings file format.",
            variant: "destructive",
          })
        }
      }
      reader.readAsText(file)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Settings</h2>
          <p className="text-muted-foreground">Configure your JAEGIS NexusSync environment</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" onClick={() => document.getElementById('import-settings')?.click()}>
            <Upload className="h-4 w-4 mr-2" />
            Import
          </Button>
          <input
            id="import-settings"
            type="file"
            accept=".json"
            className="hidden"
            onChange={handleImport}
          />
          <Button onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" />
            Save Settings
          </Button>
        </div>
      </div>

      <Tabs defaultValue="api-keys" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="api-keys">API Keys</TabsTrigger>
          <TabsTrigger value="google-drive">Google Drive</TabsTrigger>
          <TabsTrigger value="vector-store">Vector Store</TabsTrigger>
          <TabsTrigger value="llm">LLM Settings</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
        </TabsList>

        {/* API Keys Tab */}
        <TabsContent value="api-keys">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Key className="h-5 w-5 mr-2" />
                API Keys Configuration
              </CardTitle>
              <CardDescription>
                Configure your API keys for external services
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center space-x-2">
                <Switch
                  checked={showSecrets}
                  onCheckedChange={setShowSecrets}
                />
                <Label>Show API keys</Label>
              </div>

              <div className="grid gap-4">
                <div className="space-y-2">
                  <Label htmlFor="openai-key">OpenAI API Key</Label>
                  <div className="relative">
                    <Input
                      id="openai-key"
                      type={showSecrets ? "text" : "password"}
                      placeholder="sk-..."
                      value={settings.openaiApiKey}
                      onChange={(e) => setSettings({ ...settings, openaiApiKey: e.target.value })}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                      onClick={() => setShowSecrets(!showSecrets)}
                    >
                      {showSecrets ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="google-key">Google API Key</Label>
                  <Input
                    id="google-key"
                    type={showSecrets ? "text" : "password"}
                    placeholder="AIza..."
                    value={settings.googleApiKey}
                    onChange={(e) => setSettings({ ...settings, googleApiKey: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="tavily-key">Tavily Search API Key</Label>
                  <Input
                    id="tavily-key"
                    type={showSecrets ? "text" : "password"}
                    placeholder="tvly-..."
                    value={settings.tavilyApiKey}
                    onChange={(e) => setSettings({ ...settings, tavilyApiKey: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="ollama-url">Ollama Base URL</Label>
                  <Input
                    id="ollama-url"
                    value={settings.ollamaBaseUrl}
                    onChange={(e) => setSettings({ ...settings, ollamaBaseUrl: e.target.value })}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Google Drive Tab */}
        <TabsContent value="google-drive">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Cloud className="h-5 w-5 mr-2" />
                Google Drive Integration
              </CardTitle>
              <CardDescription>
                Configure OAuth 2.0 credentials and folder monitoring
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <Alert>
                <Shield className="h-4 w-4" />
                <AlertDescription>
                  Create OAuth 2.0 credentials in Google Cloud Console with Drive API enabled.
                  Use scopes: drive.file or drive.readonly for minimal access.
                </AlertDescription>
              </Alert>

              <div className="grid gap-4">
                <div className="space-y-2">
                  <Label htmlFor="gdrive-client-id">Client ID</Label>
                  <Input
                    id="gdrive-client-id"
                    value={settings.googleDriveClientId}
                    onChange={(e) => setSettings({ ...settings, googleDriveClientId: e.target.value })}
                    placeholder="your-client-id.apps.googleusercontent.com"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="gdrive-client-secret">Client Secret</Label>
                  <Input
                    id="gdrive-client-secret"
                    type={showSecrets ? "text" : "password"}
                    value={settings.googleDriveClientSecret}
                    onChange={(e) => setSettings({ ...settings, googleDriveClientSecret: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="gdrive-folder-id">Folder ID (Optional)</Label>
                  <Input
                    id="gdrive-folder-id"
                    value={settings.googleDriveFolderId}
                    onChange={(e) => setSettings({ ...settings, googleDriveFolderId: e.target.value })}
                    placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
                  />
                  <p className="text-sm text-muted-foreground">
                    Leave empty to monitor entire Drive or specify a folder ID
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Vector Store Tab */}
        <TabsContent value="vector-store">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Database className="h-5 w-5 mr-2" />
                Vector Store Configuration
              </CardTitle>
              <CardDescription>
                Configure your vector database for document storage
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Vector Store Provider</Label>
                <Select
                  value={settings.vectorStore}
                  onValueChange={(value) => setSettings({ ...settings, vectorStore: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="qdrant">Qdrant</SelectItem>
                    <SelectItem value="chroma">Chroma</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {settings.vectorStore === 'qdrant' && (
                <div className="grid gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="qdrant-url">Qdrant URL</Label>
                    <Input
                      id="qdrant-url"
                      value={settings.qdrantUrl}
                      onChange={(e) => setSettings({ ...settings, qdrantUrl: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="qdrant-api-key">API Key (Optional)</Label>
                    <Input
                      id="qdrant-api-key"
                      type={showSecrets ? "text" : "password"}
                      value={settings.qdrantApiKey}
                      onChange={(e) => setSettings({ ...settings, qdrantApiKey: e.target.value })}
                    />
                  </div>
                </div>
              )}

              {settings.vectorStore === 'chroma' && (
                <div className="space-y-2">
                  <Label htmlFor="chroma-path">Chroma DB Path</Label>
                  <Input
                    id="chroma-path"
                    value={settings.chromaPath}
                    onChange={(e) => setSettings({ ...settings, chromaPath: e.target.value })}
                  />
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* LLM Settings Tab */}
        <TabsContent value="llm">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Language Model Settings</CardTitle>
                <CardDescription>Configure LLM parameters and behavior</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="default-model">Default Model</Label>
                  <Select
                    value={settings.defaultModel}
                    onValueChange={(value) => setSettings({ ...settings, defaultModel: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gpt-4">GPT-4</SelectItem>
                      <SelectItem value="gpt-4-turbo">GPT-4 Turbo</SelectItem>
                      <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                      <SelectItem value="llama2">Llama 2 (Ollama)</SelectItem>
                      <SelectItem value="mistral">Mistral (Ollama)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="temperature">Temperature</Label>
                    <Input
                      id="temperature"
                      type="number"
                      min="0"
                      max="2"
                      step="0.1"
                      value={settings.temperature}
                      onChange={(e) => setSettings({ ...settings, temperature: parseFloat(e.target.value) })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="max-tokens">Max Tokens</Label>
                    <Input
                      id="max-tokens"
                      type="number"
                      min="100"
                      max="8000"
                      step="100"
                      value={settings.maxTokens}
                      onChange={(e) => setSettings({ ...settings, maxTokens: parseInt(e.target.value) })}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>RAG Configuration</CardTitle>
                <CardDescription>Configure document processing and retrieval settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="chunk-size">Chunk Size</Label>
                    <Input
                      id="chunk-size"
                      type="number"
                      min="100"
                      max="4000"
                      step="100"
                      value={settings.chunkSize}
                      onChange={(e) => setSettings({ ...settings, chunkSize: parseInt(e.target.value) })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="chunk-overlap">Chunk Overlap</Label>
                    <Input
                      id="chunk-overlap"
                      type="number"
                      min="0"
                      max="1000"
                      step="50"
                      value={settings.chunkOverlap}
                      onChange={(e) => setSettings({ ...settings, chunkOverlap: parseInt(e.target.value) })}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="embedding-model">Embedding Model</Label>
                  <Select
                    value={settings.embeddingModel}
                    onValueChange={(value) => setSettings({ ...settings, embeddingModel: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="text-embedding-ada-002">text-embedding-ada-002</SelectItem>
                      <SelectItem value="text-embedding-3-small">text-embedding-3-small</SelectItem>
                      <SelectItem value="text-embedding-3-large">text-embedding-3-large</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Advanced Tab */}
        <TabsContent value="advanced">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Background Service</CardTitle>
                <CardDescription>Configure automated synchronization and monitoring</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Enable Background Sync</Label>
                    <p className="text-sm text-muted-foreground">
                      Automatically sync Google Drive in the background
                    </p>
                  </div>
                  <Switch
                    checked={settings.enableBackgroundSync}
                    onCheckedChange={(checked) => setSettings({ ...settings, enableBackgroundSync: checked })}
                  />
                </div>

                {settings.enableBackgroundSync && (
                  <div className="space-y-2">
                    <Label htmlFor="sync-interval">Sync Interval (seconds)</Label>
                    <Input
                      id="sync-interval"
                      type="number"
                      min="60"
                      max="3600"
                      step="60"
                      value={settings.syncInterval}
                      onChange={(e) => setSettings({ ...settings, syncInterval: parseInt(e.target.value) })}
                    />
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>MCP Server</CardTitle>
                <CardDescription>Configure Model Context Protocol server settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Enable MCP Server</Label>
                    <p className="text-sm text-muted-foreground">
                      Expose CLI tools via MCP protocol
                    </p>
                  </div>
                  <Switch
                    checked={settings.enableMCP}
                    onCheckedChange={(checked) => setSettings({ ...settings, enableMCP: checked })}
                  />
                </div>

                {settings.enableMCP && (
                  <div className="space-y-2">
                    <Label htmlFor="mcp-port">MCP Server Port</Label>
                    <Input
                      id="mcp-port"
                      type="number"
                      min="1000"
                      max="9999"
                      value={settings.mcpPort}
                      onChange={(e) => setSettings({ ...settings, mcpPort: parseInt(e.target.value) })}
                    />
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}