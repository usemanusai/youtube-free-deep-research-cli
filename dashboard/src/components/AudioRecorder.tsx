'use client';

import { useState, useRef, useEffect } from 'react';
import { useUploadReference } from '@/hooks/useVoiceCloning';

export function AudioRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [voiceName, setVoiceName] = useState('');
  const [duration, setDuration] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const uploadMutation = useUploadReference();

  useEffect(() => {
    return () => {
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/wav' });
        setRecordedBlob(blob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setDuration(0);

      durationIntervalRef.current = setInterval(() => {
        setDuration((d) => d + 1);
      }, 1000);
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }
    }
  };

  const handleUpload = async () => {
    if (!recordedBlob || !voiceName.trim()) return;

    const file = new File([recordedBlob], `${voiceName}.wav`, { type: 'audio/wav' });
    await uploadMutation.mutateAsync({
      name: voiceName,
      file,
    });

    if (uploadMutation.isSuccess) {
      setRecordedBlob(null);
      setVoiceName('');
      setDuration(0);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-700/50 rounded-lg p-8 text-center border border-slate-600">
        <div className="text-6xl mb-4">🎙️</div>
        <p className="text-white font-medium mb-2">
          {isRecording ? 'Recording...' : 'Ready to record'}
        </p>
        <p className="text-slate-400 text-sm mb-4">
          {isRecording ? `Duration: ${formatDuration(duration)}` : 'Click the button below to start'}
        </p>

        <div className="flex gap-3 justify-center">
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
            >
              🔴 Start Recording
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="px-6 py-3 bg-slate-600 hover:bg-slate-500 text-white rounded-lg font-medium transition-colors"
            >
              ⏹️ Stop Recording
            </button>
          )}
        </div>
      </div>

      {recordedBlob && (
        <div className="space-y-4">
          <div className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
            <p className="text-white font-medium mb-2">Preview</p>
            <audio
              controls
              src={URL.createObjectURL(recordedBlob)}
              className="w-full"
            />
            <p className="text-xs text-slate-400 mt-2">
              Duration: {formatDuration(duration)} • Size: {(recordedBlob.size / 1024).toFixed(2)} KB
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-white mb-2">
              Voice Name
            </label>
            <input
              type="text"
              value={voiceName}
              onChange={(e) => setVoiceName(e.target.value)}
              placeholder="e.g., My Recorded Voice"
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => {
                setRecordedBlob(null);
                setVoiceName('');
                setDuration(0);
              }}
              className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
            >
              Discard
            </button>
            <button
              onClick={handleUpload}
              disabled={!voiceName.trim() || uploadMutation.isPending}
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg font-medium transition-colors"
            >
              {uploadMutation.isPending ? 'Uploading...' : 'Save Voice'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

