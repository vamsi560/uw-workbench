# Deployment Guide - Retool + Gemini + Vercel

This guide covers deploying the Underwriting Workbench API to Vercel with your specific configuration.

## Prerequisites

- Vercel account
- Retool PostgreSQL database (already configured)
- Google Gemini API key (already provided)

## Step 1: Prepare for Deployment

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

## Step 2: Deploy to Vercel

1. **Initialize Vercel project** (in your project directory):
   ```bash
   vercel
   ```

2. **Deploy to production**:
   ```bash
   vercel --prod
   ```

## Step 3: Configure Environment Variables

In your Vercel dashboard:

1. Go to your project
2. Navigate to **Settings** → **Environment Variables**
3. Add the following variables:

```env
DATABASE_URL=postgresql://retool:npg_yf3gdzwl4RqE@ep-silent-sun-afdlv6pj.c-2.us-west-2.retooldb.com/retool?sslmode=require
GEMINI_API_KEY=AIzaSyAZKwC1d_krqu5d6B0j_7xxkxBAkYS0Jfw
GEMINI_MODEL=gemini-2.0-flash-exp
MAX_TOKENS=1000
LOG_LEVEL=INFO
UPLOAD_DIR=uploads
CORS_ORIGINS=*
CORS_CREDENTIALS=true
CORS_METHODS=*
CORS_HEADERS=*
```

## Step 4: Update Logic Apps

Update your Logic Apps to call your Vercel endpoint:

**Endpoint URL**: `https://your-app-name.vercel.app/api/email/intake`

**Payload**:
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

**Response**:
```json
{
  "submission_ref": "uuid-string",
  "submission_id": 1,
  "status": "success",
  "message": "Email processed successfully and submission created"
}
```

## Step 5: Test the Deployment

1. **Health Check**:
   ```bash
   curl https://your-app-name.vercel.app/health
   ```

2. **Test Email Intake**:
   ```bash
   curl -X POST https://your-app-name.vercel.app/api/email/intake \
     -H "Content-Type: application/json" \
     -d '{
       "subject": "Test Submission",
       "from_email": "test@example.com",
       "received_at": "2024-01-15T10:30:00Z",
       "body": "Test email body",
       "attachments": []
     }'
   ```

3. **Get Submission** (using the submission_ref from step 2):
   ```bash
   curl https://your-app-name.vercel.app/api/submissions/{submission_ref}
   ```

## Database Tables

The application will automatically create the following tables in your Retool database on first startup:

- `submissions` - Main table storing all submission data with extracted fields
- `work_items` - Work items assigned to underwriters

The `submissions` table matches your existing schema with fields like `submission_id`, `submission_ref`, `subject`, `sender_email`, `body_text`, `extracted_fields`, `assigned_to`, and `task_status`.

## Monitoring

### Vercel Dashboard
- Monitor function execution times
- Check error logs
- View deployment status

### Application Logs
- Structured JSON logs available in Vercel function logs
- Search by email_id, submission_id, etc.

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify DATABASE_URL is correct
   - Check if Retool database allows external connections

2. **Gemini API Errors**:
   - Verify GEMINI_API_KEY is correct
   - Check API quotas and limits

3. **Function Timeouts**:
   - Large file processing may timeout
   - Consider implementing async processing for large files

4. **CORS Issues**:
   - Verify CORS_ORIGINS configuration
   - Check if your frontend domain is allowed

### Debug Mode

To enable debug logging, set `LOG_LEVEL=DEBUG` in Vercel environment variables.

## Performance Considerations

### File Processing
- Large files may cause timeouts
- Consider implementing file size limits
- Use streaming for very large files

### Database
- Retool database has connection limits
- Consider connection pooling for high volume

### LLM Usage
- Gemini has rate limits
- Monitor API usage in Google Cloud Console

## Security

### Production Recommendations

1. **Restrict CORS**:
   ```env
   CORS_ORIGINS=https://your-frontend-domain.com
   ```

2. **API Authentication**:
   - Add API key authentication for production
   - Implement rate limiting

3. **Input Validation**:
   - Validate file types and sizes
   - Sanitize input data

4. **Database Security**:
   - Use read-only database users where possible
   - Implement proper indexing

## Scaling

For high-volume production use:

1. **Database Optimization**:
   - Add proper indexes
   - Consider read replicas

2. **Caching**:
   - Implement Redis for frequently accessed data
   - Cache LLM responses for similar documents

3. **Queue System**:
   - Use background job processing for file parsing
   - Implement retry mechanisms

## Support

For issues specific to your deployment:
1. Check Vercel function logs
2. Monitor Retool database performance
3. Verify Gemini API status
4. Review application logs for specific error patterns
