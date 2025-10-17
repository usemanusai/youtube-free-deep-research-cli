'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  List, 
  Play, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Loader2,
  AlertCircle,
  FileText
} from 'lucide-react'
import { useProcessingQueue, useProcessQueue } from '@/hooks/use-api'
import { formatDistanceToNow } from 'date-fns'

export function QueueManager() {
  const [activeTab, setActiveTab] = useState('all')
  
  const { data: allQueue, isLoading: allLoading, refetch: refetchAll } = useProcessingQueue()
  const { data: pendingQueue, isLoading: pendingLoading, refetch: refetchPending } = useProcessingQueue('pending')
  const { data: processingQueue, isLoading: processingLoading, refetch: refetchProcessing } = useProcessingQueue('processing')
  const { data: completedQueue, isLoading: completedLoading, refetch: refetchCompleted } = useProcessingQueue('completed')
  const { data: failedQueue, isLoading: failedLoading, refetch: refetchFailed } = useProcessingQueue('failed')
  
  const processQueue = useProcessQueue()

  const handleProcessQueue = () => {
    processQueue.mutate(10, {
      onSuccess: () => {
        refetchAll()
        refetchPending()
        refetchProcessing()
        refetchCompleted()
        refetchFailed()
      },
    })
  }

  const handleRefresh = () => {
    refetchAll()
    refetchPending()
    refetchProcessing()
    refetchCompleted()
    refetchFailed()
  }

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return <Badge variant="secondary"><Clock className="h-3 w-3 mr-1" />Pending</Badge>
      case 'processing':
        return <Badge variant="default"><Loader2 className="h-3 w-3 mr-1 animate-spin" />Processing</Badge>
      case 'completed':
        return <Badge variant="default" className="bg-green-500"><CheckCircle className="h-3 w-3 mr-1" />Completed</Badge>
      case 'failed':
        return <Badge variant="destructive"><XCircle className="h-3 w-3 mr-1" />Failed</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const getPriorityBadge = (priority: number) => {
    if (priority >= 10) {
      return <Badge variant="destructive">High</Badge>
    } else if (priority >= 5) {
      return <Badge variant="secondary">Medium</Badge>
    } else {
      return <Badge variant="outline">Low</Badge>
    }
  }

  const renderQueueItems = (items: any[] | undefined, loading: boolean) => {
    if (loading) {
      return (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      )
    }

    if (!items || items.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
          <List className="h-12 w-12 mb-2 opacity-50" />
          <p>No items in queue</p>
        </div>
      )
    }

    return (
      <div className="space-y-3">
        {items.map((item) => (
          <div
            key={item.id}
            className="flex items-center gap-3 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
          >
            <FileText className="h-5 w-5 text-muted-foreground flex-shrink-0" />
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <p className="text-sm font-medium truncate">
                  {item.file_name}
                </p>
                {getStatusBadge(item.status)}
                {getPriorityBadge(item.priority)}
              </div>
              
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <span>Source: {item.source}</span>
                <span>ID: {item.file_id.substring(0, 8)}...</span>
                <span>
                  Added {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <List className="h-5 w-5" />
              Processing Queue
            </CardTitle>
            <CardDescription>
              Manage and monitor file processing queue
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={allLoading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${allLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button
              size="sm"
              onClick={handleProcessQueue}
              disabled={processQueue.isPending || !pendingQueue?.count}
            >
              <Play className={`h-4 w-4 mr-2 ${processQueue.isPending ? 'animate-spin' : ''}`} />
              Process Queue
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Queue Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-2xl font-bold">{allQueue?.count || 0}</p>
                <p className="text-xs text-muted-foreground">Total</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-2xl font-bold text-yellow-600">{pendingQueue?.count || 0}</p>
                <p className="text-xs text-muted-foreground">Pending</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">{processingQueue?.count || 0}</p>
                <p className="text-xs text-muted-foreground">Processing</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{completedQueue?.count || 0}</p>
                <p className="text-xs text-muted-foreground">Completed</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-2xl font-bold text-red-600">{failedQueue?.count || 0}</p>
                <p className="text-xs text-muted-foreground">Failed</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Queue Items Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="pending">Pending</TabsTrigger>
            <TabsTrigger value="processing">Processing</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
            <TabsTrigger value="failed">Failed</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-4">
            <ScrollArea className="h-[400px]">
              {renderQueueItems(allQueue?.items, allLoading)}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="pending" className="mt-4">
            <ScrollArea className="h-[400px]">
              {renderQueueItems(pendingQueue?.items, pendingLoading)}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="processing" className="mt-4">
            <ScrollArea className="h-[400px]">
              {renderQueueItems(processingQueue?.items, processingLoading)}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="completed" className="mt-4">
            <ScrollArea className="h-[400px]">
              {renderQueueItems(completedQueue?.items, completedLoading)}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="failed" className="mt-4">
            <ScrollArea className="h-[400px]">
              {renderQueueItems(failedQueue?.items, failedLoading)}
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

