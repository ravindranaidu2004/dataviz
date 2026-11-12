"""
Streamlit UI for the Data Analysis Agent.
Modern, user-friendly interface for data analysis with AI.
"""

import streamlit as st
import pandas as pd
import io
import tempfile
import logging
from typing import Optional, Dict, Any

from agent import get_agent
from utils import parse_keys_and_types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🤖 Data Analyst Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1f77b4;
    }
    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .result-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .error-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #d62728;
        background-color: #ffe6e6;
    }
    .success-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #2ca02c;
        background-color: #e6ffe6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and description
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        '<p class="main-title">🤖 Data Analyst Agent</p>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="subtitle">Upload your questions and data to get intelligent analysis with visualizations</p>',
        unsafe_allow_html=True,
    )

st.divider()

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    show_advanced = st.checkbox("Show Advanced Options", value=False)

    if show_advanced:
        st.subheader("Model Settings")
        st.info(
            "Model selection is automatic based on API key availability and rate limits. "
            "The agent will fallback to alternative models if needed."
        )


def load_questions_file(file_content: bytes) -> Optional[str]:
    """Load and parse questions from uploaded file.

    Args:
        file_content: Raw file content bytes

    Returns:
        Decoded text content or None if error
    """
    try:
        return file_content.decode("utf-8")
    except Exception as e:
        st.error(f"Failed to read questions file: {str(e)}")
        return None


def load_data_file(file_content: bytes, filename: str) -> Optional[pd.DataFrame]:
    """Load data from various file formats.

    Args:
        file_content: Raw file content bytes
        filename: Original filename (used to detect format)

    Returns:
        Loaded DataFrame or None if error
    """
    try:
        filename_lower = filename.lower()

        if filename_lower.endswith(".csv"):
            return pd.read_csv(io.BytesIO(file_content))
        elif filename_lower.endswith((".xlsx", ".xls")):
            return pd.read_excel(io.BytesIO(file_content))
        elif filename_lower.endswith(".json"):
            return pd.read_json(io.BytesIO(file_content))
        elif filename_lower.endswith(".parquet"):
            return pd.read_parquet(io.BytesIO(file_content))
        else:
            st.error(f"Unsupported file format: {filename}")
            return None
    except Exception as e:
        st.error(f"Failed to load data file: {str(e)}")
        return None


def format_result(question: str, answer: Any) -> str:
    """Format a single result for display.

    Args:
        question: The question asked
        answer: The answer/result

    Returns:
        Formatted string
    """
    # Handle base64 encoded images
    if isinstance(answer, str) and answer.startswith("iVBOR"):
        # It's likely a base64 PNG
        import base64

        return f"[Image: base64-encoded PNG]"

    # Handle dict/list results
    if isinstance(answer, (dict, list)):
        return str(answer)

    return str(answer)


# Main content area
col1, col2 = st.columns([1, 1])

# Left column: File uploads
with col1:
    st.header("📤 Upload Files")

    # Questions file - REQUIRED
    st.subheader("Questions File ⭐ Required", divider=True)
    questions_file = st.file_uploader(
        "Upload a .txt file with your questions",
        type=["txt"],
        help="Text file containing your analysis questions. "
        "Each line can be a question, or use '- `key`: type' format for structured output.",
    )

    if questions_file:
        st.success(f"✓ Questions file loaded: {questions_file.name}")

    # Dataset file - OPTIONAL
    st.subheader("Dataset File (Optional)", divider=True)
    data_file = st.file_uploader(
        "Upload a dataset file (optional)",
        type=["csv", "xlsx", "xls", "json", "parquet"],
        help="Optional dataset for analysis. Supports CSV, Excel, JSON, and Parquet formats.",
    )

    if data_file:
        st.success(f"✓ Data file loaded: {data_file.name}")


# Right column: Preview and controls
with col2:
    st.header("👁️ Preview & Analysis")

    # Show file previews
    if questions_file:
        with st.expander("📄 Questions Preview", expanded=True):
            questions_content = load_questions_file(questions_file.getvalue())
            if questions_content:
                # Show first 500 chars
                preview = questions_content[:500]
                if len(questions_content) > 500:
                    preview += "\n\n[... truncated ...]"
                st.text(preview)

    if data_file:
        with st.expander("📊 Data Preview"):
            df = load_data_file(data_file.getvalue(), data_file.name)
            if df is not None:
                st.info(
                    f"Dataset shape: **{len(df)} rows × {len(df.columns)} columns**"
                )
                st.dataframe(df.head(10), width="stretch")

# Analysis button
st.divider()
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    analyze_button = st.button(
        "🚀 Analyze",
        width="stretch",
        type="primary",
        disabled=(questions_file is None),
    )

st.divider()

# Process analysis
if analyze_button:
    if questions_file is None:
        st.error("❌ Please upload a questions file (.txt)")
    else:
        # Load questions
        questions_content = load_questions_file(questions_file.getvalue())
        if not questions_content:
            st.stop()

        # Parse keys and types if provided
        keys_list, type_map = parse_keys_and_types(questions_content)

        # Load data if provided
        pickle_path = None
        df_preview = ""
        dataset_uploaded = False

        if data_file:
            dataset_uploaded = True
            df = load_data_file(data_file.getvalue(), data_file.name)
            if df is None:
                st.stop()

            st.success(f"✓ Loaded dataset: {len(df)} rows, {len(df.columns)} columns")

            # Create pickle for agent
            temp_pkl = tempfile.NamedTemporaryFile(suffix=".pkl", delete=False)
            temp_pkl.close()
            df.to_pickle(temp_pkl.name)
            pickle_path = temp_pkl.name

            df_preview = (
                f"\n\nThe uploaded dataset has {len(df)} rows and {len(df.columns)} columns.\n"
                f"Columns: {', '.join(df.columns.astype(str))}\n"
                f"First rows:\n{df.head(5).to_markdown(index=False)}\n"
            )

        # Build rules based on data presence
        if dataset_uploaded:
            llm_rules = (
                "Rules:\n"
                "1) You have access to a pandas DataFrame called `df` and its dictionary form `data`.\n"
                "2) DO NOT call scrape_url_to_dataframe() or fetch any external data.\n"
                "3) Use only the uploaded dataset for answering questions.\n"
                "4) Produce a final JSON object with keys:\n"
                '   - "questions": [ ... original question strings ... ]\n'
                '   - "code": "..."  (Python code that fills `results` with exact question strings as keys)\n'
                "5) For plots: use plot_to_base64() helper to return base64 image data under 100kB.\n"
            )
        else:
            llm_rules = (
                "Rules:\n"
                "1) If you need web data, CALL scrape_url_to_dataframe(url).\n"
                "2) Produce a final JSON object with keys:\n"
                '   - "questions": [ ... original question strings ... ]\n'
                '   - "code": "..."  (Python code that fills `results` with exact question strings as keys)\n'
                "3) For plots: use plot_to_base64() helper to return base64 image data under 100kB.\n"
            )

        llm_input = (
            f"{llm_rules}\nQuestions:\n{questions_content}\n"
            f"{df_preview if df_preview else ''}"
            "Respond with the JSON object only."
        )

        # Run analysis with progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("🤖 Initializing agent...")
        progress_bar.progress(20)

        agent = get_agent()

        status_text.text("🔄 Processing by LLM...")
        progress_bar.progress(50)

        results = agent.run(llm_input, pickle_path=pickle_path)

        status_text.text("✅ Complete!")
        progress_bar.progress(100)

        # Display results
        st.divider()
        st.header("📊 Analysis Results")

        if "error" in results:
            st.markdown(
                f'<div class="error-box"><strong>❌ Error:</strong> {results["error"]}</div>',
                unsafe_allow_html=True,
            )
            if results.get("raw"):
                with st.expander("🔍 Debug Information"):
                    st.text(results["raw"])
        else:
            st.markdown(
                '<div class="success-box"><strong>✓ Analysis completed successfully!</strong></div>',
                unsafe_allow_html=True,
            )

            # Display each result
            for question, answer in results.items():
                with st.expander(f"❓ {question}", expanded=True):
                    # Handle base64 images
                    if isinstance(answer, str) and answer.startswith("iVBOR"):
                        import base64

                        try:
                            image_data = base64.b64decode(answer)
                            st.image(image_data, use_column_width=True)
                        except Exception as e:
                            st.text(f"Error displaying image: {e}")
                    else:
                        st.write(answer)

            # Option to download results
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                # Export as JSON
                results_json = pd.Series(results).to_json(indent=2)
                st.download_button(
                    label="📥 Download Results (JSON)",
                    data=results_json,
                    file_name="analysis_results.json",
                    mime="application/json",
                )

            with col2:
                # Export as CSV
                results_df = pd.DataFrame(
                    [
                        {"Question": q, "Answer": str(a)[:500]}
                        for q, a in results.items()
                    ]
                )
                csv_data = results_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results (CSV)",
                    data=csv_data,
                    file_name="analysis_results.csv",
                    mime="text/csv",
                )


# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9rem; margin-top: 2rem;'>
    🤖 Data Analyst Agent | Powered by LangChain & Google Generative AI<br>
    Made with ❤️ using Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
