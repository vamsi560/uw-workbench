// Frontend API Client for Java Backend Integration
// File: src/lib/api-client.ts (or similar path in your frontend project)

import { 
  API_CONFIG, 
  ENDPOINTS, 
  HTTP_CONFIG,
  WorkItemDto,
  EmailIntakeRequest,
  EmailIntakeResponse,
  HealthResponse,
  LLMStatusResponse,
  ApiErrorResponse
} from './config';

// Enhanced fetch wrapper with error handling and retries
class ApiClient {
  private baseUrl: string;
  private defaultHeaders: Record<string, string>;

  constructor() {
    this.baseUrl = API_CONFIG.API_URL;
    this.defaultHeaders = HTTP_CONFIG.headers;
  }

  private async fetchWithRetry(
    url: string, 
    options: RequestInit = {}, 
    retries = API_CONFIG.MAX_RETRY_ATTEMPTS
  ): Promise<Response> {
    const fullUrl = url.startsWith('http') ? url : `${this.baseUrl}${url}`;
    
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await fetch(fullUrl, {
          ...options,
          headers: {
            ...this.defaultHeaders,
            ...options.headers,
          },
        });

        if (response.ok) {
          return response;
        }

        // If it's the last attempt or a non-retriable error, throw
        if (attempt === retries || response.status < 500) {
          const errorData = await response.json().catch(() => ({}));
          throw new ApiError(
            errorData.message || `HTTP ${response.status}: ${response.statusText}`,
            response.status,
            errorData
          );
        }

      } catch (error) {
        if (attempt === retries) {
          throw error;
        }
        
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, API_CONFIG.RETRY_DELAY * (attempt + 1)));
      }
    }

    throw new Error('Max retries exceeded');
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    // Handle non-JSON responses
    const text = await response.text();
    return text as unknown as T;
  }

  // Health Check
  async checkHealth(): Promise<HealthResponse> {
    const response = await this.fetchWithRetry(ENDPOINTS.HEALTH);
    return this.handleResponse<HealthResponse>(response);
  }

  // LLM Service Status
  async getLLMStatus(): Promise<LLMStatusResponse> {
    const response = await this.fetchWithRetry(ENDPOINTS.LLM_STATUS);
    return this.handleResponse<LLMStatusResponse>(response);
  }

  // Work Items Polling
  async pollWorkItems(params: {
    sinceId?: number;
    since?: string;
    limit?: number;
  } = {}): Promise<WorkItemDto[]> {
    const url = new URL(ENDPOINTS.WORKITEMS_POLL, this.baseUrl);
    
    if (params.sinceId) url.searchParams.set('sinceId', params.sinceId.toString());
    if (params.since) url.searchParams.set('since', params.since);
    if (params.limit) url.searchParams.set('limit', params.limit.toString());

    const response = await this.fetchWithRetry(url.toString());
    return this.handleResponse<WorkItemDto[]>(response);
  }

  // Get Work Item by ID
  async getWorkItem(id: number): Promise<WorkItemDto> {
    const response = await this.fetchWithRetry(ENDPOINTS.WORKITEMS_DETAIL(id));
    return this.handleResponse<WorkItemDto>(response);
  }

  // Update Work Item Status
  async updateWorkItemStatus(id: number, status: string): Promise<WorkItemDto> {
    const response = await this.fetchWithRetry(ENDPOINTS.WORKITEMS_UPDATE_STATUS(id), {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
    return this.handleResponse<WorkItemDto>(response);
  }

  // Assign Work Item
  async assignWorkItem(id: number, assignedTo: string): Promise<WorkItemDto> {
    const response = await this.fetchWithRetry(ENDPOINTS.WORKITEMS_ASSIGN(id), {
      method: 'PUT',
      body: JSON.stringify({ assigned_to: assignedTo }),
    });
    return this.handleResponse<WorkItemDto>(response);
  }

  // Update Work Item Priority
  async updateWorkItemPriority(id: number, priority: string): Promise<WorkItemDto> {
    const response = await this.fetchWithRetry(ENDPOINTS.WORKITEMS_UPDATE_PRIORITY(id), {
      method: 'PUT',
      body: JSON.stringify({ priority }),
    });
    return this.handleResponse<WorkItemDto>(response);
  }

  // Get Work Items Needing Attention
  async getWorkItemsNeedingAttention(): Promise<WorkItemDto[]> {
    const response = await this.fetchWithRetry(ENDPOINTS.WORKITEMS_ATTENTION);
    return this.handleResponse<WorkItemDto[]>(response);
  }

  // Search Work Items
  async searchWorkItems(params: {
    q: string;
    page?: number;
    size?: number;
  }): Promise<{ content: WorkItemDto[]; totalElements: number; totalPages: number }> {
    const url = new URL(ENDPOINTS.WORKITEMS_SEARCH, this.baseUrl);
    
    url.searchParams.set('q', params.q);
    if (params.page) url.searchParams.set('page', params.page.toString());
    if (params.size) url.searchParams.set('size', params.size.toString());

    const response = await this.fetchWithRetry(url.toString());
    return this.handleResponse(response);
  }

  // Get Work Items for Submission
  async getWorkItemsForSubmission(submissionId: number): Promise<WorkItemDto[]> {
    const response = await this.fetchWithRetry(ENDPOINTS.WORKITEMS_FOR_SUBMISSION(submissionId));
    return this.handleResponse<WorkItemDto[]>(response);
  }

  // Email Intake
  async submitEmailIntake(emailData: EmailIntakeRequest): Promise<EmailIntakeResponse> {
    const response = await this.fetchWithRetry(ENDPOINTS.EMAIL_INTAKE, {
      method: 'POST',
      body: JSON.stringify(emailData),
    });
    return this.handleResponse<EmailIntakeResponse>(response);
  }

  // Create Work Item
  async createWorkItem(workItem: Partial<WorkItemDto>): Promise<WorkItemDto> {
    const response = await this.fetchWithRetry('/api/workitems', {
      method: 'POST',
      body: JSON.stringify(workItem),
    });
    return this.handleResponse<WorkItemDto>(response);
  }

  // Update Work Item
  async updateWorkItem(id: number, workItem: Partial<WorkItemDto>): Promise<WorkItemDto> {
    const response = await this.fetchWithRetry(`/api/workitems/${id}`, {
      method: 'PUT',
      body: JSON.stringify(workItem),
    });
    return this.handleResponse<WorkItemDto>(response);
  }
}

// Custom Error Class
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// React Hook for API Client (if using React)
import { useCallback, useState } from 'react';

export function useApiClient() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const executeRequest = useCallback(async <T>(
    request: Promise<T>
  ): Promise<T | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await request;
      return result;
    } catch (err) {
      const errorMessage = err instanceof ApiError 
        ? err.message 
        : err instanceof Error 
        ? err.message 
        : 'An unknown error occurred';
      
      setError(errorMessage);
      console.error('API Request Error:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    executeRequest,
    client: apiClient,
  };
}

// Polling Hook for Work Items
export function useWorkItemPolling(
  onNewItems: (items: WorkItemDto[]) => void,
  interval = API_CONFIG.POLL_INTERVAL
) {
  const [isPolling, setIsPolling] = useState(false);
  const [lastPollTime, setLastPollTime] = useState<string | null>(null);

  const startPolling = useCallback(() => {
    if (isPolling) return;
    
    setIsPolling(true);
    
    const poll = async () => {
      try {
        const params: any = {};
        if (lastPollTime) {
          params.since = lastPollTime;
        }
        
        const items = await apiClient.pollWorkItems(params);
        
        if (items && items.length > 0) {
          onNewItems(items);
          setLastPollTime(new Date().toISOString());
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    };

    // Initial poll
    poll();
    
    // Set up interval
    const intervalId = setInterval(poll, interval);
    
    return () => {
      clearInterval(intervalId);
      setIsPolling(false);
    };
  }, [isPolling, lastPollTime, onNewItems, interval]);

  const stopPolling = useCallback(() => {
    setIsPolling(false);
  }, []);

  return {
    isPolling,
    startPolling,
    stopPolling,
  };
}

export default apiClient;