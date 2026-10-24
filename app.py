"""
AI-Powered Business Intelligence, Predictive Analytics and Decision Support System
MCA Final-Semester Project - Streamlit Application Dashboard
Day 1: Baseline Architecture, Data Ingestion, and Schema Validation
"""

from pathlib import Path
import streamlit as st
import pandas as pd

from src.data_loader import load_csv_data
from src.validator import validate_dataset, REQUIRED_COLUMNS


DEFAULT_SAMPLE_PATH = Path("data/sample_sales_data.csv")


def set_page_layout() -> None:
    """Configure page settings and theme layout."""
    st.set_page_config(
        page_title="AI Business Intelligence & Decision Support",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_header() -> None:
    """Render top application header and project information."""
    st.title("📈 AI-Powered Business Intelligence & Decision Support System")
    st.markdown(
        """
        **Academic Project:** Master of Computer Applications (MCA) Final-Semester Project  
        **Core Focus:** Data Validation, Exploratory Data Analysis, K-Means Customer Segmentation, and Predictive Analytics.
        """
    )
    st.divider()


def render_sidebar() -> tuple[pd.DataFrame | None, str]:
    """
    Render sidebar controls for data source selection and file upload.

    Returns
    -------
    tuple[pd.DataFrame | None, str]
        Loaded DataFrame (or None if load failed) and description of the source.
    """
    st.sidebar.header("📁 Data Source")

    data_source = st.sidebar.radio(
        "Select Dataset Origin:",
        options=["Bundled Sample Dataset", "Upload Custom CSV"],
        index=0,
        help="Choose between the verified synthetic retail dataset or upload your own CSV."
    )

    df: pd.DataFrame | None = None
    source_name = ""

    if data_source == "Bundled Sample Dataset":
        source_name = f"Bundled Dataset ({DEFAULT_SAMPLE_PATH.name})"
        if not DEFAULT_SAMPLE_PATH.exists():
            st.sidebar.error(f"Sample data file not found at {DEFAULT_SAMPLE_PATH}")
        else:
            try:
                df = load_csv_data(DEFAULT_SAMPLE_PATH)
                st.sidebar.success("Loaded bundled sample dataset.")
            except Exception as e:
                st.sidebar.error(f"Error loading bundled data: {e}")

    else:
        uploaded_file = st.sidebar.file_uploader(
            "Upload Business Sales CSV",
            type=["csv"],
            help=f"File must include columns: {', '.join(REQUIRED_COLUMNS)}"
        )
        if uploaded_file is not None:
            source_name = f"Uploaded File: {uploaded_file.name}"
            try:
                df = load_csv_data(uploaded_file)
                st.sidebar.success(f"Successfully loaded '{uploaded_file.name}'.")
            except Exception as e:
                st.sidebar.error(f"Error reading file: {e}")
        else:
            st.sidebar.info("Please upload a CSV file to begin validation.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📌 Expected Schema")
    st.sidebar.caption("Required columns:")
    for col in REQUIRED_COLUMNS:
        st.sidebar.markdown(f"- `{col}`")

    st.sidebar.markdown("---")
    st.sidebar.caption("**Status:** Day 1 Implementation (MVP Foundation)")

    return df, source_name


def render_validation_dashboard(df: pd.DataFrame, source_name: str) -> None:
    """Render validation summary cards and data preview."""
    st.subheader(f"1. Dataset Ingestion & Validation — {source_name}")

    # Perform validation
    validation = validate_dataset(df)

    # Top-level Metric Badges
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Rows", value=f"{validation.total_rows:,}")
    with col2:
        st.metric(label="Total Columns", value=validation.total_columns)
    with col3:
        status_label = "✅ Valid Schema" if validation.is_valid else "❌ Validation Failed"
        st.metric(label="Validation Status", value=status_label)
    with col4:
        st.metric(label="Duplicate Rows", value=validation.duplicate_rows_count)

    # Validation messages
    if validation.is_valid:
        st.success("✅ **Dataset passed all schema and critical business integrity checks!** Ready for EDA and ML modeling.")
    else:
        st.error("❌ **Critical validation errors encountered:**")
        for err in validation.errors:
            st.error(f"• {err}")

    if validation.warnings:
        with st.expander("⚠️ Data Quality Warnings & Notices", expanded=False):
            for warn in validation.warnings:
                st.warning(f"• {warn}")

    st.divider()

    # Data Preview & Summary tabs
    st.subheader("2. Dataset Exploration Preview")
    tab_preview, tab_schema, tab_stats = st.tabs(["📋 Data Preview", "🔍 Column Types", "📊 Statistical Summary"])

    with tab_preview:
        st.caption("First 10 records of the loaded dataset:")
        st.dataframe(df.head(10), use_container_width=True)

    with tab_schema:
        schema_df = pd.DataFrame({
            "Column Name": df.columns,
            "Data Type": [str(t) for t in df.dtypes],
            "Non-Null Count": [df[c].count() for c in df.columns],
            "Null Count": [int(df[c].isnull().sum()) for c in df.columns],
            "Is Required": [c in REQUIRED_COLUMNS for c in df.columns],
        })
        st.dataframe(schema_df, use_container_width=True)

    with tab_stats:
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            st.dataframe(df.describe().T, use_container_width=True)
        else:
            st.info("No numeric columns found for descriptive statistics.")

    # Next phases roadmap card
    st.divider()
    st.info(
        """
        🚀 **Upcoming Phase (Day 2):** Exploratory Data Analysis (EDA) module with interactive Plotly visualizers 
        (Sales Trends, Category Performance, Regional Distributions, Profitability Analysis).
        """
    )


def main() -> None:
    set_page_layout()
    render_header()
    df, source_name = render_sidebar()

    if df is not None:
        render_validation_dashboard(df, source_name)
    else:
        st.warning("No dataset currently loaded. Select the bundled dataset from the sidebar or upload a CSV.")


if __name__ == "__main__":
    main()
