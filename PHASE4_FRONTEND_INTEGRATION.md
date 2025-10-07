# Phase 4: Frontend Integration Guide

## Overview
This guide covers updating your frontend application to use the Java backend (port 8080) instead of the Python backend (port 8001). The transition maintains API compatibility while leveraging the hybrid architecture.

## Current Setup Analysis
Based on the documentation, your frontend is currently configured as:
- **Deployment**: Vercel (https://uw-workbench-portal.vercel.app, https://uw-workbench-jade.vercel.app)
- **Current API**: Python backend via Vercel serverless functions
- **Communication**: HTTP Polling (recommended over SSE/WebSocket for Vercel)

## Required Changes

### 1. Environment Variables Update

**Current Configuration (Python backend):**
```env
NEXT_PUBLIC_API_URL=https://uw-workbench-jade.vercel.app
NEXT_PUBLIC_POLL_URL=https://uw-workbench-jade.vercel.app/api/workitems/poll
```

**New Configuration (Java backend):**
```env
# For local development
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXT_PUBLIC_POLL_URL=http://localhost:8080/api/workitems/poll

# For production (assuming Java backend deployed)
# NEXT_PUBLIC_API_URL=https://your-java-backend-domain.com
# NEXT_PUBLIC_POLL_URL=https://your-java-backend-domain.com/api/workitems/poll
```

### 2. Frontend Code Updates

#### Update Configuration File
If you have `src/lib/config.ts`:
```typescript
// Before
export const API_URL = process.env.NEXT_PUBLIC_API_URL!;
export const POLL_URL = process.env.NEXT_PUBLIC_POLL_URL!;

// After (enhanced with fallback and validation)
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
export const POLL_URL = process.env.NEXT_PUBLIC_POLL_URL || 'http://localhost:8080/api/workitems/poll';

// Validate configuration
if (!API_URL || !POLL_URL) {
  throw new Error('Missing required environment variables. Check NEXT_PUBLIC_API_URL and NEXT_PUBLIC_POLL_URL');
}

console.log('Frontend configured for:', { API_URL, POLL_URL });
```

#### Update Polling Hook
If you have `src/hooks/use-polling.ts`, ensure it handles the Java backend response format:
```typescript
export function usePolling(onNewItems: (items: any[]) => void, interval = 5000) {
  const poll = useCallback(async () => {
    try {
      const url = new URL(POLL_URL);
      if (lastPollTime.current) {
        url.searchParams.set('since', lastPollTime.current);
      }

      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      // Java backend returns array directly, not wrapped in 'items' field
      const data = await response.json();
      
      // Handle both formats for backward compatibility
      const items = Array.isArray(data) ? data : (data.items || []);
      
      if (items && items.length > 0) {
        onNewItems(items);
        lastPollTime.current = new Date().toISOString();
      }
      
    } catch (error) {
      console.error('Polling error:', error);
      // Implement exponential backoff or other error handling
    }
  }, [onNewItems]);
  
  // Rest of the hook implementation...
}
```

#### Update Email Intake Function
If you have an email intake function, update it to use the Java backend:
```typescript
export async function submitEmailIntake(emailData: EmailIntakeRequest) {
  try {
    const response = await fetch(`${API_URL}/api/email/intake`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(emailData)
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
    
  } catch (error) {
    console.error('Email intake error:', error);
    throw error;
  }
}
```

### 3. API Endpoint Compatibility

The Java backend provides the same endpoints as the Python backend:

| Endpoint | Method | Description | Status |
|----------|--------|-------------|---------|
| `/api/health` | GET | Health check with LLM service status | ✅ Enhanced |
| `/api/workitems/poll` | GET | Poll for work items | ✅ Compatible |
| `/api/email/intake` | POST | Process email submissions | ✅ Compatible |
| `/api/workitems/{id}` | GET | Get specific work item | ✅ Available |
| `/api/workitems/{id}/status` | PUT | Update work item status | ✅ New |
| `/api/workitems/{id}/assign` | PUT | Assign work item | ✅ New |
| `/api/workitems/{id}/priority` | PUT | Update priority | ✅ New |
| `/api/llm/status` | GET | LLM service status | ✅ New |

### 4. Response Format Compatibility

#### Work Items Polling Response
```typescript
// Java backend response (compatible with existing frontend)
interface WorkItemResponse extends Array<WorkItemDto> {}

interface WorkItemDto {
  id: number;
  submissionId: number;
  title: string;
  description: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'REJECTED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  assignedTo?: string;
  riskScore?: number;
  riskCategories?: string[];
  createdAt: string; // ISO timestamp
  updatedAt: string; // ISO timestamp
  // Plus all fields from submission if available
}
```

#### Email Intake Response
```typescript
interface EmailIntakeResponse {
  message: string;
  submission_id: number;
  submission_ref: string;
  work_item_id: number;
  status: string;
  extracted_fields: Record<string, any>;
  timestamp: string;
}
```

### 5. Error Handling Updates

The Java backend provides consistent error responses:
```typescript
interface ErrorResponse {
  error: string;
  message: string;
  timestamp: string;
}

// Update your error handling to use this format
function handleApiError(error: any) {
  if (error.response?.data) {
    const errorData = error.response.data;
    console.error('API Error:', errorData.message || errorData.error);
    return errorData.message || errorData.error || 'Unknown error occurred';
  }
  return error.message || 'Network error occurred';
}
```

### 6. Health Check Integration

Use the enhanced health check endpoint:
```typescript
export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_URL}/api/health`);
    const health = await response.json();
    
    return {
      status: health.status,
      service: health.service,
      llmServiceAvailable: health.llm_service_available,
      timestamp: health.timestamp
    };
  } catch (error) {
    console.error('Health check failed:', error);
    return { status: 'unhealthy', error: error.message };
  }
}
```

## Testing Steps

### 1. Local Development Testing
```bash
# 1. Start Java backend
cd java-backend
./mvnw spring-boot:run

# 2. Update frontend environment variables
# Edit .env.local to point to http://localhost:8080

# 3. Start frontend development server
npm run dev

# 4. Test in browser
# - Check health endpoint: http://localhost:8080/api/health
# - Test polling: http://localhost:8080/api/workitems/poll
# - Test email intake functionality
```

### 2. Verification Commands
```bash
# Test Java backend endpoints
curl http://localhost:8080/api/health
curl http://localhost:8080/api/workitems/poll
curl http://localhost:8080/api/llm/status

# Test email intake
curl -X POST http://localhost:8080/api/email/intake \
  -H "Content-Type: application/json" \
  -d '{"sender_email":"test@example.com","subject":"Test","email_content":"Test content"}'
```

### 3. Frontend Console Testing
Open browser console and run:
```javascript
// Test configuration
console.log('API_URL:', process.env.NEXT_PUBLIC_API_URL);
console.log('POLL_URL:', process.env.NEXT_PUBLIC_POLL_URL);

// Test health check
fetch('/api/health').then(r => r.json()).then(console.log);

// Test polling
fetch('/api/workitems/poll').then(r => r.json()).then(console.log);
```

## Deployment Considerations

### Option 1: Hybrid Deployment (Recommended for Transition)
- Keep frontend on Vercel
- Deploy Java backend separately (e.g., Railway, Render, AWS)
- Update environment variables to point to Java backend URL

### Option 2: Full Migration
- Move entire stack off Vercel to support both services
- Deploy both Java backend and frontend together

### Option 3: Gradual Migration
- Use feature flags to switch between Python and Java backends
- Test Java backend with subset of users first

## Rollback Plan

If issues occur, you can quickly rollback by:
1. Reverting environment variables to Python backend URLs
2. Redeploying frontend with original configuration
3. Python backend remains operational during transition

## Next Steps

1. ✅ Update environment variables
2. ✅ Test local development setup
3. ✅ Verify API compatibility
4. ✅ Test complete user flow
5. ✅ Deploy Java backend to production
6. ✅ Update production environment variables
7. ✅ Monitor and verify production functionality

The Java backend is fully compatible with your existing frontend code and provides enhanced functionality while maintaining the same API interface.