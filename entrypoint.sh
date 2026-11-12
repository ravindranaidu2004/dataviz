#!/bin/sh
# ============================================================
# Docker Entrypoint Script for Data Analyst Agent
# ============================================================
# This script is executed when the Docker container starts.
# It validates the environment and runs the Streamlit app.
# ============================================================

set -e  # Exit on error

echo "================================================"
echo "Data Analyst Agent - Starting Streamlit App"
echo "================================================"

# Check if API keys are configured
if [ -z "$gemini_api_1" ]; then
    echo "WARNING: gemini_api_1 environment variable not set!"
    echo "The app will fail without valid API keys."
    echo "Set it using: -e gemini_api_1=YOUR_KEY"
    echo ""
fi

# Log configuration
echo "Configuration:"
echo "  Streamlit Port: 8501"
echo "  Streamlit Address: 0.0.0.0"
echo "  Python Version: $(python --version)"
echo "  Log Level: ${LOG_LEVEL:-INFO}"
echo ""

# Run Streamlit app
echo "Starting Streamlit application..."
echo "App will be available at: http://localhost:8501"
echo "================================================"
echo ""

exec streamlit run streamlit_app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --logger.level="${LOG_LEVEL:-info}" \
    --client.showErrorDetails=true
