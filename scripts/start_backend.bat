@echo off
REM =============================================================================
REM BizInsightIQ: Spring Boot Startup Script (Port 8080)
REM Uses application.yml defaults directly - Zero prompts needed!
REM =============================================================================
cd /d "D:\PROJECTS_Workspace_2026\MCA_AI_ML_Project_and_Report\BizInsightIQ\backend"
echo [INFO] Starting Spring Boot Backend on http://localhost:8080...
mvn spring-boot:run
