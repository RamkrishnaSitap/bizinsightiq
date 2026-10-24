"""
Exploratory Data Analysis (EDA) Module for BizInsightIQ.

Provides framework-agnostic statistical computation functions and interactive
Plotly visualization builders for business performance metrics.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


REQUIRED_EDA_COLUMNS = [
    "CustomerID",
    "OrderDate",
    "Category",
    "Region",
    "Quantity",
    "Discount",
    "Sales",
    "Profit",
]


def _validate_columns(df: pd.DataFrame, required: list[str]) -> None:
    """Validate that required columns exist in the DataFrame."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"DataFrame is missing required columns for EDA: {', '.join(missing)}")


# ---------------------------------------------------------------------------
# Core Analytical Computation Functions (Pure Logic, Framework Independent)
# ---------------------------------------------------------------------------

def compute_business_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute executive summary KPIs from sales transaction data.

    Parameters
    ----------
    df : pd.DataFrame
        Sales dataset.

    Returns
    -------
    Dict[str, Any]
        Dictionary of business KPIs.
    """
    _validate_columns(df, ["Sales", "Profit", "Quantity", "CustomerID", "Discount"])

    if df.empty:
        return {
            "total_sales": 0.0,
            "total_profit": 0.0,
            "total_units": 0,
            "unique_customers": 0,
            "total_orders": 0,
            "profit_margin_pct": 0.0,
            "avg_order_value": 0.0,
            "avg_discount_pct": 0.0,
        }

    total_sales = float(df["Sales"].sum())
    total_profit = float(df["Profit"].sum())
    total_units = int(df["Quantity"].sum())
    unique_customers = int(df["CustomerID"].nunique())
    total_orders = len(df)

    profit_margin_pct = (total_profit / total_sales * 100.0) if total_sales > 0 else 0.0
    avg_order_value = (total_sales / total_orders) if total_orders > 0 else 0.0
    avg_discount_pct = float(df["Discount"].mean() * 100.0)

    return {
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "total_units": total_units,
        "unique_customers": unique_customers,
        "total_orders": total_orders,
        "profit_margin_pct": round(profit_margin_pct, 2),
        "avg_order_value": round(avg_order_value, 2),
        "avg_discount_pct": round(avg_discount_pct, 2),
    }


def compute_sales_profit_trends(df: pd.DataFrame, freq: str = "ME") -> pd.DataFrame:
    """
    Aggregate sales and profit over time by chronological period.

    Parameters
    ----------
    df : pd.DataFrame
        Sales dataset containing OrderDate, Sales, Profit, and Quantity.
    freq : str, default "ME"
        Pandas frequency string ('ME' for Month End, 'W' for Weekly).

    Returns
    -------
    pd.DataFrame
        Chronologically sorted trends with Period, Sales, Profit, Quantity,
        OrderCount, and ProfitMarginPct.
    """
    _validate_columns(df, ["OrderDate", "Sales", "Profit", "Quantity"])

    if df.empty:
        return pd.DataFrame(columns=["Period", "Sales", "Profit", "Quantity", "OrderCount", "ProfitMarginPct"])

    data = df.copy()
    data["ParsedDate"] = pd.to_datetime(data["OrderDate"], errors="coerce", format="mixed")
    data = data.dropna(subset=["ParsedDate"])

    if data.empty:
        return pd.DataFrame(columns=["Period", "Sales", "Profit", "Quantity", "OrderCount", "ProfitMarginPct"])

    data = data.sort_values("ParsedDate")
    data = data.set_index("ParsedDate")

    # Resample using PeriodIndex for cleaner string labels
    resampled = data.resample(freq).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        OrderCount=("Sales", "count"),
    ).reset_index()

    # Format period label as YYYY-MM
    resampled["Period"] = resampled["ParsedDate"].dt.strftime("%Y-%m")
    resampled = resampled.drop(columns=["ParsedDate"])

    resampled["ProfitMarginPct"] = np.where(
        resampled["Sales"] > 0,
        (resampled["Profit"] / resampled["Sales"]) * 100.0,
        0.0,
    ).round(2)

    resampled["Sales"] = resampled["Sales"].round(2)
    resampled["Profit"] = resampled["Profit"].round(2)

    return resampled


def compute_category_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate business metrics grouped by product category.

    Parameters
    ----------
    df : pd.DataFrame
        Sales dataset.

    Returns
    -------
    pd.DataFrame
        Category performance sorted by Sales descending.
    """
    _validate_columns(df, ["Category", "Sales", "Profit", "Quantity", "Discount"])

    if df.empty:
        return pd.DataFrame(columns=["Category", "Sales", "Profit", "Quantity", "OrderCount", "ProfitMarginPct", "AvgDiscountPct"])

    grouped = df.groupby("Category").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        OrderCount=("Sales", "count"),
        AvgDiscountPct=("Discount", lambda s: s.mean() * 100.0),
    ).reset_index()

    grouped["ProfitMarginPct"] = np.where(
        grouped["Sales"] > 0,
        (grouped["Profit"] / grouped["Sales"]) * 100.0,
        0.0,
    ).round(2)

    grouped["Sales"] = grouped["Sales"].round(2)
    grouped["Profit"] = grouped["Profit"].round(2)
    grouped["AvgDiscountPct"] = grouped["AvgDiscountPct"].round(2)

    return grouped.sort_values("Sales", ascending=False).reset_index(drop=True)


def compute_regional_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate business metrics grouped by geographic region.

    Parameters
    ----------
    df : pd.DataFrame
        Sales dataset.

    Returns
    -------
    pd.DataFrame
        Regional performance sorted by Sales descending.
    """
    _validate_columns(df, ["Region", "Sales", "Profit", "Quantity", "CustomerID"])

    if df.empty:
        return pd.DataFrame(columns=["Region", "Sales", "Profit", "Quantity", "UniqueCustomers", "ProfitMarginPct"])

    grouped = df.groupby("Region").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        UniqueCustomers=("CustomerID", "nunique"),
    ).reset_index()

    grouped["ProfitMarginPct"] = np.where(
        grouped["Sales"] > 0,
        (grouped["Profit"] / grouped["Sales"]) * 100.0,
        0.0,
    ).round(2)

    grouped["Sales"] = grouped["Sales"].round(2)
    grouped["Profit"] = grouped["Profit"].round(2)

    return grouped.sort_values("Sales", ascending=False).reset_index(drop=True)


def compute_discount_profitability_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze the financial impact of promotional discounts on sales and profit margins.

    Parameters
    ----------
    df : pd.DataFrame
        Sales dataset containing Discount, Sales, and Profit.

    Returns
    -------
    pd.DataFrame
        Performance grouped by discount tier brackets.
    """
    _validate_columns(df, ["Discount", "Sales", "Profit", "Quantity"])

    if df.empty:
        return pd.DataFrame(columns=["DiscountBracket", "OrderCount", "TotalSales", "TotalProfit", "ProfitMarginPct"])

    data = df.copy()

    bins = [-0.01, 0.00, 0.10, 0.20, 1.00]
    labels = ["0% (No Discount)", "1-10% (Low)", "11-20% (Moderate)", ">20% (High Discount)"]
    data["DiscountBracket"] = pd.cut(data["Discount"], bins=bins, labels=labels)

    grouped = data.groupby("DiscountBracket", observed=False).agg(
        OrderCount=("Sales", "count"),
        TotalSales=("Sales", "sum"),
        TotalProfit=("Profit", "sum"),
    ).reset_index()

    grouped["ProfitMarginPct"] = np.where(
        grouped["TotalSales"] > 0,
        (grouped["TotalProfit"] / grouped["TotalSales"]) * 100.0,
        0.0,
    ).round(2)

    grouped["TotalSales"] = grouped["TotalSales"].round(2)
    grouped["TotalProfit"] = grouped["TotalProfit"].round(2)

    return grouped


def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Pearson correlation between numeric transaction features.

    Parameters
    ----------
    df : pd.DataFrame
        Sales dataset.

    Returns
    -------
    pd.DataFrame
        Correlation matrix across Quantity, Discount, Sales, and Profit.
    """
    numeric_cols = ["Quantity", "Discount", "Sales", "Profit"]
    _validate_columns(df, numeric_cols)

    if len(df) < 2:
        return pd.DataFrame(index=numeric_cols, columns=numeric_cols).fillna(0.0)

    corr = df[numeric_cols].corr()
    return corr.round(3)


# ---------------------------------------------------------------------------
# Interactive Plotly Chart Generators (Reusable Visual Presentation)
# ---------------------------------------------------------------------------

def create_trend_chart(trend_df: pd.DataFrame) -> go.Figure:
    """Create a synchronized dual-axis line/bar chart for monthly sales and profit."""
    if trend_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No trend data available")
        return fig

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Sales Bar
    fig.add_trace(
        go.Bar(
            x=trend_df["Period"],
            y=trend_df["Sales"],
            name="Monthly Sales ($)",
            marker_color="#2b6cb0",
            opacity=0.85,
        ),
        secondary_y=False,
    )

    # Profit Line
    fig.add_trace(
        go.Scatter(
            x=trend_df["Period"],
            y=trend_df["Profit"],
            name="Monthly Profit ($)",
            mode="lines+markers",
            marker=dict(size=7, color="#38a169"),
            line=dict(width=3, color="#38a169"),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="<b>Monthly Revenue & Profitability Trends</b>",
        xaxis_title="Billing Period (Year-Month)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white",
    )
    fig.update_yaxes(title_text="Sales ($)", secondary_y=False)
    fig.update_yaxes(title_text="Profit ($)", secondary_y=True)

    return fig


def create_category_bar_chart(cat_df: pd.DataFrame) -> go.Figure:
    """Create a grouped bar chart comparing sales and profit by product category."""
    if cat_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No category data available")
        return fig

    fig = go.Figure(
        data=[
            go.Bar(name="Total Sales ($)", x=cat_df["Category"], y=cat_df["Sales"], marker_color="#3182ce"),
            go.Bar(name="Total Profit ($)", x=cat_df["Category"], y=cat_df["Profit"], marker_color="#48bb78"),
        ]
    )
    fig.update_layout(
        barmode="group",
        title="<b>Sales and Profit by Product Category</b>",
        xaxis_title="Category",
        yaxis_title="Amount ($)",
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def create_region_pie_chart(reg_df: pd.DataFrame) -> go.Figure:
    """Create a donut chart illustrating regional sales distribution."""
    if reg_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No regional data available")
        return fig

    fig = px.pie(
        reg_df,
        names="Region",
        values="Sales",
        hole=0.45,
        title="<b>Regional Sales Distribution</b>",
        color_discrete_sequence=px.colors.qualitative.Prism,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(template="plotly_white", margin=dict(l=30, r=30, t=50, b=30))
    return fig


def create_discount_profit_scatter(df: pd.DataFrame) -> go.Figure:
    """Create a scatter plot of Discount Rate vs. Profit colored by Category."""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No scatter data available")
        return fig

    fig = px.scatter(
        df,
        x="Discount",
        y="Profit",
        color="Category",
        size="Quantity",
        hover_data=["CustomerID", "Sales"],
        title="<b>Discount Rate vs. Profitability Impact</b>",
        labels={"Discount": "Discount Rate (0.0 - 1.0)", "Profit": "Net Profit ($)"},
        template="plotly_white",
        color_discrete_sequence=["#e53e3e", "#3182ce", "#38a169"],
    )
    # Add zero profit reference line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Break-even Profit Line")
    fig.update_layout(margin=dict(l=40, r=40, t=50, b=40))
    return fig


def create_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    """Create a heatmap for feature correlations."""
    if corr_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No correlation data available")
        return fig

    fig = px.imshow(
        corr_df,
        text_auto=".2f",
        aspect="auto",
        title="<b>Numeric Feature Correlation Matrix</b>",
        color_continuous_scale="RdBu_r",
        zmin=-1.0,
        zmax=1.0,
    )
    fig.update_layout(template="plotly_white", margin=dict(l=40, r=40, t=50, b=40))
    return fig
