'use client';

import { useState } from 'react';
import { useVoices, useGenerateSpeech } from '@/hooks/useVoiceCloning';

export function SpeechGenerator() {
  const { data: voices, isLoading: voicesLoading } = useVoices();
  const generateMutation = useGenerateSpeech();

  const [voiceId, setVoiceId] = useState<string>('');
  const [text, setText] = useState('');
  const [speed, setSpeed] = useState(1.0);
  const [quality, setQuality] = useState<'fast' | 'balanced' | 'high'>('balanced');
  const [generatedAudio, setGeneratedAudio] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!voiceId || !text.trim()) return;

    const result = await generateMutation.mutateAsync({
      voice_id: parseInt(voiceId),
      text,
      speed,
      quality,
    });

    if (result.success) {
      setGeneratedAudio(result.output_path);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-white mb-2">
          Select Voice
        </label>
        <select
          value={voiceId}
          onChange={(e) => setVoiceId(e.target.value)}
          disabled={voicesLoading}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500 disabled:opacity-50"
        >
          <option value="">
            {voicesLoading ? 'Loading voices...' : 'Choose a voice...'}
          </option>
          {voices?.map((voice) => (
            <option key={voice.id} value={voice.id}>
              {voice.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-white mb-2">
          Text to Generate
        </label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter the text you want to convert to speech..."
          rows={6}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 resize-none"
        />
        <p className="text-xs text-slate-400 mt-1">
          {text.length} characters
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-white mb-2">
            Speed: {speed.toFixed(1)}x
          </label>
          <input
            type="range"
            min="0.5"
            max="2.0"
            step="0.1"
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            className="w-full"
          />
          <p className="text-xs text-slate-400 mt-1">0.5x - 2.0x</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-white mb-2">
            Quality
          </label>
          <select
            value={quality}
            onChange={(e) => setQuality(e.target.value as any)}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
          >
            <option value="fast">Fast (1-2s)</option>
            <option value="balanced">Balanced (2-3s)</option>
            <option value="high">High (4-5s)</option>
          </select>
        </div>
      </div>

      <button
        onClick={handleGenerate}
        disabled={!voiceId || !text.trim() || generateMutation.isPending}
        className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg font-medium transition-colors"
      >
        {generateMutation.isPending ? '🔄 Generating...' : '🔊 Generate Speech'}
      </button>

      {generatedAudio && (
        <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
          <p className="text-green-300 font-medium mb-3">✅ Speech Generated</p>
          <audio
            controls
            src={generatedAudio}
            className="w-full"
          />
          <p className="text-xs text-green-200 mt-2">
            Output: {generatedAudio}
          </p>
        </div>
      )}
    </div>
  );
}

