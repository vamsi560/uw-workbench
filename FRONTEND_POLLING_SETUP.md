# Frontend Polling Setup Guide

## Overview
This guide helps you update your frontend to use polling instead of SSE for real-time work item updates. This change eliminates Vercel timeout issues while maintaining near real-time functionality.

---

## 1. Environment Variables

Add this to your `.env.local` file:

```env
NEXT_PUBLIC_POLL_URL=https://uw-workbench-jade.vercel.app/api/workitems/poll
NEXT_PUBLIC_API_URL=https://uw-workbench-jade.vercel.app
```



## 2. Update Config File

Create or update `src/lib/config.ts`:

```typescript
export const API_URL = process.env.NEXT_PUBLIC_API_URL!;
export const POLL_URL = process.env.NEXT_PUBLIC_POLL_URL!;
// Optional: Keep WebSocket URL for fallback if moving off Vercel
export const WS_URL = process.env.NEXT_PUBLIC_WEBSOCKET_URL;
```

---

## 3. Create Polling Hook

Create `src/hooks/use-polling.ts`:

```typescript
import { useEffect, useRef, useState, useCallback } from 'react';
import { POLL_URL } from '@/lib/config';

export function usePolling(onNewItems: (items: any[]) => void, interval = 5000) {
  const [isPolling, setIsPolling] = useState(false);
  const lastPollTime = useRef<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const poll = useCallback(async () => {
    try {
      const url = new URL(POLL_URL);
      if (lastPollTime.current) {
        url.searchParams.set('since', lastPollTime.current);
      }

      const response = await fetch(url.toString());
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      
      if (data.items && data.items.length > 0) {
        onNewItems(data.items);
      }
      
      // Update last poll time to current server timestamp
      lastPollTime.current = data.timestamp;
      
    } catch (error) {
      console.error('Polling error:', error);
    }
  }, [onNewItems]);

  const startPolling = useCallback(() => {
    if (intervalRef.current) return; // Already polling
    
    setIsPolling(true);
    // Poll immediately, then at intervals
    poll();
    intervalRef.current = setInterval(poll, interval);
  }, [poll, interval]);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsPolling(false);
  }, []);

  useEffect(() => {
    startPolling();
    return stopPolling;
  }, [startPolling, stopPolling]);

  return { isPolling, startPolling, stopPolling };
}
```

---

## 4. Create/Update Work Item Updates Hook

Create or update `src/hooks/use-workitem-updates.ts`:

```typescript
import { useCallback, useState } from 'react';
import { usePolling } from './use-polling';

export function useWorkItemUpdates() {
  const [items, setItems] = useState<any[]>([]);

  const handleNewItems = useCallback((newItems: any[]) => {
    // Add new items to the beginning of the list
    setItems((prev) => {
      // Avoid duplicates by filtering out items we already have
      const existingIds = new Set(prev.map(item => item.submission_ref));
      const uniqueNewItems = newItems.filter(item => !existingIds.has(item.submission_ref));
      return [...uniqueNewItems, ...prev];
    });
    
    // Optional: Add toast notification for new items
    if (newItems.length > 0) {
      console.log(`Received ${newItems.length} new work items`);
      // You can add toast notifications here if desired
    }
  }, []);

  const { isPolling } = usePolling(handleNewItems, 5000); // Poll every 5 seconds

  return { items, connected: isPolling };
}
```

---

## 5. Update Your UI Components

Update your workbench component (e.g., `src/components/workbench/workbench-client.tsx`):

```typescript
import { useWorkItemUpdates } from '@/hooks/use-workitem-updates';

export default function WorkbenchClient() {
  const { items, connected } = useWorkItemUpdates();

  return (
    <div className="workbench-container">
      {/* Status indicator */}
      <div className="status-bar">
        <span className={`status-indicator ${connected ? 'active' : 'inactive'}`}>
          Polling: {connected ? 'Active' : 'Inactive'}
        </span>
      </div>

      {/* Work items list */}
      <div className="work-items">
        <h2>Work Items ({items.length})</h2>
        {items.length === 0 ? (
          <p>No work items yet...</p>
        ) : (
          <ul>
            {items.map((item) => (
              <li key={item.submission_ref} className="work-item">
                <div className="item-header">
                  <span className="submission-id">#{item.submission_id}</span>
                  <span className={`status ${item.status}`}>{item.status}</span>
                </div>
                <div className="item-content">
                  <h3>{item.subject}</h3>
                  <p>From: {item.from_email}</p>
                  <p>Created: {new Date(item.created_at).toLocaleString()}</p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
```

---

## 6. Optional: Add CSS Styles

Add these styles to your CSS file:

```css
.status-indicator.active {
  color: green;
}

.status-indicator.inactive {
  color: red;
}

.work-item {
  border: 1px solid #ddd;
  padding: 1rem;
  margin: 0.5rem 0;
  border-radius: 4px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.status.pending {
  background: orange;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}

.status.in_progress {
  background: blue;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}
```

---

## 7. Testing

1. **Start your frontend** and confirm the status shows "Polling: Active"

2. **Test with curl or Postman**:
   ```bash
   # Create a test work item
   POST https://your-vercel-app.vercel.app/api/test/workitem
   
   # Manual polling test
   GET https://your-vercel-app.vercel.app/api/workitems/poll
   ```

3. **Verify new items appear** within 5 seconds in your frontend

---

## 8. API Response Format

Your frontend will receive this format from the polling endpoint:

```json
{
  "items": [
    {
      "id": 123,
      "submission_id": 456,
      "submission_ref": "uuid-string",
      "subject": "Insurance Policy Submission",
      "from_email": "broker@example.com",
      "created_at": "2025-09-28T10:15:00Z",
      "status": "pending",
      "extracted_fields": {
        "insured_name": "Company Name",
        "policy_type": "General Liability"
      }
    }
  ],
  "count": 1,
  "timestamp": "2025-09-28T10:15:30Z"
}
```

---

## 9. Configuration Options

You can customize the polling behavior:

```typescript
// Poll every 3 seconds (more frequent)
const { isPolling } = usePolling(handleNewItems, 3000);

// Poll every 10 seconds (less frequent)
const { isPolling } = usePolling(handleNewItems, 10000);
```

**Recommended intervals:**
- **High activity**: 3-5 seconds
- **Normal activity**: 5-10 seconds
- **Low activity**: 10-30 seconds

---

## 10. Benefits

✅ **No more Vercel timeouts** - Each request completes quickly  
✅ **Near real-time updates** - 5-second delay feels immediate  
✅ **Efficient** - Only fetches new items using timestamps  
✅ **Scalable** - No persistent connections  
✅ **Same user experience** - Items appear automatically  

---

## 11. Migration from SSE

If you're migrating from SSE:

1. **Remove SSE hooks** (use-sse.ts, EventSource code)
2. **Replace SSE_URL** with POLL_URL in config
3. **Update imports** to use new polling hooks
4. **Test thoroughly** to ensure all functionality works

The UI interface remains the same - users won't notice the difference!