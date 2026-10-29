/**
 * Centralized API client for communicating with the Spring Boot main backend.
 * Never connects directly to Python FastAPI microservice from browser.
 */

import {
  AuthResponse,
  Dataset,
  UploadDatasetResponse,
  EDAResponse,
  SegmentationRunResponse,
  SegmentationRunHistory,
  PredictionTrainingResponse,
  QuoteSimulationRequest,
  QuoteSimulationResponse,
  PredictionExplanationResponse,
  ScenarioComparisonResponse,
  CompareScenariosRequest,
  InsightsResponse,
  UserProfile,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

class ApiErrorClass extends Error {
  status: number;
  error: string;
  validationErrors?: Record<string, string>;

  constructor(status: number, error: string, message: string, validationErrors?: Record<string, string>) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.error = error;
    this.validationErrors = validationErrors;
  }
}

function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  const token = localStorage.getItem('bizinsightiq_jwt');
  if (!token || token === 'undefined' || token === 'null') return null;
  return token;
}

export function setAuthToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('bizinsightiq_jwt', token);
  }
}

export function removeAuthToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('bizinsightiq_jwt');
    localStorage.removeItem('bizinsightiq_user');
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const url = `${API_BASE_URL}${endpoint}`;
  let response: Response;

  try {
    response = await fetch(url, { ...options, headers });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Network request failed';
    throw new ApiErrorClass(0, 'Network Error', `Cannot connect to server at ${API_BASE_URL}: ${errorMsg}`);
  }

  if (response.status === 401) {
    removeAuthToken();
    if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
      window.location.href = '/login?expired=true';
    }
  }

  if (response.status === 204) {
    return {} as T;
  }

  let data: Record<string, unknown> = {};
  try {
    data = await response.json();
  } catch {
    // Non-JSON or empty response body
  }

  if (!response.ok) {
    const status = response.status;
    const errorTitle = (data.error as string) || response.statusText || 'Error';
    const message = (data.message as string) || (data.detail as string) || 'An unexpected error occurred';
    const validationErrors = data.validationErrors as Record<string, string> | undefined;

    throw new ApiErrorClass(status, errorTitle, message, validationErrors);
  }

  return data as T;
}

// ---------------------------------------------------------------------------
// Authentication API
// ---------------------------------------------------------------------------

export const authApi = {
  login: async (credentials: { username: string; password: string }): Promise<AuthResponse> => {
    return request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  getCurrentUser: async (): Promise<UserProfile> => {
    return request<UserProfile>('/auth/me');
  },
};

// ---------------------------------------------------------------------------
// Dataset Management API
// ---------------------------------------------------------------------------

export const datasetApi = {
  list: async (): Promise<Dataset[]> => {
    return request<Dataset[]>('/datasets');
  },

  getById: async (id: string): Promise<Dataset> => {
    return request<Dataset>(`/datasets/${id}`);
  },

  upload: async (file: File, name?: string): Promise<UploadDatasetResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (name) {
      formData.append('name', name);
    }
    return request<UploadDatasetResponse>('/datasets/upload', {
      method: 'POST',
      body: formData,
    });
  },

  delete: async (id: string): Promise<void> => {
    return request<void>(`/datasets/${id}`, {
      method: 'DELETE',
    });
  },
};

// ---------------------------------------------------------------------------
// Analytical Orchestration API
// ---------------------------------------------------------------------------

export const analyticsApi = {
  getEda: async (datasetId: string): Promise<EDAResponse> => {
    return request<EDAResponse>(`/datasets/${datasetId}/analytics/eda`);
  },

  runSegmentation: async (
    datasetId: string,
    params: { nClusters?: number; randomState?: number; evaluateCandidates?: boolean }
  ): Promise<SegmentationRunResponse> => {
    return request<SegmentationRunResponse>(`/datasets/${datasetId}/analytics/segmentation`, {
      method: 'POST',
      body: JSON.stringify(params),
    });
  },

  getSegmentationRuns: async (datasetId: string): Promise<SegmentationRunHistory[]> => {
    return request<SegmentationRunHistory[]>(`/datasets/${datasetId}/analytics/segmentation/runs`);
  },

  trainPredictions: async (
    datasetId: string,
    params: { splitStrategy?: string; testSize?: number; randomState?: number }
  ): Promise<PredictionTrainingResponse> => {
    return request<PredictionTrainingResponse>(`/datasets/${datasetId}/analytics/predictions/train`, {
      method: 'POST',
      body: JSON.stringify(params),
    });
  },

  simulateQuote: async (
    datasetId: string,
    params: QuoteSimulationRequest
  ): Promise<QuoteSimulationResponse> => {
    return request<QuoteSimulationResponse>(`/datasets/${datasetId}/analytics/predictions`, {
      method: 'POST',
      body: JSON.stringify(params),
    });
  },

  explainQuote: async (
    datasetId: string,
    params: QuoteSimulationRequest
  ): Promise<PredictionExplanationResponse> => {
    return request<PredictionExplanationResponse>(`/datasets/${datasetId}/analytics/predictions/explain`, {
      method: 'POST',
      body: JSON.stringify(params),
    });
  },

  compareScenarios: async (
    datasetId: string,
    params: CompareScenariosRequest
  ): Promise<ScenarioComparisonResponse> => {
    return request<ScenarioComparisonResponse>(`/datasets/${datasetId}/analytics/predictions/compare`, {
      method: 'POST',
      body: JSON.stringify(params),
    });
  },

  getQuoteHistory: async (): Promise<QuoteSimulationResponse[]> => {
    return request<QuoteSimulationResponse[]>('/analytics/quotes');
  },

  getInsights: async (
    datasetId: string,
    filters?: { severity?: string; category?: string }
  ): Promise<InsightsResponse> => {
    const query = new URLSearchParams();
    if (filters?.severity) query.append('severity', filters.severity);
    if (filters?.category) query.append('category', filters.category);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return request<InsightsResponse>(`/datasets/${datasetId}/analytics/insights${qs}`);
  },
};
