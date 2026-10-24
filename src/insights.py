"""
Decision Support & Actionable Business Insights Engine for BizInsightIQ.

Synthesizes descriptive KPIs, category/regional performance, discount elasticity,
customer segmentation personas, and predictive regression models into structured,
explainable, evidence-based business recommendations.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.eda import (
    compute_business_kpis,
    compute_category_performance,
    compute_regional_performance,
    compute_discount_profitability_analysis,
    compute_sales_profit_trends,
    REQUIRED_EDA_COLUMNS,
)
from src.segmentation import (
    aggregate_customer_features,
    perform_kmeans_clustering,
    generate_cluster_profiles,
)
from src.prediction import (
    train_and_evaluate_models,
)


@dataclass
class BusinessInsight:
    """Structured, explainable business recommendation with empirical evidence."""
    insight_id: str
    category: str        # 'Sales & Profitability', 'Discount Effectiveness', 'Customer Segmentation', 'Predictive Decision Support'
    severity: str        # 'critical', 'warning', 'info'
    title: str
    evidence: Dict[str, Any]
    recommendation: str
    limitations: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert insight to dictionary for UI rendering or API responses."""
        return {
            "insight_id": self.insight_id,
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "limitations": self.limitations,
        }


def _validate_raw_dataframe(df: pd.DataFrame, required_cols: Optional[List[str]] = None) -> None:
    """Ensure input is a valid pandas DataFrame with required columns."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
    if required_cols is None:
        required_cols = REQUIRED_EDA_COLUMNS
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"DataFrame is missing required columns for insights generation: {', '.join(missing)}")


# ---------------------------------------------------------------------------
# 1. Sales & Profitability Insights
# ---------------------------------------------------------------------------

def generate_sales_profitability_insights(
    df: pd.DataFrame,
    kpis: Optional[Dict[str, Any]] = None,
    category_df: Optional[pd.DataFrame] = None,
    regional_df: Optional[pd.DataFrame] = None,
) -> List[BusinessInsight]:
    """
    Generate heuristic insights on revenue concentration, category margins, and regional disparities.

    Parameters
    ----------
    df : pd.DataFrame
        Sales transactions.
    kpis : Optional[Dict[str, Any]]
        Pre-computed business KPIs from compute_business_kpis.
    category_df : Optional[pd.DataFrame]
        Pre-computed category performance from compute_category_performance.
    regional_df : Optional[pd.DataFrame]
        Pre-computed regional performance from compute_regional_performance.

    Returns
    -------
    List[BusinessInsight]
        Generated insights for sales and profitability.
    """
    _validate_raw_dataframe(df, ["Sales", "Profit", "Category", "Region", "Quantity", "CustomerID", "Discount"])

    if df.empty:
        return []

    insights: List[BusinessInsight] = []

    # 1. Compute or reuse foundations
    if kpis is None:
        kpis = compute_business_kpis(df)
    if category_df is None:
        category_df = compute_category_performance(df)
    if regional_df is None:
        regional_df = compute_regional_performance(df)

    overall_margin = kpis.get("profit_margin_pct", 0.0)
    total_sales = kpis.get("total_sales", 0.0)

    if total_sales <= 0 or category_df.empty:
        return []

    # Rule A1: Revenue Concentration & Margin Disparity in Categories
    top_cat = category_df.iloc[0]
    top_cat_name = str(top_cat["Category"])
    top_cat_sales = float(top_cat["Sales"])
    top_cat_share = (top_cat_sales / total_sales * 100.0) if total_sales > 0 else 0.0
    top_cat_margin = float(top_cat["ProfitMarginPct"])

    if top_cat_share >= 50.0:
        severity = "warning" if top_cat_margin < overall_margin else "info"
        insights.append(
            BusinessInsight(
                insight_id="INS-SALES-001",
                category="Sales & Profitability",
                severity=severity,
                title=f"High Revenue Concentration in {top_cat_name}",
                evidence={
                    "top_category": top_cat_name,
                    "sales_share_pct": round(top_cat_share, 1),
                    "category_sales": round(top_cat_sales, 2),
                    "category_profit_margin_pct": round(top_cat_margin, 2),
                    "overall_profit_margin_pct": round(overall_margin, 2),
                },
                recommendation=(
                    f"The {top_cat_name} category accounts for {top_cat_share:.1f}% of total enterprise revenue. "
                    f"Evaluate cross-selling and catalog diversification into other categories to mitigate "
                    f"single-category demand dependency while maintaining gross margins."
                ),
                limitations=(
                    "Heuristic rule based on macro category grouping; does not account for sub-product line "
                    "margins or supplier cost contracts."
                ),
            )
        )

    # Rule A2: Regional Margin Underperformance
    if not regional_df.empty and len(regional_df) > 1:
        mean_reg_sales = float(regional_df["Sales"].mean())
        for _, reg_row in regional_df.iterrows():
            reg_name = str(reg_row["Region"])
            reg_sales = float(reg_row["Sales"])
            reg_margin = float(reg_row["ProfitMarginPct"])

            # Check for below-average margin (at least 1.5 percentage points lower)
            if reg_margin < (overall_margin - 1.5):
                margin_gap = overall_margin - reg_margin
                insights.append(
                    BusinessInsight(
                        insight_id=f"INS-REG-{reg_name.upper()}-MARGIN",
                        category="Sales & Profitability",
                        severity="warning",
                        title=f"Sub-Benchmark Profit Margin in {reg_name} Region",
                        evidence={
                            "region": reg_name,
                            "regional_sales": round(reg_sales, 2),
                            "regional_profit_margin_pct": round(reg_margin, 2),
                            "overall_profit_margin_pct": round(overall_margin, 2),
                            "margin_gap_pct_pts": round(margin_gap, 2),
                        },
                        recommendation=(
                            f"The {reg_name} region exhibits an observed profit margin of {reg_margin:.2f}%, which is "
                            f"{margin_gap:.2f} percentage points below the overall business benchmark ({overall_margin:.2f}%). "
                            f"Audit regional promotional discounts and fulfillment logistics costs in {reg_name} to "
                            f"identify potential margin restoration opportunities."
                        ),
                        limitations=(
                            "Regional differences correlate with observed transactional profits but do not prove "
                            "operational inefficiency without field operational expenditure data."
                        ),
                    )
                )

            # Check for low sales volume (more than 15% below regional average)
            if reg_sales < (mean_reg_sales * 0.85):
                sales_gap = mean_reg_sales - reg_sales
                insights.append(
                    BusinessInsight(
                        insight_id=f"INS-REG-{reg_name.upper()}-VOLUME",
                        category="Sales & Profitability",
                        severity="info",
                        title=f"Below-Average Sales Volume in {reg_name} Region",
                        evidence={
                            "region": reg_name,
                            "regional_sales": round(reg_sales, 2),
                            "mean_regional_sales": round(mean_reg_sales, 2),
                            "volume_gap_dollars": round(sales_gap, 2),
                        },
                        recommendation=(
                            f"The {reg_name} region generated ${reg_sales:,.2f} in sales, trailing the regional mean "
                            f"of ${mean_reg_sales:,.2f}. Consider evaluating regional market penetration and customer "
                            f"acquisition campaigns in {reg_name}."
                        ),
                        limitations=(
                            "Does not account for differences in territory population, customer density, or local market size."
                        ),
                    )
                )

    # Rule A3: Monthly Trend Profit Margin Contraction
    if "OrderDate" in df.columns:
        trend_df = compute_sales_profit_trends(df)
        if len(trend_df) >= 3:
            # Check if any recent period experienced negative profit or steep margin decline
            negative_periods = trend_df[trend_df["Profit"] < 0]
            if not negative_periods.empty:
                neg_period_names = negative_periods["Period"].tolist()
                insights.append(
                    BusinessInsight(
                        insight_id="INS-TREND-NEG-PROFIT",
                        category="Sales & Profitability",
                        severity="critical",
                        title="Unprofitable Operating Periods Detected",
                        evidence={
                            "negative_profit_periods": neg_period_names,
                            "unprofitable_period_count": len(neg_period_names),
                        },
                        recommendation=(
                            f"Transaction aggregates reveal negative net operating profit in period(s): "
                            f"{', '.join(neg_period_names)}. Investigate specific discounting anomalies and return rates "
                            f"during these months to establish preventive guardrails."
                        ),
                        limitations=(
                            "Period-level aggregations may reflect seasonal clearance events or one-off inventory liquidations."
                        ),
                    )
                )

    return insights


# ---------------------------------------------------------------------------
# 2. Discount Effectiveness Insights
# ---------------------------------------------------------------------------

def generate_discount_insights(
    df: pd.DataFrame,
    discount_df: Optional[pd.DataFrame] = None,
) -> List[BusinessInsight]:
    """
    Analyze promotional discount brackets to detect severe margin erosion.

    Parameters
    ----------
    df : pd.DataFrame
        Sales dataset.
    discount_df : Optional[pd.DataFrame]
        Pre-computed discount tier performance from compute_discount_profitability_analysis.

    Returns
    -------
    List[BusinessInsight]
        Generated discount effectiveness insights.
    """
    _validate_raw_dataframe(df, ["Discount", "Sales", "Profit", "Quantity"])

    if df.empty:
        return []

    insights: List[BusinessInsight] = []

    if discount_df is None:
        discount_df = compute_discount_profitability_analysis(df)

    if discount_df.empty:
        return []

    # Rule B1: Deep Discount Margin Collapse (>20% discount tier)
    high_disc_rows = discount_df[discount_df["DiscountBracket"] == ">20% (High Discount)"]
    no_disc_rows = discount_df[discount_df["DiscountBracket"] == "0% (No Discount)"]

    if not high_disc_rows.empty and not no_disc_rows.empty:
        high_disc = high_disc_rows.iloc[0]
        no_disc = no_disc_rows.iloc[0]

        high_margin = float(high_disc["ProfitMarginPct"])
        no_margin = float(no_disc["ProfitMarginPct"])
        high_sales = float(high_disc["TotalSales"])
        high_orders = int(high_disc["OrderCount"])

        # Check if deep discounts coincide with severe margin erosion (e.g. margin drop > 15 percentage points)
        if high_margin < (no_margin - 15.0) or high_margin < 5.0:
            severity = "critical" if high_margin < 5.0 else "warning"
            margin_loss = no_margin - high_margin
            insights.append(
                BusinessInsight(
                    insight_id="INS-DISC-001",
                    category="Discount Effectiveness",
                    severity=severity,
                    title="Severe Margin Compression on Deep Discounts (>20%)",
                    evidence={
                        "high_discount_margin_pct": round(high_margin, 2),
                        "no_discount_margin_pct": round(no_margin, 2),
                        "margin_compression_pct_pts": round(margin_loss, 2),
                        "high_discount_order_count": high_orders,
                        "high_discount_sales": round(high_sales, 2),
                    },
                    recommendation=(
                        f"Orders discounted above 20% coincide with an observed profit margin of {high_margin:.2f}%, "
                        f"representing a {margin_loss:.2f} percentage point contraction compared to non-discounted "
                        f"orders ({no_margin:.2f}%). Review the commercial justification for discounts exceeding 20% "
                        f"and evaluate introducing a mandatory managerial approval threshold for deep discounts."
                    ),
                    limitations=(
                        "Observational retail data does not establish whether steep discounts caused lower margins "
                        "or whether deep discounts were applied selectively to low-margin clearance merchandise."
                    ),
                )
            )

    # Rule B2: Moderate Discount Elasticity Assessment (11-20% tier)
    mod_disc_rows = discount_df[discount_df["DiscountBracket"] == "11-20% (Moderate)"]
    low_disc_rows = discount_df[discount_df["DiscountBracket"] == "1-10% (Low)"]

    if not mod_disc_rows.empty and not low_disc_rows.empty:
        mod_disc = mod_disc_rows.iloc[0]
        low_disc = low_disc_rows.iloc[0]

        mod_margin = float(mod_disc["ProfitMarginPct"])
        low_margin = float(low_disc["ProfitMarginPct"])

        if mod_margin < (low_margin - 10.0):
            insights.append(
                BusinessInsight(
                    insight_id="INS-DISC-002",
                    category="Discount Effectiveness",
                    severity="warning",
                    title="Noticeable Margin Drop-off in Moderate Discount Tier (11-20%)",
                    evidence={
                        "moderate_discount_margin_pct": round(mod_margin, 2),
                        "low_discount_margin_pct": round(low_margin, 2),
                        "margin_step_down_pct_pts": round(low_margin - mod_margin, 2),
                    },
                    recommendation=(
                        f"Profit margins contract from {low_margin:.2f}% in the 1-10% discount bracket to "
                        f"{mod_margin:.2f}% in the 11-20% bracket. Conduct pricing elasticity tests before running "
                        f"campaigns in the 11-20% range to verify whether volume gains compensate for margin compression."
                    ),
                    limitations=(
                        "Synthetic benchmark data lacks demand price elasticity experiments; empirical testing with "
                        "actual customer cohorts is recommended before adjusting policy."
                    ),
                )
            )

    return insights


# ---------------------------------------------------------------------------
# 3. Customer Segmentation Insights
# ---------------------------------------------------------------------------

def generate_segmentation_insights(
    df: pd.DataFrame,
    cluster_profiles_df: Optional[pd.DataFrame] = None,
) -> List[BusinessInsight]:
    """
    Generate retention, loyalty, and discount-dependence insights from customer segments.

    Parameters
    ----------
    df : pd.DataFrame
        Sales dataset.
    cluster_profiles_df : Optional[pd.DataFrame]
        Pre-computed cluster profiles from generate_cluster_profiles.

    Returns
    -------
    List[BusinessInsight]
        Generated customer segment behavioral recommendations.
    """
    _validate_raw_dataframe(df, ["CustomerID", "OrderDate", "Sales", "Profit", "Quantity", "Discount"])

    if df.empty:
        return []

    insights: List[BusinessInsight] = []

    # 1. Compute cluster profiles if not supplied
    if cluster_profiles_df is None:
        customer_df = aggregate_customer_features(df)
        if len(customer_df) < 4:
            return []
        clustering_result = perform_kmeans_clustering(customer_df, n_clusters=4, random_state=42)
        cluster_profiles_df = generate_cluster_profiles(clustering_result["clustered_df"])

    if cluster_profiles_df.empty or "Cluster" not in cluster_profiles_df.columns:
        return []

    pop_median_recency = float(cluster_profiles_df["MeanRecencyDays"].median())
    pop_mean_discount = float(cluster_profiles_df["MeanDiscountPct"].mean())

    for _, prof in cluster_profiles_df.iterrows():
        c_id = int(prof["Cluster"])
        c_size = int(prof["CustomerCount"])
        c_pct = float(prof["CustomerPct"])
        c_spend = float(prof["MeanSales"])
        c_margin = float(prof["ProfitMarginPct"])
        c_recency = float(prof["MeanRecencyDays"])
        c_disc = float(prof["MeanDiscountPct"])
        persona = str(prof.get("DescriptivePersona", f"Cluster {c_id}"))

        # Rule C1: Churn Risk / High-Recency Cohort
        if c_recency >= max(120.0, pop_median_recency * 1.5):
            insights.append(
                BusinessInsight(
                    insight_id=f"INS-SEG-C{c_id}-RECENCY",
                    category="Customer Segmentation",
                    severity="warning",
                    title=f"Dormancy / Churn Risk in Cluster {c_id} ({persona})",
                    evidence={
                        "cluster_id": c_id,
                        "customer_count": c_size,
                        "customer_share_pct": round(c_pct, 1),
                        "mean_recency_days": round(c_recency, 1),
                        "population_median_recency": round(pop_median_recency, 1),
                        "mean_sales_spend": round(c_spend, 2),
                    },
                    recommendation=(
                        f"Cluster {c_id} comprises {c_size} customers ({c_pct:.1f}% of base) with an average recency "
                        f"of {c_recency:.0f} days since their last recorded order. Evaluate targeted re-engagement "
                        f"surveys or win-back campaigns before these relationships lapse into permanent churn."
                    ),
                    limitations=(
                        "Recency is measured against a fixed benchmark date and assumes regular ordering cycles; "
                        "irregular or seasonal buyers may naturally register high recency values."
                    ),
                )
            )

        # Rule C2: High Discount-Dependent Cohort
        if c_disc >= 20.0 and c_disc >= (pop_mean_discount * 1.5):
            insights.append(
                BusinessInsight(
                    insight_id=f"INS-SEG-C{c_id}-DISCOUNT",
                    category="Customer Segmentation",
                    severity="warning",
                    title=f"Discount Dependency in Cluster {c_id} ({persona})",
                    evidence={
                        "cluster_id": c_id,
                        "customer_count": c_size,
                        "mean_discount_pct": round(c_disc, 1),
                        "profit_margin_pct": round(c_margin, 2),
                        "mean_sales": round(c_spend, 2),
                    },
                    recommendation=(
                        f"Cluster {c_id} exhibits an average discount rate of {c_disc:.1f}% and an observed profit "
                        f"margin of {c_margin:.1f}%. Explore transitioning this segment toward value-oriented bundles "
                        f"or loyalty rewards rather than direct price cuts to protect margin realization."
                    ),
                    limitations=(
                        "Transactional records do not reveal competitor price sensitivity or bargaining power of "
                        "individual wholesale buyers."
                    ),
                )
            )

        # Rule C3: High-Value VIP Retention
        if c_spend >= cluster_profiles_df["MeanSales"].max() * 0.9 and c_margin >= 18.0:
            insights.append(
                BusinessInsight(
                    insight_id=f"INS-SEG-C{c_id}-VIP",
                    category="Customer Segmentation",
                    severity="info",
                    title=f"High-Value Core Customer Group in Cluster {c_id} ({persona})",
                    evidence={
                        "cluster_id": c_id,
                        "customer_count": c_size,
                        "mean_spend_dollars": round(c_spend, 2),
                        "profit_margin_pct": round(c_margin, 2),
                    },
                    recommendation=(
                        f"Cluster {c_id} represents top-spending accounts averaging ${c_spend:,.2f} per customer at a "
                        f"healthy {c_margin:.1f}% profit margin. Implement dedicated account management, prioritized SLA "
                        f"support, and proactive relationship outreach to safeguard this core revenue source."
                    ),
                    limitations=(
                        "Purchase frequency serves as a proxy based on transaction row count, as distinct order IDs are not present."
                    ),
                )
            )

    return insights


# ---------------------------------------------------------------------------
# 4. Predictive Decision Support Insights
# ---------------------------------------------------------------------------

def generate_predictive_insights(
    df: pd.DataFrame,
    prediction_results: Optional[Dict[str, Any]] = None,
) -> List[BusinessInsight]:
    """
    Synthesize regression model evaluation diagnostics into operational decision-support advice.

    Parameters
    ----------
    df : pd.DataFrame
        Sales dataset.
    prediction_results : Optional[Dict[str, Any]]
        Pre-computed model results from train_and_evaluate_models.

    Returns
    -------
    List[BusinessInsight]
        Generated predictive decision-support insights.
    """
    _validate_raw_dataframe(df, ["OrderDate", "Category", "Region", "Quantity", "Discount", "Sales"])

    if len(df) < 50:
        return []

    insights: List[BusinessInsight] = []

    if prediction_results is None:
        try:
            prediction_results = train_and_evaluate_models(df, split_strategy="chronological", test_size=0.2, random_state=42)
        except Exception:
            return []

    eval_lr = prediction_results["evaluations"]["linear_regression"]
    eval_rf = prediction_results["evaluations"]["random_forest"]

    rf_mae = eval_rf["mae"]
    rf_r2 = eval_rf["r2"]
    lr_mae = eval_lr["mae"]
    lr_r2 = eval_lr["r2"]

    # Rule D1: Model Champion & Benchmark Summary
    best_model_name = "Random Forest Regressor" if rf_mae <= lr_mae else "Linear Regression"
    mae_diff = abs(lr_mae - rf_mae)
    insights.append(
        BusinessInsight(
            insight_id="INS-PRED-CHAMPION",
            category="Predictive Decision Support",
            severity="info",
            title=f"Predictive Model Benchmark: {best_model_name} Recommended",
            evidence={
                "recommended_model": best_model_name,
                "random_forest_mae": rf_mae,
                "random_forest_r2": rf_r2,
                "linear_regression_mae": lr_mae,
                "linear_regression_r2": lr_r2,
                "mae_reduction_dollars": round(mae_diff, 2),
            },
            recommendation=(
                f"Out-of-sample chronological evaluation demonstrates that the {best_model_name} achieves an MAE "
                f"of ${rf_mae:,.2f} on unseen future test transactions (vs. ${lr_mae:,.2f} for baseline OLS). "
                f"Utilize the Random Forest engine for transactional sales quote simulations while referencing "
                f"the residual bounds."
            ),
            limitations=(
                f"The held-out R² score of {rf_r2:.4f} indicates that approximately {(1 - rf_r2) * 100:.1f}% of sales "
                f"variance remains unexplained by pre-transaction attributes. Predictions represent expected point "
                f"estimates with uncertainty intervals."
            ),
        )
    )

    # Rule D2: Operational Decision Scope & Cautionary Caveat
    insights.append(
        BusinessInsight(
            insight_id="INS-PRED-CAVEAT",
            category="Predictive Decision Support",
            severity="warning",
            title="Operational Scope: Transaction Quotes vs. Aggregate Demand",
            evidence={
                "prediction_target": "Sales (Transaction-Level Gross Revenue)",
                "evaluation_samples": eval_rf["test_size"],
                "r2_explained_variance": rf_r2,
            },
            recommendation=(
                "Predicted sales values generated by the model are tailored for evaluating prospective order-level "
                "scenarios (varying quantities, discounts, and regional seasonality). Do not use transaction-level "
                "predictions as macroeconomic demand forecasts or guaranteed future revenue commitments without "
                "external validation."
            ),
            limitations=(
                "Models were trained on synthetic retail sales data generated with a pseudo-random seed. "
                "Model parameters must be re-calibrated against authentic enterprise transaction ledgers before "
                "production deployment."
            ),
        )
    )

    return insights


# ---------------------------------------------------------------------------
# 5. Master Facade: Synthesize All Business Insights
# ---------------------------------------------------------------------------

def generate_all_insights(
    df: pd.DataFrame,
    kpis: Optional[Dict[str, Any]] = None,
    category_df: Optional[pd.DataFrame] = None,
    regional_df: Optional[pd.DataFrame] = None,
    discount_df: Optional[pd.DataFrame] = None,
    cluster_profiles_df: Optional[pd.DataFrame] = None,
    prediction_results: Optional[Dict[str, Any]] = None,
) -> List[BusinessInsight]:
    """
    Synthesize end-to-end explainable business recommendations across all analytical pillars.

    Parameters
    ----------
    df : pd.DataFrame
        Validated sales transactions dataset.
    kpis : Optional[Dict[str, Any]]
        Pre-computed business KPIs.
    category_df : Optional[pd.DataFrame]
        Pre-computed category summary.
    regional_df : Optional[pd.DataFrame]
        Pre-computed regional summary.
    discount_df : Optional[pd.DataFrame]
        Pre-computed discount tier summary.
    cluster_profiles_df : Optional[pd.DataFrame]
        Pre-computed customer segmentation cluster profiles.
    prediction_results : Optional[Dict[str, Any]]
        Pre-computed machine learning prediction results.

    Returns
    -------
    List[BusinessInsight]
        Consolidated, prioritized list of business insights.
    """
    _validate_raw_dataframe(df)

    if df.empty:
        return []

    all_insights: List[BusinessInsight] = []

    # 1. Sales & Profitability
    all_insights.extend(
        generate_sales_profitability_insights(
            df=df,
            kpis=kpis,
            category_df=category_df,
            regional_df=regional_df,
        )
    )

    # 2. Discount Effectiveness
    all_insights.extend(
        generate_discount_insights(
            df=df,
            discount_df=discount_df,
        )
    )

    # 3. Customer Segmentation
    all_insights.extend(
        generate_segmentation_insights(
            df=df,
            cluster_profiles_df=cluster_profiles_df,
        )
    )

    # 4. Predictive Decision Support
    all_insights.extend(
        generate_predictive_insights(
            df=df,
            prediction_results=prediction_results,
        )
    )

    # Sort deterministically by severity priority ('critical' -> 'warning' -> 'info'), then insight_id
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    all_insights.sort(key=lambda x: (severity_order.get(x.severity, 3), x.insight_id))

    return all_insights


# ---------------------------------------------------------------------------
# 6. Filtering & Visual Summary Utilities
# ---------------------------------------------------------------------------

def filter_insights(
    insights: List[BusinessInsight],
    category: Optional[str] = None,
    severity: Optional[str] = None,
) -> List[BusinessInsight]:
    """Filter list of insights by category and/or severity."""
    filtered = insights
    if category and category != "All":
        filtered = [ins for ins in filtered if ins.category == category]
    if severity and severity != "All":
        filtered = [ins for ins in filtered if ins.severity == severity]
    return filtered


def get_insights_summary(insights: List[BusinessInsight]) -> Dict[str, Any]:
    """Compute summary statistics for generated insights."""
    total = len(insights)
    by_severity = {"critical": 0, "warning": 0, "info": 0}
    by_category = {
        "Sales & Profitability": 0,
        "Discount Effectiveness": 0,
        "Customer Segmentation": 0,
        "Predictive Decision Support": 0,
    }

    for ins in insights:
        if ins.severity in by_severity:
            by_severity[ins.severity] += 1
        if ins.category in by_category:
            by_category[ins.category] += 1

    return {
        "total": total,
        "by_severity": by_severity,
        "by_category": by_category,
    }


def create_insights_distribution_chart(insights: List[BusinessInsight]) -> go.Figure:
    """Create a Plotly stacked breakdown of insights by category and severity."""
    if not insights:
        fig = go.Figure()
        fig.update_layout(title="No insights available to display")
        return fig

    records = [
        {"category": ins.category, "severity": ins.severity.capitalize()}
        for ins in insights
    ]
    df_chart = pd.DataFrame(records)
    summary_df = df_chart.groupby(["category", "severity"]).size().reset_index(name="count")

    color_map = {
        "Critical": "#e53e3e",
        "Warning": "#dd6b20",
        "Info": "#3182ce",
    }

    fig = px.bar(
        summary_df,
        x="category",
        y="count",
        color="severity",
        barmode="stack",
        color_discrete_map=color_map,
        title="Distribution of Actionable Insights by Category & Severity",
        labels={"category": "Analytical Pillar", "count": "Insight Count", "severity": "Severity Level"},
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Generated Insights",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig
