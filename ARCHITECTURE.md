# Architecture Overview - Updated for Your Database Schema

## Overview

The Underwriting Workbench API has been updated to work with your existing `submissions` table schema. The system processes insurance submissions from email intake through LLM extraction to underwriter assignment.

## Updated Database Schema

### Primary Table: `submissions`

The application now uses a single `submissions` table that matches your existing schema:

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Primary key (auto-increment) |
| `submission_id` | integer | Sequential submission number |
| `submission_ref` | uuid | UUID reference for API access |
| `subject` | text | Email subject line |
| `sender_email` | text | Email sender address |
| `body_text` | text | Email body content |
| `extracted_fields` | jsonb | LLM-extracted structured data |
| `assigned_to` | text | Assigned underwriter email/name |
| `task_status` | text | Current status (pending, in_progress, completed) |
| `created_at` | timestamp | Creation timestamp |

### Supporting Table: `work_items`

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Primary key |
| `submission_id` | integer | Foreign key to submissions.id |
| `assigned_to` | string | Underwriter email/name |
| `status` | string | Work item status |
| `created_at` | timestamp | Creation timestamp |
| `updated_at` | timestamp | Last update timestamp |

## API Workflow

### 1. Email Intake
**POST** `/api/email/intake`

- Receives email with attachments from Logic Apps
- Parses attachments (PDF, DOCX, XLSX, images with OCR)
- Extracts structured data using Google Gemini
- Creates submission record with `task_status = "pending"`
- Returns `submission_ref` and `submission_id`

### 2. Retrieve Submission
**GET** `/api/submissions/{submission_ref}`

- Retrieves submission by UUID reference
- Returns all submission data including extracted fields
- Used by frontend to display submission details

### 3. Get All Submissions
**GET** `/api/submissions`

- Lists all submissions with pagination
- Supports `skip` and `limit` parameters
- Used for dashboard/listing views

### 4. Confirm and Assign
**POST** `/api/submissions/confirm/{submission_ref}`

- Assigns submission to underwriter
- Updates `task_status` to "in_progress"
- Creates work item record
- Used when submission is ready for underwriting

## Data Flow

```
Logic Apps Email → API Intake → File Parsing → LLM Extraction → Database Storage
                                                      ↓
Frontend Dashboard ← API Retrieval ← Database Query ← Submission Record
                                                      ↓
Underwriter Assignment ← API Confirmation ← Frontend Action ← Submission Review
```

## LLM Integration

### Google Gemini Configuration
- **Model**: `gemini-2.0-flash-exp`
- **API Key**: Configured in environment variables
- **Max Tokens**: 1000 (configurable)
- **Temperature**: 0.1 (for consistent extraction)

### Extracted Fields
The LLM extracts the following structured data into the `extracted_fields` JSONB column:

```json
{
  "insured_name": "ABC Manufacturing Company",
  "policy_type": "General Liability",
  "coverage_amount": "$2,000,000",
  "effective_date": "2024-03-01",
  "broker": "John Smith Insurance Agency"
}
```

## File Processing

### Supported Formats
- **PDF**: Text extraction with pdfplumber + PyMuPDF fallback
- **DOCX**: Text and table extraction
- **XLSX/XLS**: Data extraction with pandas
- **Images**: OCR with Tesseract (JPG, PNG, TIFF, BMP)

### Processing Pipeline
1. Base64 decode attachments
2. Save temporarily to `uploads/` directory
3. Parse based on file extension
4. Extract text/content
5. Clean up temporary files
6. Combine with email body for LLM processing

## Deployment Architecture

### Vercel Serverless Functions
- **Runtime**: Python 3.11
- **Entry Point**: `main.py`
- **Dependencies**: Listed in `requirements-vercel.txt`
- **Environment**: Configured via Vercel dashboard

### Database Connection
- **Provider**: Retool PostgreSQL
- **Connection**: SSL-enabled connection string
- **ORM**: SQLAlchemy with automatic table creation
- **Connection Pooling**: Handled by SQLAlchemy

## Security Considerations

### CORS Configuration
- **Origins**: Configurable via environment variables
- **Credentials**: Enabled for authenticated requests
- **Methods**: All HTTP methods allowed
- **Headers**: All headers allowed

### Input Validation
- **Pydantic Models**: Request/response validation
- **File Type Checking**: Extension-based validation
- **Size Limits**: Configurable file size limits
- **Base64 Validation**: Proper encoding validation

## Monitoring and Logging

### Structured Logging
- **Format**: JSON structured logs
- **Levels**: Configurable via `LOG_LEVEL` environment variable
- **Context**: Includes submission_ref, submission_id, and other relevant data

### Error Handling
- **Database Transactions**: Automatic rollback on errors
- **File Cleanup**: Temporary files cleaned up on errors
- **HTTP Status Codes**: Proper error responses
- **Exception Logging**: Full stack traces logged

## Performance Considerations

### Database Optimization
- **Indexes**: On submission_ref, submission_id, and created_at
- **Pagination**: Built-in pagination for large datasets
- **Connection Management**: Proper connection pooling

### File Processing
- **Temporary Storage**: Files processed in memory when possible
- **Cleanup**: Automatic cleanup of temporary files
- **Size Limits**: Configurable limits to prevent timeouts

### LLM Integration
- **Rate Limiting**: Built-in retry logic for API limits
- **Token Management**: Configurable max tokens
- **Fallback**: Graceful degradation if LLM fails

## Integration Points

### Logic Apps Integration
- **Endpoint**: `/api/email/intake`
- **Payload**: Email data with Base64 attachments
- **Response**: Submission reference for tracking

### Frontend Integration
- **Submission Retrieval**: `/api/submissions/{submission_ref}`
- **Listing**: `/api/submissions` with pagination
- **Assignment**: `/api/submissions/confirm/{submission_ref}`

### Retool Database Integration
- **Direct Access**: Retool can query the `submissions` table directly
- **Real-time Updates**: Changes reflected immediately
- **Dashboard Views**: Build dashboards using submission data

## Future Enhancements

### Potential Improvements
1. **Async Processing**: Background job processing for large files
2. **Caching**: Redis integration for frequently accessed data
3. **Authentication**: API key or JWT authentication
4. **Rate Limiting**: Request rate limiting for production
5. **Monitoring**: Application metrics and alerting
6. **Testing**: Comprehensive test suite
7. **Documentation**: OpenAPI/Swagger documentation

### Scaling Considerations
1. **Database Sharding**: For very high volume
2. **CDN Integration**: For file storage
3. **Microservices**: Split into specialized services
4. **Queue System**: For background processing
5. **Load Balancing**: For multiple instances
