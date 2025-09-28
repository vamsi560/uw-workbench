# Business Rules API Documentation

## Overview

The cyber insurance underwriting workbench now includes a comprehensive business rules and validation framework that automates submission processing, risk assessment, and workflow management.

## Architecture

### Core Components

1. **CyberInsuranceValidator** - Main validation engine
2. **WorkflowEngine** - Status transition management  
3. **MessageService** - Automated communication
4. **BusinessConfig** - Centralized configuration
5. **Enhanced Database Models** - Risk assessments, history tracking

### Business Logic Flow

```
Email Intake → Business Validation → Risk Assessment → Underwriter Assignment → Work Item Creation
     ↓              ↓                    ↓                       ↓                    ↓
Submission      Validation Status    Risk Categories      Automated Assignment    Database Storage
Creation        Missing Fields       Risk Score           Priority Calculation    History Tracking
                Rejection Check      Industry Analysis    Workflow Rules          WebSocket Broadcast
```

## API Endpoints

### 1. Enhanced Email Intake
**POST** `/api/email-intake`

Now includes automatic business rule validation:

**Request:**
```json
{
  "subject": "Cyber Insurance Request - Healthcare Corp",
  "sender_email": "cto@healthcorp.com", 
  "body": "We need $25M cyber coverage for our healthcare organization...",
  "attachments": []
}
```

**Enhanced Response:**
```json
{
  "submission_ref": "SUB-2024-001234",
  "submission_id": 123,
  "status": "success",
  "message": "Email processed successfully and submission created",
  "validation_status": "Complete",        // NEW
  "risk_priority": "high",               // NEW  
  "assigned_underwriter": "Sarah Mitchell" // NEW
}
```

**Business Rules Applied:**
- Industry-specific validation
- Coverage limit checking
- Auto-rejection criteria
- Risk-based priority assignment
- Intelligent underwriter assignment
- Automatic risk assessment creation

### 2. Submission Validation
**POST** `/api/validate-submission`

Validate submission data without creating work items:

**Request:**
```json
{
  "extracted_data": {
    "company_name": "TechCorp Inc",
    "industry": "technology",
    "contact_email": "cto@techcorp.com",
    "company_size": "medium",
    "coverage_amount": "10000000",
    "policy_type": "cyber",
    "employee_count": "500",
    "data_types": "PII, payment data"
  }
}
```

**Response:**
```json
{
  "validation_status": "Complete",
  "missing_fields": [],
  "rejection_reason": null,
  "risk_priority": "medium",
  "risk_categories": {
    "technical": 0.6,
    "operational": 0.4,
    "compliance": 0.7,
    "financial": 0.5
  },
  "assigned_underwriter": "James Wilson",
  "overall_risk_score": 0.55
}
```

### 3. Work Item Status Updates
**PUT** `/api/work-items/{work_item_id}/status`

Update work item status with business rule validation:

**Request:**
```json
{
  "status": "under_review",
  "changed_by": "Sarah Mitchell", 
  "notes": "Beginning technical review"
}
```

**Response:**
```json
{
  "message": "Status updated successfully",
  "work_item_id": 123,
  "old_status": "assigned",
  "new_status": "under_review"
}
```

**Business Rules:**
- Validates status transitions using workflow rules
- Automatically triggers notifications
- Creates audit history
- Broadcasts updates via WebSocket

### 4. Risk Assessment Retrieval
**GET** `/api/work-items/{work_item_id}/risk-assessment`

Get comprehensive risk assessment for a work item:

**Response:**
```json
{
  "work_item_id": 123,
  "assessment_id": 456,
  "overall_score": 0.65,
  "risk_categories": {
    "technical": 0.7,
    "operational": 0.5,
    "compliance": 0.8,
    "financial": 0.6
  },
  "assessment_date": "2024-01-15T10:30:00Z",
  "assessed_by": "System",
  "assessment_notes": "Initial automated assessment based on submission data. Validation status: Complete"
}
```

### 5. Work Item History
**GET** `/api/work-items/{work_item_id}/history`

Get complete audit trail for a work item:

**Response:**
```json
{
  "work_item_id": 123,
  "history": [
    {
      "id": 789,
      "action": "status_changed_from_assigned_to_under_review",
      "changed_by": "Sarah Mitchell",
      "timestamp": "2024-01-15T14:30:00Z",
      "details": {
        "old_status": "assigned",
        "new_status": "under_review", 
        "notes": "Beginning technical review"
      }
    },
    {
      "id": 788,
      "action": "created",
      "changed_by": "System",
      "timestamp": "2024-01-15T10:00:00Z",
      "details": {
        "validation_status": "Complete",
        "missing_fields": [],
        "risk_priority": "medium",
        "assigned_underwriter": "Sarah Mitchell"
      }
    }
  ]
}
```

## Enhanced Work Items Endpoint

The existing `/api/workitems` endpoint now includes business rule data:

**Enhanced Response Fields:**
```json
{
  "work_items": [
    {
      "id": 123,
      "validation_status": "Complete",     // NEW
      "business_risk_score": 0.65,        // NEW  
      "assigned_underwriter": "Sarah Mitchell", // Enhanced
      "risk_score": 0.65,
      "risk_categories": {                 // Enhanced
        "technical": 0.7,
        "operational": 0.5,
        "compliance": 0.8,
        "financial": 0.6
      },
      // ... existing fields
    }
  ]
}
```

## Business Configuration

### Industry Coverage Limits

```javascript
const INDUSTRY_LIMITS = {
  "healthcare": 25,        // $25M max
  "financial_services": 50, // $50M max  
  "banking": 50,           // $50M max
  "technology": 30,        // $30M max
  "manufacturing": 20,     // $20M max
  // ... other industries
}
```

### Risk Scoring Weights

```javascript
const RISK_WEIGHTS = {
  "industry_risk": 0.25,        // 25% weight
  "coverage_amount": 0.20,      // 20% weight
  "company_size": 0.15,         // 15% weight
  "security_measures": 0.20,    // 20% weight
  "compliance_certifications": 0.10, // 10% weight
  "previous_incidents": 0.10    // 10% weight
}
```

### Status Transition Rules

```javascript
const VALID_TRANSITIONS = {
  "pending": ["assigned", "rejected", "under_review"],
  "assigned": ["under_review", "pending_info", "rejected"],
  "under_review": ["pending_info", "quote_ready", "rejected", "assigned"],
  "pending_info": ["under_review", "rejected"],
  "quote_ready": ["approved", "rejected", "under_review"],
  "approved": ["policy_issued", "rejected"],
  "rejected": [],        // Terminal state
  "policy_issued": []    // Terminal state
}
```

### Underwriter Assignment Logic

```javascript
const UNDERWRITER_ASSIGNMENTS = {
  "senior_underwriters": {
    "industries": ["healthcare", "financial_services", "banking", "government"],
    "min_coverage": 20000000  // $20M minimum
  },
  "standard_underwriters": {
    "industries": ["technology", "insurance", "energy", "telecommunications"],
    "min_coverage": 5000000   // $5M minimum
  },
  "junior_underwriters": {
    "industries": ["manufacturing", "retail", "education", "consulting"],
    "min_coverage": 0         // No minimum
  }
}
```

## Automated Notifications

### Assignment Notifications
- Sent when work item is assigned to underwriter
- Includes risk score, industry, coverage amount
- Formatted using centralized templates

### Rejection Notifications  
- Sent to broker when submission is rejected
- Includes rejection reason and next steps
- Professional, templated communication

### Information Requests
- Sent when additional information is needed
- Lists specific missing fields
- Maintains communication audit trail

## WebSocket Enhancements

Enhanced real-time broadcasts now include:

```json
{
  "type": "new_work_item",
  "data": {
    "id": 123,
    "validation_status": "Complete",
    "risk_score": 0.65,
    "assigned_underwriter": "Sarah Mitchell",
    "priority": "medium",
    // ... standard fields
  }
}
```

```json
{
  "type": "work_item_status_update", 
  "data": {
    "id": 123,
    "old_status": "assigned",
    "new_status": "under_review",
    "changed_by": "Sarah Mitchell",
    "timestamp": "2024-01-15T14:30:00Z"
  }
}
```

## Error Handling

### Business Rule Violations

**Invalid Status Transition:**
```json
{
  "detail": "Invalid status transition: Invalid transition from rejected to approved. Valid transitions: []"
}
```

**Coverage Limit Exceeded:**
```json
{
  "validation_status": "Rejected",
  "rejection_reason": "Coverage amount exceeds industry limit of $30M for technology companies"
}
```

**Auto-Rejection Criteria:**
```json
{
  "validation_status": "Rejected", 
  "rejection_reason": "Coverage amount too low (minimum $100,000)"
}
```

## Testing

Use the comprehensive test suite:

```bash
python test_business_integration.py
```

This tests:
- ✅ Email intake with business validation
- ✅ Submission validation endpoint
- ✅ Work item status transitions  
- ✅ Risk assessment creation
- ✅ History tracking
- ✅ Business configuration
- ✅ Individual validators

## Integration Benefits

1. **Automated Processing** - Reduces manual validation effort
2. **Consistent Risk Assessment** - Standardized scoring across all submissions
3. **Intelligent Assignment** - Routes work to appropriate underwriters
4. **Workflow Compliance** - Prevents invalid status transitions
5. **Audit Trail** - Complete history of all actions and decisions
6. **Real-time Updates** - Enhanced WebSocket broadcasts
7. **Centralized Configuration** - Easy to modify business rules
8. **Professional Communication** - Templated messages to brokers

## Configuration Management

All business rules are centralized in `business_config.py`:
- Industry limits and risk multipliers
- Status transition rules  
- Underwriter assignment criteria
- Message templates
- Validation thresholds
- Auto-rejection criteria

This makes it easy to modify business logic without code changes.