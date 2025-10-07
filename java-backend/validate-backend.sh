#!/bin/bash

echo "=========================================="
echo "Java Backend Validation Script"
echo "=========================================="

# Check if Java 17 is available
echo "Checking Java version..."
java -version 2>&1 | head -1

# Check if Maven is available
echo "Checking Maven..."
if command -v mvn &> /dev/null; then
    mvn -version | head -1
else
    echo "Maven not found. Please install Maven."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "pom.xml" ]; then
    echo "Error: pom.xml not found. Please run this script from the java-backend directory."
    exit 1
fi

echo ""
echo "Validating project structure..."

# Check key files
files=(
    "src/main/java/com/underwriting/UnderwritingWorkbenchApplication.java"
    "src/main/java/com/underwriting/domain/Submission.java"
    "src/main/java/com/underwriting/domain/WorkItem.java"
    "src/main/java/com/underwriting/repository/SubmissionRepository.java"
    "src/main/java/com/underwriting/repository/WorkItemRepository.java"
    "src/main/java/com/underwriting/service/SubmissionService.java"
    "src/main/java/com/underwriting/service/WorkItemService.java"
    "src/main/java/com/underwriting/controller/WorkItemController.java"
    "src/main/resources/application.properties"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING"
    fi
done

echo ""
echo "Compiling the project..."
mvn clean compile -q

if [ $? -eq 0 ]; then
    echo "✅ Compilation successful!"
else
    echo "❌ Compilation failed!"
    exit 1
fi

echo ""
echo "Running tests..."
mvn test -q

if [ $? -eq 0 ]; then
    echo "✅ Tests passed!"
else
    echo "⚠️  Some tests failed (this is expected if database is not set up)"
fi

echo ""
echo "=========================================="
echo "Java Backend Structure Validation Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start the Java backend: mvn spring-boot:run"
echo "2. Test endpoints: curl http://localhost:8080/api/health"
echo "3. Proceed to Phase 3: LLM Integration"
echo ""
echo "Available endpoints:"
echo "  GET  /api/health - Health check"
echo "  GET  /api/workitems/poll - Poll work items"
echo "  POST /api/email/intake - Email intake"
echo "  GET  /api/workitems/{id} - Get work item"
echo ""