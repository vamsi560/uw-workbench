# Underwriting Workbench - Java Backend

This is the Java Spring Boot backend for the Underwriting Workbench application, designed to work alongside the Python LLM microservice.

## Architecture

```
Frontend (Next.js) → Java Backend (Spring Boot) → Python LLM Service
                            ↓
                     PostgreSQL Database
```

## Features

- **REST API** with comprehensive endpoints for submissions and work items
- **JPA/Hibernate** for database operations
- **CORS Support** for frontend integration
- **Validation** using Bean Validation
- **PostgreSQL Integration** with the same database as Python service
- **LLM Service Client** for AI/ML integration (Phase 3)

## Prerequisites

- Java 17 or later
- Maven 3.6 or later
- PostgreSQL database (shared with Python service)
- Python LLM microservice running on port 8001

## Getting Started

### 1. Validate Setup
```bash
# Windows
validate-backend.bat

# Linux/Mac
chmod +x validate-backend.sh
./validate-backend.sh
```

### 2. Run the Application
```bash
mvn spring-boot:run
```

The application will start on `http://localhost:8080`

### 3. Test the API
```bash
# Health check
curl http://localhost:8080/api/health

# Poll work items
curl http://localhost:8080/api/workitems/poll
```

## API Endpoints

### Core Endpoints
- `GET /api/health` - Health check
- `GET /api/workitems/poll` - Poll for work items (frontend polling)
- `POST /api/email/intake` - Process email submissions
- `GET /api/workitems/{id}` - Get work item by ID
- `POST /api/workitems` - Create new work item
- `PUT /api/workitems/{id}` - Update work item

### Work Item Management
- `GET /api/workitems/attention` - Get items needing attention
- `GET /api/workitems/search?q={term}` - Search work items
- `GET /api/submissions/{id}/workitems` - Get work items for submission

## Configuration

Key configuration in `src/main/resources/application.properties`:

```properties
# Server configuration
server.port=8080

# Database (shared with Python service)
spring.datasource.url=postgresql://...
spring.datasource.username=retool
spring.datasource.password=...

# LLM Service integration
llm.service.url=http://localhost:8001

# CORS for frontend
cors.allowed-origins=https://uw-workbench-portal.vercel.app,https://uw-workbench-jade.vercel.app
```

## Database Schema

The Java backend uses the same PostgreSQL database as the Python service:

- **submissions** - Main submission records
- **work_items** - Individual work items for processing
- **submission_history** - Audit trail (future)
- **risk_assessments** - AI risk scoring (future)

## Development

### Project Structure
```
src/main/java/com/underwriting/
├── domain/          # JPA entities
│   ├── Submission.java
│   ├── WorkItem.java
│   └── Enums.java
├── repository/      # Data access layer
│   ├── SubmissionRepository.java
│   └── WorkItemRepository.java
├── service/         # Business logic
│   ├── SubmissionService.java
│   ├── WorkItemService.java
│   └── LLMServiceClient.java
├── controller/      # REST endpoints
│   └── WorkItemController.java
├── dto/            # Data transfer objects
├── config/         # Configuration classes
└── UnderwritingWorkbenchApplication.java
```

### Adding New Features

1. **Add Entity**: Create JPA entity in `domain/`
2. **Add Repository**: Create repository interface extending `JpaRepository`
3. **Add Service**: Create service class with business logic
4. **Add Controller**: Create REST controller with endpoints
5. **Add DTO**: Create data transfer objects for API

### Testing

```bash
# Run all tests
mvn test

# Run specific test
mvn test -Dtest=SubmissionServiceTest

# Run integration tests
mvn verify
```

## Integration with Python Service

The Java backend communicates with the Python LLM microservice via HTTP:

- **LLMServiceClient** handles REST calls to Python service
- **WebClient** for reactive HTTP communication
- **Fallback handling** for service unavailability

## Deployment

### Local Development
```bash
mvn spring-boot:run
```

### Production Build
```bash
mvn clean package
java -jar target/uw-workbench-backend-1.0.0.jar
```

### Docker (Future)
```bash
docker build -t uw-workbench-backend .
docker run -p 8080:8080 uw-workbench-backend
```

## Monitoring

- **Actuator endpoints**: `/actuator/health`, `/actuator/metrics`
- **Application logs**: Configured for structured logging
- **Database connection**: Health checks included

## Next Steps (Phase 3)

1. **Complete LLM Integration**: Implement full REST client for Python service
2. **Add Authentication**: JWT or OAuth2 integration
3. **Add Audit Trail**: Complete audit logging
4. **Add Caching**: Redis for performance
5. **Add Monitoring**: Metrics and alerting

## Troubleshooting

### Common Issues

1. **Database Connection**
   - Verify PostgreSQL is running
   - Check database URL and credentials
   - Ensure database schema exists

2. **Python Service Communication**
   - Verify Python LLM service is running on port 8001
   - Check network connectivity
   - Review LLM service logs

3. **Port Conflicts**
   - Change port in `application.properties`: `server.port=8081`
   - Update frontend configuration accordingly

### Logs
```bash
# View application logs
tail -f logs/application.log

# Enable debug logging
logging.level.com.underwriting=DEBUG
```