'use client';

import { useState } from 'react';
import { VoiceUpload } from '@/components/VoiceUpload';
import { VoiceList } from '@/components/VoiceList';
import { SpeechGenerator } from '@/components/SpeechGenerator';
import { AudioRecorder } from '@/components/AudioRecorder';

type Tab = 'upload' | 'list' | 'generate' | 'record';

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>('upload');

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'upload', label: 'Upload Voice', icon: '📤' },
    { id: 'record', label: 'Record Voice', icon: '🎙️' },
    { id: 'list', label: 'My Voices', icon: '🎤' },
    { id: 'generate', label: 'Generate Speech', icon: '🔊' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white">
        <h2 className="text-3xl font-bold mb-2">Voice Cloning Studio</h2>
        <p className="text-blue-100">
          Create professional-quality speech with your own voice using E2-F5-TTS
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-700 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-3 font-medium whitespace-nowrap transition-colors ${
              activeTab === tab.id
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-slate-400 hover:text-slate-300'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
        {activeTab === 'upload' && <VoiceUpload />}
        {activeTab === 'record' && <AudioRecorder />}
        {activeTab === 'list' && <VoiceList />}
        {activeTab === 'generate' && <SpeechGenerator />}
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
          <h3 className="font-semibold text-white mb-2">📊 Quality</h3>
          <p className="text-sm text-slate-400">
            Studio-quality output with zero-shot voice cloning
          </p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
          <h3 className="font-semibold text-white mb-2">⚡ Speed</h3>
          <p className="text-sm text-slate-400">
            Generate speech in 1-5 seconds depending on quality preset
          </p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
          <h3 className="font-semibold text-white mb-2">🔒 Privacy</h3>
          <p className="text-sm text-slate-400">
            Your voice data is stored securely with consent tracking
          </p>
        </div>
      </div>
    </div>
  );
}

