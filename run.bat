@echo off
REM Activate virtual environment and run Streamlit app
REM This script uses the venv in the current directory

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Data Analyst Agent...
echo.
echo App will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the app
echo.

streamlit run streamlit_app.py

pause
