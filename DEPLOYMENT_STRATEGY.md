# Deployment Strategy for Hybrid Architecture

## Overview
Our hybrid architecture requires **two separate deployments** because:
- **Python LLM Service**: Best suited for Vercel serverless functions
- **Java Backend**: Requires persistent runtime environment

## Recommended Deployment: Two-Platform Strategy

### Architecture Flow:
```
Frontend (Vercel) → Java Backend (Railway/Render) → Python LLM Service (Vercel) → Database
```

## Deployment Plan

### 1. Python LLM Service → Vercel ✅ (Already Deployed)
- **Current Status**: Already running on Vercel
- **URL**: `https://uw-workbench-jade.vercel.app`
- **Endpoints**: `/api/extract`, `/api/triage`, `/api/risk-assessment`
- **Benefits**: Serverless scaling, zero maintenance

### 2. Java Backend → Railway (Recommended)
- **Platform**: Railway.app (best for Spring Boot)
- **Runtime**: Java 21 with Maven/Gradle
- **Database**: Shared PostgreSQL with Python service
- **Port**: 8080 (will be mapped to Railway's port)

### 3. Frontend → Vercel ✅ (Already Deployed)
- **Update**: Environment variables to point to Java backend
- **URL**: `https://uw-workbench-portal.vercel.app`

## Java Backend Deployment Options

### Option 1: Railway (Recommended)
**Why Railway:**
- ✅ Native Java/Spring Boot support
- ✅ Automatic builds from Git
- ✅ Environment variable management
- ✅ Built-in PostgreSQL if needed
- ✅ $5/month for hobby projects
- ✅ Easy scaling and monitoring

**Railway Deployment Steps:**
1. Connect GitHub repository
2. Select java-backend folder
3. Railway auto-detects Spring Boot
4. Configure environment variables
5. Deploy automatically

### Option 2: Render
**Why Render:**
- ✅ Free tier available
- ✅ Java/Spring Boot support
- ✅ Auto-deploy from Git
- ✅ Built-in SSL certificates

### Option 3: AWS/Google Cloud
**For Production Scale:**
- AWS Elastic Beanstalk
- Google Cloud Run
- More complex but highly scalable

## Deployment Configuration Files

### For Railway Deployment
Create these files in java-backend/:

#### `railway.toml`:
```toml
[build]
builder = "maven"
buildCommand = "mvn clean package -DskipTests"

[deploy]
startCommand = "java -jar target/uw-workbench-backend-*.jar"
restartPolicyType = "always"

[env]
JAVA_TOOL_OPTIONS = "-XX:MaxRAMPercentage=75.0"
```

#### `Procfile` (Alternative):
```
web: java -jar target/uw-workbench-backend-*.jar --server.port=$PORT
```

### Environment Variables for Java Backend
```env
# Database (same as Python service)
SPRING_DATASOURCE_URL=postgresql://retool:npg_yf3gdzwl4RqE@ep-silent-sun-afdlv6pj.c-2.us-west-2.retooldb.com/retool?sslmode=require
SPRING_DATASOURCE_USERNAME=retool
SPRING_DATASOURCE_PASSWORD=npg_yf3gdzwl4RqE

# LLM Service URL (Vercel deployment)
LLM_SERVICE_URL=https://uw-workbench-jade.vercel.app

# CORS for frontend
CORS_ALLOWED_ORIGINS=https://uw-workbench-portal.vercel.app,https://uw-workbench-jade.vercel.app

# Server configuration
SERVER_PORT=${PORT:8080}
```

## Alternative: Single Platform Deployment

### If you prefer single platform (Railway for everything):

```
Frontend (Railway) → Java Backend (Railway) → Python LLM (Railway) → Database
```

**Steps:**
1. Move Python LLM service to Railway
2. Deploy Java backend to Railway  
3. Deploy frontend to Railway
4. Update all cross-references

**Trade-offs:**
- ✅ Single platform management
- ✅ Better integration
- ❌ More expensive than Vercel for frontend
- ❌ Need to migrate existing Vercel deployments

## Frontend Configuration Update

### Current (Python only):
```env
NEXT_PUBLIC_API_URL=https://uw-workbench-jade.vercel.app
NEXT_PUBLIC_POLL_URL=https://uw-workbench-jade.vercel.app/api/workitems/poll
```

### New (Hybrid with Java backend):
```env
# Primary API (Java Backend)
NEXT_PUBLIC_API_URL=https://your-java-backend.railway.app
NEXT_PUBLIC_POLL_URL=https://your-java-backend.railway.app/api/workitems/poll

# LLM Service (Python - via Java proxy)
NEXT_PUBLIC_LLM_STATUS_URL=https://your-java-backend.railway.app/api/llm/status
```

## Deployment Steps

### Step 1: Deploy Java Backend to Railway
1. **Sign up**: Create Railway account
2. **Connect GitHub**: Link your repository
3. **Create Service**: New project from GitHub
4. **Select Path**: Choose `java-backend` folder
5. **Configure**: Add environment variables
6. **Deploy**: Railway auto-builds and deploys

### Step 2: Update Frontend
1. **Update Vercel Environment Variables**:
   - `NEXT_PUBLIC_API_URL` → Railway Java backend URL
   - Keep existing Vercel domain for frontend

### Step 3: Test Integration
1. Java backend calls Python LLM service on Vercel
2. Frontend calls Java backend on Railway
3. End-to-end functionality verification

## Cost Analysis

### Recommended Setup (Hybrid):
- **Vercel**: $0 (hobby) / $20/month (pro) - Frontend + Python LLM
- **Railway**: $5/month - Java Backend
- **Total**: $5-25/month

### Single Platform (Railway):
- **Railway**: $15-30/month for all services
- **Migration effort**: Medium

## Next Steps

1. **Choose Platform**: Railway (recommended) or Render
2. **Prepare Java Backend**: Add deployment configuration files
3. **Deploy Java Backend**: Connect GitHub and deploy
4. **Update Frontend**: Change API URLs to Java backend
5. **Test Integration**: Verify end-to-end functionality

**Recommendation: Start with Railway for Java backend while keeping Python LLM on Vercel. This gives you the best of both worlds with minimal migration effort.**