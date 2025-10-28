import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { voiceCloningClient, VoiceInfo, GenerateSpeechRequest, GenerateSpeechResponse, AudioValidationResponse } from '@/lib/api-client';
import toast from 'react-hot-toast';

export function useVoices() {
  return useQuery({
    queryKey: ['voices'],
    queryFn: () => voiceCloningClient.listVoices(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function useUploadReference() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ name, file, consentIp }: { name: string; file: File; consentIp?: string }) => {
      return voiceCloningClient.uploadReference(name, file, consentIp);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['voices'] });
      toast.success(`Voice "${data.name}" created successfully!`);
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to upload reference audio';
      toast.error(message);
    },
  });
}

export function useGenerateSpeech() {
  return useMutation({
    mutationFn: async (request: GenerateSpeechRequest) => {
      return voiceCloningClient.generateSpeech(request);
    },
    onSuccess: (data) => {
      toast.success('Speech generated successfully!');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to generate speech';
      toast.error(message);
    },
  });
}

export function useDeleteVoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (voiceId: number) => {
      return voiceCloningClient.deleteVoice(voiceId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['voices'] });
      toast.success('Voice deleted successfully!');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to delete voice';
      toast.error(message);
    },
  });
}

export function useValidateAudio() {
  return useMutation({
    mutationFn: async (file: File) => {
      return voiceCloningClient.validateAudio(file);
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to validate audio';
      toast.error(message);
    },
  });
}

export function useVoiceCloningSettings() {
  return useQuery({
    queryKey: ['voice-cloning-settings'],
    queryFn: () => voiceCloningClient.getSettings(),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}

