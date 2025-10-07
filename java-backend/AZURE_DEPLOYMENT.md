# Azure Web App Deployment Guide - Java Backend

## ✅ Why Azure Free Web App is Perfect for Your Java Backend

### Azure Free Tier Benefits:
- ✅ **Free for 12 months** (then $13/month for Basic)
- ✅ **Native Java Support** (Java 8, 11, 17, 21)
- ✅ **Maven/Gradle Build** support
- ✅ **Custom Domains** and SSL
- ✅ **Auto-scaling** capabilities
- ✅ **Git Deployment** from GitHub
- ✅ **Environment Variables** management
- ✅ **Built-in Monitoring** and logs

### Resource Limits (Free Tier):
- ✅ **1 GB RAM** - Perfect for Spring Boot
- ✅ **1 GB Storage** - Sufficient for Java app
- ✅ **180 CPU minutes/day** - Good for development/testing
- ✅ **10 Apps** - Can host multiple services

## Azure Deployment Steps

### 1. Prerequisites
- Azure account (free at https://azure.microsoft.com/free/)
- GitHub repository with java-backend folder

### 2. Create Azure Web App

#### Option A: Azure Portal (GUI)
1. **Go to**: https://portal.azure.com
2. **Create Resource** → **Web App**
3. **Configuration**:
   ```
   Subscription: Free Trial
   Resource Group: Create new "uw-workbench-rg"
   Name: uw-workbench-backend (must be globally unique)
   Publish: Code
   Runtime Stack: Java 21
   Java web server stack: Java SE (Embedded Web Server)
   Operating System: Linux
   Region: East US (or closest to you)
   Pricing Tier: Free F1
   ```
4. **Review + Create**

#### Option B: Azure CLI
```bash
# Install Azure CLI first
# Create resource group
az group create --name uw-workbench-rg --location eastus

# Create web app
az webapp create \
  --resource-group uw-workbench-rg \
  --plan uw-workbench-plan \
  --name uw-workbench-backend \
  --runtime "JAVA:21-java21" \
  --sku FREE
```

### 3. Configure Deployment

#### GitHub Integration
1. **In Azure Portal** → Your Web App → **Deployment Center**
2. **Source**: GitHub
3. **Organization**: vamsi560
4. **Repository**: uw-workbench
5. **Branch**: main
6. **Build Provider**: App Service Build Service
7. **Root Path**: /java-backend
8. **Save**

### 4. Configure Environment Variables
**In Azure Portal** → Your Web App → **Configuration** → **Application Settings**:

```env
# Database Configuration
SPRING_DATASOURCE_URL=postgresql://retool:npg_yf3gdzwl4RqE@ep-silent-sun-afdlv6pj.c-2.us-west-2.retooldb.com/retool?sslmode=require
SPRING_DATASOURCE_USERNAME=retool
SPRING_DATASOURCE_PASSWORD=npg_yf3gdzwl4RqE

# LLM Service URL (Your Vercel deployment)
LLM_SERVICE_URL=https://uw-workbench-jade.vercel.app

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://uw-workbench-portal.vercel.app,https://uw-workbench-jade.vercel.app

# Spring Boot Profile
SPRING_PROFILES_ACTIVE=azure

# Java Options for Azure
JAVA_OPTS=-Xmx512m -Dserver.port=80
```

### 5. Azure-Specific Configuration Files

#### Create `web.config` (for Windows App Service):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="httpPlatformHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="%JAVA_HOME%\bin\java.exe"
        arguments="-Djava.net.preferIPv4Stack=true -Dserver.port=%HTTP_PLATFORM_PORT% -jar &quot;%HOME%\site\wwwroot\target\uw-workbench-backend-*.jar&quot;">
    </httpPlatform>
  </system.webServer>
</configuration>
```

#### Update `pom.xml` for Azure (if needed):
```xml
<properties>
    <maven.compiler.source>21</maven.compiler.source>
    <maven.compiler.target>21</maven.compiler.target>
    <java.version>21</java.version>
    <azure.version>3.19.0</azure.version>
</properties>

<!-- Azure Spring Boot Starter (optional) -->
<dependency>
    <groupId>com.azure.spring</groupId>
    <artifactId>spring-cloud-azure-starter</artifactId>
    <version>${azure.version}</version>
</dependency>
```

### 6. Azure Deployment Files Created ✅

The following files are now ready in your `java-backend/` folder:
- ✅ `application-azure.properties` - Azure-optimized configuration
- ✅ `web.config` - Windows App Service configuration  
- ✅ `Procfile` - Linux App Service startup command

## Deployment Process

### 7. Deploy via GitHub Integration
Once configured, Azure will automatically:
1. ✅ **Detect** your GitHub repository changes
2. ✅ **Build** using Maven (`mvn clean package`)
3. ✅ **Deploy** the JAR file
4. ✅ **Start** your Spring Boot application
5. ✅ **Assign** a public URL: `https://uw-workbench-backend.azurewebsites.net`

### 8. Manual Deployment (Alternative)
If you prefer manual deployment:

#### Using Azure CLI:
```bash
# Build locally
cd java-backend
mvn clean package

# Deploy to Azure
az webapp deploy \
  --resource-group uw-workbench-rg \
  --name uw-workbench-backend \
  --src-path target/uw-workbench-backend-*.jar \
  --type jar
```

#### Using Maven Plugin:
Add to `pom.xml`:
```xml
<plugin>
    <groupId>com.microsoft.azure</groupId>
    <artifactId>azure-webapp-maven-plugin</artifactId>
    <version>2.5.0</version>
    <configuration>
        <subscriptionId>your-subscription-id</subscriptionId>
        <resourceGroup>uw-workbench-rg</resourceGroup>
        <appName>uw-workbench-backend</appName>
        <region>eastus</region>
        <runtime>
            <os>Linux</os>
            <javaVersion>Java 21</javaVersion>
            <webContainer>Java SE</webContainer>
        </runtime>
        <deployment>
            <resources>
                <resource>
                    <directory>${project.basedir}/target</directory>
                    <includes>
                        <include>*.jar</include>
                    </includes>
                </resource>
            </resources>
        </deployment>
    </configuration>
</plugin>
```

Then deploy with: `mvn azure-webapp:deploy`

## Testing Your Azure Deployment

### 1. Health Check
```bash
# Replace with your actual Azure URL
AZURE_URL="https://uw-workbench-backend.azurewebsites.net"

# Test health endpoint
curl $AZURE_URL/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-10-06T16:30:00",
  "service": "java-backend",
  "llm_service_available": true
}
```

### 2. Test API Endpoints
```bash
# Test work items polling
curl $AZURE_URL/api/workitems/poll

# Test LLM status
curl $AZURE_URL/api/llm/status

# Test email intake
curl -X POST $AZURE_URL/api/email/intake \
  -H "Content-Type: application/json" \
  -d '{
    "sender_email": "test@example.com",
    "subject": "Test Azure Deployment",
    "email_content": "Testing Azure Web App deployment"
  }'
```

### 3. Check Application Logs
In Azure Portal → Your Web App → **Log stream** or **Diagnose and solve problems**

## Frontend Configuration Update

### Update Vercel Environment Variables
After successful Azure deployment, update your frontend:

**In Vercel Dashboard** → Project Settings → Environment Variables:
```env
# Replace with your actual Azure URL
NEXT_PUBLIC_API_URL=https://uw-workbench-backend.azurewebsites.net
NEXT_PUBLIC_POLL_URL=https://uw-workbench-backend.azurewebsites.net/api/workitems/poll
NEXT_PUBLIC_HEALTH_URL=https://uw-workbench-backend.azurewebsites.net/api/health
NEXT_PUBLIC_LLM_STATUS_URL=https://uw-workbench-backend.azurewebsites.net/api/llm/status

# Feature flags
NEXT_PUBLIC_USE_JAVA_BACKEND=true
NEXT_PUBLIC_ENABLE_ENHANCED_FEATURES=true
```

### Redeploy Frontend
1. Update environment variables in Vercel
2. Trigger new deployment
3. Frontend now uses Azure Java backend

## Architecture After Azure Deployment

```
Frontend (Vercel) → Java Backend (Azure) → Python LLM (Vercel) → PostgreSQL
```

## Monitoring and Troubleshooting

### Azure Web App Features:
- ✅ **Application Insights**: Built-in monitoring
- ✅ **Log Stream**: Real-time logs
- ✅ **Metrics**: CPU, Memory, Requests
- ✅ **Alerts**: Custom alerts and notifications
- ✅ **Scaling**: Manual and auto-scaling
- ✅ **Deployment Slots**: Blue-green deployments

### Common Azure Issues:

#### 1. Port Configuration
```bash
# Ensure your app listens on the correct port
# Azure sets PORT environment variable
server.port=${PORT:80}
```

#### 2. Memory Issues
```bash
# Optimize JVM for Azure (512MB RAM limit)
JAVA_OPTS=-Xmx400m -XX:+UseG1GC
```

#### 3. Cold Start
```bash
# Azure apps may sleep after 20 minutes of inactivity
# Ping your health endpoint periodically to keep warm
```

#### 4. Database Connection
```bash
# Ensure firewall allows Azure IPs
# Check connection string format
```

## Cost Analysis

### Azure Free Tier:
- ✅ **Free for 12 months**: $0/month
- ✅ **After free tier**: ~$13/month (Basic B1)
- ✅ **Compared to Railway**: Similar pricing
- ✅ **Additional Azure credits**: $200 free credit for first month

### Total Architecture Cost:
- **Vercel (Frontend + Python LLM)**: $0-20/month
- **Azure (Java Backend)**: $0-13/month  
- **Database**: Already included
- **Total**: $0-33/month

## Quick Start Commands

### Deploy to Azure (Complete Process):
```bash
# 1. Create Azure Web App (via Portal or CLI)
az webapp create --resource-group uw-workbench-rg --plan uw-workbench-plan --name uw-workbench-backend --runtime "JAVA:21-java21" --sku FREE

# 2. Configure GitHub deployment (via Portal)
# 3. Set environment variables (via Portal)

# 4. Test deployment
curl https://uw-workbench-backend.azurewebsites.net/api/health

# 5. Update frontend environment variables in Vercel
# 6. Test end-to-end functionality
```

## Success Criteria

After successful Azure deployment:
- ✅ Java backend accessible at `https://your-app.azurewebsites.net`
- ✅ Health endpoint returns "healthy" status
- ✅ LLM service integration working (connects to Vercel Python service)
- ✅ Database operations functional
- ✅ Frontend successfully connects to Azure backend
- ✅ Complete email intake flow working
- ✅ Real-time work item polling operational

**Your hybrid architecture will be fully operational with Azure hosting the Java backend, providing enterprise-grade reliability and global availability!**