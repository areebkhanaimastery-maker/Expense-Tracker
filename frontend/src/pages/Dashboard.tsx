import React, { useEffect, useState } from 'react';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  CreditCard,
  PieChart,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Bot,
} from 'lucide-react';
import { api } from '../api/client';
import type { AnalyticsSummary, BudgetAnalysis, Expense } from '../types';
import type { PageId } from '../layouts/DashboardLayout';

interface DashboardProps {
  onNavigate: (page: PageId) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [budget, setBudget] = useState<BudgetAnalysis | null>(null);
  const [recentExpenses, setRecentExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [sumData, budData, expData] = await Promise.all([
          api.analytics.getSummary(),
          api.intelligence.getBudget(),
          api.expenses.list({ page: 1, page_size: 5 }),
        ]);
        setSummary(sumData);
        setBudget(budData);
        setRecentExpenses(expData.items);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard statistics.');
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-medium text-slate-500">Loading intelligence dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-2xl text-red-700 dark:text-red-300">
        <h3 className="font-bold text-base mb-1">Error Loading Dashboard</h3>
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  // Calculate Month-Over-Month spending change
  const currentMonthTotal = summary ? Object.values(summary.monthly_totals).pop() || 0 : 0;
  const momChange = summary?.monthly_change?.percentage_change ?? 0;
  const topCategoryEntry = summary
    ? Object.entries(summary.category_totals).sort((a, b) => b[1] - a[1])[0]
    : null;

  return (
    <div className="space-y-6">
      {/* Top Welcome & Quick Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-6 text-white shadow-lg shadow-blue-600/15">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Expense Intelligence System</h2>
          <p className="text-blue-100 text-sm mt-1">
            Real-time statistical tracking, ML forecasts, and local LLM financial analytics.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => onNavigate('ai')}
            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-white text-blue-700 font-semibold text-sm hover:bg-blue-50 transition-colors shadow-sm"
          >
            <Bot className="w-4 h-4 text-blue-600" />
            <span>Ask Expense AI</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Lifetime Spending */}
        <div className="glass-panel p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Total Spending
            </span>
            <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400">
              <DollarSign className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <h3 className="text-2xl font-extrabold text-slate-900 dark:text-white">
              Rs. {summary?.total_spending.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              across <span className="font-semibold text-slate-700 dark:text-slate-300">{summary?.transaction_count}</span> transactions
            </p>
          </div>
        </div>

        {/* Current Month Spending */}
        <div className="glass-panel p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Current Month
            </span>
            <div className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400">
              <CreditCard className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <h3 className="text-2xl font-extrabold text-slate-900 dark:text-white">
              Rs. {currentMonthTotal.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </h3>
            <div className="flex items-center space-x-1 mt-1">
              {momChange >= 0 ? (
                <TrendingUp className="w-3.5 h-3.5 text-rose-500" />
              ) : (
                <TrendingDown className="w-3.5 h-3.5 text-emerald-500" />
              )}
              <span className={`text-xs font-semibold ${momChange >= 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                {momChange >= 0 ? `+${momChange.toFixed(1)}%` : `${momChange.toFixed(1)}%`} MoM
              </span>
            </div>
          </div>
        </div>

        {/* Average Expense */}
        <div className="glass-panel p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Average Expense
            </span>
            <div className="p-2 rounded-lg bg-purple-50 dark:bg-purple-950 text-purple-600 dark:text-purple-400">
              <Sparkles className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <h3 className="text-2xl font-extrabold text-slate-900 dark:text-white">
              Rs. {summary?.average_expense.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </h3>
            <p className="text-xs text-slate-500 mt-1">mean size per transaction</p>
          </div>
        </div>

        {/* Top Spending Category */}
        <div className="glass-panel p-5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Top Category
            </span>
            <div className="p-2 rounded-lg bg-amber-50 dark:bg-amber-950 text-amber-600 dark:text-amber-400">
              <PieChart className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3">
            <h3 className="text-2xl font-extrabold text-slate-900 dark:text-white">
              {topCategoryEntry ? topCategoryEntry[0] : 'N/A'}
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              Rs. {topCategoryEntry ? topCategoryEntry[1].toLocaleString(undefined, { minimumFractionDigits: 2 }) : '0.00'}
            </p>
          </div>
        </div>
      </div>

      {/* Main Grid: Category Distribution + Budget Risks */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Breakdown (2 Cols) */}
        <div className="lg:col-span-2 glass-panel p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-base text-slate-900 dark:text-white">Category Breakdown</h3>
            <button
              onClick={() => onNavigate('analytics')}
              className="text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline flex items-center space-x-1"
            >
              <span>View Full Analytics</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            {summary &&
              Object.entries(summary.category_totals).map(([category, amount]) => {
                const percentage = summary.category_percentages[category] || 0;
                return (
                  <div key={category} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-medium">
                      <span className="text-slate-700 dark:text-slate-300">{category}</span>
                      <span className="text-slate-900 dark:text-white font-mono font-semibold">
                        Rs. {amount.toLocaleString(undefined, { minimumFractionDigits: 2 })} ({percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="w-full bg-slate-100 dark:bg-slate-800 h-2.5 rounded-full overflow-hidden">
                      <div
                        className="bg-blue-600 dark:bg-blue-500 h-full rounded-full transition-all duration-300"
                        style={{ width: `${Math.min(percentage, 100)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
          </div>
        </div>

        {/* Budget Status Widget (1 Col) */}
        <div className="glass-panel p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-base text-slate-900 dark:text-white">Budget Health</h3>
              <button
                onClick={() => onNavigate('intelligence')}
                className="text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline"
              >
                Details
              </button>
            </div>

            {budget?.at_risk_count ? (
              <div className="p-3 mb-4 rounded-xl bg-amber-50 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-200 flex items-start space-x-3">
                <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                <div className="text-xs">
                  <span className="font-bold">{budget.at_risk_count} category(ies) at risk</span>
                  <p className="mt-0.5">High spending velocity detected against historical thresholds.</p>
                </div>
              </div>
            ) : null}

            <div className="space-y-3">
              {budget?.category_budgets.slice(0, 4).map((b) => (
                <div key={b.category} className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100 dark:border-slate-800/80 last:border-0">
                  <span className="font-medium text-slate-700 dark:text-slate-300">{b.category}</span>
                  <span
                    className={`font-semibold px-2 py-0.5 rounded-md text-[10px] ${
                      b.status === 'UNDER BUDGET'
                        ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                        : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                    }`}
                  >
                    {b.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={() => onNavigate('intelligence')}
            className="w-full mt-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-bold transition-colors"
          >
            Run What-If Scenario Calculator
          </button>
        </div>
      </div>

      {/* Recent Transactions Widget */}
      <div className="glass-panel p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-base text-slate-900 dark:text-white">Recent Transactions</h3>
          <button
            onClick={() => onNavigate('expenses')}
            className="text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline flex items-center space-x-1"
          >
            <span>Manage All Expenses</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-500">
                <th className="pb-3 font-semibold">ID</th>
                <th className="pb-3 font-semibold">Description</th>
                <th className="pb-3 font-semibold">Category</th>
                <th className="pb-3 font-semibold">Date</th>
                <th className="pb-3 font-semibold text-right">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {recentExpenses.map((exp) => (
                <tr key={exp.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40">
                  <td className="py-3 font-mono text-slate-400">#{exp.id}</td>
                  <td className="py-3 font-medium text-slate-900 dark:text-white">{exp.description}</td>
                  <td className="py-3">
                    <span className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium">
                      {exp.category}
                    </span>
                  </td>
                  <td className="py-3 text-slate-500 font-mono">{exp.date.split(' ')[0]}</td>
                  <td className="py-3 text-right font-mono font-bold text-slate-900 dark:text-white">
                    Rs. {exp.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
