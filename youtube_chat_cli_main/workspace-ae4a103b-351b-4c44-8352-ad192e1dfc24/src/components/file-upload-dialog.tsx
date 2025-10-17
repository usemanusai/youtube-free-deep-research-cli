'use client'

import { useState, useRef } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Upload, File, Folder, CheckCircle, XCircle, Loader2, HardDrive, Cloud } from 'lucide-react'
import { toast } from 'sonner'

interface FileUploadDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onFileUploaded: (fileInfo: any) => void
}

interface GDriveFile {
  id: string
  name: string
  mimeType: string
  size?: string
  modifiedTime: string
}

export function FileUploadDialog({ open, onOpenChange, onFileUploaded }: FileUploadDialogProps) {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [gdriveFiles, setGdriveFiles] = useState<GDriveFile[]>([])
  const [loadingGDrive, setLoadingGDrive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8555'

  const handleLocalFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleLocalFileUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a file first')
      return
    }

    setUploading(true)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const xhr = new XMLHttpRequest()

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const progress = (e.loaded / e.total) * 100
          setUploadProgress(progress)
        }
      })

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText)
          toast.success(`File "${selectedFile.name}" uploaded successfully!`)
          onFileUploaded(response)
          setSelectedFile(null)
          if (fileInputRef.current) {
            fileInputRef.current.value = ''
          }
          onOpenChange(false)
        } else {
          toast.error('Upload failed')
        }
        setUploading(false)
        setUploadProgress(0)
      })

      xhr.addEventListener('error', () => {
        toast.error('Upload failed')
        setUploading(false)
        setUploadProgress(0)
      })

      xhr.open('POST', `${API_URL}/api/v1/files/upload`)
      xhr.send(formData)
    } catch (error: any) {
      toast.error(`Upload failed: ${error.message}`)
      setUploading(false)
      setUploadProgress(0)
    }
  }

  const loadGDriveFiles = async () => {
    setLoadingGDrive(true)
    try {
      const response = await fetch(`${API_URL}/api/v1/gdrive/list?page_size=50`)
      const data = await response.json()
      
      if (data.success) {
        setGdriveFiles(data.files || [])
        toast.success(`Loaded ${data.count} files from Google Drive`)
      } else {
        toast.error('Failed to load Google Drive files')
      }
    } catch (error: any) {
      toast.error(`Failed to load Google Drive files: ${error.message}`)
    } finally {
      setLoadingGDrive(false)
    }
  }

  const handleGDriveFileSelect = async (fileId: string, fileName: string) => {
    setUploading(true)
    setUploadProgress(0)

    try {
      // Simulate progress for download
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 10, 90))
      }, 200)

      const response = await fetch(`${API_URL}/api/v1/gdrive/download`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_id: fileId })
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      const data = await response.json()

      if (data.success) {
        toast.success(`File "${fileName}" downloaded and added to queue!`)
        onFileUploaded(data)
        onOpenChange(false)
      } else {
        toast.error('Failed to download file')
      }
    } catch (error: any) {
      toast.error(`Download failed: ${error.message}`)
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  const formatFileSize = (bytes?: string) => {
    if (!bytes) return 'Unknown size'
    const size = parseInt(bytes)
    if (size < 1024) return `${size} B`
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
    return `${(size / (1024 * 1024)).toFixed(1)} MB`
  }

  const getFileIcon = (mimeType: string) => {
    if (mimeType.includes('folder')) return <Folder className="h-4 w-4" />
    return <File className="h-4 w-4" />
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>Upload File to Knowledge Base</DialogTitle>
          <DialogDescription>
            Choose a file from your computer or Google Drive to add to the knowledge base
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="local" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="local">
              <HardDrive className="h-4 w-4 mr-2" />
              Local Files
            </TabsTrigger>
            <TabsTrigger value="gdrive" onClick={loadGDriveFiles}>
              <Cloud className="h-4 w-4 mr-2" />
              Google Drive
            </TabsTrigger>
          </TabsList>

          {/* Local Files Tab */}
          <TabsContent value="local" className="space-y-4">
            <div className="border-2 border-dashed rounded-lg p-8 text-center">
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleLocalFileSelect}
                className="hidden"
                id="file-upload"
                accept=".pdf,.txt,.doc,.docx,.md,.csv,.json"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-sm font-medium mb-2">
                  Click to select a file or drag and drop
                </p>
                <p className="text-xs text-muted-foreground">
                  Supported: PDF, TXT, DOC, DOCX, MD, CSV, JSON
                </p>
              </label>
            </div>

            {selectedFile && (
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-3">
                  <File className="h-5 w-5 text-primary" />
                  <div>
                    <p className="text-sm font-medium">{selectedFile.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {(selectedFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
                <Button
                  onClick={() => {
                    setSelectedFile(null)
                    if (fileInputRef.current) {
                      fileInputRef.current.value = ''
                    }
                  }}
                  variant="ghost"
                  size="sm"
                >
                  <XCircle className="h-4 w-4" />
                </Button>
              </div>
            )}

            {uploading && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Uploading...</span>
                  <span>{uploadProgress.toFixed(0)}%</span>
                </div>
                <Progress value={uploadProgress} />
              </div>
            )}

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => onOpenChange(false)} disabled={uploading}>
                Cancel
              </Button>
              <Button onClick={handleLocalFileUpload} disabled={!selectedFile || uploading}>
                {uploading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload File
                  </>
                )}
              </Button>
            </div>
          </TabsContent>

          {/* Google Drive Tab */}
          <TabsContent value="gdrive" className="space-y-4">
            {loadingGDrive ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <span className="ml-2">Loading Google Drive files...</span>
              </div>
            ) : gdriveFiles.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Cloud className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No files found in Google Drive</p>
                <Button variant="outline" onClick={loadGDriveFiles} className="mt-4">
                  Refresh
                </Button>
              </div>
            ) : (
              <>
                <ScrollArea className="h-[300px] border rounded-lg">
                  <div className="p-4 space-y-2">
                    {gdriveFiles.map((file) => (
                      <div
                        key={file.id}
                        className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted cursor-pointer transition-colors"
                        onClick={() => !uploading && handleGDriveFileSelect(file.id, file.name)}
                      >
                        <div className="flex items-center gap-3 flex-1">
                          {getFileIcon(file.mimeType)}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{file.name}</p>
                            <p className="text-xs text-muted-foreground">
                              {formatFileSize(file.size)} • {new Date(file.modifiedTime).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <Badge variant="secondary" className="ml-2">
                          Select
                        </Badge>
                      </div>
                    ))}
                  </div>
                </ScrollArea>

                {uploading && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Downloading from Google Drive...</span>
                      <span>{uploadProgress.toFixed(0)}%</span>
                    </div>
                    <Progress value={uploadProgress} />
                  </div>
                )}
              </>
            )}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}

