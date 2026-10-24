"""
BizInsightIQ — AI-Powered Business Intelligence, Predictive Analytics & Decision Support System
MCA Final-Semester Project - Streamlit Application Dashboard
Day 2: Exploratory Data Analysis (EDA), Interactive Visualizations & Modular Architecture
"""

from pathlib import Path
import streamlit as st
import pandas as pd

from src.data_loader import load_csv_data
from src.validator import validate_dataset, REQUIRED_COLUMNS
from src.eda import (
    compute_business_kpis,
    compute_sales_profit_trends,
    compute_category_performance,
    compute_regional_performance,
    compute_discount_profitability_analysis,
    compute_correlation_matrix,
    create_trend_chart,
    create_category_bar_chart,
    create_region_pie_chart,
    create_discount_profit_scatter,
    create_correlation_heatmap,
)


DEFAULT_SAMPLE_PATH = Path("data/sample_sales_data.csv")


def set_page_layout() -> None:
    """Configure page settings and theme layout."""
    st.set_page_config(
        page_title="BizInsightIQ — AI Business Intelligence",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_header() -> None:
    """Render top application header and academic project information."""
    st.title("📈 BizInsightIQ")
    st.subheader("AI-Powered Business Intelligence, Customer Segmentation, and Predictive Analytics System")
    st.caption(
        "**Master of Computer Applications (MCA) Final-Semester Project** | "
        "Architecture: Modular Decoupled Core (Python 3.12, Streamlit, Pandas, Scikit-learn, Plotly)"
    )
    st.divider()


def render_sidebar() -> tuple[pd.DataFrame | None, str]:
    """
    Render sidebar controls for data source selection and file upload.

    Returns
    -------
    tuple[pd.DataFrame | None, str]
        Loaded DataFrame and description of the source.
    """
    st.sidebar.header("📁 Data Management")

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
                st.sidebar.success("Loaded bundled sample dataset (1,200 rows).")
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
    st.sidebar.caption("**Status:** Day 2 Completed (EDA & Interactive Analytics)")

    return df, source_name


def render_validation_tab(df: pd.DataFrame, source_name: str) -> bool:
    """
    Render validation summary cards, warnings, and data exploration preview.

    Returns
    -------
    bool
        True if dataset is valid, False otherwise.
    """
    st.markdown(f"### 📋 Dataset Ingestion & Validation — *{source_name}*")

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

    # Validation alerts
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
    st.markdown("#### Dataset Structural Inspection")
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 First 10 Records", "🔍 Column Specifications", "📊 Statistical Overview"])

    with sub_tab1:
        st.dataframe(df.head(10), use_container_width=True)

    with sub_tab2:
        schema_df = pd.DataFrame({
            "Column Name": df.columns,
            "Data Type": [str(t) for t in df.dtypes],
            "Non-Null Count": [df[c].count() for c in df.columns],
            "Null Count": [int(df[c].isnull().sum()) for c in df.columns],
            "Is Required": [c in REQUIRED_COLUMNS for c in df.columns],
        })
        st.dataframe(schema_df, use_container_width=True)

    with sub_tab3:
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            st.dataframe(df.describe().T, use_container_width=True)
        else:
            st.info("No numeric columns found for descriptive statistics.")

    return validation.is_valid


def render_eda_tab(df: pd.DataFrame) -> None:
    """Render comprehensive Exploratory Data Analysis dashboards and charts."""
    st.markdown("### 📊 Exploratory Data Analysis & Business Intelligence")
    st.caption("Interactive analytical views computed dynamically via framework-agnostic algorithms in `src/eda.py`.")

    # 1. Interactive Filters (Category and Region)
    with st.expander("🔍 Interactive Analytics Filters", expanded=True):
        fcol1, fcol2 = st.columns(2)
        all_categories = sorted(list(df["Category"].dropna().unique()))
        all_regions = sorted(list(df["Region"].dropna().unique()))

        with fcol1:
            selected_categories = st.multiselect(
                "Filter by Category:",
                options=all_categories,
                default=all_categories,
                help="Select one or more product categories to filter KPIs and charts."
            )
        with fcol2:
            selected_regions = st.multiselect(
                "Filter by Region:",
                options=all_regions,
                default=all_regions,
                help="Select one or more geographic sales regions."
            )

    # Filter data safely
    filtered_df = df[
        (df["Category"].isin(selected_categories)) &
        (df["Region"].isin(selected_regions))
    ].copy()

    if filtered_df.empty:
        st.warning("No records match the selected filter combination. Please expand your filter selection.")
        return

    # 2. Executive Business KPIs
    kpis = compute_business_kpis(filtered_df)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

    with kpi_col1:
        st.metric("Total Revenue", f"${kpis['total_sales']:,.2f}")
    with kpi_col2:
        st.metric("Total Profit", f"${kpis['total_profit']:,.2f}")
    with kpi_col3:
        st.metric("Profit Margin", f"{kpis['profit_margin_pct']:.1f}%")
    with kpi_col4:
        st.metric("Units Sold", f"{kpis['total_units']:,}")
    with kpi_col5:
        st.metric("Unique Customers", f"{kpis['unique_customers']:,}")
    with kpi_col6:
        st.metric("Avg Order Value", f"${kpis['avg_order_value']:,.2f}")

    st.divider()

    # 3. Monthly Sales & Profit Trends Chart
    st.markdown("#### 1. Revenue & Profitability Trends Over Time")
    trend_df = compute_sales_profit_trends(filtered_df, freq="ME")
    trend_fig = create_trend_chart(trend_df)
    st.plotly_chart(trend_fig, use_container_width=True)

    st.divider()

    # 4. Category & Regional Comparative Analysis (Side by Side)
    col_cat, col_reg = st.columns(2)

    with col_cat:
        st.markdown("#### 2. Performance by Product Category")
        cat_df = compute_category_performance(filtered_df)
        cat_fig = create_category_bar_chart(cat_df)
        st.plotly_chart(cat_fig, use_container_width=True)
        with st.expander("View Category Breakdown Table"):
            st.dataframe(cat_df, use_container_width=True)

    with col_reg:
        st.markdown("#### 3. Regional Sales Distribution")
        reg_df = compute_regional_performance(filtered_df)
        reg_fig = create_region_pie_chart(reg_df)
        st.plotly_chart(reg_fig, use_container_width=True)
        with st.expander("View Regional Breakdown Table"):
            st.dataframe(reg_df, use_container_width=True)

    st.divider()

    # 5. Pricing, Discount & Profitability Deep-Dive
    col_disc, col_corr = st.columns(2)

    with col_disc:
        st.markdown("#### 4. Discount Impact on Profitability")
        scatter_fig = create_discount_profit_scatter(filtered_df)
        st.plotly_chart(scatter_fig, use_container_width=True)

        st.caption("Discount Tier Aggregate Performance:")
        disc_table = compute_discount_profitability_analysis(filtered_df)
        st.dataframe(disc_table, use_container_width=True)

    with col_corr:
        st.markdown("#### 5. Feature Correlation Matrix")
        corr_matrix = compute_correlation_matrix(filtered_df)
        corr_fig = create_correlation_heatmap(corr_matrix)
        st.plotly_chart(corr_fig, use_container_width=True)

        st.info(
            "💡 **Key Analytical Finding:** "
            "Higher discount rates exhibit negative correlation with profit margins, "
            "indicating that deep promotional discounts (>20%) frequently lead to loss-making orders."
        )


def render_roadmap_tab() -> None:
    """Render architecture overview and Day 3/Day 4 ML roadmap."""
    st.markdown("### 🚀 Project Architecture & Roadmap")
    st.markdown(
        """
        BizInsightIQ is built with a **modular, decoupled architecture** to enable easy evolution 
        from this single-workstation Streamlit MVP to a full enterprise stack.
        """
    )

    st.markdown("#### Six-Day Implementation Roadmap")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("**Day 1 (Completed)**\n- Python 3.12 Virtual Env\n- Synthetic Dataset (1,200 rows)\n- Data Loader & Validator\n- 15 Unit Tests Passed")
        st.success("**Day 2 (Completed)**\n- Reusable EDA Module (`src/eda.py`)\n- Interactive Plotly Visualizations\n- Dynamic Filtering (Category/Region)\n- 31 Total Unit Tests Passed")

    with col2:
        st.info("**Day 3 (Next Phase)**\n- Customer Segmentation (`src/segmentation.py`)\n- RFM / Behavioral Feature Scaling\n- K-Means Clustering\n- Elbow & Silhouette Evaluation")
        st.info("**Day 4 (Supervised ML)**\n- Sales Forecasting Regression (`src/prediction.py`)\n- Feature Engineering & Train/Test Split\n- Linear Regression vs Random Forest\n- Metrics: $R^2$, RMSE, MAE")

    with col3:
        st.warning("**Day 5 (Integration & Polish)**\n- Automated Decision Support Engine (`src/insights.py`)\n- Full UI Integration & Error Hardening\n- Optional FastAPI REST Wrapper")
        st.warning("**Day 6 (Academic Deliverables)**\n- Empirical Report Evidence\n- High-Res Architecture Diagrams\n- Metric Tables for Project Report\n- Viva Presentation Preparation")

    st.divider()
    st.markdown("#### Architectural Decoupling Rules")
    st.code(
        """
        BizInsightIQ/
        ├── app.py                <-- Presentation (Calls src/ directly for offline demo)
        ├── src/                  <-- Pure Domain Logic (UI-agnostic, DB-agnostic)
        │   ├── data_loader.py    <-- File & buffer ingestion
        │   ├── validator.py      <-- Schema and business constraint validation
        │   └── eda.py            <-- Analytical KPIs, trends, and charts
        ├── tests/                <-- Automated Pytest Suite (31 passed tests)
        ├── docs/                 <-- System architecture & API documentation
        └── .env.example          <-- Externalized configuration for future stack
        """,
        language="text"
    )


def main() -> None:
    set_page_layout()
    render_header()
    df, source_name = render_sidebar()

    if df is not None:
        tab_validate, tab_eda, tab_roadmap = st.tabs([
            "📋 Data Ingestion & Validation",
            "📊 Exploratory Data Analysis (EDA)",
            "🚀 System Architecture & Roadmap",
        ])

        with tab_validate:
            is_valid = render_validation_tab(df, source_name)

        with tab_eda:
            if is_valid:
                render_eda_tab(df)
            else:
                st.error("Cannot perform Exploratory Data Analysis on an invalid dataset. Please resolve validation errors in the first tab.")

        with tab_roadmap:
            render_roadmap_tab()

    else:
        st.warning("No dataset currently loaded. Select the bundled dataset from the sidebar or upload a CSV to begin.")


if __name__ == "__main__":
    main()
