"""
Unit and Integration Tests for Exploratory Data Analysis (EDA) Module.

Validates statistical accuracy, edge cases, divide-by-zero safeguards,
data immutability, and Plotly visualization generation.
"""

import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
from src.data_loader import load_csv_data


@pytest.fixture
def sample_sales_df() -> pd.DataFrame:
    """Fixture providing a deterministic 4-row sales DataFrame."""
    return pd.DataFrame({
        "CustomerID": ["CUST-101", "CUST-102", "CUST-101", "CUST-103"],
        "OrderDate": ["2024-01-15", "2024-01-20", "2024-02-10", "2024-02-15"],
        "Category": ["Technology", "Furniture", "Technology", "Office Supplies"],
        "Region": ["North", "South", "North", "West"],
        "Quantity": [2, 5, 3, 10],
        "Discount": [0.0, 0.10, 0.20, 0.05],
        "Sales": [500.0, 1000.0, 600.0, 200.0],
        "Profit": [150.0, 200.0, 60.0, 40.0],
    })


class TestBusinessKPIs:
    """Tests for KPI computation logic."""

    def test_compute_business_kpis_normal(self, sample_sales_df):
        kpis = compute_business_kpis(sample_sales_df)
        assert kpis["total_sales"] == 2300.0
        assert kpis["total_profit"] == 450.0
        assert kpis["total_units"] == 20
        assert kpis["unique_customers"] == 3
        assert kpis["total_orders"] == 4
        # Margin: (450 / 2300) * 100 = 19.57%
        assert kpis["profit_margin_pct"] == 19.57
        # AOV: 2300 / 4 = 575.0
        assert kpis["avg_order_value"] == 575.0
        # Avg discount: (0.0 + 0.10 + 0.20 + 0.05)/4 * 100 = 8.75%
        assert kpis["avg_discount_pct"] == 8.75

    def test_compute_business_kpis_zero_sales(self, sample_sales_df):
        df_zero = sample_sales_df.copy()
        df_zero["Sales"] = 0.0
        df_zero["Profit"] = 0.0
        kpis = compute_business_kpis(df_zero)
        assert kpis["total_sales"] == 0.0
        assert kpis["profit_margin_pct"] == 0.0
        assert kpis["avg_order_value"] == 0.0

    def test_compute_business_kpis_empty_dataframe(self):
        df_empty = pd.DataFrame(columns=["CustomerID", "OrderDate", "Category", "Region", "Quantity", "Discount", "Sales", "Profit"])
        kpis = compute_business_kpis(df_empty)
        assert kpis["total_sales"] == 0.0
        assert kpis["total_units"] == 0
        assert kpis["unique_customers"] == 0
        assert kpis["profit_margin_pct"] == 0.0

    def test_compute_business_kpis_missing_columns(self):
        df_bad = pd.DataFrame({"Quantity": [1, 2]})
        with pytest.raises(ValueError, match="missing required columns"):
            compute_business_kpis(df_bad)

    def test_immutability(self, sample_sales_df):
        df_copy = sample_sales_df.copy(deep=True)
        _ = compute_business_kpis(sample_sales_df)
        pd.testing.assert_frame_equal(sample_sales_df, df_copy)


class TestSalesProfitTrends:
    """Tests for chronological time-series aggregations."""

    def test_compute_sales_profit_trends_monthly(self, sample_sales_df):
        trends = compute_sales_profit_trends(sample_sales_df, freq="ME")
        assert len(trends) == 2
        assert list(trends["Period"]) == ["2024-01", "2024-02"]
        # Jan: 500 + 1000 = 1500 sales, 150 + 200 = 350 profit
        assert trends.loc[trends["Period"] == "2024-01", "Sales"].iloc[0] == 1500.0
        assert trends.loc[trends["Period"] == "2024-01", "Profit"].iloc[0] == 350.0
        # Feb: 600 + 200 = 800 sales, 60 + 40 = 100 profit
        assert trends.loc[trends["Period"] == "2024-02", "Sales"].iloc[0] == 800.0
        assert trends.loc[trends["Period"] == "2024-02", "Profit"].iloc[0] == 100.0

    def test_compute_sales_profit_trends_empty(self):
        df_empty = pd.DataFrame(columns=["OrderDate", "Sales", "Profit", "Quantity"])
        trends = compute_sales_profit_trends(df_empty)
        assert trends.empty
        assert "Period" in trends.columns

    def test_compute_sales_profit_trends_invalid_dates(self, sample_sales_df):
        df_invalid = sample_sales_df.copy()
        df_invalid.loc[0, "OrderDate"] = "not-a-date"
        trends = compute_sales_profit_trends(df_invalid)
        # Invalid date dropped safely without crashing
        assert not trends.empty


class TestCategoryAndRegionalPerformance:
    """Tests for category and regional aggregations."""

    def test_compute_category_performance(self, sample_sales_df):
        cat_df = compute_category_performance(sample_sales_df)
        assert len(cat_df) == 3
        # Technology has two rows: 500 + 600 = 1100 sales
        tech_row = cat_df[cat_df["Category"] == "Technology"].iloc[0]
        assert tech_row["Sales"] == 1100.0
        assert tech_row["Profit"] == 210.0
        assert tech_row["Quantity"] == 5
        # Must be sorted descending by Sales
        assert cat_df["Sales"].is_monotonic_decreasing

    def test_compute_regional_performance(self, sample_sales_df):
        reg_df = compute_regional_performance(sample_sales_df)
        assert len(reg_df) == 3
        # North has 2 orders from CUST-101 (1 unique customer)
        north_row = reg_df[reg_df["Region"] == "North"].iloc[0]
        assert north_row["Sales"] == 1100.0
        assert north_row["UniqueCustomers"] == 1
        assert reg_df["Sales"].is_monotonic_decreasing

    def test_empty_aggregations(self):
        empty = pd.DataFrame(columns=["Category", "Region", "Sales", "Profit", "Quantity", "Discount", "CustomerID"])
        assert compute_category_performance(empty).empty
        assert compute_regional_performance(empty).empty


class TestDiscountAndCorrelation:
    """Tests for discount impact and correlation matrices."""

    def test_compute_discount_profitability_analysis(self, sample_sales_df):
        disc_df = compute_discount_profitability_analysis(sample_sales_df)
        assert len(disc_df) == 4
        assert "DiscountBracket" in disc_df.columns
        assert "ProfitMarginPct" in disc_df.columns

    def test_compute_correlation_matrix(self, sample_sales_df):
        corr = compute_correlation_matrix(sample_sales_df)
        assert corr.shape == (4, 4)
        # Diagonal elements must be 1.0
        for col in ["Quantity", "Discount", "Sales", "Profit"]:
            assert corr.loc[col, col] == 1.0


class TestPlotlyVisualizations:
    """Smoke tests for Plotly chart generators."""

    def test_chart_creation_with_data(self, sample_sales_df):
        trends = compute_sales_profit_trends(sample_sales_df)
        cats = compute_category_performance(sample_sales_df)
        regs = compute_regional_performance(sample_sales_df)
        corr = compute_correlation_matrix(sample_sales_df)

        fig_trend = create_trend_chart(trends)
        fig_cat = create_category_bar_chart(cats)
        fig_reg = create_region_pie_chart(regs)
        fig_scatter = create_discount_profit_scatter(sample_sales_df)
        fig_corr = create_correlation_heatmap(corr)

        assert isinstance(fig_trend, go.Figure)
        assert isinstance(fig_cat, go.Figure)
        assert isinstance(fig_reg, go.Figure)
        assert isinstance(fig_scatter, go.Figure)
        assert isinstance(fig_corr, go.Figure)

    def test_chart_creation_with_empty_data(self):
        empty = pd.DataFrame()
        fig_trend = create_trend_chart(empty)
        fig_cat = create_category_bar_chart(empty)
        fig_reg = create_region_pie_chart(empty)
        fig_scatter = create_discount_profit_scatter(empty)
        fig_corr = create_correlation_heatmap(empty)

        assert isinstance(fig_trend, go.Figure)
        assert isinstance(fig_cat, go.Figure)
        assert isinstance(fig_reg, go.Figure)
        assert isinstance(fig_scatter, go.Figure)
        assert isinstance(fig_corr, go.Figure)


class TestBundledDatasetWithEDA:
    """Integration test verifying EDA functions on the bundled 1,200-row dataset."""

    def test_bundled_dataset_eda(self):
        df = load_csv_data("data/sample_sales_data.csv")
        assert len(df) == 1200

        kpis = compute_business_kpis(df)
        assert kpis["total_sales"] > 0
        assert kpis["total_profit"] > 0
        assert kpis["unique_customers"] == 150
        assert kpis["total_orders"] == 1200

        trends = compute_sales_profit_trends(df)
        assert len(trends) == 24  # 2 years of monthly data

        cats = compute_category_performance(df)
        assert len(cats) == 3

        regs = compute_regional_performance(df)
        assert len(regs) == 4
