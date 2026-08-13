import React, { useEffect, useState } from 'react';
import { AlertTriangle, ShieldAlert, Filter, Search } from 'lucide-react';
import { api } from '../api/client';
import type { AnomalyResponse, AnomalyItem } from '../types';

export const Anomalies: React.FC = () => {
  const [data, setData] = useState<AnomalyResponse | null>(null);
  const [severityFilter, setSeverityFilter] = useState('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAnomalies = async () => {
      setLoading(true);
      try {
        const res = await api.ml.getAnomalies(0.02);
        setData(res);
      } catch (err) {
        console.error('Failed to load anomalies', err);
      } finally {
        setLoading(false);
      }
    };

    loadAnomalies();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-500 text-sm font-medium">Running Isolation Forest anomaly detection...</div>
      </div>
    );
  }

  const filteredAnomalies = data
    ? data.anomalies.filter((a) => severityFilter === 'All' || a.severity === severityFilter)
    : [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">Unusual Transaction Detection</h2>
          <p className="text-xs text-slate-500 mt-0.5">Statistical anomaly detection powered by Scikit-Learn Isolation Forest.</p>
        </div>

        {/* Severity Filter */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-500 font-medium">Severity:</span>
          {['All', 'High', 'Medium', 'Low'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                severityFilter === sev
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Summary KPI Panel */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-panel p-5">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
            Analyzed Transactions
          </span>
          <h3 className="text-2xl font-extrabold text-slate-900 dark:text-white font-mono">
            {data?.total_analyzed || 0}
          </h3>
        </div>

        <div className="glass-panel p-5">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
            Flagged Anomalies
          </span>
          <h3 className="text-2xl font-extrabold text-amber-600 dark:text-amber-400 font-mono">
            {data?.total_anomalies || 0}
          </h3>
        </div>

        <div className="glass-panel p-5">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
            Contamination Base
          </span>
          <h3 className="text-2xl font-extrabold text-slate-900 dark:text-white font-mono">2.0%</h3>
        </div>
      </div>

      {/* Anomalies Table */}
      <div className="glass-panel overflow-hidden">
        {filteredAnomalies.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-sm">No unusual transactions found matching the selected severity filter.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100/60 dark:bg-slate-800/60 text-slate-500 uppercase tracking-wider border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="px-6 py-3 font-semibold">ID</th>
                  <th className="px-6 py-3 font-semibold">Description</th>
                  <th className="px-6 py-3 font-semibold">Category</th>
                  <th className="px-6 py-3 font-semibold">Date</th>
                  <th className="px-6 py-3 font-semibold text-right">Amount</th>
                  <th className="px-6 py-3 font-semibold text-center">Score</th>
                  <th className="px-6 py-3 font-semibold text-center">Severity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {filteredAnomalies.map((item) => (
                  <tr key={item.expense_id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40">
                    <td className="px-6 py-3.5 font-mono text-slate-400">#{item.expense_id}</td>
                    <td className="px-6 py-3.5 font-medium text-slate-900 dark:text-white">{item.description}</td>
                    <td className="px-6 py-3.5">
                      <span className="px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium">
                        {item.category}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-slate-500 font-mono">{item.date.split(' ')[0]}</td>
                    <td className="px-6 py-3.5 text-right font-mono font-bold text-slate-900 dark:text-white">
                      Rs. {item.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-6 py-3.5 text-center font-mono text-slate-500">
                      {item.anomaly_score.toFixed(3)}
                    </td>
                    <td className="px-6 py-3.5 text-center">
                      <span
                        className={`px-2.5 py-0.5 rounded-md text-[10px] font-bold ${
                          item.severity === 'High'
                            ? 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                            : item.severity === 'Medium'
                            ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                            : 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                        }`}
                      >
                        {item.severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
