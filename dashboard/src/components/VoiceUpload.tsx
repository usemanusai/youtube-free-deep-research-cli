'use client';

import { useState, useRef } from 'react';
import { useUploadReference, useValidateAudio } from '@/hooks/useVoiceCloning';

export function VoiceUpload() {
  const [voiceName, setVoiceName] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadMutation = useUploadReference();
  const validateMutation = useValidateAudio();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      setSelectedFile(files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleValidate = async () => {
    if (!selectedFile) return;
    await validateMutation.mutateAsync(selectedFile);
  };

  const handleUpload = async () => {
    if (!voiceName.trim() || !selectedFile) return;

    await uploadMutation.mutateAsync({
      name: voiceName,
      file: selectedFile,
    });

    if (uploadMutation.isSuccess) {
      setVoiceName('');
      setSelectedFile(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-white mb-2">
          Voice Name
        </label>
        <input
          type="text"
          value={voiceName}
          onChange={(e) => setVoiceName(e.target.value)}
          placeholder="e.g., My Professional Voice"
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-white mb-2">
          Reference Audio (3-300 seconds)
        </label>
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-500/10'
              : 'border-slate-600 bg-slate-700/30'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="audio/*"
            onChange={handleFileChange}
            className="hidden"
          />
          <div className="space-y-2">
            <p className="text-2xl">📁</p>
            <p className="text-white font-medium">
              {selectedFile ? selectedFile.name : 'Drag and drop your audio file here'}
            </p>
            <p className="text-sm text-slate-400">
              or{' '}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-blue-400 hover:text-blue-300 underline"
              >
                browse
              </button>
            </p>
            <p className="text-xs text-slate-500">
              Supported: WAV, MP3, FLAC (3-300 seconds recommended)
            </p>
          </div>
        </div>
      </div>

      {selectedFile && (
        <div className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
          <p className="text-sm text-slate-300">
            <span className="font-medium">File:</span> {selectedFile.name}
          </p>
          <p className="text-sm text-slate-300">
            <span className="font-medium">Size:</span> {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
          </p>
        </div>
      )}

      <div className="flex gap-3">
        <button
          onClick={handleValidate}
          disabled={!selectedFile || validateMutation.isPending}
          className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white rounded-lg font-medium transition-colors"
        >
          {validateMutation.isPending ? 'Validating...' : 'Validate Audio'}
        </button>
        <button
          onClick={handleUpload}
          disabled={!voiceName.trim() || !selectedFile || uploadMutation.isPending}
          className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg font-medium transition-colors"
        >
          {uploadMutation.isPending ? 'Uploading...' : 'Create Voice'}
        </button>
      </div>

      {validateMutation.data && (
        <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
          <p className="text-green-300 font-medium mb-2">✅ Audio Valid</p>
          <ul className="text-sm text-green-200 space-y-1">
            <li>Duration: {validateMutation.data.duration.toFixed(1)}s</li>
            <li>Sample Rate: {validateMutation.data.sample_rate}Hz</li>
            <li>SNR: {validateMutation.data.snr_db.toFixed(1)}dB</li>
          </ul>
        </div>
      )}
    </div>
  );
}

