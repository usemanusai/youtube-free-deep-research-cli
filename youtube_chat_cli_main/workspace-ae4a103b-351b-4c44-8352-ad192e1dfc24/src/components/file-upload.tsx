'use client'

import { useState, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Upload, 
  File, 
  FileText, 
  Image, 
  FileCode, 
  X, 
  CheckCircle, 
  Loader2,
  AlertCircle 
} from 'lucide-react'
import { useFileUpload, useProcessingQueue } from '@/hooks/use-api'
import { toast } from 'sonner'

interface UploadingFile {
  file: File
  progress: number
  status: 'uploading' | 'success' | 'error'
  error?: string
}

export function FileUpload() {
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([])
  const [isDragging, setIsDragging] = useState(false)

  const fileUpload = useFileUpload()
  const { data: queueData } = useProcessingQueue()

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase()
    
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext || '')) {
      return <Image className="h-5 w-5 text-blue-500" />
    } else if (['pdf'].includes(ext || '')) {
      return <FileText className="h-5 w-5 text-red-500" />
    } else if (['doc', 'docx', 'txt', 'md'].includes(ext || '')) {
      return <FileText className="h-5 w-5 text-blue-600" />
    } else if (['json', 'xml', 'csv'].includes(ext || '')) {
      return <FileCode className="h-5 w-5 text-green-500" />
    } else {
      return <File className="h-5 w-5 text-gray-500" />
    }
  }

  const handleFiles = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return

    const fileArray = Array.from(files)
    
    // Add files to uploading state
    const newUploadingFiles: UploadingFile[] = fileArray.map(file => ({
      file,
      progress: 0,
      status: 'uploading' as const,
    }))
    
    setUploadingFiles(prev => [...prev, ...newUploadingFiles])

    // Upload each file
    for (let i = 0; i < fileArray.length; i++) {
      const file = fileArray[i]
      
      try {
        await fileUpload.mutateAsync({
          file,
          onProgress: (progress) => {
            setUploadingFiles(prev => 
              prev.map(uf => 
                uf.file === file 
                  ? { ...uf, progress } 
                  : uf
              )
            )
          },
        })
        
        // Mark as success
        setUploadingFiles(prev => 
          prev.map(uf => 
            uf.file === file 
              ? { ...uf, status: 'success' as const, progress: 100 } 
              : uf
          )
        )
      } catch (error: any) {
        // Mark as error
        setUploadingFiles(prev => 
          prev.map(uf => 
            uf.file === file 
              ? { 
                  ...uf, 
                  status: 'error' as const, 
                  error: error.response?.data?.detail || error.message 
                } 
              : uf
          )
        )
      }
    }
  }, [fileUpload])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    handleFiles(e.dataTransfer.files)
  }, [handleFiles])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files)
  }, [handleFiles])

  const removeUploadingFile = (file: File) => {
    setUploadingFiles(prev => prev.filter(uf => uf.file !== file))
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Files
          </CardTitle>
          <CardDescription>
            Upload documents to add them to your knowledge base
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center transition-colors
              ${isDragging 
                ? 'border-primary bg-primary/5' 
                : 'border-muted-foreground/25 hover:border-primary/50'
              }
            `}
          >
            <Upload className={`h-12 w-12 mx-auto mb-4 ${isDragging ? 'text-primary' : 'text-muted-foreground'}`} />
            <h3 className="text-lg font-semibold mb-2">
              {isDragging ? 'Drop files here' : 'Drag & drop files here'}
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              or click to browse
            </p>
            <input
              type="file"
              multiple
              onChange={handleFileInput}
              className="hidden"
              id="file-upload"
              accept=".pdf,.doc,.docx,.txt,.md,.json,.xml,.csv,.jpg,.jpeg,.png,.gif,.webp"
            />
            <Button asChild>
              <label htmlFor="file-upload" className="cursor-pointer">
                Select Files
              </label>
            </Button>
            <p className="text-xs text-muted-foreground mt-4">
              Supported: PDF, DOC, DOCX, TXT, MD, JSON, XML, CSV, Images
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Uploading Files */}
      {uploadingFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Uploading Files</CardTitle>
            <CardDescription>
              {uploadingFiles.filter(f => f.status === 'success').length} of {uploadingFiles.length} completed
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[300px]">
              <div className="space-y-3">
                {uploadingFiles.map((uploadingFile, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-3 p-3 border rounded-lg"
                  >
                    {getFileIcon(uploadingFile.file.name)}
                    
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {uploadingFile.file.name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatFileSize(uploadingFile.file.size)}
                      </p>
                      
                      {uploadingFile.status === 'uploading' && (
                        <Progress value={uploadingFile.progress} className="mt-2" />
                      )}
                      
                      {uploadingFile.status === 'error' && (
                        <p className="text-xs text-red-500 mt-1">
                          {uploadingFile.error}
                        </p>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {uploadingFile.status === 'uploading' && (
                        <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                      )}
                      {uploadingFile.status === 'success' && (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      )}
                      {uploadingFile.status === 'error' && (
                        <AlertCircle className="h-4 w-4 text-red-500" />
                      )}
                      
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeUploadingFile(uploadingFile.file)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}

      {/* Processing Queue Status */}
      {queueData && queueData.count > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Processing Queue</CardTitle>
            <CardDescription>
              {queueData.count} files waiting to be processed
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">
                  Files are being processed in the background
                </span>
              </div>
              <Badge variant="secondary">
                {queueData.count} pending
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

