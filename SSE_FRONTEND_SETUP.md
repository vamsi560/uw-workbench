# Frontend Realtime (SSE) Integration Guide

## Summary
Enable real-time updates in the frontend using Server-Sent Events (SSE) against the backend endpoint `GET /sse/workitems`. Keep WebSocket code as optional fallback if you plan to move the backend off Vercel.

---

## 1) Environment Variables
Create or update `.env.local` in the frontend:

```
NEXT_PUBLIC_SSE_URL=https://<your-vercel-app>.vercel.app/sse/workitems
NEXT_PUBLIC_API_URL=https://<your-vercel-app>.vercel.app
# Optional (only if keeping WS fallback)
NEXT_PUBLIC_WEBSOCKET_URL=wss://<your-vercel-app>.vercel.app/ws/workitems
```

---

## 2) Config
Create/update `src/lib/config.ts`:

```ts
export const SSE_URL = process.env.NEXT_PUBLIC_SSE_URL!;
export const API_URL = process.env.NEXT_PUBLIC_API_URL!;
export const WS_URL = process.env.NEXT_PUBLIC_WEBSOCKET_URL; // optional fallback
```

---

## 3) SSE Hook
Create `src/hooks/use-sse.ts`:

```ts
import { useEffect, useRef, useState } from 'react';
import { SSE_URL } from '@/lib/config';

export function useSse(onMessage: (msg: any) => void) {
  const esRef = useRef<EventSource | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!SSE_URL) return;

    const es = new EventSource(SSE_URL, { withCredentials: false });
    esRef.current = es;

    es.onopen = () => setConnected(true);
    es.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        onMessage?.(msg);
      } catch {}
    };
    es.onerror = () => {
      setConnected(false);
      // Let browser auto-retry; optionally implement custom backoff
    };

    return () => {
      es.close();
      esRef.current = null;
    };
  }, [onMessage]);

  return { connected };
}
```

---

## 4) Work Item Updates Hook
Update/create `src/hooks/use-workitem-updates.ts`:

```ts
import { useCallback, useState } from 'react';
import { useSse } from './use-sse';

export function useWorkItemUpdates() {
  const [items, setItems] = useState<any[]>([]);

  const handleMessage = useCallback((msg: any) => {
    if (msg?.event === 'new_workitem' && msg.data) {
      setItems((prev) => [msg.data, ...prev]);
      // TODO: trigger toast/notification if desired
    }
  }, []);

  const { connected } = useSse(handleMessage);

  return { items, connected };
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
      <div>Realtime: {connected ? 'Connected' : 'Disconnected'}</div>
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
- Open the frontend, confirm status shows **Connected**.
- Call the backend test route to emit an event:

```
POST https://<your-vercel-app>.vercel.app/api/test/workitem
```

- Verify new item appears instantly.

---

## 8) Event Contract
Backend sends messages as:

```json
{
  "event": "new_workitem",
  "data": {
    "id": 123,
    "submission_id": 456,
    "submission_ref": "uuid",
    "subject": "Insurance Policy Submission",
    "from_email": "broker@example.com",
    "created_at": "2025-09-28T06:00:00Z",
    "status": "pending",
    "extracted_fields": { }
  }
}
```

---

## 9) Notes
- SSE works on Vercel with Python backend. No extra config needed.
- Keep WS code if you plan to move backend to a host that supports WebSockets.
- CORS for SSE: handled like normal HTTP; your backend already permits `*` by default.
