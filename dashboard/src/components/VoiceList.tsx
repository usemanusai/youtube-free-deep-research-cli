'use client';

import { useVoices, useDeleteVoice } from '@/hooks/useVoiceCloning';
import { useState } from 'react';

export function VoiceList() {
  const { data: voices, isLoading, error } = useVoices();
  const deleteMutation = useDeleteVoice();
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-2">⏳</div>
          <p className="text-slate-400">Loading voices...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
        <p className="text-red-300 font-medium">❌ Error loading voices</p>
        <p className="text-sm text-red-200 mt-1">{String(error)}</p>
      </div>
    );
  }

  if (!voices || voices.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-4xl mb-2">🎤</p>
        <p className="text-slate-400">No voices yet. Create one by uploading reference audio!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4">
        {voices.map((voice) => (
          <div
            key={voice.id}
            className="bg-slate-700/50 border border-slate-600 rounded-lg p-4 hover:border-slate-500 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white">{voice.name}</h3>
                <div className="mt-2 grid grid-cols-2 gap-4 text-sm text-slate-400">
                  <div>
                    <span className="text-slate-500">Created:</span> {new Date(voice.created_at).toLocaleDateString()}
                  </div>
                  <div>
                    <span className="text-slate-500">Usage:</span> {voice.usage_count} times
                  </div>
                  {voice.last_used && (
                    <div>
                      <span className="text-slate-500">Last used:</span> {new Date(voice.last_used).toLocaleDateString()}
                    </div>
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setConfirmDelete(voice.id)}
                  className="px-3 py-1 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded text-sm font-medium transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>

            {confirmDelete === voice.id && (
              <div className="mt-4 p-3 bg-red-900/30 border border-red-700 rounded flex items-center justify-between">
                <p className="text-red-300 text-sm">Are you sure? This cannot be undone.</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setConfirmDelete(null)}
                    className="px-3 py-1 bg-slate-600 hover:bg-slate-500 text-white rounded text-sm font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => {
                      deleteMutation.mutate(voice.id);
                      setConfirmDelete(null);
                    }}
                    disabled={deleteMutation.isPending}
                    className="px-3 py-1 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white rounded text-sm font-medium"
                  >
                    {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

