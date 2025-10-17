/**
 * React Query Hooks for JAEGIS NexusSync API
 * 
 * Provides easy-to-use hooks for data fetching, mutations, and real-time updates.
 */

import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { apiClient, ChatQueryRequest, PodcastGenerateRequest } from '@/lib/api-client';
import { toast } from 'sonner';

// ============================================================================
// Query Keys
// ============================================================================

export const queryKeys = {
  health: ['health'] as const,
  systemStatus: ['system', 'status'] as const,
  systemVerify: ['system', 'verify'] as const,
  chatHistory: (sessionId: string) => ['chat', 'history', sessionId] as const,
  processingQueue: (status?: string) => ['files', 'queue', status] as const,
  gdriveStatus: ['gdrive', 'status'] as const,
  backgroundStatus: ['background', 'status'] as const,
  config: ['config'] as const,
  podcasts: ['podcasts'] as const,
  documents: (limit: number, offset: number) => ['documents', limit, offset] as const,
};

// ============================================================================
// System Hooks
// ============================================================================

export function useSystemStatus(options?: UseQueryOptions<any>) {
  return useQuery({
    queryKey: queryKeys.systemStatus,
    queryFn: () => apiClient.getSystemStatus(),
    refetchInterval: 30000, // Refresh every 30 seconds
    ...options,
  });
}

export function useSystemVerify(options?: UseQueryOptions<any>) {
  return useQuery({
    queryKey: queryKeys.systemVerify,
    queryFn: () => apiClient.verifyConnections(),
    ...options,
  });
}

// ============================================================================
// Chat Hooks
// ============================================================================

export function useChatQuery() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: ChatQueryRequest) => apiClient.chatQuery(request),
    onSuccess: () => {
      // Invalidate chat history if session_id is provided
      queryClient.invalidateQueries({ queryKey: ['chat', 'history'] });
    },
    onError: (error: any) => {
      toast.error('Chat query failed', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
}

export function useCreateChatSession() {
  return useMutation({
    mutationFn: () => apiClient.createChatSession(),
    onError: (error: any) => {
      toast.error('Failed to create chat session', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
}

export function useChatHistory(sessionId: string, options?: UseQueryOptions<any>) {
  return useQuery({
    queryKey: queryKeys.chatHistory(sessionId),
    queryFn: () => apiClient.getChatHistory(sessionId),
    enabled: !!sessionId,
    ...options,
  });
}

// ============================================================================
// File Processing Hooks
// ============================================================================

export function useFileUpload() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, onProgress }: { file: File; onProgress?: (progress: number) => void }) =>
      apiClient.uploadFile(file, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files', 'queue'] });
      toast.success('File uploaded successfully');
    },
    onError: (error: any) => {
      toast.error('File upload failed', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
}

export function useProcessFile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ filePath, priority }: { filePath: string; priority?: number }) =>
      apiClient.processFile(filePath, priority),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files', 'queue'] });
      toast.success('File processing started');
    },
    onError: (error: any) => {
      toast.error('File processing failed', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
}

export function useProcessingQueue(status?: string, options?: UseQueryOptions<any>) {
  return useQuery({
    queryKey: queryKeys.processingQueue(status),
    queryFn: () => apiClient.getProcessingQueue(50, status),
    refetchInterval: 5000, // Refresh every 5 seconds
    ...options,
  });
}

export function useProcessQueue() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (limit: number = 10) => apiClient.processQueue(limit),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['files', 'queue'] });
      toast.success('Queue processing completed', {
        description: `Processed: ${data.processed}, Failed: ${data.failed}`,
      });
    },
    onError: (error: any) => {
      toast.error('Queue processing failed', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
}

// ============================================================================
// Google Drive Hooks
// ============================================================================

export function useSyncGoogleDrive() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiClient.syncGoogleDrive(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.gdriveStatus });
      queryClient.invalidateQueries({ queryKey: ['files', 'queue'] });
      toast.success('Google Drive sync completed', {
        description: data.message,
      });
    },
    onError: (error: any) => {
      toast.error('Google Drive sync failed', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
}

export function useGoogleDriveStatus(options?: UseQueryOptions<any>) {
  return useQuery({
    queryKey: queryKeys.gdriveStatus,
    queryFn: () => apiClient.getGoogleDriveStatus(),
    ...options,
  });
}

// ============================================================================
// Background Service Hooks
// ============================================================================

export function useStartBackgroundService() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiClient.startBackgroundService(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.backgroundStatus });
      toast.success(data.message);
    },
    onError: (error: any) => {
      toast.error('Failed to start background service', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
}

export function useStopBackgroundService() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiClient.stopBackgroundService(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.backgroundStatus });
      toast.success(data.message);
    },
    onError: (error: any) => {
      toast.error('Failed to stop background service', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
}

export function useBackgroundServiceStatus(options?: UseQueryOptions<any>) {
  return useQuery({
    queryKey: queryKeys.backgroundStatus,
    queryFn: () => apiClient.getBackgroundServiceStatus(),
    refetchInterval: 10000, // Refresh every 10 seconds
    ...options,
  });
}

// ============================================================================
// Configuration Hooks
// ============================================================================

export function useConfig(options?: UseQueryOptions<any>) {
  return useQuery({
    queryKey: queryKeys.config,
    queryFn: () => apiClient.getConfig(),
    ...options,
  });
}

export function useUpdateConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: Record<string, string>) => apiClient.updateConfig(config),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.config });
      queryClient.invalidateQueries({ queryKey: queryKeys.systemStatus });
      toast.success('Configuration updated', {
        description: `Updated ${data.updated_keys.length} settings`,
      });
    },
    onError: (error: any) => {
      toast.error('Configuration update failed', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
}

export function useReloadConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiClient.reloadConfig(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.config });
      queryClient.invalidateQueries({ queryKey: queryKeys.systemStatus });
      toast.success('Configuration reloaded');
    },
    onError: (error: any) => {
      toast.error('Configuration reload failed', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
}

// ============================================================================
// Podcast Hooks
// ============================================================================

export function useGeneratePodcast() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: PodcastGenerateRequest) => apiClient.generatePodcast(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.podcasts });
      toast.success('Podcast generated successfully');
    },
    onError: (error: any) => {
      toast.error('Podcast generation failed', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
}

export function usePodcasts(options?: UseQueryOptions<any>) {
  return useQuery({
    queryKey: queryKeys.podcasts,
    queryFn: () => apiClient.listPodcasts(),
    ...options,
  });
}

// ============================================================================
// Search & Documents Hooks
// ============================================================================

export function useSearchDocuments() {
  return useMutation({
    mutationFn: ({ query, limit }: { query: string; limit?: number }) =>
      apiClient.searchDocuments(query, limit),
    onError: (error: any) => {
      toast.error('Search failed', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
}

export function useDocuments(limit: number = 50, offset: number = 0, options?: UseQueryOptions<any>) {
  return useQuery({
    queryKey: queryKeys.documents(limit, offset),
    queryFn: () => apiClient.listDocuments(limit, offset),
    ...options,
  });
}

