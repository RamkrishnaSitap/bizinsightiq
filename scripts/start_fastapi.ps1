# =============================================================================
# BizInsightIQ: FastAPI ML Microservice Startup Script (Port 8000)
# =============================================================================

Write-Host "[INFO] Starting FastAPI Microservice on http://127.0.0.1:8000..." -ForegroundColor Cyan
Set-Location -Path "D:\PROJECTS_Workspace_2026\MCA_AI_ML_Project_and_Report\BizInsightIQ"
.\.venv\Scripts\uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
