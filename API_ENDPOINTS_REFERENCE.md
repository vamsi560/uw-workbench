# Underwriter Dashboard API Endpoints

## Complete API Reference for Frontend Integration

### Base URL
- **Local Development**: `http://localhost:8000`
- **Production**: Your deployed backend URL

---

## Core Submission & Work Item APIs

### 1. Email Intake (Create New Submission)
```
POST /api/email/intake
```
**Purpose**: Process incoming email with attachments and create submission
**Request Body**:
```json
{
  "subject": "Cyber Insurance Quote Request",
  "sender_email": "broker@company.com",
  "body": "Email content...",
  "attachments": [
    {
      "filename": "application.pdf",
      "contentBase64": "base64-encoded-content"
    }
  ]
}
```
**Response**:
```json
{
  "submission_ref": "uuid-reference",
  "submission_id": 123,
  "status": "success",
  "message": "Email processed successfully"
}
```

### 2. Get All Submissions
```
GET /api/submissions?skip=0&limit=100
```
**Purpose**: Retrieve all submissions with pagination
**Query Parameters**:
- `skip`: Number to skip (default: 0)
- `limit`: Maximum results (default: 100)

### 3. Update Submission Status
```
PUT /api/submissions/{submission_id}/status
```
**Purpose**: Update submission status with audit trail
**Request Body**:
```json
{
  "new_status": "IN_REVIEW",
  "changed_by": "underwriter@company.com",
  "reason": "Moving to review phase"
}
```

### 4. Get Submission History
```
GET /api/submissions/{submission_id}/history
```
**Purpose**: Get audit trail for submission

### 5. Summarize Submission
```
POST /api/submissions/{submission_id}/summarize
```
**Purpose**: Generate AI summary of submission content

---

## Work Items Management

### 6. Enhanced Polling for Work Items
```
GET /api/workitems/poll
```
**Purpose**: Main endpoint for retrieving work items with filters
**Query Parameters**:
- `since`: ISO timestamp for incremental updates
- `limit`: Max items (default: 50, max: 100)
- `search`: Search across title, description, industry
- `priority`: Filter by priority (Low, Medium, High, Critical)
- `status`: Filter by status (Pending, In Review, Approved, Rejected)
- `assigned_to`: Filter by underwriter
- `include_details`: Include risk assessment data
- `work_item_id`: Get details for specific work item

**Example**: `/api/workitems/poll?status=Pending&priority=High&limit=25`

### 7. Update Work Item Status
```
PUT /api/work-items/{work_item_id}/status
```
**Purpose**: Update work item status with business rule validation
**Request Body**:
```json
{
  "status": "IN_REVIEW",
  "changed_by": "underwriter@company.com",
  "notes": "Starting review process"
}
```

### 8. Update Work Item (Inline Editing)
```
PUT /api/workitems/{workitem_id}
```
**Purpose**: Update work item fields
**Request Body**:
```json
{
  "title": "Updated title",
  "priority": "High",
  "assigned_to": "senior.underwriter@company.com"
}
```

### 9. Assign Work Item
```
POST /api/workitems/{workitem_id}/assign
```
**Purpose**: Assign work item to underwriter
**Request Body**:
```json
{
  "underwriter": "underwriter@company.com"
}
```

---

## Dashboard APIs

### 10. Underwriter Dashboard
```
GET /api/dashboard/underwriter/{underwriter_id}?timeframe=WEEK
```
**Purpose**: Get comprehensive dashboard data for an underwriter
**Query Parameters**:
- `timeframe`: WEEK, MONTH, QUARTER, YEAR
**Response**: Complete dashboard with KPIs, work queue, analytics

### 11. Work Queue with Filters
```
GET /api/dashboard/work-queue/{underwriter_id}
```
**Purpose**: Get filtered work queue for underwriter
**Query Parameters**:
- `priority_filter`: Priority level filter
- `status_filter`: Status filter (array)
- `industry_filter`: Industry filter (array)
- `risk_score_min`: Minimum risk score
- `risk_score_max`: Maximum risk score  
- `limit`: Results limit (max 200)

### 12. Submission Detail View
```
GET /api/dashboard/submission/{work_item_id}/detail
```
**Purpose**: Get comprehensive submission detail for underwriter analysis
**Response**: Complete submission data with risk assessment, company profile, etc.

---

## Analytics APIs

### 13. Portfolio Analytics
```
GET /api/dashboard/analytics/portfolio?underwriter_id={id}&timeframe=MONTH
```
**Purpose**: Get comprehensive portfolio analytics report
**Query Parameters**:
- `underwriter_id`: Underwriter ID
- `timeframe`: Analysis period
- `include_benchmarks`: Include benchmark data (default: true)
- `include_trends`: Include trend analysis (default: true)

### 14. Industry Performance Comparison
```
GET /api/dashboard/analytics/industry-performance/{underwriter_id}?timeframe=MONTH
```
**Purpose**: Compare underwriter performance to industry benchmarks

### 15. Risk Distribution Analysis
```
GET /api/dashboard/analytics/risk-distribution?underwriter_id={id}&timeframe=MONTH
```
**Purpose**: Analyze risk distribution across portfolio

### 16. Performance Trends
```
GET /api/dashboard/analytics/performance-trends/{underwriter_id}
```
**Purpose**: Get performance trends for specific metrics
**Query Parameters**:
- `metrics`: Array of metrics (risk_score, processing_time, approval_rate)
- `timeframe`: Analysis period

### 17. Competitive Analysis  
```
GET /api/dashboard/analytics/competitive-analysis/{underwriter_id}?timeframe=QUARTER
```
**Purpose**: Compare underwriter to team performance

---

## Risk Assessment APIs

### 18. Generate Risk Assessment
```
POST /api/dashboard/work-item/{work_item_id}/risk-assessment
```
**Purpose**: Generate or update risk assessment for work item
**Response**: Comprehensive risk assessment with scoring

### 19. Enhanced Risk Assessment
```
POST /api/dashboard/risk/enhanced-assessment
```
**Purpose**: Generate advanced risk assessment using enhanced scoring engine
**Request Body**:
```json
{
  "work_item_id": 123,
  "include_historical": false
}
```

### 20. Industry Risk Benchmarks
```
GET /api/dashboard/risk/industry-benchmarks/{industry}
```
**Purpose**: Get risk benchmarks for specific industry

---

## Underwriting & Recommendations

### 21. Generate Underwriting Recommendation
```
POST /api/dashboard/work-item/{work_item_id}/recommendation
```
**Purpose**: Generate automated underwriting recommendation
**Response**: Recommendation with risk assessment and decision rationale

### 22. Assignment Recommendations
```
GET /api/dashboard/assignment/recommendations/{work_item_id}
```
**Purpose**: Get underwriter assignment recommendations
**Response**: Top 5 recommended underwriters with scoring

### 23. Send Information Request
```
POST /api/dashboard/message/info-request
```
**Purpose**: Send information request to broker
**Request Body**:
```json
{
  "work_item_id": 123,
  "underwriter_id": "underwriter-id",
  "requested_info": "Please provide updated financial statements"
}
```

---

## Team & User Management

### 24. Get Underwriter List
```
GET /api/dashboard/underwriters?include_workload=true
```
**Purpose**: Get list of underwriters with workload information

### 25. Team Metrics
```
GET /api/dashboard/team/metrics?timeframe=WEEK
```
**Purpose**: Get team-wide performance metrics

### 26. List Available Underwriters
```
GET /api/underwriters
```
**Purpose**: Get list of available underwriters for assignment

---

## Utility & System APIs

### 27. Health Check
```
GET /health
```
**Purpose**: Check API health status

### 28. Root Endpoint
```
GET /
```
**Purpose**: API information and available endpoints

### 29. Refresh Data
```
GET /api/refresh-data
```
**Purpose**: Get fresh summary data for frontend refresh

### 30. Cleanup Duplicates
```
POST /api/cleanup-duplicates
```
**Purpose**: Remove duplicate work items

### 31. Debug Duplicates
```
GET /api/debug/duplicates
```
**Purpose**: Identify duplicate work items

---

## Real-time Communication

### 32. WebSocket Connection
```
WebSocket: /ws/workitems
```
**Purpose**: Real-time work item updates
**Events**:
- New work item notifications
- Status change updates
- Assignment notifications

---

## Common Response Formats

### Work Item Summary
```json
{
  "id": 123,
  "submission_id": 456,
  "submission_ref": "uuid-ref",
  "title": "Cyber Insurance Request",
  "status": "Pending",
  "priority": "High",
  "assigned_to": "underwriter@company.com",
  "risk_score": 75.5,
  "industry": "healthcare",
  "coverage_amount": 5000000,
  "created_at": "2024-10-08T10:00:00Z",
  "updated_at": "2024-10-08T12:00:00Z"
}
```

### Risk Assessment
```json
{
  "overall_score": 75.5,
  "risk_categories": {
    "technical_risk": 80.0,
    "financial_risk": 65.0,
    "compliance_risk": 85.0,
    "operational_risk": 70.0
  },
  "risk_factors": ["high_data_volume", "cloud_infrastructure"],
  "recommendations": ["Additional security controls required"]
}
```

### Dashboard KPIs
```json
{
  "active_submissions": 42,
  "quotes_issued": 15,
  "portfolio_premium": 2500000,
  "risk_score_average": 68.5,
  "processing_time_avg": 3.2,
  "approval_rate": 78.5
}
```

---

## Authentication & Authorization

Currently, the API uses basic authentication patterns. For production:
- Implement JWT tokens
- Add role-based access control
- Secure sensitive endpoints

---

## Error Handling

All endpoints return standardized error responses:
```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "status_code": 400
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized  
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

---

## Frontend Integration Examples

### Polling Pattern (Recommended for Vercel)
```javascript
// Poll for new work items
const response = await fetch('/api/workitems/poll?since=2024-10-08T10:00:00Z');
const data = await response.json();

// Update UI with new items
data.items.forEach(item => {
  updateWorkItemInUI(item);
});
```

### Dashboard Data Loading
```javascript
// Load dashboard for underwriter
const dashboard = await fetch(`/api/dashboard/underwriter/${underwriterId}?timeframe=WEEK`);
const dashboardData = await dashboard.json();

// Load work queue with filters
const workQueue = await fetch(`/api/dashboard/work-queue/${underwriterId}?priority_filter=High&limit=50`);
const queueData = await workQueue.json();
```

### Risk Assessment Generation
```javascript
// Generate risk assessment
const assessment = await fetch(`/api/dashboard/work-item/${workItemId}/risk-assessment`, {
  method: 'POST'
});
const riskData = await assessment.json();
```

This comprehensive API provides all the functionality needed for a full-featured underwriter dashboard frontend!