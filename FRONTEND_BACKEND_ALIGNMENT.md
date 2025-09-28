# Frontend-Backend Alignment Specification

## Overview
This document provides detailed specifications for frontend-backend alignment for the cyber insurance underwriting workbench. Use this to verify that your frontend components are properly integrated with the enhanced backend.

---

## 1. Enhanced Polling Endpoint Specifications

### Endpoint: `GET /api/workitems/poll`

**Backend Implementation Status: ✅ COMPLETE**

#### Request Parameters
```typescript
interface PollingParams {
  // Timestamp filtering (existing)
  since?: string;          // ISO timestamp (e.g., "2025-09-28T10:00:00Z")
  limit?: number;          // Max 100, default 50
  
  // NEW: Advanced filtering
  search?: string;         // Search across title, description, industry, subject, email
  priority?: string;       // "Low" | "Moderate" | "Medium" | "High" | "Critical"
  status?: string;         // "Pending" | "In Review" | "Approved" | "Rejected"
  assigned_to?: string;    // Filter by underwriter email/name
}
```

#### Response Schema
```typescript
interface EnhancedPollingResponse {
  items: WorkItemSummary[];
  count: number;
  timestamp: string;       // ISO timestamp
}

interface WorkItemSummary {
  // Core identifiers
  id: number;                           // Work item ID
  submission_id: number;                // Related submission ID
  submission_ref: string;               // UUID string
  
  // Basic work item data
  title: string;                        // "Cyber Insurance Application - TechCorp Inc"
  description?: string;                 // "Technology company seeking cyber coverage"
  status: "Pending" | "In Review" | "Approved" | "Rejected";
  priority: "Low" | "Moderate" | "Medium" | "High" | "Critical";
  assigned_to?: string;                 // Underwriter email/name
  
  // Cyber insurance specific fields
  risk_score?: number;                  // 0-100 float
  risk_categories?: {
    technical: number;                  // 0-100 float
    operational: number;                // 0-100 float  
    financial: number;                  // 0-100 float
    compliance: number;                 // 0-100 float
  };
  industry?: string;                    // "Healthcare", "Technology", etc.
  company_size?: "Small" | "Medium" | "Large" | "Enterprise";
  policy_type?: string;                 // "Cyber Liability", "General Liability"
  coverage_amount?: number;             // Numeric value (e.g., 5000000)
  last_risk_assessment?: string;        // ISO timestamp
  
  // Collaboration data
  comments_count: number;               // Number of comments
  has_urgent_comments: boolean;         // Has any urgent comments
  
  // Timestamps
  created_at: string;                   // ISO timestamp
  updated_at: string;                   // ISO timestamp
}
```

#### Frontend Integration Checklist
- [ ] **Environment Variable**: `NEXT_PUBLIC_POLL_URL` points to `/api/workitems/poll`
- [ ] **Polling Hook**: Supports new query parameters
- [ ] **Data Processing**: Handles new fields (risk_score, priority, etc.)
- [ ] **Filtering UI**: Can send priority, status, search parameters
- [ ] **Risk Display**: Shows risk_score and risk_categories
- [ ] **Comments Badge**: Uses comments_count and has_urgent_comments

---

## 2. Comprehensive Work Items Endpoint

### Endpoint: `GET /api/workitems`

**Backend Implementation Status: ✅ COMPLETE**

#### Request Parameters
```typescript
interface WorkItemsParams {
  // Filtering (same as polling)
  search?: string;
  priority?: string;
  status?: string;
  assigned_to?: string;
  industry?: string;        // Additional filter for main endpoint
  
  // Pagination
  page?: number;           // Default 1, min 1
  limit?: number;          // Default 50, max 100
}
```

#### Response Schema
```typescript
interface WorkItemListResponse {
  work_items: WorkItemSummary[];
  total: number;
  pagination: {
    page: number;
    limit: number;
    total_pages: number;
    total_items: number;
  };
}
```

#### Frontend Integration Checklist
- [ ] **Data Table**: Uses this endpoint for main work items table
- [ ] **Pagination**: Implements page/limit parameters
- [ ] **Filtering**: All filter controls send correct parameters
- [ ] **Search**: Global search box uses search parameter
- [ ] **Industry Filter**: Dropdown uses industry parameter

---

## 3. Enhanced Email Intake Process

### Endpoint: `POST /api/email/intake`

**Backend Implementation Status: ✅ COMPLETE**

#### What Changed
- Backend now creates **both** submission AND work item
- Automatically extracts cyber insurance data
- Sets intelligent defaults for priority/status

#### Data Extraction Mapping
```typescript
// LLM extracted_fields -> Work Item fields
{
  "industry": string,           // -> work_item.industry
  "policy_type": string,        // -> work_item.policy_type  
  "coverage_amount": string,    // -> work_item.coverage_amount (parsed to number)
  "company_size": string,       // -> work_item.company_size (mapped to enum)
  
  // Existing fields still available
  "insured_name": string,
  "effective_date": string,
  "broker": string
}
```

#### Frontend Integration Checklist
- [ ] **Email Processing**: No changes needed to intake requests
- [ ] **Response Handling**: Same response format maintained
- [ ] **Real-time Updates**: New work items appear with enhanced data
- [ ] **Backward Compatibility**: Existing email processing still works

---

## 4. Database Schema Alignment

### New Tables Created
```sql
-- Work items enhanced with cyber insurance fields
ALTER TABLE work_items ADD COLUMN title VARCHAR(500);
ALTER TABLE work_items ADD COLUMN description TEXT;
ALTER TABLE work_items ADD COLUMN risk_score FLOAT;
ALTER TABLE work_items ADD COLUMN risk_categories JSON;
ALTER TABLE work_items ADD COLUMN industry VARCHAR(100);
ALTER TABLE work_items ADD COLUMN company_size VARCHAR(20);
ALTER TABLE work_items ADD COLUMN policy_type VARCHAR(100);
ALTER TABLE work_items ADD COLUMN coverage_amount FLOAT;
ALTER TABLE work_items ADD COLUMN last_risk_assessment TIMESTAMP;

-- New tables for future features
CREATE TABLE risk_assessments (...);
CREATE TABLE comments (...);
CREATE TABLE users (...);
CREATE TABLE work_item_history (...);
```

#### Data Migration Status
- [ ] **Run Migration**: Execute `python migrate_database.py`
- [ ] **Verify Data**: Check existing submissions converted to work items
- [ ] **Sample Data**: Test users and sample work items created

---

## 5. WebSocket Broadcast Enhancement

### Enhanced Broadcast Data
```typescript
interface WorkItemBroadcast {
  // Enhanced work item data (same as polling response)
  id: number;
  submission_id: number;
  submission_ref: string;
  title: string;
  description?: string;
  status: string;
  priority: string;
  assigned_to?: string;
  risk_score?: number;
  risk_categories?: RiskCategories;
  industry?: string;
  company_size?: string;
  policy_type?: string;
  coverage_amount?: number;
  created_at: string;
  updated_at: string;
  comments_count: number;
  has_urgent_comments: boolean;
  
  // Backward compatibility fields
  subject: string;          // From submission
  from_email: string;       // From submission  
  extracted_fields: object; // From submission
}
```

#### Frontend Integration Checklist
- [ ] **WebSocket Handler**: Processes enhanced broadcast data
- [ ] **Real-time Display**: Shows new fields (risk_score, priority, etc.)
- [ ] **Backward Compatibility**: Still handles legacy broadcast format

---

## 6. Test Endpoints

### Test Work Item Creation: `POST /api/test/workitem`

**Sample Response:**
```json
{
  "message": "Test work item created and broadcasted",
  "submission_id": 123,
  "work_item_id": 456, 
  "submission_ref": "uuid-string",
  "websocket_connections": 2
}
```

#### Test Data Generated
```typescript
// Sample work item created
{
  "title": "Cyber Insurance Application - TechCorp Inc",
  "description": "Technology company seeking comprehensive cyber liability coverage",
  "status": "Pending",
  "priority": "High",
  "industry": "Technology", 
  "company_size": "Medium",
  "policy_type": "Cyber Liability",
  "coverage_amount": 5000000,
  "risk_score": 75.5,
  "risk_categories": {
    "technical": 80.0,
    "operational": 65.0,
    "financial": 70.0,
    "compliance": 85.0
  }
}
```

#### Frontend Testing Checklist
- [ ] **Create Test Data**: POST to `/api/test/workitem` 
- [ ] **Verify Polling**: New item appears in polling response
- [ ] **Check WebSocket**: Real-time broadcast received
- [ ] **Validate Display**: All new fields render correctly

---

## 7. Error Handling & Validation

### Status Codes & Error Responses
```typescript
// Success responses
200: Enhanced data returned
201: Work item created

// Error responses  
400: Invalid parameters (priority, status, timestamp format)
404: Work item not found
500: Server error

// Error response format
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

#### Frontend Error Handling Checklist
- [ ] **Invalid Filters**: Handle 400 errors gracefully
- [ ] **Network Errors**: Retry logic for polling failures
- [ ] **Data Validation**: Check for required fields
- [ ] **User Feedback**: Show error messages appropriately

---

## 8. Performance & Caching

### Response Times & Limits
```typescript
// Endpoint performance targets
GET /api/workitems/poll: < 2 seconds
GET /api/workitems: < 3 seconds  
POST /api/email/intake: < 5 seconds
POST /api/test/workitem: < 2 seconds

// Data limits
Max work items per response: 100
Max search query length: 255 characters
Polling interval recommendation: 5-10 seconds
```

#### Frontend Performance Checklist
- [ ] **Polling Interval**: Set to 5-10 seconds
- [ ] **Request Timeout**: Set reasonable timeout (10-15 seconds)
- [ ] **Loading States**: Show loading during requests
- [ ] **Data Caching**: Cache responses to reduce requests

---

## 9. Frontend Component Mapping

### Data Table Toolbar Component
```typescript
// Should send these parameters to /api/workitems
interface FilterState {
  search: string;           // Global search input
  priority: string;         // Priority dropdown  
  status: string;           // Status dropdown
  assigned_to: string;      // Underwriter filter
  industry: string;         // Industry filter
}
```

### Risk Score Component  
```typescript
// Use these fields from work item response
interface RiskData {
  risk_score: number;       // Overall score 0-100
  risk_categories: {        // Category breakdown
    technical: number;
    operational: number;
    financial: number;
    compliance: number;
  };
  last_risk_assessment: string; // Timestamp
}
```

### Work Item Details Component
```typescript
// Enhanced work item data available
interface WorkItemDetail extends WorkItemSummary {
  // All summary fields plus:
  subject: string;          // From submission
  sender_email: string;     // From submission  
  body_text: string;        // From submission
  extracted_fields: object; // From submission
}
```

---

## 10. Migration & Deployment Checklist

### Backend Migration Steps
- [ ] **1. Backup Database**: Create backup before migration
- [ ] **2. Run Migration**: Execute `python migrate_database.py`
- [ ] **3. Verify Tables**: Check new tables created
- [ ] **4. Test Endpoints**: Verify all endpoints respond correctly
- [ ] **5. Create Test Data**: Use test endpoint to generate sample data

### Frontend Deployment Steps  
- [ ] **1. Update Environment**: Set new polling URL
- [ ] **2. Update Hooks**: Modify polling hook for new parameters
- [ ] **3. Update Components**: Handle new data fields
- [ ] **4. Test Integration**: Verify real-time updates work
- [ ] **5. User Acceptance**: Test complete workflows

---

## 11. Validation Commands

### Backend Validation
```bash
# Test enhanced polling
curl "http://localhost:8000/api/workitems/poll"
curl "http://localhost:8000/api/workitems/poll?priority=High&search=cyber"

# Test work items endpoint  
curl "http://localhost:8000/api/workitems?page=1&limit=10"

# Create test data
curl -X POST "http://localhost:8000/api/test/workitem"

# Check database migration
python -c "from migrate_database import verify_migration; verify_migration()"
```

### Frontend Validation
```typescript
// Verify polling response structure
const response = await fetch('/api/workitems/poll');
const data = await response.json();
console.log('Has risk_score:', data.items[0]?.risk_score !== undefined);
console.log('Has priority:', data.items[0]?.priority !== undefined);
console.log('Has risk_categories:', data.items[0]?.risk_categories !== undefined);

// Test filtering
const filtered = await fetch('/api/workitems/poll?priority=High&status=Pending');
const filteredData = await filtered.json();  
console.log('Filtered count:', filteredData.count);
```

---

## 12. Common Integration Issues & Solutions

### Issue 1: Polling Hook Doesn't Handle New Fields
**Problem**: Frontend polling hook only processes legacy fields

**Solution**: Update your polling hook:
```typescript
// Before
const item = {
  id: data.id,
  subject: data.subject,
  status: data.status
};

// After  
const item = {
  id: data.id,
  title: data.title,           // NEW
  priority: data.priority,     // NEW
  risk_score: data.risk_score, // NEW
  industry: data.industry,     // NEW
  // ... include all new fields
};
```

### Issue 2: Filter Parameters Not Sent
**Problem**: Frontend filters don't reach backend

**Solution**: Update your fetch calls:
```typescript
// Before
const url = `${POLL_URL}?since=${lastPoll}`;

// After
const params = new URLSearchParams();
if (lastPoll) params.set('since', lastPoll);
if (filters.priority) params.set('priority', filters.priority);
if (filters.status) params.set('status', filters.status);
if (filters.search) params.set('search', filters.search);
const url = `${POLL_URL}?${params.toString()}`;
```

### Issue 3: Risk Score Not Displaying  
**Problem**: Risk score shows as undefined

**Solution**: Check for null/undefined values:
```typescript
const riskScore = workItem.risk_score ?? 0;
const riskCategories = workItem.risk_categories || {
  technical: 0,
  operational: 0,
  financial: 0,
  compliance: 0
};
```

---

This comprehensive specification should help you verify that your frontend enhancements are properly aligned with the backend implementation. Each section includes specific checklists you can use to validate the integration step by step.