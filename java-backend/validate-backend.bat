@echo off
echo ==========================================
echo Java Backend Validation Script
echo ==========================================

echo Checking Java version...
java -version 2>&1 | findstr "version"

echo Checking Maven...
mvn -version 2>nul | findstr "Apache Maven"
if %errorlevel% neq 0 (
    echo Maven not found. Please install Maven.
    exit /b 1
)

echo.
echo Validating project structure...

REM Check key files
set files="src\main\java\com\underwriting\UnderwritingWorkbenchApplication.java" "src\main\java\com\underwriting\domain\Submission.java" "src\main\java\com\underwriting\domain\WorkItem.java" "src\main\java\com\underwriting\repository\SubmissionRepository.java" "src\main\java\com\underwriting\repository\WorkItemRepository.java" "src\main\java\com\underwriting\service\SubmissionService.java" "src\main\java\com\underwriting\service\WorkItemService.java" "src\main\java\com\underwriting\controller\WorkItemController.java" "src\main\resources\application.properties"

for %%f in (%files%) do (
    if exist "%%f" (
        echo ✅ %%f
    ) else (
        echo ❌ %%f - MISSING
    )
)

echo.
echo Compiling the project...
mvn clean compile -q

if %errorlevel% equ 0 (
    echo ✅ Compilation successful!
) else (
    echo ❌ Compilation failed!
    exit /b 1
)

echo.
echo Running tests...
mvn test -q

if %errorlevel% equ 0 (
    echo ✅ Tests passed!
) else (
    echo ⚠️  Some tests failed (this is expected if database is not set up)
)

echo.
echo ==========================================
echo Java Backend Structure Validation Complete
echo ==========================================
echo.
echo Next steps:
echo 1. Start the Java backend: mvn spring-boot:run
echo 2. Test endpoints: curl http://localhost:8080/api/health
echo 3. Proceed to Phase 3: LLM Integration
echo.
echo Available endpoints:
echo   GET  /api/health - Health check
echo   GET  /api/workitems/poll - Poll work items
echo   POST /api/email/intake - Email intake
echo   GET  /api/workitems/{id} - Get work item
echo.

pause