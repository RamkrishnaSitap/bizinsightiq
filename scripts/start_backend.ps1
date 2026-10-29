# =============================================================================
# BizInsightIQ: Spring Boot Startup Script (Port 8080)
# Uses application.yml defaults directly - Zero prompts needed!
# =============================================================================

Write-Host "[INFO] Starting Spring Boot Backend on http://localhost:8080..." -ForegroundColor Cyan
Set-Location -Path "D:\PROJECTS_Workspace_2026\MCA_AI_ML_Project_and_Report\BizInsightIQ\backend"
mvn spring-boot:run
