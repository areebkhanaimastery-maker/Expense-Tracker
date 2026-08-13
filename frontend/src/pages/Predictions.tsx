import React, { useEffect, useState } from 'react';
import { Sparkles, RefreshCw, AlertCircle, Calendar, CheckCircle2 } from 'lucide-react';
import { api } from '../api/client';
import type { PredictionResponse, CategoryForecast } from '../types';

export const Predictions: React.FC = () => {
  const [predictions, setPredictions] = useState<PredictionResponse | null>(null);
  const [categoryForecasts, setCategoryForecasts] = useState<CategoryForecast | null>(null);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [trainMessage, setTrainMessage] = useState<string | null>(null);

  const loadPredictions = async () => {
    setLoading(true);
    try {
      const [predRes, catRes] = await Promise.all([
        api.ml.getPredictions(),
        api.intelligence.getForecasts(),
      ]);
      setPredictions(predRes);
      setCategoryForecasts(catRes);
    } catch (err) {
      console.error('Failed to load predictions', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPredictions();
  }, []);

  const handleRetrain = async () => {
    setTraining(true);
    setTrainMessage(null);
    try {
      const res = await api.ml.trainModels();
      setTrainMessage(res.message);
      await loadPredictions();
    } catch (err: any) {
      setTrainMessage(err.message || 'Model retraining failed.');
    } finally {
      setTraining(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-500 text-sm font-medium">Running machine learning time-series forecasts...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">ML Spending Predictions</h2>
          <p className="text-xs text-slate-500 mt-0.5">HistGradientBoosting time-series forecasting & category estimates.</p>
        </div>
        <button
          onClick={handleRetrain}
          disabled={training}
          className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 text-xs font-semibold hover:opacity-90 disabled:opacity-50 transition-opacity"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${training ? 'animate-spin' : ''}`} />
          <span>{training ? 'Retraining ML Models...' : 'Retrain ML Model'}</span>
        </button>
      </div>

      {trainMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200 text-xs flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{trainMessage}</span>
        </div>
      )}

      {/* Model Disclaimer Callout */}
      <div className="p-4 rounded-xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 text-xs text-blue-900 dark:text-blue-200 flex items-start space-x-3">
        <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Statistical Disclaimer:</span>
          <p className="mt-0.5">{predictions?.disclaimer}</p>
        </div>
      </div>

      {/* Forecast Horizons Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {predictions?.predictions.map((p) => (
          <div key={p.horizon} className="glass-panel p-5">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
              {p.horizon}
            </span>
            <h3 className="text-2xl font-extrabold text-slate-900 dark:text-white font-mono">
              Rs. {p.predicted_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </h3>
            <span className="text-[10px] text-slate-400 mt-2 block font-mono">Model: {predictions.model_name}</span>
          </div>
        ))}
      </div>

      {/* Category Forecasts Table */}
      <div className="glass-panel p-6">
        <h3 className="font-bold text-base text-slate-900 dark:text-white mb-4">
          Estimated Category Spending (Next Month)
        </h3>
        <div className="space-y-3">
          {categoryForecasts &&
            Object.entries(categoryForecasts.forecasts).map(([cat, amt]) => (
              <div key={cat} className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-slate-800/80 last:border-0 text-xs">
                <span className="font-medium text-slate-800 dark:text-slate-200">{cat}</span>
                <span className="font-mono font-bold text-slate-900 dark:text-white">
                  Rs. {amt.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};
