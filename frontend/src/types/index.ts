export interface APIError {
  code: string;
  message: string;
  details?: any;
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: APIError;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Expense {
  id: number;
  amount: number;
  category: string;
  description: string;
  date: string;
}

export interface CreateExpensePayload {
  amount: number;
  category: string;
  description: string;
  date: string;
}

export interface UpdateExpensePayload {
  amount?: number;
  category?: string;
  description?: string;
  date?: string;
}

export interface ExpenseFilterParams {
  category?: string;
  start_date?: string;
  end_date?: string;
  min_amount?: number;
  max_amount?: number;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface AnalyticsSummary {
  total_spending: number;
  transaction_count: number;
  average_expense: number;
  highest_expense?: Expense;
  lowest_expense?: Expense;
  category_totals: Record<string, number>;
  category_percentages: Record<string, number>;
  monthly_totals: Record<string, number>;
  monthly_change: Record<string, number>;
}

export interface SpendingProfile {
  total_spending: number;
  avg_monthly_spending: number;
  avg_daily_spending: number;
  median_daily_spending: number;
  avg_transaction_size: number;
  largest_expense_amount: number;
  largest_expense_description: string;
  volatility_classification: string;
  transaction_count: number;
  spending_frequency: string;
}

export interface CategoryBudget {
  category: string;
  recommended_budget: number;
  current_spending: number;
  remaining: number;
  percentage_used: number;
  status: 'UNDER BUDGET' | 'AT RISK' | 'EXCEEDED' | string;
}

export interface BudgetAnalysis {
  total_budget: number;
  total_spending: number;
  total_remaining: number;
  at_risk_count: number;
  over_budget_count: number;
  category_budgets: CategoryBudget[];
}

export interface RecurringExpense {
  description: string;
  category: string;
  average_amount: number;
  frequency: string;
  last_date: string;
  confidence: number;
}

export interface Subscription {
  service_name: string;
  category: string;
  average_cost: number;
  frequency: string;
  annualized_cost: number;
  next_expected_date: string;
}

export interface HabitAnalysis {
  weekend_vs_weekday_ratio: number;
  late_month_vs_early_month_ratio: number;
  small_transaction_count: number;
  small_transaction_total: number;
  large_transaction_count: number;
  large_transaction_total: number;
  habits_summary: string[];
}

export interface Trend {
  category: string;
  direction: string;
  growth_rate: number;
  is_accelerating: boolean;
}

export interface CategoryForecast {
  forecasts: Record<string, number>;
}

export interface ScenarioRequest {
  category: string;
  change_value: number;
  is_percentage: boolean;
}

export interface ScenarioResult {
  category: string;
  change_description: string;
  original_spending: number;
  new_spending: number;
  monthly_savings: number;
  annualized_savings: number;
}

export interface InsightsResponse {
  insights: string[];
  generated_at: string;
}

export interface AnomalyItem {
  expense_id: number;
  amount: number;
  category: string;
  description: string;
  date: string;
  anomaly_score: number;
  is_anomaly: boolean;
  severity: 'High' | 'Medium' | 'Low' | string;
}

export interface AnomalyResponse {
  total_analyzed: number;
  total_anomalies: number;
  anomalies: AnomalyItem[];
}

export interface PredictionItem {
  horizon: string;
  predicted_amount: number;
  confidence?: number;
}

export interface PredictionResponse {
  next_month_prediction: number;
  predictions: PredictionItem[];
  model_name: string;
  disclaimer: string;
}

export interface ToolCallSummary {
  tool_name: string;
  arguments: Record<string, any>;
}

export interface AIChatResponse {
  reply: string;
  tool_calls: ToolCallSummary[];
  mode: 'ONLINE' | 'FALLBACK' | string;
}

export interface AIStatus {
  server_online: boolean;
  model_name: string;
  model_available: boolean;
  ai_provider: string;
  mode: 'ONLINE' | 'MODEL_MISSING' | 'OFFLINE' | string;
  base_url: string;
  tools_count: number;
  sqlite_connected: boolean;
  ml_models_available: boolean;
}

export interface SystemSettings {
  app_name: string;
  version: string;
  environment: string;
  currency: string;
  database_path: string;
  log_level: string;
  llm_provider: string;
  llm_model: string;
  ollama_base_url: string;
  ml_model_path: string;
  anomaly_contamination: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: ToolCallSummary[];
  timestamp: string;
  mode?: string;
}
