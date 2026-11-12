# ============================================================
# Makefile - Common Development Tasks
# ============================================================
# Usage:
#   make help          - Show all available commands
#   make install       - Install dependencies
#   make run           - Run the app locally
#   make docker-build  - Build Docker image
#   make docker-run    - Run app in Docker
# ============================================================

.PHONY: help install run docker-build docker-run docker-compose-up docker-compose-down clean test lint format

# Python & pip
PYTHON := python
PIP := $(PYTHON) -m pip
VENV := venv

# Docker
DOCKER_IMAGE := data-analyst
DOCKER_TAG := latest

# Streamlit
STREAMLIT := streamlit

# Default target
help:
	@echo "======================================"
	@echo "Data Analyst Agent - Development Tasks"
	@echo "======================================"
	@echo ""
	@echo "Local Development:"
	@echo "  make install              Install dependencies"
	@echo "  make run                  Run app locally (http://localhost:8501)"
	@echo "  make dev                  Run with debug logging"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build         Build Docker image"
	@echo "  make docker-run           Run Docker container"
	@echo "  make docker-compose-up    Start with docker-compose"
	@echo "  make docker-compose-down  Stop docker-compose"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint                 Lint Python files"
	@echo "  make format               Format Python files"
	@echo "  make test                 Run tests"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean                Clean up cache files"
	@echo "  make venv                 Create virtual environment"
	@echo "  make requirements          Freeze requirements"
	@echo ""
	@echo "Documentation:"
	@echo "  make readme               Display README"
	@echo "  make docker-help          Display Docker guide"
	@echo ""

# ============================================================
# Installation & Setup
# ============================================================

venv:
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created at: $(VENV)"
	@echo "Activate with: $(VENV)\Scripts\activate.bat (Windows) or source $(VENV)/bin/activate (Mac/Linux)"

install: venv
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed successfully!"

requirements:
	$(PIP) freeze > requirements.txt
	@echo "requirements.txt updated"

# ============================================================
# Local Development
# ============================================================

run:
	$(STREAMLIT) run streamlit_app.py

dev:
	$(STREAMLIT) run streamlit_app.py --logger.level=debug

# ============================================================
# Docker Commands
# ============================================================

docker-build:
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)"

docker-run:
	@echo "Starting Docker container..."
	@echo "App at: http://localhost:8501"
	docker run -p 8501:8501 \
		-e gemini_api_1=$${GEMINI_API_1} \
		$(DOCKER_IMAGE):$(DOCKER_TAG)

docker-compose-up:
	docker-compose up

docker-compose-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# ============================================================
# Code Quality
# ============================================================

lint:
	$(PYTHON) -m pylint streamlit_app.py config.py agent.py llm_service.py tools.py utils.py 2>/dev/null || echo "pylint not installed. Install with: pip install pylint"

format:
	$(PYTHON) -m black streamlit_app.py config.py agent.py llm_service.py tools.py utils.py 2>/dev/null || echo "black not installed. Install with: pip install black"

test:
	@echo "No tests configured yet."
	@echo "Add test files to tests/ directory and run: pytest"

# ============================================================
# Cleanup & Maintenance
# ============================================================

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -delete
	rm -rf build/ dist/ .eggs/ 2>/dev/null || true
	@echo "Cleanup complete"

# ============================================================
# Documentation
# ============================================================

readme:
	@cat README.md

docker-help:
	@cat DOCKER_GUIDE.md

quickstart:
	@cat QUICKSTART.md

# ============================================================
# Utility Targets
# ============================================================

.PHONY: check-api-key

check-api-key:
	@grep -q "GEMINI_API_1" .env 2>/dev/null && echo "✓ API key found in .env" || echo "✗ No API key found in .env"

version:
	@$(PYTHON) --version
	@docker --version 2>/dev/null || echo "Docker not installed"

# ============================================================
# Info
# ============================================================

.PHONY: info

info:
	@echo "Project: Data Analyst Agent"
	@echo "Python: $$(python --version)"
	@echo "Streamlit: $$(streamlit --version 2>/dev/null || echo 'not installed')"
	@echo "Docker: $$(docker --version 2>/dev/null || echo 'not installed')"
	@echo "Virtual Env: $(VENV)"
