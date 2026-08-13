import React, { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Bot } from 'lucide-react';
import { api } from '../api/client';
import type { SystemSettings, AIStatus } from '../types';

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadSettings = async () => {
      setLoading(true);
      try {
        const [settRes, statusRes] = await Promise.all([
          api.settings.getSettings(),
          api.ai.getStatus(),
        ]);
        setSettings(settRes);
        setAiStatus(statusRes);
      } catch (err) {
        console.error('Failed to load settings', err);
      } finally {
        setLoading(false);
      }
    };

    loadSettings();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-500 text-sm font-medium">Loading system diagnostics & configuration...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">Settings & Diagnostics</h2>
        <p className="text-xs text-slate-500 mt-0.5">System architecture overview, model configurations, and database state.</p>
      </div>

      {/* Application Overview Panel */}
      <div className="glass-panel p-6">
        <h3 className="font-bold text-base text-slate-900 dark:text-white mb-4 flex items-center space-x-2">
          <SettingsIcon className="w-5 h-5 text-blue-600" />
          <span>Application Parameters</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="text-slate-500 block text-[10px] uppercase font-semibold">Application Name</span>
            <span className="font-bold text-slate-900 dark:text-white mt-1 block">{settings?.app_name}</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="text-slate-500 block text-[10px] uppercase font-semibold">Version</span>
            <span className="font-mono font-bold text-slate-900 dark:text-white mt-1 block">{settings?.version}</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="text-slate-500 block text-[10px] uppercase font-semibold">Currency</span>
            <span className="font-bold text-slate-900 dark:text-white mt-1 block">{settings?.currency}</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="text-slate-500 block text-[10px] uppercase font-semibold">Database Location</span>
            <span className="font-mono text-[11px] text-slate-700 dark:text-slate-300 mt-1 block truncate">
              {settings?.database_path}
            </span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="text-slate-500 block text-[10px] uppercase font-semibold">Log Level</span>
            <span className="font-mono font-bold text-slate-900 dark:text-white mt-1 block">{settings?.log_level}</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="text-slate-500 block text-[10px] uppercase font-semibold">Isolation Contamination</span>
            <span className="font-mono font-bold text-slate-900 dark:text-white mt-1 block">
              {settings?.anomaly_contamination}
            </span>
          </div>
        </div>
      </div>

      {/* AI & ML Architecture Diagnostics Panel */}
      <div className="glass-panel p-6">
        <h3 className="font-bold text-base text-slate-900 dark:text-white mb-4 flex items-center space-x-2">
          <Bot className="w-5 h-5 text-blue-600" />
          <span>Local LLM & ML Pipeline Health</span>
        </h3>

        <div className="space-y-3 text-xs">
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="font-semibold text-slate-700 dark:text-slate-300">Ollama API Status</span>
            <span
              className={`px-2.5 py-0.5 rounded-md font-semibold text-[10px] ${
                aiStatus?.server_online
                  ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                  : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
              }`}
            >
              {aiStatus?.server_online ? 'CONNECTED' : 'OFFLINE (Fallback Active)'}
            </span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="font-semibold text-slate-700 dark:text-slate-300">Target Model</span>
            <span className="font-mono font-bold text-slate-900 dark:text-white">{aiStatus?.model_name}</span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="font-semibold text-slate-700 dark:text-slate-300">Ollama Endpoint</span>
            <span className="font-mono text-slate-700 dark:text-slate-300">{aiStatus?.base_url}</span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
            <span className="font-semibold text-slate-700 dark:text-slate-300">Registered AI Tools</span>
            <span className="font-mono font-bold text-slate-900 dark:text-white">{aiStatus?.tools_count} Tools</span>
          </div>
        </div>
      </div>
    </div>
  );
};
