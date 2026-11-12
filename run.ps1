# PowerShell script to run the Data Analyst Agent
# This script activates the venv and starts Streamlit

Set-Location $PSScriptRoot

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Starting Data Analyst Agent..." -ForegroundColor Green
Write-Host ""
Write-Host "App will open at: http://localhost:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the app" -ForegroundColor Yellow
Write-Host ""

streamlit run streamlit_app.py

Read-Host "Press Enter to exit"
