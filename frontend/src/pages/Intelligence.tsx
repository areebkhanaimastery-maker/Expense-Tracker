import React, { useEffect, useState } from 'react';
import {
  BrainCircuit,
  Calculator,
  Repeat,
  CreditCard,
  Zap,
  TrendingUp,
  TrendingDown,
  Sparkles,
} from 'lucide-react';
import { api } from '../api/client';
import type {
  SpendingProfile,
  BudgetAnalysis,
  RecurringExpense,
  Subscription,
  HabitAnalysis,
  Trend,
  ScenarioResult,
} from '../types';

export const Intelligence: React.FC = () => {
  const [profile, setProfile] = useState<SpendingProfile | null>(null);
  const [budget, setBudget] = useState<BudgetAnalysis | null>(null);
  const [recurring, setRecurring] = useState<RecurringExpense[]>([]);
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [habits, setHabits] = useState<HabitAnalysis | null>(null);
  const [trends, setTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);

  // What-If Scenario State
  const [selectedCategory, setSelectedCategory] = useState('Shopping');
  const [changeValue, setChangeValue] = useState('-20');
  const [isPercentage, setIsPercentage] = useState(true);
  const [scenarioResult, setScenarioResult] = useState<ScenarioResult | null>(null);
  const [scenarioLoading, setScenarioLoading] = useState(false);

  useEffect(() => {
    const loadIntelligenceData = async () => {
      setLoading(true);
      try {
        const [profData, budData, recData, subData, habData, treData] = await Promise.all([
          api.intelligence.getProfile(),
          api.intelligence.getBudget(),
          api.intelligence.getRecurring(),
          api.intelligence.getSubscriptions(),
          api.intelligence.getHabits(),
          api.intelligence.getTrends(),
        ]);
        setProfile(profData);
        setBudget(budData);
        setRecurring(recData);
        setSubscriptions(subData);
        setHabits(habData);
        setTrends(treData);
      } catch (err) {
        console.error('Failed to load intelligence data', err);
      } finally {
        setLoading(false);
      }
    };

    loadIntelligenceData();
  }, []);

  const handleRunScenario = async (e: React.FormEvent) => {
    e.preventDefault();
    setScenarioLoading(true);
    try {
      const res = await api.intelligence.runScenario({
        category: selectedCategory,
        change_value: parseFloat(changeValue),
        is_percentage: isPercentage,
      });
      setScenarioResult(res);
    } catch (err) {
      console.error('Failed to run scenario', err);
    } finally {
      setScenarioLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-500 text-sm font-medium">Running Intelligence Engine algorithms...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">Advanced Expense Intelligence</h2>
        <p className="text-xs text-slate-500 mt-0.5">Statistical profile, automated budgets, subscription filters, and scenario simulations.</p>
      </div>

      {/* Spending Profile Banner */}
      {profile && (
        <div className="glass-panel p-6">
          <h3 className="font-bold text-base text-slate-900 dark:text-white mb-4 flex items-center space-x-2">
            <BrainCircuit className="w-5 h-5 text-blue-600" />
            <span>Personal Spending Profile</span>
          </h3>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 text-xs">
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
              <span className="text-slate-500 block text-[10px] uppercase font-semibold">Avg Daily</span>
              <span className="text-sm font-extrabold text-slate-900 dark:text-white font-mono mt-0.5 block">
                Rs. {profile.avg_daily_spending.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
              <span className="text-slate-500 block text-[10px] uppercase font-semibold">Median Daily</span>
              <span className="text-sm font-extrabold text-slate-900 dark:text-white font-mono mt-0.5 block">
                Rs. {profile.median_daily_spending.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
              <span className="text-slate-500 block text-[10px] uppercase font-semibold">Avg Monthly</span>
              <span className="text-sm font-extrabold text-slate-900 dark:text-white font-mono mt-0.5 block">
                Rs. {profile.avg_monthly_spending.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
              <span className="text-slate-500 block text-[10px] uppercase font-semibold">Avg Transaction</span>
              <span className="text-sm font-extrabold text-slate-900 dark:text-white font-mono mt-0.5 block">
                Rs. {profile.avg_transaction_size.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
              <span className="text-slate-500 block text-[10px] uppercase font-semibold">Volatility</span>
              <span className="text-xs font-bold text-amber-600 dark:text-amber-400 mt-1 block">
                {profile.volatility_classification}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
              <span className="text-slate-500 block text-[10px] uppercase font-semibold">Frequency</span>
              <span className="text-xs font-bold text-blue-600 dark:text-blue-400 mt-1 block">
                {profile.spending_frequency}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* What-If Scenario Simulation Calculator */}
      <div className="glass-panel p-6 border-l-4 border-l-blue-600">
        <h3 className="font-bold text-base text-slate-900 dark:text-white mb-2 flex items-center space-x-2">
          <Calculator className="w-5 h-5 text-blue-600" />
          <span>What-If Scenario Simulator</span>
        </h3>
        <p className="text-xs text-slate-500 mb-4">Simulate how category budget adjustments directly affect your monthly and annualized savings.</p>

        <form onSubmit={handleRunScenario} className="grid grid-cols-1 sm:grid-cols-4 gap-3 items-end">
          <div>
            <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">Target Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white text-xs outline-none"
            >
              {['Food', 'Shopping', 'Transport', 'Bills', 'Entertainment', 'Health', 'Education', 'Other'].map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">Change Value</label>
            <input
              type="number"
              value={changeValue}
              onChange={(e) => setChangeValue(e.target.value)}
              placeholder="-20"
              className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white text-xs outline-none"
            />
          </div>

          <div>
            <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">Type</label>
            <select
              value={isPercentage ? 'pct' : 'abs'}
              onChange={(e) => setIsPercentage(e.target.value === 'pct')}
              className="w-full px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white text-xs outline-none"
            >
              <option value="pct">Percentage (%)</option>
              <option value="abs">Fixed Amount (Rs.)</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={scenarioLoading}
            className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-sm transition-colors"
          >
            {scenarioLoading ? 'Calculating...' : 'Simulate Impact'}
          </button>
        </form>

        {/* Scenario Result Callout */}
        {scenarioResult && (
          <div className="mt-4 p-4 rounded-xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 text-xs">
            <span className="font-bold text-blue-900 dark:text-blue-200 block text-sm mb-1">
              {scenarioResult.change_description}
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-2">
              <div>
                <span className="text-slate-500 block text-[10px]">Original Category Spend</span>
                <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                  Rs. {scenarioResult.original_spending.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>

              <div>
                <span className="text-slate-500 block text-[10px]">Simulated Category Spend</span>
                <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                  Rs. {scenarioResult.new_spending.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>

              <div>
                <span className="text-slate-500 block text-[10px]">Monthly Impact</span>
                <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">
                  Rs. {scenarioResult.monthly_savings.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>

              <div>
                <span className="text-slate-500 block text-[10px]">Annualized Impact</span>
                <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">
                  Rs. {scenarioResult.annualized_savings.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Recommended Category Budgets */}
      <div className="glass-panel p-6">
        <h3 className="font-bold text-base text-slate-900 dark:text-white mb-4">Recommended Category Budgets</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-200 dark:border-slate-800 text-slate-500">
              <tr>
                <th className="pb-3 font-semibold">Category</th>
                <th className="pb-3 font-semibold">Recommended Limit</th>
                <th className="pb-3 font-semibold">Current Spend</th>
                <th className="pb-3 font-semibold">Remaining</th>
                <th className="pb-3 font-semibold">Utilization</th>
                <th className="pb-3 font-semibold text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {budget?.category_budgets.map((b) => (
                <tr key={b.category}>
                  <td className="py-3 font-medium text-slate-900 dark:text-white">{b.category}</td>
                  <td className="py-3 font-mono">Rs. {b.recommended_budget.toLocaleString()}</td>
                  <td className="py-3 font-mono">Rs. {b.current_spending.toLocaleString()}</td>
                  <td className="py-3 font-mono font-semibold text-emerald-600 dark:text-emerald-400">
                    Rs. {b.remaining.toLocaleString()}
                  </td>
                  <td className="py-3 w-36">
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            b.status === 'UNDER BUDGET'
                              ? 'bg-emerald-500'
                              : 'bg-amber-500'
                          }`}
                          style={{ width: `${Math.min(b.percentage_used, 100)}%` }}
                        />
                      </div>
                      <span className="font-mono text-[10px] text-slate-500">{b.percentage_used}%</span>
                    </div>
                  </td>
                  <td className="py-3 text-center">
                    <span
                      className={`px-2 py-0.5 rounded-md text-[10px] font-semibold ${
                        b.status === 'UNDER BUDGET'
                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                          : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                      }`}
                    >
                      {b.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Behavioral Habits & Trends */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Behavioral Habits Panel */}
        <div className="glass-panel p-6">
          <h3 className="font-bold text-base text-slate-900 dark:text-white mb-4 flex items-center space-x-2">
            <Zap className="w-5 h-5 text-amber-500" />
            <span>Behavioral Habits Analysis</span>
          </h3>
          {habits && (
            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
                  <span className="text-slate-500 block text-[10px] font-semibold uppercase">Weekend / Weekday Ratio</span>
                  <span className="font-mono font-bold text-slate-900 dark:text-white text-sm mt-0.5 block">
                    {habits.weekend_vs_weekday_ratio.toFixed(2)}x
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
                  <span className="text-slate-500 block text-[10px] font-semibold uppercase">Late / Early Month Ratio</span>
                  <span className="font-mono font-bold text-slate-900 dark:text-white text-sm mt-0.5 block">
                    {habits.late_month_vs_early_month_ratio.toFixed(2)}x
                  </span>
                </div>
              </div>

              <div className="space-y-2 pt-1">
                <h4 className="font-semibold text-slate-700 dark:text-slate-300 text-xs">Habit Insights</h4>
                <ul className="space-y-1.5 list-disc list-inside text-slate-600 dark:text-slate-400 text-xs">
                  {habits.habits_summary.map((summaryItem, idx) => (
                    <li key={idx}>{summaryItem}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Category Trends Panel */}
        <div className="glass-panel p-6">
          <h3 className="font-bold text-base text-slate-900 dark:text-white mb-4 flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-purple-500" />
            <span>Category Spending Trends</span>
          </h3>
          <div className="space-y-3">
            {trends.map((t) => (
              <div key={t.category} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 text-xs">
                <div>
                  <span className="font-bold text-slate-900 dark:text-white block">{t.category}</span>
                  <span className="text-[10px] text-slate-500 font-mono">
                    Growth: {t.growth_rate >= 0 ? `+${t.growth_rate.toFixed(1)}%` : `${t.growth_rate.toFixed(1)}%`}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span
                    className={`inline-flex items-center px-2.5 py-1 rounded-md font-semibold text-[10px] ${
                      t.direction === 'UP'
                        ? 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                        : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                    }`}
                  >
                    {t.direction === 'UP' ? (
                      <TrendingUp className="w-3 h-3 mr-1" />
                    ) : (
                      <TrendingDown className="w-3 h-3 mr-1" />
                    )}
                    {t.direction}
                  </span>
                  {t.is_accelerating && (
                    <span className="px-2 py-0.5 rounded-md bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 text-[10px] font-bold">
                      ACCELERATING
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recurring & Subscriptions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Recurring Expenses Table */}
        <div className="glass-panel p-6">
          <h3 className="font-bold text-base text-slate-900 dark:text-white mb-4 flex items-center space-x-2">
            <Repeat className="w-5 h-5 text-blue-600" />
            <span>Recurring Expenses</span>
          </h3>
          {recurring.length === 0 ? (
            <p className="text-xs text-slate-500">No recurring expense patterns detected yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="border-b border-slate-200 dark:border-slate-800 text-slate-500">
                  <tr>
                    <th className="pb-2 font-semibold">Pattern</th>
                    <th className="pb-2 font-semibold">Frequency</th>
                    <th className="pb-2 font-semibold text-right">Avg Amount</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                  {recurring.map((rec, i) => (
                    <tr key={i}>
                      <td className="py-2.5 font-medium text-slate-900 dark:text-white">{rec.description}</td>
                      <td className="py-2.5 text-slate-500">{rec.frequency}</td>
                      <td className="py-2.5 text-right font-mono font-bold text-slate-900 dark:text-white">
                        Rs. {rec.average_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Active Subscriptions Table */}
        <div className="glass-panel p-6">
          <h3 className="font-bold text-base text-slate-900 dark:text-white mb-4 flex items-center space-x-2">
            <CreditCard className="w-5 h-5 text-indigo-600" />
            <span>Active Subscriptions</span>
          </h3>
          {subscriptions.length === 0 ? (
            <p className="text-xs text-slate-500">No active subscriptions detected.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="border-b border-slate-200 dark:border-slate-800 text-slate-500">
                  <tr>
                    <th className="pb-2 font-semibold">Service</th>
                    <th className="pb-2 font-semibold">Frequency</th>
                    <th className="pb-2 font-semibold text-right">Annual Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                  {subscriptions.map((sub, i) => (
                    <tr key={i}>
                      <td className="py-2.5 font-medium text-slate-900 dark:text-white">{sub.service_name}</td>
                      <td className="py-2.5 text-slate-500">{sub.frequency}</td>
                      <td className="py-2.5 text-right font-mono font-bold text-slate-900 dark:text-white">
                        Rs. {sub.annualized_cost.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
