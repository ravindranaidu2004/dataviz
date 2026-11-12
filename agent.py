import logging
import re
import tempfile
from typing import Dict, Any, List
import pandas as pd

from config import Config
from llm_service import get_llm
from tools import scrape_url_to_dataframe
from utils import clean_llm_output, write_and_run_temp_python

logger = logging.getLogger(__name__)


# System prompt for the agent
SYSTEM_PROMPT = """You are a full-stack autonomous data analyst agent.

You will receive:
- A set of **rules** for this request (these rules may differ depending on whether a dataset is uploaded or not)
- One or more **questions**
- An optional **dataset preview**

You must:
1. Follow the provided rules exactly.
2. Return only a valid JSON object — no extra commentary or formatting.
3. The JSON must contain:
   - "questions": [ list of original question strings exactly as provided ]
   - "code": "..." (Python code that creates a dict called `results` with each question string as a key and its computed answer as the value)
4. Your Python code will run in a sandbox with:
   - pandas, numpy, matplotlib available
   - A helper function `plot_to_base64(max_bytes=100000)` for generating base64-encoded images under 100KB.
5. When returning plots, always use `plot_to_base64()` to keep image sizes small.
6. Make sure all variables are defined before use, and the code can run without any undefined references.
"""


class DataAnalysisAgent:
    """Orchestrates the data analysis workflow using direct LLM calls."""

    def __init__(self):
        """Initialize the data analysis agent."""
        self.llm = get_llm()
        logger.info("DataAnalysisAgent initialized successfully")

    def run(self, llm_input: str, pickle_path: str = None) -> Dict[str, Any]:
        """
        Run the agent to answer questions about data.

        Args:
            llm_input: The input prompt for the LLM (includes rules, questions, and data preview)
            pickle_path: Path to a pickled DataFrame to inject into the sandbox

        Returns:
            Dictionary mapping questions to answers, or error details
        """
        try:
            max_retries = 3
            raw_out = ""

            # Try multiple times to get a response from LLM
            for attempt in range(1, max_retries + 1):
                logger.debug(f"LLM attempt {attempt}/{max_retries}")
                try:
                    response = self.llm.invoke(llm_input)
                    # Handle both string and message responses
                    raw_out = (
                        response if isinstance(response, str) else response.content
                    )
                    if raw_out:
                        break
                except Exception as e:
                    logger.warning(f"Attempt {attempt} failed: {e}")
                    if attempt == max_retries:
                        raise

            if not raw_out:
                error_msg = f"LLM returned no output after {max_retries} attempts"
                logger.error(error_msg)
                return {"error": error_msg}

            # Parse LLM output to extract JSON
            parsed = clean_llm_output(raw_out)
            if "error" in parsed:
                logger.error(f"Failed to parse LLM output: {parsed}")
                return parsed

            # Validate response structure
            if "code" not in parsed or "questions" not in parsed:
                error_msg = f"Invalid agent response structure: {parsed}"
                logger.error(error_msg)
                return {"error": error_msg}

            code = parsed["code"]
            questions: List[str] = parsed["questions"]

            logger.debug(f"Extracted {len(questions)} questions from agent response")

            # Handle web scraping if needed
            if pickle_path is None:
                urls = re.findall(r"scrape_url_to_dataframe\(\s*['\"](.+?)['\"]", code)
                if urls:
                    url = urls[0]
                    logger.debug(f"Detected URL to scrape: {url}")
                    tool_resp = scrape_url_to_dataframe(url)
                    if tool_resp.get("status") != "success":
                        error_msg = f"Scrape tool failed: {tool_resp.get('message')}"
                        logger.error(error_msg)
                        return {"error": error_msg}

                    # Create and pickle the DataFrame
                    df = pd.DataFrame(tool_resp["data"])
                    temp_pkl = tempfile.NamedTemporaryFile(suffix=".pkl", delete=False)
                    temp_pkl.close()
                    df.to_pickle(temp_pkl.name)
                    pickle_path = temp_pkl.name
                    logger.debug(f"Created pickle of scraped data: {pickle_path}")

            # Execute the code
            logger.debug("Executing generated code")
            exec_result = write_and_run_temp_python(
                code, injected_pickle=pickle_path, timeout=Config.CODE_EXECUTION_TIMEOUT
            )

            if exec_result.get("status") != "success":
                error_msg = f"Code execution failed: {exec_result.get('message')}"
                logger.error(error_msg)
                return {
                    "error": error_msg,
                    "raw": exec_result.get("raw"),
                }

            # Extract results and map to questions
            results_dict = exec_result.get("result", {})
            output = {q: results_dict.get(q, "Answer not found") for q in questions}

            logger.info(f"Successfully processed {len(questions)} questions")
            return output

        except Exception as e:
            error_msg = f"Agent execution failed: {str(e)}"
            logger.exception(error_msg)
            return {"error": error_msg}


# Global agent instance
_agent_instance = None


def get_agent() -> DataAnalysisAgent:
    """Get or create the global DataAnalysisAgent instance.

    Returns:
        DataAnalysisAgent instance
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = DataAnalysisAgent()
    return _agent_instance
