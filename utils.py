"""
Utility functions for data analysis and code execution.
Handles JSON parsing, code execution in sandbox, and data visualization.
"""

import json
import re
import subprocess
import sys
import tempfile
import os
import base64
import logging
from io import BytesIO
from typing import Dict, Any, List, Tuple
import pandas as pd
import matplotlib.pyplot as plt

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from config import Config

logger = logging.getLogger(__name__)


def parse_keys_and_types(raw_questions: str) -> Tuple[List[str], Dict[str, type]]:
    """
    Parse the key/type section from a questions file.

    Expected format in file:
        - `key_name`: type

    Args:
        raw_questions: Raw text from questions file

    Returns:
        Tuple of (keys_list, type_map) where:
            - keys_list: List of keys in order
            - type_map: Dict mapping key name to casting function
    """
    pattern = r"-\s*`([^`]+)`\s*:\s*(\w+)"
    matches = re.findall(pattern, raw_questions)

    type_map_def = {
        "number": float,
        "string": str,
        "integer": int,
        "int": int,
        "float": float,
    }

    type_map = {key: type_map_def.get(t.lower(), str) for key, t in matches}
    keys_list = [k for k, _ in matches]

    logger.debug(f"Parsed {len(keys_list)} keys and types from questions file")
    return keys_list, type_map


def clean_llm_output(output: str) -> Dict:
    """
    Extract and parse JSON object from LLM output robustly.
    Handles various LLM response formats including markdown code blocks.

    Args:
        output: Raw output string from LLM

    Returns:
        Dictionary (parsed JSON) or {"error": "..."}
    """
    try:
        if not output:
            return {"error": "Empty LLM output"}

        # Remove markdown code block markers if present
        s = re.sub(r"^```(?:json)?\s*", "", output.strip())
        s = re.sub(r"\s*```$", "", s)

        # Find outermost JSON object by scanning for balanced braces
        first = s.find("{")
        last = s.rfind("}")

        if first == -1 or last == -1 or last <= first:
            return {"error": "No JSON object found in LLM output", "raw": s}

        candidate = s[first : last + 1]

        try:
            return json.loads(candidate)
        except Exception as e:
            # Fallback: try progressively smaller JSON blocks scanning backwards
            for i in range(last, first, -1):
                cand = s[first : i + 1]
                try:
                    return json.loads(cand)
                except Exception:
                    continue

            return {"error": f"JSON parsing failed: {str(e)}", "raw": candidate}

    except Exception as e:
        return {"error": str(e)}


def plot_to_base64_helper(max_bytes=None) -> str:
    """
    Convert current matplotlib figure to base64-encoded image.
    Automatically reduces DPI and tries WEBP format if size exceeds max_bytes.

    Args:
        max_bytes: Maximum size in bytes (defaults to Config.MAX_IMAGE_SIZE_BYTES)

    Returns:
        Base64-encoded image string
    """
    if max_bytes is None:
        max_bytes = Config.MAX_IMAGE_SIZE_BYTES

    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    buf.seek(0)
    img_bytes = buf.getvalue()

    if len(img_bytes) <= max_bytes:
        return base64.b64encode(img_bytes).decode("ascii")

    # Try decreasing DPI iteratively
    for dpi in [80, 60, 50, 40, 30]:
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=dpi)
        buf.seek(0)
        b = buf.getvalue()
        if len(b) <= max_bytes:
            return base64.b64encode(b).decode("ascii")

    # If PIL available, try WEBP which is smaller
    if PIL_AVAILABLE:
        try:
            buf = BytesIO()
            plt.savefig(buf, format="png", bbox_inches="tight", dpi=40)
            buf.seek(0)
            im = Image.open(buf)
            out_buf = BytesIO()
            im.save(out_buf, format="WEBP", quality=80, method=6)
            out_buf.seek(0)
            ob = out_buf.getvalue()
            if len(ob) <= max_bytes:
                return base64.b64encode(ob).decode("ascii")

            # Try lower quality
            out_buf = BytesIO()
            im.save(out_buf, format="WEBP", quality=60, method=6)
            out_buf.seek(0)
            ob = out_buf.getvalue()
            if len(ob) <= max_bytes:
                return base64.b64encode(ob).decode("ascii")
        except Exception as e:
            logger.warning(f"WEBP conversion failed: {e}")

    # Last resort: return downsized PNG even if > max_bytes
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=20)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def write_and_run_temp_python(
    code: str, injected_pickle: str = None, timeout: int = None
) -> Dict[str, Any]:
    """
    Execute Python code in a sandboxed subprocess.

    The sandbox provides:
    - Common data science imports (pandas, numpy, matplotlib, etc.)
    - DataFrame loading from pickle if provided
    - plot_to_base64() helper for chart visualization
    - results dict for storing answers

    Args:
        code: Python code to execute (should populate `results` dict)
        injected_pickle: Path to pickled DataFrame to inject as `df` variable
        timeout: Execution timeout in seconds (defaults to Config.CODE_EXECUTION_TIMEOUT)

    Returns:
        Dict with format: {"status": "success"|"error", "result": {...}} or error details
    """
    if timeout is None:
        timeout = Config.CODE_EXECUTION_TIMEOUT

    # Build preamble with imports and helper functions
    preamble = [
        "import json, sys, gc",
        "import pandas as pd, numpy as np",
        "import matplotlib",
        "matplotlib.use('Agg')",
        "import matplotlib.pyplot as plt",
        "from io import BytesIO",
        "import base64",
    ]

    if PIL_AVAILABLE:
        preamble.append("from PIL import Image")

    # Inject DataFrame from pickle if provided
    if injected_pickle:
        preamble.append(f"df = pd.read_pickle(r'''{injected_pickle}''')\n")
        preamble.append("data = df.to_dict(orient='records')\n")
    else:
        preamble.append("data = globals().get('data', {})\n")

    # Add plot_to_base64 helper function
    helper = r"""
def plot_to_base64(max_bytes=100000):
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    img_bytes = buf.getvalue()
    if len(img_bytes) <= max_bytes:
        return base64.b64encode(img_bytes).decode('ascii')
    for dpi in [80, 60, 50, 40, 30]:
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)
        buf.seek(0)
        b = buf.getvalue()
        if len(b) <= max_bytes:
            return base64.b64encode(b).decode('ascii')
    try:
        from PIL import Image
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=40)
        buf.seek(0)
        im = Image.open(buf)
        out_buf = BytesIO()
        im.save(out_buf, format='WEBP', quality=80, method=6)
        out_buf.seek(0)
        ob = out_buf.getvalue()
        if len(ob) <= max_bytes:
            return base64.b64encode(ob).decode('ascii')
        out_buf = BytesIO()
        im.save(out_buf, format='WEBP', quality=60, method=6)
        out_buf.seek(0)
        ob = out_buf.getvalue()
        if len(ob) <= max_bytes:
            return base64.b64encode(ob).decode('ascii')
    except Exception:
        pass
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=20)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('ascii')
"""

    # Build complete script
    script_lines = []
    script_lines.extend(preamble)
    script_lines.append(helper)
    script_lines.append("\nresults = {}\n")
    script_lines.append(code)
    script_lines.append(
        "\nprint(json.dumps({'status':'success','result':results}, default=str), flush=True)\n"
    )

    # Write to temporary file and execute
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    )
    tmp.write("\n".join(script_lines))
    tmp.flush()
    tmp_path = tmp.name
    tmp.close()

    try:
        logger.debug(f"Executing code with timeout {timeout}s")
        completed = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if completed.returncode != 0:
            error_msg = completed.stderr.strip() or completed.stdout.strip()
            logger.error(f"Code execution failed: {error_msg[:200]}")
            return {
                "status": "error",
                "message": error_msg,
            }

        # Parse stdout as JSON
        out = completed.stdout.strip()
        try:
            parsed = json.loads(out)
            logger.debug("Code execution completed successfully")
            return parsed
        except Exception as e:
            logger.error(f"Could not parse JSON output: {str(e)}")
            return {
                "status": "error",
                "message": f"Could not parse JSON output: {str(e)}",
                "raw": out,
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Code execution timed out after {timeout}s")
        return {"status": "error", "message": f"Execution timed out after {timeout}s"}

    finally:
        # Cleanup temporary files
        try:
            os.unlink(tmp_path)
            if injected_pickle and os.path.exists(injected_pickle):
                os.unlink(injected_pickle)
                logger.debug("Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
