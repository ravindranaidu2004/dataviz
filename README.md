# 🤖 Data Analyst Agent

> **AI-Powered Data Analysis Made Simple** — Upload your questions and data, get intelligent insights with visualizations

A modular, production-ready data analysis application powered by LangChain and Google Generative AI (Gemini). This application features a modern Streamlit UI, clean architecture, and intelligent fallback mechanisms for enterprise-grade reliability.

---

## 📌 About

The **Data Analyst Agent** is an intelligent system that automatically analyzes your data and answers complex questions using AI. Simply upload:
- **Questions** (What do you want to know?)
- **Data** (Optional - your CSV, Excel, JSON, or Parquet file)

The agent will:
- 🧠 Understand your questions using Google's Gemini AI
- 🔍 Generate Python analysis code automatically
- 💾 Execute code safely in an isolated sandbox
- 📊 Create visualizations and charts
- 📥 Return results in multiple formats

**Perfect for:** Data exploration, business intelligence, research analysis, and quick data insights without writing code.

---

## ⚡ What It Does

### Input
```
Questions (.txt file)          Data (CSV/Excel/JSON) [Optional]
    ↓                                      ↓
    └─────────────────┬────────────────────┘
                      ↓
          AI Agent Processes Both
```

### Process
1. **Understands** your questions using Gemini AI
2. **Generates** Python analysis code automatically
3. **Fetches** web data if no dataset provided
4. **Executes** code safely in isolated sandbox
5. **Generates** charts, tables, and statistics

### Output
```
Results with:
✓ Numerical answers
✓ Statistical analysis
✓ Charts & visualizations
✓ Tables & summaries
✓ Download options (JSON/CSV)
```

### Example

**Question:** "What is the average sales by region and create a chart?"

**Output:**
```
North:   $125,000
South:   $98,500
East:    $142,300
West:    $87,200

[Chart showing sales by region]
```

---

## 🏗️ Architecture

### High-Level Overview

```
┌──────────────────────────────────────┐
│     Streamlit Web Interface          │
│  (User uploads files & questions)    │
└─────────────────┬────────────────────┘
                  │
┌─────────────────▼────────────────────┐
│     Application Layer                │
│  • File parsing & validation         │
│  • Data loading & preprocessing      │
└─────────────────┬────────────────────┘
                  │
┌─────────────────▼────────────────────┐
│     Agent Layer                      │
│  • Question to code generation       │
│  • LLM orchestration                 │
│  • Code execution & results          │
└─────────────────┬────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
   ┌────▼────┐      ┌───────▼──────┐
   │   LLM   │      │Execution     │
   │ Service │      │Sandbox       │
   │(Gemini) │      │(Python)      │
   └─────────┘      └──────────────┘
```

### Module Architecture

```
streamlit_app.py          ← Main UI entry point
    ├─ config.py          ← Configuration & .env loading
    ├─ agent.py           ← Agent orchestration
    │   ├─ llm_service.py ← LLM with fallback logic
    │   ├─ tools.py       ← Web scraping tool
    │   └─ utils.py       ← Code execution & helpers
    └─ requirements.txt    ← Dependencies
```

### Component Details

#### 1. **config.py** - Configuration Management
- Loads environment variables from `.env`
- Validates API keys on startup
- Centralizes all settings
- Supports up to 10 API keys for fallback

#### 2. **llm_service.py** - LLM with Smart Fallback
- Manages Gemini API communication
- Automatically tries different API keys
- Falls back to different models if quota exceeded
- Tracks slow/failing keys
- **Pattern:** Round-robin through keys × models

#### 3. **tools.py** - Data Fetching Tools
- Scrapes data from URLs (HTML tables, CSV, JSON)
- Converts web data to DataFrames
- Supports multiple formats: HTML, CSV, Excel, JSON, Parquet
- Handles network errors gracefully

#### 4. **agent.py** - Agent Orchestration
- Orchestrates the full analysis pipeline
- Converts questions → Python code using LLM
- Executes code in sandbox
- Maps results back to questions
- Retries on failure (up to 3 attempts)

#### 5. **utils.py** - Utility Functions
- `write_and_run_temp_python()`: Executes code in subprocess
- `clean_llm_output()`: Parses LLM JSON responses
- `plot_to_base64_helper()`: Converts charts to images
- `parse_keys_and_types()`: Parses structured questions

#### 6. **streamlit_app.py** - Web Interface
- Modern, responsive UI
- File upload handling
- Progress tracking
- Results display with visualizations
- Download functionality

---

## 🔄 Data Flow Diagram

```
User Input:
├─ questions.txt  → Parsed questions
└─ data.csv       → Loaded DataFrame

         ↓

Agent Processing:
├─ LLM: "Generate code to answer these questions"
├─ LLM Output: {"questions": [...], "code": "..."}
└─ Execute: Run code with data injected

         ↓

Output:
├─ results.json   → Download
├─ results.csv    → Download
├─ Charts         → Display
└─ Tables         → Display
```

---

## 🔐 Security: Sandbox Execution

Code runs in **isolated subprocess** (not in main process):

```python
# Generated code runs in:
subprocess.run([
    sys.executable,
    temp_script.py
], timeout=60)

# With imports:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# User code here...
```

✅ **Safe** - Isolated from main app
✅ **Sandboxed** - Can't access system
✅ **Timeout** - Kills long-running jobs
✅ **Memory managed** - Garbage collected

---

## ✨ Features

## ✨ Features

- **🧠 Intelligent Analysis**: Uses Google Gemini AI to understand and answer data questions
- **📊 Multi-Format Support**: Read CSV, Excel, JSON, and Parquet files
- **🌐 Web Scraping**: Automatically fetch data from URLs (HTML tables, CSV, JSON)
- **🔄 Smart Fallback**: Auto-rotate between multiple API keys when rate-limited
- **⚡ Instant Code Generation**: AI generates Python analysis code automatically
- **🔒 Secure Sandbox**: Execute code safely in isolated subprocess with timeouts
- **📈 Built-in Visualization**: Generate charts and tables automatically
- **💾 Multiple Exports**: Download results as JSON or CSV
- **⚙️ Modular Design**: Clean architecture with 6 focused modules
- **🐳 Docker Ready**: Deploy anywhere with Docker
- **📝 Environment Config**: Centralized `.env` configuration
- **🚀 Production Grade**: Error handling, logging, retry logic

## 📁 Project Structure

## 📁 Project Structure

```
data-analysis-agent-main/
│
├── 🟢 CORE APPLICATION (6 modules)
│   ├── streamlit_app.py       ← Main web interface
│   ├── config.py              ← Configuration & .env management
│   ├── llm_service.py         ← LLM with API key fallback
│   ├── agent.py               ← Agent orchestration & pipeline
│   ├── tools.py               ← Web scraping tool
│   └── utils.py               ← Code execution & utilities
│
├── ⚙️ CONFIGURATION & DEPLOYMENT
│   ├── .env                   ← API keys & settings
│   ├── .gitignore             ← Git ignore patterns
│   ├── requirements.txt       ← Python dependencies
│   ├── runtime.txt            ← Python version (3.12+)
│   ├── Dockerfile             ← Docker image
│   └── entrypoint.sh          ← Docker entry point
│
├── 🚀 RUN SCRIPTS
│   ├── run.bat                ← Windows batch script
│   ├── run.ps1                ← PowerShell script
│   └── RUN_INSTRUCTIONS.md    ← How to run guide
│
├── venv/                      ← Virtual environment (auto-created)
├── __pycache__/               ← Python cache
│
└── 📚 DOCUMENTATION
    ├── README.md              ← Project overview (this file)
    ├── QUICKSTART.md          ← 5-minute setup guide
    ├── SETUP_COMPLETE.md      ← Setup verification
    ├── CLEANUP.md             ← Cleanup & removal info
    └── MIGRATION_GUIDE.md     ← Migration from v1
```

## 🚀 Getting Started

### Prerequisites
- **Python 3.12+** 
- **Virtual environment** (recommended)
- **Google Gemini API key** (free)

### Quick Start (3 Steps)

#### Step 1: Get API Key (1 minute)
1. Go to: https://aistudio.google.com/app/apikey
2. Click **"Create API Key"**
3. Copy the key

#### Step 2: Setup Project (2 minutes)

**Using Command Prompt/PowerShell:**
```bash
# Clone or navigate to project
cd data-analysis-agent-main

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

**Using our run script (Easiest):**
```bash
# Just double-click: run.bat
# Or: .\run.ps1 (in PowerShell)
```

#### Step 3: Configure API Key
Edit `.env` file:
```env
gemini_api_1=YOUR_API_KEY_HERE
gemini_api_2=OPTIONAL_SECOND_KEY
# Optional: Add up to 10 keys for better reliability
```

#### Step 4: Run the Application

**Option A: Easy (Double-Click)**
```
Double-click: run.bat
```

**Option B: Command Line**
```bash
streamlit run streamlit_app.py
```

**Option C: With venv activated**
```bash
venv\Scripts\activate.bat
streamlit run streamlit_app.py
```

✅ App opens at: **http://localhost:8501**

---

## 📖 How to Use

### Workflow

```
1. Open App Browser
   ↓
2. Upload Questions (.txt file)
   ↓
3. Upload Data (optional) (CSV/Excel/JSON/Parquet)
   ↓
4. Click "Analyze" Button
   ↓
5. Wait for AI Processing
   ↓
6. View Results with Charts
   ↓
7. Download Results (JSON/CSV)
```

### Detailed Steps

**Step 1: Prepare Questions File**
Create a `.txt` file with your questions (one per line):
```
What is the average sales by region?
Which product has the highest revenue?
Create a bar chart of monthly trends
Is there a correlation between price and sales?
```

Or use structured format for specific output types:
```
- `revenue`: number
- `product_name`: string
- `growth_rate`: float
```

**Step 2: Prepare Data (Optional)**
You can upload:
- **CSV file** (.csv)
- **Excel workbook** (.xlsx, .xls)
- **JSON file** (.json)
- **Parquet file** (.parquet)

Or leave empty to analyze web data instead.

**Step 3: Click Analyze**
The app will:
1. Parse your questions
2. Understand your data
3. Generate Python analysis code
4. Execute code in secure sandbox
5. Create visualizations
6. Return results

**Step 4: View Results**
- See answers to each question
- View charts and tables
- Download as JSON or CSV

### Example Analysis

**Input:**
```
Questions: "What are top 3 products by revenue?"
Data: sales_data.csv (1000 rows of sales)
```

**Output:**
```
1. Product A: $125,000
2. Product B: $98,500
3. Product C: $87,200

[Bar chart showing revenue by product]
```

## 📖 Usage Details

1. **Upload Questions File**: Provide a `.txt` file with your analysis questions
   - One question per line, or use structured format: `- \`key_name\`: type`

2. **Upload Dataset (Optional)**: Provide data in one of these formats:
   - CSV (`.csv`)
   - Excel (`.xlsx`, `.xls`)
   - JSON (`.json`)
   - Parquet (`.parquet`)

3. **Click Analyze**: The agent will:
   - Parse your questions
   - Generate Python analysis code
   - Fetch web data if needed (when no dataset is provided)
   - Execute the code safely in a sandbox
   - Display results with visualizations

4. **Download Results**: Export results as JSON or CSV

## 🔧 Configuration

Edit `.env` to customize:

```env
# LLM Configuration
LLM_TEMPERATURE=0              # Creativity (0=deterministic, 1=creative)
LLM_TIMEOUT_SECONDS=240        # LLM response timeout

# Code Execution
CODE_EXECUTION_TIMEOUT=60      # Sandbox execution timeout
MAX_IMAGE_SIZE_BYTES=100000    # Max chart size (100KB)
MAX_RETRIES_PER_KEY=2          # Retries per API key

# Agent Behavior
AGENT_MAX_ITERATIONS=3         # Max agent thinking iterations
AGENT_EARLY_STOPPING_METHOD=generate

# Logging
LOG_LEVEL=INFO                 # INFO, DEBUG, ERROR
DEBUG_MODE=false               # Enable debug logging
```

## 📚 Module Overview

### `config.py`
Centralized configuration management. Loads variables from `.env` and validates setup.

### `llm_service.py`
LLM wrapper with automatic fallback:
- Tries multiple API keys when rate-limited
- Falls back to different models in order of preference
- Tracks slow/failing keys

### `utils.py`
Core utility functions:
- `parse_keys_and_types()`: Parse structured questions format
- `clean_llm_output()`: Extract JSON from LLM responses
- `write_and_run_temp_python()`: Execute code in sandbox with imports
- `plot_to_base64_helper()`: Convert charts to optimized base64

### `tools.py`
LangChain tools for the agent:
- `scrape_url_to_dataframe()`: Fetch data from URLs (HTML tables, CSV, JSON, etc.)

### `agent.py`
LangChain agent orchestration:
- Sets up the agent with tools
- Manages agent-LLM communication
- Handles code execution pipeline

### `streamlit_app.py`
Modern Streamlit UI:
- File upload interface
- Data preview
- Progress tracking
- Results display with visualizations
- Download options

## 🐳 Docker Deployment

```bash
# Build image
docker build -t data-analyst-agent .

# Run container
docker run -p 8501:8501 \
  -e gemini_api_1=YOUR_API_KEY \
  -e LLM_TIMEOUT_SECONDS=240 \
  data-analyst-agent
```

## 🔍 Troubleshooting

### "No Gemini API keys found"
- Ensure `.env` file exists in project root
- Add at least one `gemini_api_1=YOUR_KEY` to `.env`
- Restart the application

### "Quota exceeded" errors
- Add more API keys to `.env` (up to 10)
- Reduce request frequency
- Use different Gemini models

### Code execution timeout
- Increase `CODE_EXECUTION_TIMEOUT` in `.env`
- Optimize your analysis questions
- Use smaller datasets

### Port already in use
```bash
streamlit run streamlit_app.py --server.port=8502
```

## 🎯 Best Practices

1. **Questions Format**: Be specific and clear in your questions
   - "What is the average sales by region?" ✅
   - "Analyze the data" ❌

2. **Large Datasets**: Test with smaller subsets first
   - Reduces processing time
   - Easier to debug issues

3. **API Keys**: Use multiple keys for better reliability
   - Distribute API key quota across requests
   - Automatic fallback on rate limits

4. **Data Privacy**: Don't upload sensitive data without encryption
   - Verify `.env` file is in `.gitignore`
   - Consider self-hosted deployment for sensitive data

## 📝 Examples

### Example 1: Sales Analysis
**Questions file:**
```
What are the total sales by region?
Which product has the highest revenue?
What is the month-over-month growth rate?
```

**Upload:** sales_data.csv

### Example 2: Web Data Analysis
**Questions file:**
```
What are the current Bitcoin and Ethereum prices?
Create a visualization of historical price trends
```

**Upload:** None (agent will scrape data automatically)

## 🤝 Contributing

To extend this project:

1. Add new tools in `tools.py`
2. Modify system prompt in `agent.py`
3. Customize UI in `streamlit_app.py`
4. Add features in `utils.py`

## 📄 License

This project is provided as-is for educational and commercial use.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in the Streamlit UI
3. Check `.env` configuration
4. Review logs with `LOG_LEVEL=DEBUG`

---

**Made with ❤️ using Streamlit, LangChain, and Google Generative AI**
