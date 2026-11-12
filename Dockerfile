# ============================================================
# Data Analyst Agent - Docker Image
# ============================================================
# Build: docker build -t data-analyst .
# Run:   docker run -p 8501:8501 \
#          -e gemini_api_1=YOUR_KEY \
#          data-analyst
# ============================================================

# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set metadata labels
LABEL maintainer="Data Analyst Agent"
LABEL description="AI-Powered Data Analysis Agent with Streamlit UI"
LABEL version="2.0"

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY --chown=appuser:appuser config.py .
COPY --chown=appuser:appuser llm_service.py .
COPY --chown=appuser:appuser utils.py .
COPY --chown=appuser:appuser tools.py .
COPY --chown=appuser:appuser agent.py .
COPY --chown=appuser:appuser streamlit_app.py .
COPY --chown=appuser:appuser entrypoint.sh .

# Copy environment file if it exists (optional)
COPY --chown=appuser:appuser .env* ./

# Copy documentation
COPY --chown=appuser:appuser README.md .
COPY --chown=appuser:appuser QUICKSTART.md .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Switch to non-root user
USER appuser

# Expose the port (Streamlit default)
EXPOSE 8501

# Health check to ensure app is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["./entrypoint.sh"]