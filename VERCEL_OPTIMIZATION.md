# Vercel Deployment Optimization

## Problem
The application exceeded Vercel's 250MB unzipped size limit due to heavy dependencies:
- `pandas` (~100MB)
- `PyMuPDF` (~50MB) 
- `pytesseract` (~30MB)
- `Pillow` (~20MB)
- `pdfplumber` (depends on PyMuPDF)

## Solution
Created a minimal deployment configuration that removes heavy dependencies while maintaining core functionality.

### Changes Made

#### 1. **Minimal Requirements** (`requirements.txt`)
**Removed heavy dependencies:**
- `pandas==2.1.4` (very large)
- `pdfplumber==0.10.3` (depends on PyMuPDF)
- `PyMuPDF==1.23.9` (large)
- `pytesseract==0.3.10` (requires system tesseract)
- `Pillow==10.1.0` (large)

**Kept essential dependencies:**
- FastAPI core
- Database (SQLAlchemy, psycopg2)
- Google Gemini LLM
- Basic file parsing (DOCX, XLSX)

#### 2. **Minimal File Parser** (`file_parsers_minimal.py`)
- **Supports**: DOCX, XLSX files only
- **Graceful degradation**: Unsupported files show informative message
- **No heavy dependencies**: Uses only `python-docx` and `openpyxl`

#### 3. **Conditional Import** (`main.py`)
```python
# Use minimal file parser for Vercel deployment
try:
    from file_parsers_minimal import parse_attachments
    logger.info("Using minimal file parser for Vercel deployment")
except ImportError:
    from file_parsers import parse_attachments
    logger.info("Using full file parser")
```

#### 4. **Vercel Configuration** (`vercel.json`)
- Added `maxLambdaSize: "50mb"` limit
- Set `maxDuration: 30` seconds
- Optimized for serverless deployment

## Supported File Types

### ✅ **Fully Supported**
- **DOCX**: Full text and table extraction
- **XLSX/XLS**: Complete data extraction
- **Email body text**: Always processed

### ⚠️ **Limited Support**
- **PDF**: Not supported in minimal mode
- **Images**: Not supported in minimal mode
- **Other formats**: Show informative message

## Deployment Benefits

### ✅ **Size Reduction**
- **Before**: ~250MB+ (exceeded limit)
- **After**: ~50MB (well under limit)

### ✅ **Faster Deployment**
- Fewer dependencies to install
- Smaller package size
- Faster cold starts

### ✅ **Cost Effective**
- Lower Vercel function costs
- Reduced bandwidth usage
- Better performance

## Trade-offs

### ❌ **Limited File Support**
- PDF files won't be processed
- Images won't be OCR'd
- Some file types will show "not supported" message

### ✅ **Core Functionality Preserved**
- Email processing works
- LLM extraction works
- Database operations work
- DOCX/XLSX files work

## Alternative Solutions

### For Full File Support
If you need PDF/image processing, consider:

1. **External API**: Use a service like Adobe PDF Services API
2. **Separate Microservice**: Deploy file processing separately
3. **Client-side Processing**: Process files in the frontend
4. **Different Platform**: Use AWS Lambda or Google Cloud Functions

### For Production
- Use the full `file_parsers.py` for local development
- Use `file_parsers_minimal.py` for Vercel deployment
- Consider hybrid approach with external services

## Testing

The application will:
1. ✅ Process DOCX and XLSX files normally
2. ✅ Show informative messages for unsupported files
3. ✅ Continue with email body text processing
4. ✅ Extract insurance data using Gemini LLM
5. ✅ Store results in database

## Rollback Plan

If you need full file support:
1. Revert `requirements.txt` to include heavy dependencies
2. Remove conditional import in `main.py`
3. Deploy to a platform with higher limits (AWS Lambda, etc.)
