import React, { useEffect, useState } from 'react';
import {
  PieChart,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Calendar,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { api } from '../api/client';
import type { AnalyticsSummary } from '../types';

export const Analytics: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [dailyTotals, setDailyTotals] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAnalytics = async () => {
      setLoading(true);
      try {
        const [sumRes, dailyRes] = await Promise.all([
          api.analytics.getSummary(),
          api.analytics.getDaily(),
        ]);
        setSummary(sumRes);
        setDailyTotals(dailyRes);
      } catch (err) {
        console.error('Failed to load analytics', err);
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-500 text-sm font-medium">Loading financial analytics...</div>
      </div>
    );
  }

  const monthlyEntries = summary ? Object.entries(summary.monthly_totals) : [];
  const maxMonthly = Math.max(...monthlyEntries.map((m) => m[1]), 1);

  const recentDailyEntries = Object.entries(dailyTotals).slice(-14);
  const maxDaily = Math.max(...recentDailyEntries.map((d) => d[1]), 1);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">Financial Analytics</h2>
        <p className="text-xs text-slate-500 mt-0.5">Statistical distributions, monthly trends, and expense metrics.</p>
      </div>

      {/* Highest / Lowest Expense Banner Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Highest Expense Card */}
        <div className="glass-panel p-5 border-l-4 border-l-rose-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Single Largest Expense
            </span>
            <div className="p-1.5 rounded-lg bg-rose-50 dark:bg-rose-950 text-rose-600">
              <ArrowUpRight className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2">
            <h3 className="text-2xl font-extrabold text-slate-900 dark:text-white">
              Rs. {summary?.highest_expense?.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </h3>
            <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 mt-1">
              {summary?.highest_expense?.description} ({summary?.highest_expense?.category})
            </p>
            <span className="text-[10px] text-slate-400 font-mono mt-0.5 block">
              Date: {summary?.highest_expense?.date}
            </span>
          </div>
        </div>

        {/* Lowest Expense Card */}
        <div className="glass-panel p-5 border-l-4 border-l-emerald-500">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Single Smallest Expense
            </span>
            <div className="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950 text-emerald-600">
              <ArrowDownRight className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2">
            <h3 className="text-2xl font-extrabold text-slate-900 dark:text-white">
              Rs. {summary?.lowest_expense?.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </h3>
            <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 mt-1">
              {summary?.lowest_expense?.description} ({summary?.lowest_expense?.category})
            </p>
            <span className="text-[10px] text-slate-400 font-mono mt-0.5 block">
              Date: {summary?.lowest_expense?.date}
            </span>
          </div>
        </div>
      </div>

      {/* Monthly Spending Trend Bar Chart */}
      <div className="glass-panel p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-base text-slate-900 dark:text-white">Monthly Spending Trend</h3>
          <span className="text-xs font-mono text-slate-500">YYYY-MM</span>
        </div>

        <div className="space-y-3 pt-2">
          {monthlyEntries.map(([month, amount]) => {
            const pct = (amount / maxMonthly) * 100;
            return (
              <div key={month} className="space-y-1">
                <div className="flex items-center justify-between text-xs font-medium">
                  <span className="font-mono text-slate-700 dark:text-slate-300">{month}</span>
                  <span className="font-mono font-bold text-slate-900 dark:text-white">
                    Rs. {amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </span>
                </div>
                <div className="w-full bg-slate-100 dark:bg-slate-800 h-4 rounded-lg overflow-hidden flex items-center p-0.5">
                  <div
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 h-full rounded-md transition-all duration-300"
                    style={{ width: `${Math.max(pct, 2)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Daily Spending Trend (Last 14 Days) */}
      <div className="glass-panel p-6">
        <h3 className="font-bold text-base text-slate-900 dark:text-white mb-4">Recent Daily Activity (Last 14 Days)</h3>
        <div className="flex items-end space-x-2 h-44 pt-6 pb-2 px-2 overflow-x-auto">
          {recentDailyEntries.map(([dateStr, amt]) => {
            const heightPct = (amt / maxDaily) * 100;
            return (
              <div key={dateStr} className="flex-1 flex flex-col items-center min-w-[36px] group">
                <div className="w-full bg-slate-100 dark:bg-slate-800/80 rounded-t-md h-full flex items-end justify-center relative">
                  <div
                    className="w-full bg-blue-500 group-hover:bg-blue-600 rounded-t-md transition-all duration-200"
                    style={{ height: `${Math.max(heightPct, 4)}%` }}
                  />
                  {/* Tooltip on Hover */}
                  <div className="absolute -top-8 hidden group-hover:block bg-slate-900 text-white text-[10px] py-1 px-2 rounded font-mono z-10 whitespace-nowrap shadow-lg">
                    Rs. {amt.toLocaleString()}
                  </div>
                </div>
                <span className="text-[10px] text-slate-400 font-mono mt-1 rotate-45 sm:rotate-0">
                  {dateStr.split('-').slice(1).join('/')}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
