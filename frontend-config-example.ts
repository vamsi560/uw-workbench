// Frontend Configuration for Java Backend Integration
// File: src/lib/config.ts (or similar path in your frontend project)

// API Configuration
export const API_CONFIG = {
  // Base URLs
  API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  POLL_URL: process.env.NEXT_PUBLIC_POLL_URL || 'http://localhost:8080/api/workitems/poll',
  HEALTH_URL: process.env.NEXT_PUBLIC_HEALTH_URL || 'http://localhost:8080/api/health',
  LLM_STATUS_URL: process.env.NEXT_PUBLIC_LLM_STATUS_URL || 'http://localhost:8080/api/llm/status',
  
  // Feature flags
  USE_JAVA_BACKEND: process.env.NEXT_PUBLIC_USE_JAVA_BACKEND === 'true',
  ENABLE_ENHANCED_FEATURES: process.env.NEXT_PUBLIC_ENABLE_ENHANCED_FEATURES === 'true',
  
  // Polling configuration
  POLL_INTERVAL: 5000, // 5 seconds
  MAX_RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
} as const;

// Validate configuration
const requiredEnvVars = ['NEXT_PUBLIC_API_URL'] as const;

for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    console.warn(`Missing environment variable: ${envVar}`);
  }
}

// Log configuration (only in development)
if (process.env.NODE_ENV === 'development') {
  console.log('Frontend API Configuration:', {
    API_URL: API_CONFIG.API_URL,
    POLL_URL: API_CONFIG.POLL_URL,
    USE_JAVA_BACKEND: API_CONFIG.USE_JAVA_BACKEND,
    ENABLE_ENHANCED_FEATURES: API_CONFIG.ENABLE_ENHANCED_FEATURES
  });
}

// Export individual configs for backward compatibility
export const API_URL = API_CONFIG.API_URL;
export const POLL_URL = API_CONFIG.POLL_URL;
export const HEALTH_URL = API_CONFIG.HEALTH_URL;
export const LLM_STATUS_URL = API_CONFIG.LLM_STATUS_URL;

// API Endpoints
export const ENDPOINTS = {
  // Work Items
  WORKITEMS_POLL: '/api/workitems/poll',
  WORKITEMS_DETAIL: (id: number) => `/api/workitems/${id}`,
  WORKITEMS_UPDATE_STATUS: (id: number) => `/api/workitems/${id}/status`,
  WORKITEMS_ASSIGN: (id: number) => `/api/workitems/${id}/assign`,
  WORKITEMS_UPDATE_PRIORITY: (id: number) => `/api/workitems/${id}/priority`,
  WORKITEMS_FOR_SUBMISSION: (submissionId: number) => `/api/submissions/${submissionId}/workitems`,
  WORKITEMS_ATTENTION: '/api/workitems/attention',
  WORKITEMS_SEARCH: '/api/workitems/search',
  
  // Submissions
  EMAIL_INTAKE: '/api/email/intake',
  
  // System
  HEALTH: '/api/health',
  LLM_STATUS: '/api/llm/status',
} as const;

// Type definitions for API responses
export interface WorkItemDto {
  id: number;
  submissionId: number;
  title: string;
  description: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'REJECTED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  assignedTo?: string;
  riskScore?: number;
  riskCategories?: string[];
  industry?: string;
  companySize?: string;
  policyType?: string;
  coverageAmount?: number;
  lastRiskAssessment?: string;
  createdAt: string;
  updatedAt: string;
  submission?: any; // SubmissionDto if included
}

export interface EmailIntakeRequest {
  sender_email: string;
  subject: string;
  email_content: string;
  attachments?: any[];
}

export interface EmailIntakeResponse {
  message: string;
  submission_id: number;
  submission_ref: string;
  work_item_id: number;
  status: string;
  extracted_fields: Record<string, any>;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  service: string;
  llm_service_available: boolean;
}

export interface LLMStatusResponse {
  available: boolean;
  models: string[];
  timestamp: string;
}

export interface ApiErrorResponse {
  error: string;
  message: string;
  timestamp: string;
}

// HTTP Client configuration
export const HTTP_CONFIG = {
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 30000, // 30 seconds
} as const;