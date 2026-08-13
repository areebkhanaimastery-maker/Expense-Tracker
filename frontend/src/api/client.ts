import type {
  APIResponse,
  PaginatedResponse,
  Expense,
  CreateExpensePayload,
  UpdateExpensePayload,
  ExpenseFilterParams,
  AnalyticsSummary,
  SpendingProfile,
  BudgetAnalysis,
  RecurringExpense,
  Subscription,
  HabitAnalysis,
  Trend,
  CategoryForecast,
  ScenarioRequest,
  ScenarioResult,
  InsightsResponse,
  AnomalyResponse,
  PredictionResponse,
  AIChatResponse,
  AIStatus,
  SystemSettings,
} from '../types';

const API_BASE = '/api';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options?.headers || {}),
  };

  const response = await fetch(url, { ...options, headers });
  const json: APIResponse<T> = await response.json();

  if (!response.ok || !json.success) {
    const errorMsg = json.error?.message || `HTTP Error ${response.status}: ${response.statusText}`;
    throw new Error(errorMsg);
  }

  return json.data as T;
}

export const api = {
  // Health
  health: () => request<{ status: string; version: string }>('/health'),

  // Expenses
  expenses: {
    list: (params?: ExpenseFilterParams) => {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.set('page', params.page.toString());
      if (params?.page_size) queryParams.set('page_size', params.page_size.toString());
      if (params?.category) queryParams.set('category', params.category);
      if (params?.search) queryParams.set('search', params.search);
      if (params?.start_date) queryParams.set('start_date', params.start_date);
      if (params?.end_date) queryParams.set('end_date', params.end_date);
      if (params?.min_amount !== undefined) queryParams.set('min_amount', params.min_amount.toString());
      if (params?.max_amount !== undefined) queryParams.set('max_amount', params.max_amount.toString());

      const queryStr = queryParams.toString() ? `?${queryParams.toString()}` : '';
      return request<PaginatedResponse<Expense>>(`/expenses${queryStr}`);
    },
    get: (id: number) => request<Expense>(`/expenses/${id}`),
    create: (payload: CreateExpensePayload) =>
      request<Expense>('/expenses', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    update: (id: number, payload: UpdateExpensePayload) =>
      request<Expense>(`/expenses/${id}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      }),
    delete: (id: number) =>
      request<{ message: string }>(`/expenses/${id}`, {
        method: 'DELETE',
      }),
    getCategories: () => request<string[]>('/categories'),
    search: (query: string) => request<Expense[]>(`/search?query=${encodeURIComponent(query)}`),
  },

  // Analytics
  analytics: {
    getSummary: () => request<AnalyticsSummary>('/analytics/summary'),
    getDaily: () => request<Record<string, number>>('/analytics/daily'),
    getMonthly: () => request<Record<string, number>>('/analytics/monthly'),
    getCategories: () => request<Record<string, number>>('/analytics/categories'),
  },

  // Intelligence
  intelligence: {
    getProfile: () => request<SpendingProfile>('/intelligence/profile'),
    getBudget: () => request<BudgetAnalysis>('/intelligence/budget'),
    getRecurring: () => request<RecurringExpense[]>('/intelligence/recurring'),
    getSubscriptions: () => request<Subscription[]>('/intelligence/subscriptions'),
    getHabits: () => request<HabitAnalysis>('/intelligence/habits'),
    getTrends: () => request<Trend[]>('/intelligence/trends'),
    getForecasts: () => request<CategoryForecast>('/intelligence/forecasts'),
    runScenario: (payload: ScenarioRequest) =>
      request<ScenarioResult>('/intelligence/scenario', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    getInsights: () => request<{ insights: string[]; generated_at: string }>('/intelligence/insights'),
  },

  // Machine Learning
  ml: {
    getAnomalies: (contamination = 0.02) =>
      request<AnomalyResponse>(`/ml/anomalies?contamination=${contamination}`),
    getPredictions: () => request<PredictionResponse>('/ml/predictions'),
    trainModels: () =>
      request<{ success: boolean; message: string; trained_at: string }>('/ml/train', {
        method: 'POST',
      }),
  },

  // AI Assistant
  ai: {
    chat: (message: string) =>
      request<AIChatResponse>('/ai/chat', {
        method: 'POST',
        body: JSON.stringify({ message }),
      }),
    getStatus: () => request<AIStatus>('/ai/status'),
  },

  // Settings
  settings: {
    getSettings: () => request<SystemSettings>('/settings'),
  },
};
