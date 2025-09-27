# Underwriting Workbench Backend API

A Python FastAPI backend for processing insurance submissions from email intake to work item creation.

## Features

- **Email Intake Processing**: Receives emails with attachments from Logic Apps
- **Multi-format File Parsing**: Supports PDF, DOCX, XLSX, and image files (with OCR)
- **LLM Integration**: Extracts structured insurance data using OpenAI, Azure OpenAI, or Google Gemini
- **Database Management**: PostgreSQL with SQLAlchemy ORM
- **Workflow Management**: Draft submissions → Final submissions → Work items
- **Comprehensive Logging**: Structured logging with JSON output

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd uw-workbench
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up PostgreSQL database**
   - Create a database named `uw_workbench`
   - Update `DATABASE_URL` in your `.env` file

5. **Install system dependencies for OCR**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # macOS
   brew install tesseract
   
   # Windows
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

## Configuration

### Environment Variables

```env
# Database Configuration - Retool PostgreSQL
DATABASE_URL=postgresql://retool:npg_yf3gdzwl4RqE@ep-silent-sun-afdlv6pj.c-2.us-west-2.retooldb.com/retool?sslmode=require

# Google Gemini Configuration
GEMINI_API_KEY=AIzaSyAZKwC1d_krqu5d6B0j_7xxkxBAkYS0Jfw
GEMINI_MODEL=gemini-2.0-flash-exp
MAX_TOKENS=1000

# Alternative LLM APIs (optional)
OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Application Settings
UPLOAD_DIR=uploads
LOG_LEVEL=INFO

# CORS Settings (for production, restrict these)
CORS_ORIGINS=*
CORS_CREDENTIALS=true
CORS_METHODS=*
CORS_HEADERS=*
```

### LLM Provider Setup

The application is configured to use **Google Gemini** as the primary LLM provider. The configuration includes:

1. **Google Gemini**: Primary LLM (configured with API key and model)
2. **OpenAI**: Fallback option (optional)
3. **Azure OpenAI**: Fallback option (optional)

## Running the Application

### Development
```bash
python run.py
```

### Production with Vercel

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy to Vercel**
   ```bash
   vercel --prod
   ```

3. **Set Environment Variables in Vercel Dashboard**
   - Go to your project in Vercel dashboard
   - Navigate to Settings → Environment Variables
   - Add all the environment variables from your `.env` file

### Local Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000` (local) or your Vercel URL (production)

## Quick Start for Your Setup

Since you're using **Retool database**, **Google Gemini**, and **Vercel**, here's the quick start:

1. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd uw-workbench
   pip install -r requirements.txt
   ```

2. **Test locally**:
   ```bash
   python test_setup.py  # Verify setup
   python run.py         # Start development server
   ```

3. **Deploy to Vercel**:
   ```bash
   vercel --prod
   ```

4. **Configure in Vercel Dashboard**:
   - Add environment variables (database URL, Gemini API key, etc.)
   - The app will automatically create database tables on first startup

Your Logic Apps can now call your Vercel endpoint: `https://your-app.vercel.app/api/email/intake`

## API Endpoints

### 1. Email Intake
**POST** `/api/email/intake`

Processes incoming emails with attachments and creates draft submissions.

**Request Body:**
```json
{
  "subject": "Insurance Submission",
  "from_email": "broker@example.com",
  "received_at": "2024-01-15T10:30:00Z",
  "body": "Please find attached insurance application...",
  "attachments": [
    {
      "filename": "application.pdf",
      "contentBase64": "JVBERi0x..."
    }
  ]
}
```

**Response:**
```json
{
  "submission_ref": "uuid-string",
  "submission_id": 1,
  "status": "success",
  "message": "Email processed successfully and submission created"
}
```

### 2. Get Submission
**GET** `/api/submissions/{submission_ref}`

Retrieves a submission by its UUID reference.

**Response:**
```json
{
  "id": 1,
  "submission_id": 1,
  "submission_ref": "uuid-string",
  "subject": "Insurance Submission",
  "sender_email": "broker@example.com",
  "body_text": "Please find attached...",
  "extracted_fields": {
    "insured_name": "ABC Company",
    "policy_type": "General Liability",
    "coverage_amount": "$1,000,000",
    "effective_date": "2024-02-01",
    "broker": "John Smith"
  },
  "assigned_to": null,
  "task_status": "pending",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 3. Get All Submissions
**GET** `/api/submissions`

Retrieves all submissions with pagination.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)

### 4. Confirm Submission
**POST** `/api/submissions/confirm/{submission_ref}`

Confirms a submission and assigns it to an underwriter.

**Request Body:**
```json
{
  "underwriter_email": "underwriter@company.com"
}
```

**Response:**
```json
{
  "submission_id": 1,
  "submission_ref": "uuid-string",
  "work_item_id": 1,
  "assigned_to": "underwriter@company.com",
  "task_status": "in_progress"
}
```

### 5. Health Check
**GET** `/health`

Returns application health status.

## Database Schema

### Tables

- **submissions**: Main table storing all submission data with extracted fields
- **work_items**: Work items assigned to underwriters

### Models

The application uses SQLAlchemy models defined in `database.py`:

- `Submission`: Main submission record with all data including extracted fields
- `WorkItem`: Work items for underwriters

### Submission Table Schema

The `submissions` table contains:
- `id`: Primary key
- `submission_id`: Sequential submission number
- `submission_ref`: UUID reference for API access
- `subject`: Email subject
- `sender_email`: Email sender address
- `body_text`: Email body content
- `extracted_fields`: JSONB field with LLM-extracted structured data
- `assigned_to`: Assigned underwriter
- `task_status`: Current status (pending, in_progress, completed)
- `created_at`: Creation timestamp

## File Processing

### Supported Formats

- **PDF**: Text extraction using pdfplumber (with PyMuPDF fallback)
- **DOCX**: Text and table extraction using python-docx
- **XLSX/XLS**: Data extraction using pandas/openpyxl
- **Images**: OCR using pytesseract (JPG, PNG, TIFF, BMP)

### Processing Flow

1. Base64 decode attachments
2. Save temporarily to `uploads/` directory
3. Parse based on file extension
4. Extract text/content
5. Clean up temporary files
6. Combine with email body text

## LLM Integration

### Data Extraction

The LLM extracts the following structured fields:
- `insured_name`: Name of the insured party/company
- `policy_type`: Type of insurance policy
- `coverage_amount`: Coverage amount or limit
- `effective_date`: Policy effective date
- `broker`: Insurance broker or agent name

### Prompt Engineering

The system uses a structured prompt to ensure consistent JSON output format across different LLM providers.

## Error Handling

- Comprehensive error logging with structured JSON
- Graceful fallbacks for file parsing failures
- Database transaction rollback on errors
- HTTP status codes for different error types

## Logging

The application uses structured logging with JSON output:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "logger": "main",
  "message": "Processing email intake",
  "subject": "Insurance Submission",
  "from_email": "broker@example.com"
}
```

## Development

### Project Structure

```
uw-workbench/
├── main.py                 # FastAPI application
├── database.py            # SQLAlchemy models and database setup
├── file_parsers.py        # File parsing modules
├── llm_service.py         # LLM integration
├── models.py              # Pydantic models
├── config.py              # Configuration management
├── logging_config.py      # Logging setup
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Adding New File Types

1. Add parsing logic to `FileParser` class in `file_parsers.py`
2. Update the `parse_file` method to handle the new extension
3. Add appropriate dependencies to `requirements.txt`

### Adding New LLM Providers

1. Add configuration to `config.py`
2. Implement extraction method in `LLMService` class in `llm_service.py`
3. Update the `extract_insurance_data` method to try the new provider

## Production Considerations

- Set up proper PostgreSQL connection pooling
- Configure reverse proxy (nginx) for production
- Set up monitoring and alerting
- Implement proper secret management
- Configure log aggregation
- Set up database backups
- Implement rate limiting
- Add API authentication/authorization

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Install tesseract-ocr system package
2. **Database connection errors**: Check DATABASE_URL configuration
3. **LLM API errors**: Verify API keys and endpoints
4. **File parsing failures**: Check file format support and dependencies

### Logs

Check application logs for detailed error information. The structured JSON format makes it easy to search and filter logs.
