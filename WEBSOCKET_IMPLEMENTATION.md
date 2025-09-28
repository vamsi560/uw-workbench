# WebSocket Real-time Implementation

## 🚀 **Overview**

This implementation adds real-time WebSocket functionality to your FastAPI backend, allowing the frontend to receive instant updates when new work items are created or status changes occur.

## 📁 **Files Added/Modified**

### **New Files:**
- `websocket_manager.py` - WebSocket connection management
- `frontend_websocket_example.html` - Complete frontend example
- `WEBSOCKET_IMPLEMENTATION.md` - This documentation

### **Modified Files:**
- `main.py` - Added WebSocket endpoints and broadcast integration
- `requirements.txt` - Added WebSocket dependencies

## 🔧 **Backend Implementation**

### **1. WebSocket Manager (`websocket_manager.py`)**

```python
class WebSocketManager:
    - Manages active WebSocket connections
    - Handles connection/disconnection
    - Broadcasts messages to all connected clients
    - Includes error handling and dead connection cleanup
```

**Key Methods:**
- `connect(websocket)` - Accept new connections
- `disconnect(websocket)` - Remove connections
- `broadcast_workitem(data)` - Send new work item to all clients
- `broadcast_status_update(ref, status)` - Send status updates

### **2. WebSocket Endpoint (`/ws/workitems`)**

```python
@app.websocket("/ws/workitems")
async def websocket_endpoint(websocket: WebSocket):
    # Handles WebSocket connections
    # Keeps connections alive
    # Manages disconnections gracefully
```

### **3. Integration with Email Intake**

The existing `/api/email/intake` endpoint now:
1. Processes email and creates submission
2. **Automatically broadcasts** the new work item to all connected clients
3. Returns the same response as before

### **4. Test Endpoint (`/api/test/workitem`)**

```python
@app.post("/api/test/workitem")
async def test_workitem(db: Session = Depends(get_db)):
    # Creates a fake work item
    # Broadcasts it to all connected clients
    # Returns connection count for monitoring
```

## 📡 **WebSocket Message Format**

### **New Work Item Event:**
```json
{
  "event": "new_workitem",
  "data": {
    "id": 123,
    "submission_id": 456,
    "submission_ref": "uuid-string",
    "subject": "Insurance Policy Submission",
    "from_email": "broker@example.com",
    "created_at": "2025-09-28T06:00:00Z",
    "status": "pending",
    "extracted_fields": {
      "insured_name": "ABC Corp",
      "policy_type": "General Liability",
      "coverage_amount": "$2,000,000",
      "effective_date": "2024-01-01",
      "broker": "Smith Insurance"
    }
  }
}
```

### **Status Update Event:**
```json
{
  "event": "status_update",
  "data": {
    "submission_ref": "uuid-string",
    "status": "in_progress",
    "updated_at": "2025-09-28T06:30:00Z"
  }
}
```

## 🎨 **Frontend Integration**

### **1. Basic WebSocket Connection (JavaScript)**

```javascript
const socket = new WebSocket("wss://your-app.vercel.app/ws/workitems");

socket.onopen = function(event) {
    console.log("WebSocket connected");
};

socket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    
    if (message.event === "new_workitem") {
        console.log("New Work Item:", message.data);
        // Add to UI
        addWorkItemToUI(message.data);
    }
    
    if (message.event === "status_update") {
        console.log("Status Update:", message.data);
        // Update UI
        updateWorkItemStatus(message.data);
    }
};

socket.onclose = function(event) {
    console.log("WebSocket disconnected");
    // Implement reconnection logic
};
```

### **2. Complete Frontend Example**

The `frontend_websocket_example.html` includes:
- **Real-time dashboard** with work items
- **Connection status** indicator
- **Test controls** for creating fake work items
- **Responsive design** with animations
- **Error handling** and reconnection logic

## 🧪 **Testing the Implementation**

### **1. Test WebSocket Connection:**
```bash
# Using wscat (install with: npm install -g wscat)
wscat -c wss://your-app.vercel.app/ws/workitems
```

### **2. Test Work Item Creation:**
```bash
# Create a test work item
curl -X POST https://your-app.vercel.app/api/test/workitem
```

### **3. Test Email Intake (Real Data):**
```bash
# Send real email data
curl -X POST https://your-app.vercel.app/api/email/intake \
  -H "Content-Type: application/json" \
  -d @corrected_test_payload.json
```

## 🔄 **Real-time Flow**

### **Complete End-to-End Flow:**

1. **Email Received** → Logic App processes email
2. **API Call** → Logic App sends data to `/api/email/intake`
3. **Database Save** → FastAPI saves submission to database
4. **WebSocket Broadcast** → FastAPI broadcasts to all connected clients
5. **Frontend Update** → Connected browsers receive real-time update
6. **UI Refresh** → Work item appears instantly in dashboard

## 🛡️ **Error Handling & Resilience**

### **Backend:**
- **Dead connection cleanup** - Removes failed connections automatically
- **Graceful disconnection** - Handles client disconnects without crashing
- **Error logging** - Comprehensive logging for debugging
- **Null safety** - Handles missing data gracefully

### **Frontend:**
- **Connection status** - Visual indicator of WebSocket state
- **Reconnection logic** - Can be added for automatic reconnection
- **Error handling** - Graceful handling of connection failures
- **Message validation** - Validates incoming WebSocket messages

## 📊 **Monitoring & Debugging**

### **Connection Monitoring:**
```python
# Get active connection count
websocket_manager.get_connection_count()
```

### **Logs to Watch:**
- `WebSocket connected. Total connections: X`
- `Broadcasting work item to X connections`
- `WebSocket disconnected. Total connections: X`

### **Frontend Console:**
- Connection status messages
- Incoming WebSocket messages
- Error messages for debugging

## 🚀 **Deployment Considerations**

### **Vercel WebSocket Support:**
- WebSockets are supported on Vercel
- No additional configuration needed
- Works with your existing deployment

### **Scaling:**
- Current implementation uses in-memory connection storage
- For multiple server instances, consider Redis for connection sharing
- Current setup works well for single-instance deployments

## 🔮 **Future Enhancements**

### **Potential Improvements:**
1. **User-specific filtering** - Only show work items for specific underwriters
2. **Redis integration** - For multi-instance scaling
3. **Authentication** - Secure WebSocket connections
4. **Message persistence** - Store messages for offline clients
5. **Rate limiting** - Prevent WebSocket spam
6. **Heartbeat/ping** - Keep connections alive longer

## 📝 **Usage Examples**

### **1. Basic Integration:**
```javascript
// Connect to WebSocket
const socket = new WebSocket("wss://your-app.vercel.app/ws/workitems");

// Listen for new work items
socket.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.event === "new_workitem") {
        addWorkItemToTable(msg.data);
    }
};
```

### **2. React Integration:**
```jsx
useEffect(() => {
    const socket = new WebSocket("wss://your-app.vercel.app/ws/workitems");
    
    socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.event === "new_workitem") {
            setWorkItems(prev => [message.data, ...prev]);
        }
    };
    
    return () => socket.close();
}, []);
```

### **3. Vue Integration:**
```javascript
mounted() {
    this.socket = new WebSocket("wss://your-app.vercel.app/ws/workitems");
    
    this.socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.event === "new_workitem") {
            this.workItems.unshift(message.data);
        }
    };
}
```

## ✅ **Implementation Complete!**

Your FastAPI backend now supports real-time WebSocket updates! The system will automatically broadcast new work items to all connected clients whenever:

1. A new email is processed via `/api/email/intake`
2. A test work item is created via `/api/test/workitem`
3. Status updates occur (when implemented)

The frontend example provides a complete dashboard that you can use as a starting point for your own UI implementation.
