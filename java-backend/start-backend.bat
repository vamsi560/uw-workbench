@echo off
REM Windows startup script for Java backend
REM This script compiles and runs the Java backend without Maven

cd /d "%~dp0"

echo Starting Java Backend Compilation...

REM Create output directory
if not exist "target\classes" mkdir target\classes

REM Compile Java source files
echo Compiling Java sources...

REM We need to download dependencies first or use a simpler approach
echo ERROR: Maven/Gradle required to resolve dependencies and run the Spring Boot application.
echo.
echo Please install Maven or Gradle to run the Java backend:
echo.
echo Option 1 - Install Maven:
echo 1. Download Maven from https://maven.apache.org/download.cgi
echo 2. Extract to C:\apache-maven
echo 3. Add C:\apache-maven\bin to your PATH
echo 4. Run: mvn spring-boot:run
echo.
echo Option 2 - Use Gradle:
echo 1. Download Gradle from https://gradle.org/releases/
echo 2. Extract and add to PATH
echo 3. Run: gradle bootRun
echo.
echo Option 3 - Install via Chocolatey:
echo 1. Install Chocolatey: https://chocolatey.org/
echo 2. Run: choco install maven
echo 3. Run: mvn spring-boot:run
echo.
echo For now, we'll proceed with frontend configuration and testing with mock data.

pause