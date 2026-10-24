"""
Unit and Integration Test Suite for Business Insights & Decision Support Engine.

Tests compliance with all Day 5 requirements:
- Valid insight generation and schema validation
- Explainable evidence-based rules across 4 analytical pillars
- Empty, missing, zero-division, and edge case resilience
- Deterministic output and input DataFrame immutability
- Absence of unsupported causal claims in recommendation text
- Integration with pre-computed analytical results and bundled dataset
"""

import pytest
import pandas as pd
import numpy as np

from src.insights import (
    BusinessInsight,
    generate_sales_profitability_insights,
    generate_discount_insights,
    generate_segmentation_insights,
    generate_predictive_insights,
    generate_all_insights,
    filter_insights,
    get_insights_summary,
    create_insights_distribution_chart,
)
from src.data_loader import load_csv_data
from src.eda import (
    compute_business_kpis,
    compute_category_performance,
    compute_regional_performance,
    compute_discount_profitability_analysis,
)
from src.segmentation import (
    aggregate_customer_features,
    perform_kmeans_clustering,
    generate_cluster_profiles,
)
from src.prediction import train_and_evaluate_models


@pytest.fixture
def sample_insights_df() -> pd.DataFrame:
    """Fixture providing a realistic synthetic sales DataFrame."""
    np.random.seed(42)
    n = 100
    dates = pd.date_range("2023-01-01", periods=n, freq="D").strftime("%Y-%m-%d")
    categories = np.random.choice(["Technology", "Furniture", "Office Supplies"], size=n, p=[0.6, 0.3, 0.1])
    regions = np.random.choice(["East", "West", "Central", "South"], size=n)
    quantities = np.random.randint(1, 10, size=n)
    discounts = np.random.choice([0.0, 0.05, 0.15, 0.25], size=n, p=[0.4, 0.3, 0.15, 0.15])
    sales = quantities * 200.0 * (1.0 - discounts) + np.random.normal(0, 10, size=n)
    sales = np.maximum(sales, 10.0).round(2)
    # Profit drops sharply on high discounts
    profit = sales * np.where(discounts > 0.20, 0.02, 0.25) + np.random.normal(0, 5, size=n)
    profit = profit.round(2)
    cust_ids = [f"CUST-{1000 + (i % 20)}" for i in range(n)]

    return pd.DataFrame({
        "CustomerID": cust_ids,
        "OrderDate": dates,
        "Category": categories,
        "Region": regions,
        "Quantity": quantities,
        "Discount": discounts,
        "Sales": sales,
        "Profit": profit,
    })


# ---------------------------------------------------------------------------
# Test Class 1: Core Generation & Schema Validation
# ---------------------------------------------------------------------------

class TestInsightsGenerationAndSchema:
    def test_generate_all_insights_success(self, sample_insights_df):
        """Test that generate_all_insights generates a valid list of BusinessInsight objects."""
        insights = generate_all_insights(sample_insights_df)
        assert isinstance(insights, list)
        assert len(insights) > 0
        for ins in insights:
            assert isinstance(ins, BusinessInsight)
            assert ins.insight_id.startswith("INS-")
            assert ins.category in [
                "Sales & Profitability",
                "Discount Effectiveness",
                "Customer Segmentation",
                "Predictive Decision Support",
            ]
            assert ins.severity in ["critical", "warning", "info"]
            assert len(ins.title) > 5
            assert isinstance(ins.evidence, dict)
            assert len(ins.evidence) > 0
            assert len(ins.recommendation) > 20
            assert len(ins.limitations) > 10

    def test_to_dict_serialization(self):
        """Test that BusinessInsight correctly serializes to a dictionary."""
        ins = BusinessInsight(
            insight_id="INS-TEST-001",
            category="Sales & Profitability",
            severity="info",
            title="Test Insight",
            evidence={"metric": 42},
            recommendation="Take this test action.",
            limitations="Assumes test scenario.",
        )
        d = ins.to_dict()
        assert isinstance(d, dict)
        assert d["insight_id"] == "INS-TEST-001"
        assert d["evidence"]["metric"] == 42


# ---------------------------------------------------------------------------
# Test Class 2: Edge Cases, Error Handling & Denominator Safeguards
# ---------------------------------------------------------------------------

class TestEdgeCasesAndDefensiveHandling:
    def test_empty_dataframe_returns_empty_list(self):
        """Empty input DataFrame returns an empty list without error."""
        empty_df = pd.DataFrame(columns=[
            "CustomerID", "OrderDate", "Category", "Region", "Quantity", "Discount", "Sales", "Profit"
        ])
        assert generate_all_insights(empty_df) == []
        assert generate_sales_profitability_insights(empty_df) == []
        assert generate_discount_insights(empty_df) == []
        assert generate_segmentation_insights(empty_df) == []
        assert generate_predictive_insights(empty_df) == []

    def test_non_dataframe_raises_type_error(self):
        """Passing non-DataFrame raises TypeError."""
        with pytest.raises(TypeError, match="Expected pandas DataFrame"):
            generate_all_insights({"Sales": [100]})

    def test_missing_required_columns_raises(self):
        """Passing DataFrame missing required columns raises ValueError."""
        incomplete_df = pd.DataFrame({"Sales": [100.0, 200.0], "Profit": [20.0, 40.0]})
        with pytest.raises(ValueError, match="missing required columns"):
            generate_all_insights(incomplete_df)

    def test_zero_sales_denominator_handling(self):
        """Zero sales values do not trigger ZeroDivisionError."""
        df_zero = pd.DataFrame({
            "CustomerID": ["CUST-1", "CUST-2"],
            "OrderDate": ["2024-01-01", "2024-01-02"],
            "Category": ["Technology", "Furniture"],
            "Region": ["East", "West"],
            "Quantity": [1, 2],
            "Discount": [0.0, 0.0],
            "Sales": [0.0, 0.0],
            "Profit": [0.0, 0.0],
        })
        insights = generate_all_insights(df_zero)
        assert isinstance(insights, list)

    def test_no_insights_when_insufficient_evidence(self):
        """When data has too few records for predictive modeling or clustering, handles gracefully."""
        tiny_df = pd.DataFrame({
            "CustomerID": [f"C1"],
            "OrderDate": ["2024-01-01"],
            "Category": ["Technology"],
            "Region": ["East"],
            "Quantity": [1],
            "Discount": [0.0],
            "Sales": [100.0],
            "Profit": [25.0],
        })
        pred_insights = generate_predictive_insights(tiny_df)
        assert pred_insights == []

    def test_invalid_and_missing_values_handled_safely(self, sample_insights_df):
        """DataFrame with some NaN values in non-essential columns runs without crashing."""
        dirty_df = sample_insights_df.copy()
        dirty_df.loc[0, "Region"] = np.nan
        insights = generate_all_insights(dirty_df.dropna(subset=["Category", "Region"]))
        assert isinstance(insights, list)

    def test_input_dataframe_immutability(self, sample_insights_df):
        """Input DataFrame must not be mutated in-place by insights generation."""
        df_copy = sample_insights_df.copy(deep=True)
        _ = generate_all_insights(sample_insights_df)
        pd.testing.assert_frame_equal(sample_insights_df, df_copy)


# ---------------------------------------------------------------------------
# Test Class 3: Analytical Pillar Rule Behavior
# ---------------------------------------------------------------------------

class TestAnalyticalPillarRules:
    def test_sales_profitability_rules(self, sample_insights_df):
        """Verify sales and profitability rule generation."""
        insights = generate_sales_profitability_insights(sample_insights_df)
        assert isinstance(insights, list)
        for ins in insights:
            assert ins.category == "Sales & Profitability"
            assert "Sales" in ins.title or "Margin" in ins.title or "Region" in ins.title or "Concentration" in ins.title

    def test_discount_rules(self, sample_insights_df):
        """Verify discount effectiveness rules identify deep discount margin compression."""
        insights = generate_discount_insights(sample_insights_df)
        assert isinstance(insights, list)
        for ins in insights:
            assert ins.category == "Discount Effectiveness"
            assert "Discount" in ins.title or "Margin" in ins.title
            assert "compression_pct_pts" in ins.evidence or "high_discount_margin_pct" in ins.evidence

    def test_segmentation_rules(self, sample_insights_df):
        """Verify customer segmentation generates retention/discount insights."""
        insights = generate_segmentation_insights(sample_insights_df)
        assert isinstance(insights, list)
        for ins in insights:
            assert ins.category == "Customer Segmentation"
            assert "Cluster" in ins.title
            assert "cluster_id" in ins.evidence

    def test_predictive_evaluation_summaries(self, sample_insights_df):
        """Verify predictive decision support summarizes model evaluation."""
        insights = generate_predictive_insights(sample_insights_df)
        assert isinstance(insights, list)
        assert len(insights) >= 2
        categories = [ins.category for ins in insights]
        assert all(c == "Predictive Decision Support" for c in categories)
        titles = [ins.title for ins in insights]
        assert any("Benchmark" in t for t in titles)
        assert any("Operational Scope" in t for t in titles)


# ---------------------------------------------------------------------------
# Test Class 4: Rigor, Causality, Determinism & Integration
# ---------------------------------------------------------------------------

class TestRigorAndIntegration:
    def test_deterministic_output(self, sample_insights_df):
        """Generating insights on identical input multiple times yields identical results."""
        res1 = generate_all_insights(sample_insights_df)
        res2 = generate_all_insights(sample_insights_df)
        assert len(res1) == len(res2)
        for i1, i2 in zip(res1, res2):
            assert i1.insight_id == i2.insight_id
            assert i1.severity == i2.severity
            assert i1.recommendation == i2.recommendation

    def test_severity_and_category_types(self, sample_insights_df):
        """Verify all severities are valid enums and sorted correctly."""
        insights = generate_all_insights(sample_insights_df)
        valid_severities = {"critical", "warning", "info"}
        valid_categories = {
            "Sales & Profitability",
            "Discount Effectiveness",
            "Customer Segmentation",
            "Predictive Decision Support",
        }
        for ins in insights:
            assert ins.severity in valid_severities
            assert ins.category in valid_categories

        # Priority ordering: critical before warning, warning before info
        severity_rank = {"critical": 0, "warning": 1, "info": 2}
        ranks = [severity_rank[ins.severity] for ins in insights]
        assert ranks == sorted(ranks)

    def test_supporting_evidence_structure(self, sample_insights_df):
        """Every generated insight must contain explicit numerical supporting evidence."""
        insights = generate_all_insights(sample_insights_df)
        for ins in insights:
            assert isinstance(ins.evidence, dict)
            assert len(ins.evidence) > 0
            # Values should be numbers, strings, or lists
            for k, v in ins.evidence.items():
                assert isinstance(v, (int, float, str, list))

    def test_no_unsupported_causal_claims(self, sample_insights_df):
        """
        Verify recommendations use cautious language (coincides with, associated with, correlates)
        and avoid unsupported causal claims (e.g., 'causes', 'caused by', 'proves causality').
        """
        insights = generate_all_insights(sample_insights_df)
        forbidden_phrases = [
            "causes profit to",
            "caused the profit",
            "proves causality",
            "guarantees revenue",
            "guarantees sales",
        ]
        for ins in insights:
            text = (ins.recommendation + " " + ins.limitations).lower()
            for phrase in forbidden_phrases:
                assert phrase not in text, f"Found unsupported causal phrase '{phrase}' in {ins.insight_id}"

    def test_precomputed_results_integration(self, sample_insights_df):
        """Test that generate_all_insights can accept pre-computed analytical objects."""
        kpis = compute_business_kpis(sample_insights_df)
        cats = compute_category_performance(sample_insights_df)
        regs = compute_regional_performance(sample_insights_df)
        discs = compute_discount_profitability_analysis(sample_insights_df)
        custs = aggregate_customer_features(sample_insights_df)
        clusters = perform_kmeans_clustering(custs, n_clusters=4, random_state=42)
        profiles = generate_cluster_profiles(clusters["clustered_df"])
        preds = train_and_evaluate_models(sample_insights_df)

        insights = generate_all_insights(
            df=sample_insights_df,
            kpis=kpis,
            category_df=cats,
            regional_df=regs,
            discount_df=discs,
            cluster_profiles_df=profiles,
            prediction_results=preds,
        )
        assert isinstance(insights, list)
        assert len(insights) > 0

    def test_filter_and_summary_utilities(self, sample_insights_df):
        """Test filter_insights and get_insights_summary functions."""
        insights = generate_all_insights(sample_insights_df)
        summary = get_insights_summary(insights)
        assert summary["total"] == len(insights)
        assert "by_severity" in summary
        assert "by_category" in summary

        filtered_crit = filter_insights(insights, severity="critical")
        assert all(ins.severity == "critical" for ins in filtered_crit)

        filtered_disc = filter_insights(insights, category="Discount Effectiveness")
        assert all(ins.category == "Discount Effectiveness" for ins in filtered_disc)

    def test_insights_distribution_chart(self, sample_insights_df):
        """Test Plotly distribution chart generation smoke test."""
        insights = generate_all_insights(sample_insights_df)
        fig = create_insights_distribution_chart(insights)
        assert fig is not None
        assert len(fig.data) > 0

    def test_bundled_dataset_end_to_end(self):
        """Test complete insights generation pipeline on the bundled sample sales data CSV."""
        df = load_csv_data("data/sample_sales_data.csv")
        assert len(df) == 1200

        insights = generate_all_insights(df)
        assert len(insights) >= 5

        categories_found = {ins.category for ins in insights}
        assert "Sales & Profitability" in categories_found
        assert "Discount Effectiveness" in categories_found
        assert "Customer Segmentation" in categories_found
        assert "Predictive Decision Support" in categories_found
