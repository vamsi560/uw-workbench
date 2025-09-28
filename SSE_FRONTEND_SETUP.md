# Frontend Realtime (Polling) Integration Guide

## Summary
Enable real-time updates in the frontend using polling against the backend endpoint `GET /## 6) Optional: WebSocket Fallback
If you keep a WebSocket hook, you can conditionally use it when polling fails. Example sketch inside `useWorkItemUpdates`:

```ts
// pseudo-code: start WS connection if polling fails multiple times
// This would be useful if you move backend off Vercel to support WebSockets
```kitems/poll`. This approach is optimized for Vercel serverless functions and avoids SSE timeout issues. Keep WebSocket code as optional fallback if you plan to move the backend off Vercel.

---

## 1) Environment Variables
Create or update `.env.local` in the frontend:

```
NEXT_PUBLIC_API_URL=https://<your-vercel-app>.vercel.app
NEXT_PUBLIC_POLL_URL=https://<your-vercel-app>.vercel.app/api/workitems/poll
# Optional (only if keeping WS fallback)
NEXT_PUBLIC_WEBSOCKET_URL=wss://<your-vercel-app>.vercel.app/ws/workitems
```

---

## 2) Config
Create/update `src/lib/config.ts`:

```ts
export const API_URL = process.env.NEXT_PUBLIC_API_URL!;
export const POLL_URL = process.env.NEXT_PUBLIC_POLL_URL!;
export const WS_URL = process.env.NEXT_PUBLIC_WEBSOCKET_URL; // optional fallback
```

---

## 3) Polling Hook
Create `src/hooks/use-polling.ts`:

```ts
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

## 4) Work Item Updates Hook
Update/create `src/hooks/use-workitem-updates.ts`:

```ts
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
    
    // TODO: trigger toast/notification if desired
    if (newItems.length > 0) {
      console.log(`Received ${newItems.length} new work items`);
    }
  }, []);

  const { isPolling } = usePolling(handleNewItems, 5000); // Poll every 5 seconds

  return { items, connected: isPolling };
}
```

---

## 5) UI Integration
In your client component (e.g., `src/components/workbench/workbench-client.tsx`):

```tsx
import { useWorkItemUpdates } from '@/hooks/use-workitem-updates';

export default function WorkbenchClient() {
  const { items, connected } = useWorkItemUpdates();

  return (
    <div>
      <div>Polling: {connected ? 'Active' : 'Inactive'}</div>
      <ul>
        {items.map((item) => (
          <li key={item.submission_ref}>
            #{item.submission_id} — {item.subject} — {item.status}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 6) Optional: WebSocket Fallback
If you keep a WebSocket hook, you can conditionally use it when SSE isn’t connected after N seconds. Example sketch inside `useWorkItemUpdates`:

```ts
// pseudo-code
// if (!connected) start WS via WS_URL and reuse the same handleMessage
```

---

## 7) Testing
- Open the frontend, confirm status shows **Active**.
- Call the backend test route to create a new work item:

```
POST https://<your-vercel-app>.vercel.app/api/test/workitem
```

- Verify new item appears within 5 seconds (or your configured polling interval).
- Test manual polling:

```
GET https://<your-vercel-app>.vercel.app/api/workitems/poll
GET https://<your-vercel-app>.vercel.app/api/workitems/poll?since=2025-09-28T10:00:00Z
```

---

## 8) API Contract
Backend polling endpoint returns:

```json
{
  "items": [
    {
      "id": 123,
      "submission_id": 456,
      "submission_ref": "uuid",
      "subject": "Insurance Policy Submission",
      "from_email": "broker@example.com",
      "created_at": "2025-09-28T06:00:00Z",
      "status": "pending",
      "extracted_fields": { }
    }
  ],
  "count": 1,
  "timestamp": "2025-09-28T10:15:00Z"
}
```

---

## 9) Notes
- Polling works perfectly with Vercel serverless functions and avoids timeout issues.
- Recommended polling interval: 5-10 seconds for real-time feel without overwhelming the server.
- Keep WS code if you plan to move backend to a host that supports WebSockets for true real-time.
- CORS for polling: handled like normal HTTP; your backend already permits `*` by default.
- The `since` parameter ensures you only get new items, avoiding duplicate processing.
