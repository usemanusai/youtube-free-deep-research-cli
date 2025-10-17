'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Activity,
  Database,
  Cloud,
  Server,
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw,
  Zap,
  FileText,
  Clock,
  TrendingUp
} from 'lucide-react'
import { useSystemStatus, useSystemVerify } from '@/hooks/use-api'
import { Skeleton } from '@/components/ui/skeleton'

interface ServiceStatus {
  name: string
  status: 'healthy' | 'unhealthy' | 'warning' | 'unknown' | 'error' | 'ok' | 'running' | 'stopped'
  lastCheck: Date
  responseTime?: number
  error?: string
  type?: string
  running?: boolean
}

interface SystemMetrics {
  cpuUsage: number
  memoryUsage: number
  diskUsage: number
  activeConnections: number
  documentsProcessed: number
  queriesServed: number
  uptime: number
}

export function SystemStatus() {
  const { data: systemStatus, isLoading, refetch } = useSystemStatus()
  const { data: verifyData, refetch: refetchVerify } = useSystemVerify({ enabled: false })
  const [isRefreshing, setIsRefreshing] = useState(false)

  const [metrics, setMetrics] = useState<SystemMetrics>({
    cpuUsage: 25,
    memoryUsage: 68,
    diskUsage: 42,
    activeConnections: 12,
    documentsProcessed: 1234,
    queriesServed: 5678,
    uptime: 86400, // 24 hours in seconds
  })

  const [isRefreshing, setIsRefreshing] = useState(false)

  const refreshStatus = async () => {
    setIsRefreshing(true)
    try {
      // Simulate API call to refresh status
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Update last check times
      setServices(prev => prev.map(service => ({
        ...service,
        lastCheck: new Date(),
        responseTime: Math.floor(Math.random() * 300) + 10,
      })))
      
      // Update metrics
      setMetrics(prev => ({
        ...prev,
        cpuUsage: Math.floor(Math.random() * 30) + 10,
        memoryUsage: Math.floor(Math.random() * 40) + 50,
        activeConnections: Math.floor(Math.random() * 20) + 5,
      }))
    } catch (error) {
      console.error('Failed to refresh status:', error)
    } finally {
      setIsRefreshing(false)
    }
  }

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`
    } else {
      return `${minutes}m`
    }
  }

  const getStatusIcon = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'unhealthy':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />
    }
  }

  const getStatusBadge = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'healthy':
        return <Badge variant="default" className="bg-green-500">Healthy</Badge>
      case 'unhealthy':
        return <Badge variant="destructive">Unhealthy</Badge>
      case 'warning':
        return <Badge variant="secondary" className="bg-yellow-500 text-yellow-900">Warning</Badge>
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">System Status</h2>
          <p className="text-muted-foreground">Monitor your JAEGIS NexusSync system health and performance</p>
        </div>
        <Button onClick={refreshStatus} disabled={isRefreshing}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
          <TabsTrigger value="logs">Recent Logs</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatUptime(metrics.uptime)}</div>
                <p className="text-xs text-muted-foreground">Since last restart</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Services</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {services.filter(s => s.status === 'healthy').length}/{services.length}
                </div>
                <p className="text-xs text-muted-foreground">Services running</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Documents</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.documentsProcessed.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">In knowledge base</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Queries Served</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.queriesServed.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">Total queries</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Progress value={metrics.cpuUsage} className="h-2" />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{metrics.cpuUsage}%</span>
                    <span>100%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Progress value={metrics.memoryUsage} className="h-2" />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{metrics.memoryUsage}%</span>
                    <span>100%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Disk Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Progress value={metrics.diskUsage} className="h-2" />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{metrics.diskUsage}%</span>
                    <span>100%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Services Tab */}
        <TabsContent value="services">
          <Card>
            <CardHeader>
              <CardTitle>Service Health</CardTitle>
              <CardDescription>Status of all connected services and APIs</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {services.map((service) => (
                  <div key={service.name} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(service.status)}
                      <div>
                        <h4 className="font-medium">{service.name}</h4>
                        <p className="text-sm text-muted-foreground">
                          Last checked: {service.lastCheck.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      {service.responseTime && (
                        <span className="text-sm text-muted-foreground">
                          {service.responseTime}ms
                        </span>
                      )}
                      {getStatusBadge(service.status)}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Metrics Tab */}
        <TabsContent value="metrics">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
                <CardDescription>Real-time system performance data</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Active Connections</span>
                      <span className="text-sm">{metrics.activeConnections}</span>
                    </div>
                    <Progress value={(metrics.activeConnections / 50) * 100} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Query Rate</span>
                      <span className="text-sm">12.5/min</span>
                    </div>
                    <Progress value={25} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Resource Usage</CardTitle>
                <CardDescription>System resource consumption</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">CPU</span>
                      <span className="text-sm">{metrics.cpuUsage}%</span>
                    </div>
                    <Progress value={metrics.cpuUsage} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Memory</span>
                      <span className="text-sm">{metrics.memoryUsage}%</span>
                    </div>
                    <Progress value={metrics.memoryUsage} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Disk</span>
                      <span className="text-sm">{metrics.diskUsage}%</span>
                    </div>
                    <Progress value={metrics.diskUsage} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Logs Tab */}
        <TabsContent value="logs">
          <Card>
            <CardHeader>
              <CardTitle>Recent Logs</CardTitle>
              <CardDescription>Latest system events and activities</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]">
                <div className="space-y-2 font-mono text-sm">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-muted-foreground">10:23:45</span>
                    <CheckCircle className="h-3 w-3 text-green-500" />
                    <span>Google Drive sync completed successfully</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-muted-foreground">10:22:30</span>
                    <Zap className="h-3 w-3 text-blue-500" />
                    <span>RAG query processed in 1.2s</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-muted-foreground">10:21:15</span>
                    <FileText className="h-3 w-3 text-purple-500" />
                    <span>New document added: research_paper.pdf</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-muted-foreground">10:20:00</span>
                    <Server className="h-3 w-3 text-gray-500" />
                    <span>Background service health check passed</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-muted-foreground">10:18:45</span>
                    <AlertCircle className="h-3 w-3 text-yellow-500" />
                    <span>High memory usage warning: 85%</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-muted-foreground">10:15:30</span>
                    <Cloud className="h-3 w-3 text-blue-500" />
                    <span>Google Drive API connection established</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-muted-foreground">10:12:15</span>
                    <Database className="h-3 w-3 text-green-500" />
                    <span>Vector store indexed 150 new documents</span>
                  </div>
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}