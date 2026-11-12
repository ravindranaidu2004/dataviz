"""
Tools for the data analysis agent.
Provides web scraping capabilities to fetch and parse data from URLs.
"""

import logging
import re
from typing import Dict, Any
import requests
import pandas as pd
from io import BytesIO, StringIO
from bs4 import BeautifulSoup
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def scrape_url_to_dataframe(url: str) -> Dict[str, Any]:
    """
    Fetch a URL and return data as a DataFrame.

    Supports multiple formats:
    - HTML tables
    - CSV files
    - Excel files (.xls, .xlsx)
    - Parquet files
    - JSON data
    - Plain text

    Args:
        url: The URL to fetch data from

    Returns:
        Dictionary with format:
        {
            "status": "success" or "error",
            "data": [...],  # List of dicts if successful
            "columns": [...],  # Column names if successful
            "message": "..."  # Error message if status is "error"
        }
    """
    logger.info(f"Scraping URL: {url}")

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.google.com/",
        }

        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        ctype = resp.headers.get("Content-Type", "").lower()

        df = None

        # --- CSV ---
        if "text/csv" in ctype or url.lower().endswith(".csv"):
            logger.debug("Detected CSV format")
            df = pd.read_csv(BytesIO(resp.content))

        # --- Excel ---
        elif (
            any(url.lower().endswith(ext) for ext in (".xls", ".xlsx"))
            or "spreadsheetml" in ctype
        ):
            logger.debug("Detected Excel format")
            df = pd.read_excel(BytesIO(resp.content))

        # --- Parquet ---
        elif url.lower().endswith(".parquet"):
            logger.debug("Detected Parquet format")
            df = pd.read_parquet(BytesIO(resp.content))

        # --- JSON ---
        elif "application/json" in ctype or url.lower().endswith(".json"):
            logger.debug("Detected JSON format")
            try:
                data = resp.json()
                df = pd.json_normalize(data)
            except Exception:
                df = pd.DataFrame([{"text": resp.text}])

        # --- HTML / Fallback ---
        elif "text/html" in ctype or re.search(
            r"/wiki/|\.org|\.com", url, re.IGNORECASE
        ):
            logger.debug("Detected HTML format")
            html_content = resp.text

            # Try HTML tables first
            try:
                tables = pd.read_html(StringIO(html_content), flavor="bs4")
                if tables:
                    df = tables[0]
                    logger.debug(f"Extracted table with {len(df)} rows")
            except ValueError:
                logger.debug("No HTML tables found, falling back to text extraction")

            # If no table found, fallback to plain text
            if df is None:
                soup = BeautifulSoup(html_content, "html.parser")
                text = soup.get_text(separator="\n", strip=True)
                df = pd.DataFrame({"text": [text]})

        # --- Unknown type fallback ---
        else:
            logger.debug(f"Unknown content type: {ctype}, using fallback")
            df = pd.DataFrame({"text": [resp.text]})

        # --- Normalize columns ---
        df.columns = (
            df.columns.map(str).str.replace(r"\[.*\]", "", regex=True).str.strip()
        )

        logger.info(f"Successfully scraped {len(df)} rows from {url}")

        return {
            "status": "success",
            "data": df.to_dict(orient="records"),
            "columns": df.columns.tolist(),
        }

    except Exception as e:
        error_msg = f"Failed to scrape {url}: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "data": [],
            "columns": [],
        }


def get_tools():
    """Get list of all available tools for the agent.

    Returns:
        List of tool functions
    """
    return [scrape_url_to_dataframe]
