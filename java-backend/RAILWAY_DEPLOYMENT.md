# Railway Deployment Guide - Java Backend

## Quick Deployment Steps

### 1. Prepare Repository
✅ All files are ready in `java-backend/` folder:
- `pom.xml` - Maven configuration
- `railway.toml` - Railway deployment config
- `Procfile` - Alternative deployment command
- `application-production.properties` - Production settings

### 2. Deploy to Railway

#### Option A: Railway Web Interface
1. **Go to**: https://railway.app
2. **Sign up/Login** with GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Select**: `uw-workbench` repository
5. **Root Directory**: Set to `java-backend`
6. **Framework**: Railway auto-detects Spring Boot

#### Option B: Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy from java-backend folder
cd java-backend
railway init
railway up
```

### 3. Configure Environment Variables
In Railway dashboard, add these environment variables:

```env
# Database Configuration
SPRING_DATASOURCE_URL=postgresql://retool:npg_yf3gdzwl4RqE@ep-silent-sun-afdlv6pj.c-2.us-west-2.retooldb.com/retool?sslmode=require
SPRING_DATASOURCE_USERNAME=retool
SPRING_DATASOURCE_PASSWORD=npg_yf3gdzwl4RqE

# LLM Service URL (Your existing Vercel deployment)
LLM_SERVICE_URL=https://uw-workbench-jade.vercel.app

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://uw-workbench-portal.vercel.app,https://uw-workbench-jade.vercel.app

# Java Configuration
JAVA_TOOL_OPTIONS=-XX:MaxRAMPercentage=75.0 -XX:+UseG1GC
SPRING_PROFILES_ACTIVE=production
```

### 4. Deployment Process
Railway will automatically:
1. ✅ Detect Spring Boot application
2. ✅ Run `mvn clean package`
3. ✅ Start with `java -jar target/uw-workbench-backend-*.jar`
4. ✅ Assign a public URL (e.g., `https://your-app.railway.app`)

### 5. Verify Deployment
Once deployed, test these endpoints:
```bash
# Health check
curl https://your-app.railway.app/api/health

# Work items polling
curl https://your-app.railway.app/api/workitems/poll

# LLM status (should connect to Vercel Python service)
curl https://your-app.railway.app/api/llm/status
```

## Alternative Platforms

### Render.com Deployment
```yaml
# render.yaml
services:
  - type: web
    name: uw-workbench-backend
    env: java
    buildCommand: mvn clean package -DskipTests
    startCommand: java -jar target/uw-workbench-backend-*.jar --server.port=$PORT
    envVars:
      - key: SPRING_PROFILES_ACTIVE
        value: production
```

### Heroku Deployment
```bash
# Install Heroku CLI
heroku create uw-workbench-backend

# Set environment variables
heroku config:set SPRING_PROFILES_ACTIVE=production
heroku config:set LLM_SERVICE_URL=https://uw-workbench-jade.vercel.app

# Deploy
git push heroku main
```

## Frontend Configuration Update

### After Java Backend Deployment
Update your Vercel environment variables:

**In Vercel Dashboard** → Project Settings → Environment Variables:
```env
# Replace with your Railway URL
NEXT_PUBLIC_API_URL=https://your-java-backend.railway.app
NEXT_PUBLIC_POLL_URL=https://your-java-backend.railway.app/api/workitems/poll
NEXT_PUBLIC_HEALTH_URL=https://your-java-backend.railway.app/api/health
NEXT_PUBLIC_LLM_STATUS_URL=https://your-java-backend.railway.app/api/llm/status

# Feature flags
NEXT_PUBLIC_USE_JAVA_BACKEND=true
NEXT_PUBLIC_ENABLE_ENHANCED_FEATURES=true
```

### Redeploy Frontend
After updating environment variables:
1. Go to Vercel dashboard
2. Trigger a new deployment
3. Frontend will now use Java backend

## Testing Your Deployment

### 1. Test Java Backend Directly
```bash
# Get your Railway URL from dashboard
JAVA_BACKEND_URL="https://your-app.railway.app"

# Test health
curl $JAVA_BACKEND_URL/api/health

# Test email intake
curl -X POST $JAVA_BACKEND_URL/api/email/intake \
  -H "Content-Type: application/json" \
  -d '{
    "sender_email": "test@example.com",
    "subject": "Test Deployment",
    "email_content": "Testing Railway deployment"
  }'
```

### 2. Test Frontend Integration
1. Open your Vercel frontend URL
2. Check browser console for API calls
3. Verify work items polling works
4. Test email submission functionality

### 3. Test Full Integration Flow
```
User → Frontend (Vercel) → Java Backend (Railway) → Python LLM (Vercel) → Database
```

## Troubleshooting

### Common Issues:

#### Build Failures
```bash
# Check Railway build logs
railway logs

# Common fixes:
# 1. Ensure pom.xml is in java-backend folder
# 2. Check Java version compatibility
# 3. Verify all dependencies are available
```

#### Database Connection Issues
```bash
# Test database connection
# Update CORS settings if needed
# Check firewall rules
```

#### CORS Issues
```bash
# Verify CORS_ALLOWED_ORIGINS includes your frontend URL
# Check browser network tab for blocked requests
```

## Monitoring and Maintenance

### Railway Features:
- ✅ **Automatic HTTPS**: SSL certificates included
- ✅ **Custom Domains**: Add your own domain
- ✅ **Scaling**: Vertical scaling available
- ✅ **Metrics**: Built-in monitoring
- ✅ **Logs**: Real-time log streaming

### Cost Management:
- **Hobby Plan**: $5/month - Good for development
- **Pro Plan**: $20/month - Production ready
- **Usage-based billing** for resources

## Success Metrics

After successful deployment:
- ✅ Java backend accessible at Railway URL
- ✅ Frontend connects to Java backend
- ✅ Java backend connects to Python LLM service
- ✅ Database operations working
- ✅ Real-time polling functional
- ✅ Email intake processing works

**Your hybrid architecture will be fully operational across three platforms:**
1. **Frontend**: Vercel
2. **Java Backend**: Railway  
3. **Python LLM**: Vercel

This gives you the best performance and cost optimization for each service type!