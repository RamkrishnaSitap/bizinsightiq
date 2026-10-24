"""
BizInsightIQ — AI-Powered Business Intelligence, Predictive Analytics & Decision Support System
MCA Final-Semester Project - Streamlit Application Dashboard
Day 5: Decision Support & Actionable Business Insights Engine
"""

from pathlib import Path
from typing import Any
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
from src.segmentation import (
    aggregate_customer_features,
    perform_kmeans_clustering,
    evaluate_cluster_candidates,
    generate_cluster_profiles,
    create_elbow_silhouette_chart,
    create_pca_cluster_chart,
    create_cluster_profile_bar_chart,
)
from src.prediction import (
    prepare_prediction_data,
    train_and_evaluate_models,
    predict_sales,
    create_actual_vs_predicted_chart,
    create_residual_distribution_chart,
    create_model_comparison_bar_chart,
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
)
from src.insights import (
    BusinessInsight,
    generate_all_insights,
    filter_insights,
    get_insights_summary,
    create_insights_distribution_chart,
)


DEFAULT_SAMPLE_PATH = Path("data/sample_sales_data.csv")


def _format_inr_number(val: float, indian_grouping: bool = False) -> str:
    """Format numeric value into Indian Rupee string with proper sign and grouping."""
    is_neg = val < 0
    abs_val = abs(val)
    if not indian_grouping:
        num_str = f"{abs_val:,.2f}"
    else:
        s = f"{abs_val:.2f}"
        int_part, dec_part = s.split(".")
        if len(int_part) <= 3:
            num_str = f"{int_part}.{dec_part}"
        else:
            last3 = int_part[-3:]
            rest = int_part[:-3]
            chunks = []
            while len(rest) > 2:
                chunks.insert(0, rest[-2:])
                rest = rest[:-2]
            if rest:
                chunks.insert(0, rest)
            num_str = f"{','.join(chunks)},{last3}.{dec_part}"
    return f"-₹{num_str}" if is_neg else f"₹{num_str}"


def get_currency_config() -> dict[str, Any]:
    """Retrieve active currency settings from Streamlit session state."""
    mode = st.session_state.get("currency_mode", "Rupees (₹)")
    rate = float(st.session_state.get("exchange_rate", 83.0))
    source_curr = st.session_state.get("data_currency", "US Dollars ($)")
    indian_grouping = st.session_state.get("use_indian_grouping", False)

    is_source_inr = "Rupees" in source_curr or "INR" in source_curr or "₹" in source_curr

    if is_source_inr:
        inr_multiplier = 1.0
        usd_multiplier = 1.0 / rate if rate > 0 else 1.0
    else:
        inr_multiplier = rate
        usd_multiplier = 1.0

    if mode == "Rupees (₹)":
        primary_symbol = "₹"
        scale = inr_multiplier
    elif mode == "US Dollars ($)":
        primary_symbol = "$"
        scale = usd_multiplier
    else:  # "Both (₹ & $)"
        primary_symbol = "₹"
        scale = inr_multiplier

    return {
        "mode": mode,
        "rate": rate,
        "source_currency": source_curr,
        "is_source_inr": is_source_inr,
        "inr_multiplier": inr_multiplier,
        "usd_multiplier": usd_multiplier,
        "scale": scale,
        "primary_symbol": primary_symbol,
        "indian_grouping": indian_grouping,
    }


def format_currency(
    val: float,
    mode: str | None = None,
    rate: float | None = None,
    source_currency: str | None = None,
    indian_grouping: bool | None = None,
) -> str:
    """
    Format monetary amounts dynamically according to user-selected currency configuration.

    Modes:
    - 'Rupees (₹)' (Default): Converts amounts to Indian Rupees using active exchange rate.
    - 'Both (₹ & $)': Displays primary amount in Rupees with USD in parentheses.
    - 'US Dollars ($)': Displays amount in US Dollars.
    """
    if pd.isna(val):
        return "-"

    try:
        val_float = float(val)
    except (ValueError, TypeError):
        return str(val)

    if mode is None:
        mode = st.session_state.get("currency_mode", "Rupees (₹)")
    if rate is None:
        rate = float(st.session_state.get("exchange_rate", 83.0))
    if source_currency is None:
        source_currency = st.session_state.get("data_currency", "US Dollars ($)")
    if indian_grouping is None:
        indian_grouping = st.session_state.get("use_indian_grouping", False)

    is_source_inr = "Rupees" in source_currency or "INR" in source_currency or "₹" in source_currency
    if is_source_inr:
        inr_val = val_float
        usd_val = val_float / rate if rate > 0 else val_float
    else:
        usd_val = val_float
        inr_val = val_float * rate

    inr_str = _format_inr_number(inr_val, indian_grouping=indian_grouping)
    usd_str = f"-${abs(usd_val):,.2f}" if usd_val < 0 else f"${usd_val:,.2f}"

    if mode == "Rupees (₹)":
        return inr_str
    elif mode == "US Dollars ($)":
        return usd_str
    else:  # "Both (₹ & $)"
        return f"{inr_str} ({usd_str})"


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
    st.sidebar.header("💱 Currency Configuration")
    currency_mode = st.sidebar.radio(
        "Display Currency:",
        options=["Rupees (₹)", "Both (₹ & $)", "US Dollars ($)"],
        index=0,
        help="Select display currency. Converted values are computed dynamically from dataset amounts."
    )

    with st.sidebar.expander("⚙️ Currency & Conversion Settings", expanded=True):
        exchange_rate = st.number_input(
            "USD to INR Rate (₹ / $):",
            min_value=1.0,
            max_value=250.0,
            value=83.0,
            step=0.5,
            format="%.2f",
            help="Exchange rate used to convert US Dollar amounts into Indian Rupees (default: 1 USD = ₹83.00)."
        )
        source_curr = st.selectbox(
            "Raw Dataset Currency:",
            options=["US Dollars ($)", "Indian Rupees (₹)"],
            index=0,
            help="Currency of the raw input dataset. Bundled sample sales data is priced in US Dollars ($)."
        )
        use_indian_grouping = st.checkbox(
            "Indian Number Format (Lakhs/Crores)",
            value=False,
            help="Format amounts with Indian numbering grouping (e.g. ₹12,63,98,304.62 instead of ₹126,398,304.62)."
        )

    st.session_state["currency_mode"] = currency_mode
    st.session_state["exchange_rate"] = exchange_rate
    st.session_state["data_currency"] = source_curr
    st.session_state["use_indian_grouping"] = use_indian_grouping

    # Visual confirmation indicator
    if currency_mode == "Rupees (₹)":
        st.sidebar.success(f"Active: **Indian Rupees (₹)**  \n*(Converted at ₹{exchange_rate:.2f} / $1 USD)*")
    elif currency_mode == "Both (₹ & $)":
        st.sidebar.info(f"Active: **Both (₹ & $)**  \n*(₹ amounts converted at ₹{exchange_rate:.2f} / $)*")
    else:
        st.sidebar.warning("Active: **US Dollars ($)**  \n*(Native unconverted USD values)*")

    st.sidebar.markdown("---")
    st.sidebar.caption("**Status:** Day 6 Completed (MCA Academic Deliverables & System Verification)")

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
        st.metric("Total Revenue", format_currency(kpis['total_sales']))
    with kpi_col2:
        st.metric("Total Profit", format_currency(kpis['total_profit']))
    with kpi_col3:
        st.metric("Profit Margin", f"{kpis['profit_margin_pct']:.1f}%")
    with kpi_col4:
        st.metric("Units Sold", f"{kpis['total_units']:,}")
    with kpi_col5:
        st.metric("Unique Customers", f"{kpis['unique_customers']:,}")
    with kpi_col6:
        st.metric("Avg Order Value", format_currency(kpis['avg_order_value']))

    st.divider()

    # 3. Monthly Sales & Profit Trends Chart
    curr_cfg = get_currency_config()
    chart_scale = curr_cfg["scale"]
    chart_sym = curr_cfg["primary_symbol"]

    st.markdown("#### 1. Revenue & Profitability Trends Over Time")
    trend_df = compute_sales_profit_trends(filtered_df, freq="ME")
    trend_df_plot = trend_df.copy()
    if chart_scale != 1.0:
        trend_df_plot["Sales"] = trend_df_plot["Sales"] * chart_scale
        trend_df_plot["Profit"] = trend_df_plot["Profit"] * chart_scale
    trend_fig = create_trend_chart(trend_df_plot)
    trend_fig.update_yaxes(title_text=f"Sales ({chart_sym})", secondary_y=False)
    trend_fig.update_yaxes(title_text=f"Profit ({chart_sym})", secondary_y=True)
    if len(trend_fig.data) > 0:
        trend_fig.data[0].name = f"Monthly Sales ({chart_sym})"
    if len(trend_fig.data) > 1:
        trend_fig.data[1].name = f"Monthly Profit ({chart_sym})"
    st.plotly_chart(trend_fig, use_container_width=True)

    st.divider()

    # 4. Category & Regional Comparative Analysis (Side by Side)
    col_cat, col_reg = st.columns(2)

    with col_cat:
        st.markdown("#### 2. Performance by Product Category")
        cat_df = compute_category_performance(filtered_df)
        cat_df_plot = cat_df.copy()
        if chart_scale != 1.0:
            cat_df_plot["Sales"] = cat_df_plot["Sales"] * chart_scale
            cat_df_plot["Profit"] = cat_df_plot["Profit"] * chart_scale
        cat_fig = create_category_bar_chart(cat_df_plot)
        cat_fig.update_layout(yaxis_title=f"Amount ({chart_sym})")
        if len(cat_fig.data) > 0:
            cat_fig.data[0].name = f"Total Sales ({chart_sym})"
        if len(cat_fig.data) > 1:
            cat_fig.data[1].name = f"Total Profit ({chart_sym})"
        st.plotly_chart(cat_fig, use_container_width=True)
        with st.expander("View Category Breakdown Table"):
            fmt_cat_df = cat_df.copy()
            if "Sales" in fmt_cat_df.columns:
                fmt_cat_df["Sales"] = fmt_cat_df["Sales"].apply(format_currency)
            if "Profit" in fmt_cat_df.columns:
                fmt_cat_df["Profit"] = fmt_cat_df["Profit"].apply(format_currency)
            st.dataframe(fmt_cat_df, use_container_width=True)

    with col_reg:
        st.markdown("#### 3. Regional Sales Distribution")
        reg_df = compute_regional_performance(filtered_df)
        reg_df_plot = reg_df.copy()
        if chart_scale != 1.0:
            reg_df_plot["Sales"] = reg_df_plot["Sales"] * chart_scale
            reg_df_plot["Profit"] = reg_df_plot["Profit"] * chart_scale
        reg_fig = create_region_pie_chart(reg_df_plot)
        st.plotly_chart(reg_fig, use_container_width=True)
        with st.expander("View Regional Breakdown Table"):
            fmt_reg_df = reg_df.copy()
            if "Sales" in fmt_reg_df.columns:
                fmt_reg_df["Sales"] = fmt_reg_df["Sales"].apply(format_currency)
            if "Profit" in fmt_reg_df.columns:
                fmt_reg_df["Profit"] = fmt_reg_df["Profit"].apply(format_currency)
            st.dataframe(fmt_reg_df, use_container_width=True)

    st.divider()

    # 5. Pricing, Discount & Profitability Deep-Dive
    col_disc, col_corr = st.columns(2)

    with col_disc:
        st.markdown("#### 4. Discount Impact on Profitability")
        scatter_plot_df = filtered_df.copy()
        if chart_scale != 1.0:
            scatter_plot_df["Profit"] = scatter_plot_df["Profit"] * chart_scale
            scatter_plot_df["Sales"] = scatter_plot_df["Sales"] * chart_scale
        scatter_fig = create_discount_profit_scatter(scatter_plot_df)
        scatter_fig.update_layout(yaxis_title=f"Net Profit ({chart_sym})")
        st.plotly_chart(scatter_fig, use_container_width=True)

        st.caption("Discount Tier Aggregate Performance:")
        disc_table = compute_discount_profitability_analysis(filtered_df)
        fmt_disc = disc_table.copy()
        for col_name in ["Sales", "Profit", "Gross Sales", "Net Profit"]:
            if col_name in fmt_disc.columns:
                fmt_disc[col_name] = fmt_disc[col_name].apply(format_currency)
        st.dataframe(fmt_disc, use_container_width=True)

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


def render_segmentation_tab(df: pd.DataFrame) -> None:
    """Render Unsupervised Customer Segmentation dashboard powered by Scikit-learn K-Means."""
    st.markdown("### 🎯 Unsupervised Customer Segmentation (K-Means)")
    st.caption("Behavioral & RFM Customer Clustering implemented via decoupled algorithms in `src/segmentation.py`.")

    # Important Academic Disclaimers and Limitations
    st.info(
        """
        ℹ️ **Methodology & Data Notes:**
        - **Frequency Definition:** In the absence of an explicit `OrderID` attribute in the dataset schema, transaction-row count serves as a proxy for purchase frequency.
        - **Recency Calculation:** Computed deterministically relative to one day post-dataset maximum transaction date (`2024-12-31`).
        - **Synthetic Data Notice:** Clusters reflect synthetic behavioral distributions generated for academic research demonstration.
        - **Cluster Labels:** Cluster numbers (0, 1, 2...) are arbitrary categorical identifiers, not rankings or quality scores.
        """
    )

    # 1. Feature Aggregation
    try:
        customer_df = aggregate_customer_features(df)
    except Exception as e:
        st.error(f"Error computing customer features: {e}")
        return

    n_customers = len(customer_df)
    if n_customers < 4:
        st.warning(f"Insufficient customer observations ({n_customers}) to perform reliable clustering.")
        return

    # Top-level Customer Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Customers", f"{n_customers:,}")
    with m2:
        st.metric("Median Customer Spend", format_currency(customer_df['MonetaryValue'].median()))
    with m3:
        st.metric("Median Recency", f"{int(customer_df['Recency'].median())} days")
    with m4:
        st.metric("Median Discount", f"{customer_df['AvgDiscount'].median() * 100.0:.1f}%")

    with st.expander("📋 View Customer-Level Aggregated Feature Table (First 10 records)"):
        fmt_cust_df = customer_df.head(10).copy()
        if "MonetaryValue" in fmt_cust_df.columns:
            fmt_cust_df["MonetaryValue"] = fmt_cust_df["MonetaryValue"].apply(format_currency)
        st.dataframe(fmt_cust_df, use_container_width=True)

    st.divider()

    # 2. Diagnostic Evaluation: Elbow Method & Silhouette Curve
    with st.expander("📈 View Cluster Diagnostic Analysis (Elbow Method & Silhouette Curves)", expanded=False):
        st.caption("Evaluates cluster compact-ness (Inertia) and cluster separation (Silhouette Score) across candidate values of k.")
        eval_df = evaluate_cluster_candidates(customer_df, k_min=2, k_max=min(7, n_customers - 1))
        diag_fig = create_elbow_silhouette_chart(eval_df)
        st.plotly_chart(diag_fig, use_container_width=True)
        st.caption(
            "💡 **Interpretation:** The optimal number of clusters typically corresponds to the 'elbow' inflection point "
            "in Inertia accompanied by a healthy Silhouette Score (typically > 0.30)."
        )

    # 3. Model Controls & Execution
    st.markdown("#### 1. Configure Clustering Parameters")
    ctrl_col1, ctrl_col2 = st.columns([1, 2])

    with ctrl_col1:
        k_val = st.slider(
            "Select Number of Clusters (k):",
            min_value=2,
            max_value=min(7, n_customers - 1),
            value=4,
            step=1,
            help="Choose the number of customer behavioral segments to form."
        )

    # Execute clustering
    try:
        clustering_result = perform_kmeans_clustering(customer_df, n_clusters=k_val, random_state=42)
    except Exception as e:
        st.error(f"Clustering execution error: {e}")
        return

    sil_score = clustering_result["silhouette_score"]
    inertia = clustering_result["inertia"]
    var_ratio = clustering_result["pca_variance_ratio"]

    with ctrl_col2:
        st.markdown("**Model Evaluation Diagnostics:**")
        d1, d2, d3 = st.columns(3)
        with d1:
            st.metric("Within-Cluster Inertia", f"{inertia:,.1f}")
        with d2:
            sil_str = f"{sil_score:.3f}" if sil_score is not None else "N/A"
            st.metric("Silhouette Score", sil_str)
        with d3:
            st.metric("2D PCA Variance", f"{sum(var_ratio):.1f}%")

    st.divider()

    # 4. 2D Visual Cluster Projection (PCA)
    st.markdown("#### 2. Two-Dimensional Customer Cluster Projection (PCA)")
    st.caption(
        f"Multi-dimensional customer features (Recency, Frequency, Spend, Profit, Discount, Quantity) "
        f"projected onto top 2 Principal Components. Component 1 captures {var_ratio[0]}% variance; "
        f"Component 2 captures {var_ratio[1]}% variance."
    )
    pca_fig = create_pca_cluster_chart(clustering_result["pca_df"], var_ratio)
    st.plotly_chart(pca_fig, use_container_width=True)

    st.divider()

    # 5. Cluster Profiles & Segment Insights
    st.markdown("#### 3. Segment Characteristics & Behavioral Profiles")
    profile_df = generate_cluster_profiles(clustering_result["clustered_df"])

    fmt_profile = profile_df.copy()
    if "MeanSales" in fmt_profile.columns:
        fmt_profile["MeanSales"] = fmt_profile["MeanSales"].apply(format_currency)
    if "MeanProfit" in fmt_profile.columns:
        fmt_profile["MeanProfit"] = fmt_profile["MeanProfit"].apply(format_currency)
    st.dataframe(fmt_profile, use_container_width=True)

    # Profile Bar Chart
    curr_cfg = get_currency_config()
    chart_scale = curr_cfg["scale"]
    chart_sym = curr_cfg["primary_symbol"]

    profile_df_plot = profile_df.copy()
    if chart_scale != 1.0:
        profile_df_plot["MeanSales"] = profile_df_plot["MeanSales"] * chart_scale
        profile_df_plot["MeanProfit"] = profile_df_plot["MeanProfit"] * chart_scale
    prof_fig = create_cluster_profile_bar_chart(profile_df_plot)
    prof_fig.update_layout(yaxis_title=f"Amount ({chart_sym})")
    if len(prof_fig.data) > 0:
        prof_fig.data[0].name = f"Mean Sales ({chart_sym})"
    if len(prof_fig.data) > 1:
        prof_fig.data[1].name = f"Mean Profit ({chart_sym})"
    st.plotly_chart(prof_fig, use_container_width=True)

    # Detailed Segment Cards
    st.markdown("##### 📌 Segment Behavioral Breakdown:")
    card_cols = st.columns(k_val)
    for idx, row in profile_df.iterrows():
        c_num = int(row["Cluster"])
        with card_cols[c_num]:
            st.markdown(
                f"""
                <div style="background-color: rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 8px; border-left: 4px solid #3182ce;">
                    <h4 style="margin:0;">Cluster {c_num}</h4>
                    <p style="color:#d69e2e; font-weight:bold; margin-bottom:8px;">{row['DescriptivePersona']}</p>
                    <p style="margin:2px 0;"><b>Size:</b> {row['CustomerCount']} ({row['CustomerPct']}%)</p>
                    <p style="margin:2px 0;"><b>Avg Spend:</b> {format_currency(row['MeanSales'])}</p>
                    <p style="margin:2px 0;"><b>Avg Profit:</b> {format_currency(row['MeanProfit'])}</p>
                    <p style="margin:2px 0;"><b>Margin:</b> {row['ProfitMarginPct']:.1f}%</p>
                    <p style="margin:2px 0;"><b>Avg Recency:</b> {row['MeanRecencyDays']:.0f} days</p>
                    <p style="margin:2px 0;"><b>Avg Discount:</b> {row['MeanDiscountPct']:.1f}%</p>
                </div>
                """,
                unsafe_allow_html=True
            )


@st.cache_data(show_spinner=False)
def _cached_train_models(df: pd.DataFrame, split_strategy: str, test_size: float) -> dict:
    """Cache model training to ensure rapid UI responsiveness."""
    return train_and_evaluate_models(df, split_strategy=split_strategy, test_size=test_size, random_state=42)


def render_prediction_tab(df: pd.DataFrame) -> None:
    """
    Render supervised ML sales prediction, regression model evaluation,
    actual vs predicted diagnostics, and what-if scenario simulator.
    """
    st.markdown("### 🔮 Supervised Machine Learning: Sales Prediction & Regression Evaluation")
    st.markdown(
        """
        BizInsightIQ employs supervised regression algorithms to forecast transaction-level sales 
        using historical sales records, discount allowances, and seasonal calendar markers.
        """
    )

    # 1. Split Strategy and Model Execution
    st.markdown("#### 1. Configure Model Training & Evaluation")
    cfg_col1, cfg_col2 = st.columns([1, 1])

    with cfg_col1:
        split_choice = st.selectbox(
            "Evaluation Split Strategy:",
            options=["Chronological Split (Time-Ordered)", "Random Split (80/20 Shuffle)"],
            index=0,
            help="Chronological split evaluates strictly on unseen future dates, preventing temporal lookahead bias."
        )
        split_strategy = "chronological" if "Chronological" in split_choice else "random"

    with cfg_col2:
        test_pct = st.slider(
            "Test Set Ratio (%):",
            min_value=10,
            max_value=40,
            value=20,
            step=5,
            help="Percentage of transactions reserved strictly for out-of-sample model evaluation."
        ) / 100.0

    # Train and evaluate models
    try:
        with st.spinner("Training Linear Regression and Random Forest Regressors..."):
            results = _cached_train_models(df, split_strategy, test_pct)
    except Exception as e:
        st.error(f"Error during model training and evaluation: {e}")
        return

    meta = results["metadata"]
    comparison_df = results["comparison_df"]
    eval_lr = results["evaluations"]["linear_regression"]
    eval_rf = results["evaluations"]["random_forest"]

    # Split metadata callout
    st.info(
        f"📅 **Split Diagnostics ({meta['split_strategy'].capitalize()}):** "
        f"Training set: **{meta['train_size']:,}** records ({meta['train_period']}) | "
        f"Test set: **{meta['test_size']:,}** records ({meta['test_period']})"
    )

    # Metric Badges
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric(
            label="Random Forest R²",
            value=f"{eval_rf['r2']:.4f}",
            delta=f"{eval_rf['r2'] - eval_lr['r2']:+.4f} vs LR",
            help="Coefficient of Determination: Proportion of variance explained on unseen test set."
        )
    with m_col2:
        st.metric(
            label="Random Forest MAE",
            value=format_currency(eval_rf['mae']),
            delta=f"-{format_currency(eval_lr['mae'] - eval_rf['mae'])} vs LR",
            delta_color="inverse",
            help="Mean Absolute Error: Average deviation from actual sales in selected currency."
        )
    with m_col3:
        st.metric(
            label="Random Forest RMSE",
            value=format_currency(eval_rf['rmse']),
            delta=f"-{format_currency(eval_lr['rmse'] - eval_rf['rmse'])} vs LR",
            delta_color="inverse",
            help="Root Mean Squared Error: Penalizes larger prediction errors."
        )
    with m_col4:
        st.metric(
            label="Baseline (Linear Reg) R²",
            value=f"{eval_lr['r2']:.4f}",
            help="Standard OLS benchmark model performance on identical test split."
        )

    st.divider()

    # 2. Model Performance Comparison Table and Charts
    st.markdown("#### 2. Comparative Evaluation Metrics")
    c_tab1, c_tab2, c_tab3 = st.tabs([
        "📊 Model Comparison Bar Chart",
        "🎯 Actual vs. Predicted Parity",
        "📉 Residual Distribution",
    ])

    curr_cfg = get_currency_config()
    chart_scale = curr_cfg["scale"]
    chart_sym = curr_cfg["primary_symbol"]

    with c_tab1:
        fmt_comp = comparison_df.copy()
        curr_label = "₹" if curr_cfg["mode"] == "Rupees (₹)" else ("₹ / $" if "Both" in curr_cfg["mode"] else "$")
        if "MAE ($)" in fmt_comp.columns and "RMSE ($)" in fmt_comp.columns:
            fmt_comp[f"MAE ({curr_label})"] = fmt_comp["MAE ($)"].apply(format_currency)
            fmt_comp[f"RMSE ({curr_label})"] = fmt_comp["RMSE ($)"].apply(format_currency)
            fmt_comp = fmt_comp.drop(columns=["MAE ($)", "RMSE ($)"])
        st.dataframe(fmt_comp, use_container_width=True)

        comp_df_plot = comparison_df.copy()
        if chart_scale != 1.0:
            if "MAE ($)" in comp_df_plot.columns:
                comp_df_plot["MAE ($)"] = comp_df_plot["MAE ($)"] * chart_scale
            if "RMSE ($)" in comp_df_plot.columns:
                comp_df_plot["RMSE ($)"] = comp_df_plot["RMSE ($)"] * chart_scale
        comp_fig = create_model_comparison_bar_chart(comp_df_plot)
        comp_fig.update_layout(yaxis_title=f"Error Metric Value ({chart_sym})")
        if len(comp_fig.data) > 0:
            comp_fig.data[0].name = f"MAE ({chart_sym})"
        if len(comp_fig.data) > 1:
            comp_fig.data[1].name = f"RMSE ({chart_sym})"
        st.plotly_chart(comp_fig, use_container_width=True)

    with c_tab2:
        model_choice_viz = st.radio(
            "Select Model for Parity Diagnostic:",
            options=["Random Forest Regressor", "Linear Regression (Baseline)"],
            horizontal=True,
            key="parity_model_choice"
        )
        selected_eval = eval_rf if "Random Forest" in model_choice_viz else eval_lr
        parity_y_true = selected_eval["y_true"] * chart_scale if chart_scale != 1.0 else selected_eval["y_true"]
        parity_y_pred = selected_eval["y_pred"] * chart_scale if chart_scale != 1.0 else selected_eval["y_pred"]
        parity_fig = create_actual_vs_predicted_chart(
            parity_y_true,
            parity_y_pred,
            model_name=model_choice_viz,
        )
        parity_fig.update_layout(
            xaxis_title=f"Actual Sales ({chart_sym})",
            yaxis_title=f"Predicted Sales ({chart_sym})",
        )
        st.plotly_chart(parity_fig, use_container_width=True)

    with c_tab3:
        res_model_choice = st.radio(
            "Select Model for Residual Diagnostic:",
            options=["Random Forest Regressor", "Linear Regression (Baseline)"],
            horizontal=True,
            key="res_model_choice"
        )
        selected_res = eval_rf if "Random Forest" in res_model_choice else eval_lr
        res_values = selected_res["residuals"] * chart_scale if chart_scale != 1.0 else selected_res["residuals"]
        res_fig = create_residual_distribution_chart(
            res_values,
            model_name=res_model_choice,
        )
        res_fig.update_layout(
            xaxis_title=f"Residual Error ({chart_sym})",
        )
        st.plotly_chart(res_fig, use_container_width=True)

    st.divider()

    # 3. Interactive What-If Scenario Simulator
    st.markdown("#### 3. 🎯 Interactive 'What-If' Scenario Simulator")
    st.caption("Forecast gross transaction revenue for hypothetical business quotes and order scenarios.")

    categories = sorted(df["Category"].dropna().unique().tolist())
    regions = sorted(df["Region"].dropna().unique().tolist())

    with st.form("what_if_prediction_form"):
        sim_col1, sim_col2, sim_col3 = st.columns(3)

        with sim_col1:
            cat_input = st.selectbox("Product Category:", options=categories, index=0)
            region_input = st.selectbox("Target Region:", options=regions, index=0)
            model_engine = st.selectbox(
                "Prediction Model:",
                options=["Random Forest Regressor (Recommended)", "Linear Regression (Baseline)"],
                index=0
            )

        with sim_col2:
            qty_input = st.number_input("Order Quantity:", min_value=1, max_value=100, value=5, step=1)
            discount_input = st.slider("Promotional Discount (%):", min_value=0, max_value=70, value=15, step=5) / 100.0

        with sim_col3:
            month_names = [
                "1 - January", "2 - February", "3 - March", "4 - April",
                "5 - May", "6 - June", "7 - July", "8 - August",
                "9 - September", "10 - October", "11 - November", "12 - December"
            ]
            month_choice = st.selectbox("Order Month:", options=month_names, index=5)
            month_input = int(month_choice.split(" - ")[0])
            quarter_input = (month_input - 1) // 3 + 1

            day_names = ["0 - Monday", "1 - Tuesday", "2 - Wednesday", "3 - Thursday", "4 - Friday", "5 - Saturday", "6 - Sunday"]
            day_choice = st.selectbox("Day of Week:", options=day_names, index=2)
            day_input = int(day_choice.split(" - ")[0])

        submit_scenario = st.form_submit_button("🔮 Calculate Predicted Sales")

    # Generate prediction
    selected_pipeline = results["models"]["random_forest"] if "Random Forest" in model_engine else results["models"]["linear_regression"]
    scenario_input = {
        "Quantity": qty_input,
        "Discount": discount_input,
        "Category": cat_input,
        "Region": region_input,
        "Month": month_input,
        "Quarter": quarter_input,
        "DayOfWeek": day_input,
    }

    pred_val = predict_sales(selected_pipeline, scenario_input)
    implied_unit_price = pred_val / qty_input if qty_input > 0 else 0.0

    st.markdown("##### 📌 Forecast Result:")
    res_card1, res_card2, res_card3 = st.columns(3)
    with res_card1:
        st.metric(
            label=f"Predicted Gross Sales ({model_engine.split(' ')[0]} {model_engine.split(' ')[1]})",
            value=format_currency(pred_val)
        )
    with res_card2:
        st.metric(
            label="Implied Unit Realization",
            value=f"{format_currency(implied_unit_price)} / unit"
        )
    with res_card3:
        st.metric(
            label="Discount Allowance Applied",
            value=f"{discount_input * 100:.0f}%"
        )

    st.divider()

    # 4. Target Leakage Prevention & Academic Rigor
    st.markdown("#### 4. 🛡️ Academic Methodology: Target Leakage Prevention")
    st.info(
        """
        **Why is `Profit` excluded from prediction features?**
        
        In retail financial accounting, `Profit` is derived directly from `Sales` 
        ($\\text{Profit} = \\text{Sales} \\times (1 - \\text{Discount}) - \\text{COGS}$). Including `Profit` in 
        training data constitutes severe **Target Leakage**, giving the model future knowledge of financial outcomes 
        and yielding artificial $R^2 > 0.95$. 
        
        BizInsightIQ strictly enforces pre-transaction feature boundaries (`Category`, `Region`, `Quantity`, 
        `Discount`, and calendar seasonality), ensuring the system functions reliably as an operational 
        decision-support tool for sales quotes before orders are fulfilled.
        """
    )


def render_insights_tab(df: pd.DataFrame) -> None:
    """
    Render decision support engine with prioritized, evidence-based business insights.
    """
    st.markdown("### 💡 Business Insights & Actionable Decision Support")
    st.caption(
        "Automated rule-based heuristic decision engine synthesizing descriptive KPIs, "
        "category margins, discount brackets, customer clusters, and predictive regression models "
        "into prioritized, evidence-based recommendations."
    )

    try:
        with st.spinner("Synthesizing multi-pillar business insights..."):
            insights = generate_all_insights(df)
    except Exception as e:
        st.error(f"Error generating business insights: {e}")
        return

    if not insights:
        st.info("No actionable rule-based insights were identified for the current dataset parameters.")
        return

    summary = get_insights_summary(insights)

    # 1. Executive Metric Summary Cards
    col_tot, col_crit, col_warn, col_info = st.columns(4)
    with col_tot:
        st.metric(label="Total Insights Generated", value=summary["total"])
    with col_crit:
        st.metric(label="Critical Priority", value=summary["by_severity"]["critical"])
    with col_warn:
        st.metric(label="Warning / Action Needed", value=summary["by_severity"]["warning"])
    with col_info:
        st.metric(label="Informational / Best Practice", value=summary["by_severity"]["info"])

    st.divider()

    # 2. Interactive Filtering Controls
    st.markdown("#### 1. Filter Strategic Recommendations")
    f_col1, f_col2 = st.columns([1, 1])

    with f_col1:
        cat_options = ["All"] + list(summary["by_category"].keys())
        selected_cat = st.selectbox("Filter by Analytical Pillar:", options=cat_options, index=0)

    with f_col2:
        sev_options = ["All", "Critical", "Warning", "Info"]
        selected_sev_label = st.selectbox("Filter by Severity Level:", options=sev_options, index=0)
        selected_sev = selected_sev_label.lower() if selected_sev_label != "All" else "All"

    filtered_insights = filter_insights(insights, category=selected_cat, severity=selected_sev)

    # 3. Visual Breakdown Chart
    with st.expander("📊 View Insights Distribution Chart", expanded=False):
        chart_fig = create_insights_distribution_chart(insights)
        st.plotly_chart(chart_fig, use_container_width=True)

    st.markdown(f"**Showing {len(filtered_insights)} of {len(insights)} Recommendations:**")

    # 4. Render Prioritized Recommendation Cards
    severity_styles = {
        "critical": {
            "border": "#e53e3e",
            "bg": "rgba(229, 62, 62, 0.08)",
            "badge": "🔴 CRITICAL",
            "color": "#e53e3e",
        },
        "warning": {
            "border": "#dd6b20",
            "bg": "rgba(221, 107, 32, 0.08)",
            "badge": "🟠 WARNING",
            "color": "#dd6b20",
        },
        "info": {
            "border": "#3182ce",
            "bg": "rgba(49, 130, 206, 0.08)",
            "badge": "🔵 INFORMATIONAL",
            "color": "#3182ce",
        },
    }

    for ins in filtered_insights:
        style = severity_styles.get(ins.severity, severity_styles["info"])

        # Format evidence key-values
        evidence_lines = []
        for k, v in ins.evidence.items():
            k_formatted = k.replace("_", " ").title()
            is_monetary = any(term in k.lower() for term in ["sales", "profit", "spend", "loss", "revenue", "cogs", "price"]) and not any(term in k.lower() for term in ["pct", "margin", "ratio", "count", "days"])
            if isinstance(v, (int, float)) and is_monetary:
                v_formatted = format_currency(v)
            elif isinstance(v, float):
                v_formatted = f"{v:,.2f}"
            elif isinstance(v, int):
                v_formatted = f"{v:,}"
            elif isinstance(v, list):
                v_formatted = ", ".join(str(item) for item in v)
            else:
                v_formatted = str(v)
            evidence_lines.append(f"• **{k_formatted}:** {v_formatted}")
        evidence_text = "<br>".join(evidence_lines)

        st.markdown(
            f"""
            <div style="background-color: {style['bg']}; border-left: 5px solid {style['border']}; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: bold; font-size: 1.1em; color: {style['color']};">
                        {style['badge']} | {ins.title}
                    </span>
                    <span style="font-size: 0.85em; opacity: 0.8; font-family: monospace;">
                        [{ins.insight_id}] • {ins.category}
                    </span>
                </div>
                <div style="margin-bottom: 10px; font-size: 0.95em; line-height: 1.4;">
                    <b>📊 Empirical Evidence:</b><br>
                    {evidence_text}
                </div>
                <div style="margin-bottom: 8px; font-size: 0.95em;">
                    <b>🎯 Strategic Recommendation:</b> {ins.recommendation}
                </div>
                <div style="font-size: 0.85em; opacity: 0.75; font-style: italic;">
                    <b>⚠️ Limitations:</b> {ins.limitations}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # 5. Synthetic Data & Operational Caveat Notice
    st.info(
        "🛡️ **Academic & Operational Methodology Notice:**  \n"
        "All recommendations are generated by deterministic heuristic decision rules evaluated on the bundled synthetic retail dataset. "
        "Observed correlations (such as margin compression in high-discount brackets) do not establish causal necessity. "
        "Business stakeholders should conduct controlled A/B pricing experiments and consult cost accountants before enacting policy adjustments."
    )


def render_roadmap_tab() -> None:
    """Render architecture overview and multi-day project delivery roadmap."""
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
        st.success("**Day 3 (Completed)**\n- Customer Segmentation (`src/segmentation.py`)\n- RFM / Behavioral Feature Scaling\n- K-Means Clustering & PCA Projection\n- 48 Total Unit Tests Passed")
        st.success("**Day 4 (Completed)**\n- Sales Forecasting Regression (`src/prediction.py`)\n- Feature Engineering & Chronological Split\n- Linear Regression vs Random Forest\n- Metrics: $R^2$, RMSE, MAE (70 Tests Passed)")

    with col3:
        st.success("**Day 5 (Completed)**\n- Decision Support Engine (`src/insights.py`)\n- Explainable Multi-Pillar Rules & Evidence\n- Interactive Streamlit Dashboard Tab\n- 91 Total Unit Tests Passed")
        st.info("**Day 6 (Academic Deliverables - Next Phase)**\n- Final End-to-End System Verification\n- High-Res Architecture Diagrams\n- Performance Tables for Project Report\n- Viva Presentation Preparation")

    st.divider()
    st.markdown("#### Architectural Decoupling Rules")
    st.code(
        """
        BizInsightIQ/
        ├── app.py                <-- Presentation (Calls src/ directly for offline demo)
        ├── src/                  <-- Pure Domain Logic (UI-agnostic, DB-agnostic)
        │   ├── data_loader.py    <-- File & buffer ingestion
        │   ├── validator.py      <-- Schema and business constraint validation
        │   ├── eda.py            <-- Analytical KPIs, trends, and charts
        │   ├── segmentation.py   <-- K-Means clustering, PCA projection, & profiling
        │   ├── prediction.py     <-- Supervised regression, evaluation & what-if
        │   └── insights.py       <-- Decision support & actionable recommendations
        ├── tests/                <-- Automated Pytest Suite (91 passed tests)
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
        tab_validate, tab_eda, tab_segmentation, tab_prediction, tab_insights, tab_roadmap = st.tabs([
            "📋 Data Ingestion & Validation",
            "📊 Exploratory Data Analysis (EDA)",
            "🎯 Customer Segmentation (K-Means)",
            "🔮 Sales Prediction (Regression)",
            "💡 Business Insights & Recommendations",
            "🚀 System Architecture & Roadmap",
        ])

        with tab_validate:
            is_valid = render_validation_tab(df, source_name)

        with tab_eda:
            if is_valid:
                render_eda_tab(df)
            else:
                st.error("Cannot perform Exploratory Data Analysis on an invalid dataset. Please resolve validation errors in the first tab.")

        with tab_segmentation:
            if is_valid:
                render_segmentation_tab(df)
            else:
                st.error("Cannot perform Customer Segmentation on an invalid dataset. Please resolve validation errors in the first tab.")

        with tab_prediction:
            if is_valid:
                render_prediction_tab(df)
            else:
                st.error("Cannot perform Sales Prediction on an invalid dataset. Please resolve validation errors in the first tab.")

        with tab_insights:
            if is_valid:
                render_insights_tab(df)
            else:
                st.error("Cannot generate Business Insights on an invalid dataset. Please resolve validation errors in the first tab.")

        with tab_roadmap:
            render_roadmap_tab()

    else:
        st.warning("No dataset currently loaded. Select the bundled dataset from the sidebar or upload a CSV to begin.")


if __name__ == "__main__":
    main()
