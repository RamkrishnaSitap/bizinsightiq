"""
Unit and Integration Tests for Customer Segmentation Engine (src/segmentation.py).

Verifies RFM aggregation, reference date reproducibility, feature preparation,
zero-variance handling, K-Means clustering, silhouette/elbow evaluation,
cluster profiling, and visualization smoke tests.
"""

import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler

from src.segmentation import (
    aggregate_customer_features,
    prepare_features_for_clustering,
    perform_kmeans_clustering,
    evaluate_cluster_candidates,
    generate_cluster_profiles,
    create_elbow_silhouette_chart,
    create_pca_cluster_chart,
    create_cluster_profile_bar_chart,
    DEFAULT_FEATURE_COLS,
)
from src.data_loader import load_csv_data


@pytest.fixture
def small_sales_df() -> pd.DataFrame:
    """Deterministic 6-row transaction dataset with 3 customers."""
    return pd.DataFrame({
        "CustomerID": ["CUST-1", "CUST-2", "CUST-1", "CUST-3", "CUST-2", "CUST-1"],
        "OrderDate": [
            "2024-01-10", "2024-01-15", "2024-02-01",
            "2024-02-10", "2024-02-20", "2024-03-01",
        ],
        "Category": ["Technology", "Furniture", "Technology", "Office Supplies", "Furniture", "Technology"],
        "Region": ["North", "South", "North", "West", "South", "North"],
        "Quantity": [2, 5, 3, 1, 4, 1],
        "Discount": [0.0, 0.10, 0.05, 0.0, 0.20, 0.0],
        "Sales": [200.0, 500.0, 300.0, 50.0, 400.0, 100.0],
        "Profit": [50.0, 100.0, 75.0, 15.0, 40.0, 25.0],
    })


@pytest.fixture
def multi_customer_df() -> pd.DataFrame:
    """Deterministic customer-level dataset with 10 customers suitable for k=2..4 clustering."""
    np.random.seed(42)
    return pd.DataFrame({
        "CustomerID": [f"CUST-{i}" for i in range(1, 11)],
        "Recency": [10, 15, 12, 120, 150, 140, 45, 50, 60, 55],
        "Frequency": [15, 14, 16, 2, 1, 2, 8, 7, 9, 8],
        "MonetaryValue": [5000.0, 4800.0, 5200.0, 300.0, 150.0, 280.0, 2100.0, 1900.0, 2300.0, 2050.0],
        "TotalProfit": [1500.0, 1400.0, 1600.0, 20.0, -10.0, 15.0, 450.0, 400.0, 500.0, 420.0],
        "AvgDiscount": [0.05, 0.05, 0.04, 0.25, 0.30, 0.20, 0.10, 0.10, 0.12, 0.08],
        "TotalQuantity": [50, 48, 55, 5, 2, 4, 25, 22, 28, 26],
        "AvgOrderValue": [333.33, 342.86, 325.0, 150.0, 150.0, 140.0, 262.5, 271.43, 255.56, 256.25],
        "ProfitMarginPct": [30.0, 29.17, 30.77, 6.67, -6.67, 5.36, 21.43, 21.05, 21.74, 20.49],
    })


class TestCustomerAggregation:
    """Tests for aggregate_customer_features."""

    def test_aggregation_calculations(self, small_sales_df):
        # Reference date set to 2024-03-02
        cust_df = aggregate_customer_features(small_sales_df, reference_date="2024-03-02")
        assert len(cust_df) == 3
        assert list(cust_df["CustomerID"]) == ["CUST-1", "CUST-2", "CUST-3"]

        # CUST-1: 3 rows, latest 2024-03-01 -> Recency = 1 day
        c1 = cust_df[cust_df["CustomerID"] == "CUST-1"].iloc[0]
        assert c1["Recency"] == 1
        assert c1["Frequency"] == 3
        assert c1["MonetaryValue"] == 600.0  # 200 + 300 + 100
        assert c1["TotalProfit"] == 150.0   # 50 + 75 + 25
        assert c1["TotalQuantity"] == 6     # 2 + 3 + 1
        assert c1["AvgOrderValue"] == 200.0 # 600 / 3
        assert c1["ProfitMarginPct"] == 25.0

        # CUST-2: 2 rows, latest 2024-02-20 -> Recency = 11 days
        c2 = cust_df[cust_df["CustomerID"] == "CUST-2"].iloc[0]
        assert c2["Recency"] == 11
        assert c2["Frequency"] == 2
        assert c2["MonetaryValue"] == 900.0 # 500 + 400

    def test_default_reference_date_deterministic(self, small_sales_df):
        # Max date in small_sales_df is 2024-03-01; default reference is 2024-03-02
        cust_df1 = aggregate_customer_features(small_sales_df)
        cust_df2 = aggregate_customer_features(small_sales_df)
        pd.testing.assert_frame_equal(cust_df1, cust_df2)
        assert cust_df1.loc[cust_df1["CustomerID"] == "CUST-1", "Recency"].iloc[0] == 1

    def test_immutability(self, small_sales_df):
        copy_df = small_sales_df.copy(deep=True)
        _ = aggregate_customer_features(small_sales_df)
        pd.testing.assert_frame_equal(small_sales_df, copy_df)

    def test_empty_input(self):
        empty = pd.DataFrame(columns=["CustomerID", "OrderDate", "Sales", "Profit", "Quantity", "Discount"])
        res = aggregate_customer_features(empty)
        assert res.empty
        assert "CustomerID" in res.columns
        assert "Recency" in res.columns

    def test_missing_columns_raises(self):
        bad_df = pd.DataFrame({"CustomerID": ["CUST-1"], "Sales": [100.0]})
        with pytest.raises(ValueError, match="Missing required columns"):
            aggregate_customer_features(bad_df)

    def test_invalid_dates_dropped_safely(self, small_sales_df):
        bad_dates = small_sales_df.copy()
        bad_dates.loc[0, "OrderDate"] = "unparseable-date-string"
        res = aggregate_customer_features(bad_dates)
        # Should still process remaining valid rows
        assert not res.empty


class TestFeaturePreparation:
    """Tests for prepare_features_for_clustering."""

    def test_scaling_output_dimensions(self, multi_customer_df):
        X_scaled, scaler, features = prepare_features_for_clustering(multi_customer_df)
        assert isinstance(scaler, StandardScaler)
        assert X_scaled.shape == (10, len(features))
        # Scaled features should have ~0 mean and ~1 std
        np.testing.assert_allclose(X_scaled.mean(axis=0), 0.0, atol=1e-7)
        np.testing.assert_allclose(X_scaled.std(axis=0), 1.0, atol=1e-7)

    def test_zero_variance_feature_dropped(self, multi_customer_df):
        df_zero_var = multi_customer_df.copy()
        df_zero_var["ZeroVarCol"] = 42.0
        X_scaled, _, features = prepare_features_for_clustering(
            df_zero_var, feature_cols=DEFAULT_FEATURE_COLS + ["ZeroVarCol"]
        )
        assert "ZeroVarCol" not in features
        assert X_scaled.shape[1] == len(DEFAULT_FEATURE_COLS)

    def test_insufficient_samples(self):
        single_row = pd.DataFrame({"CustomerID": ["CUST-1"], "Recency": [5], "Frequency": [1], "MonetaryValue": [100.0], "TotalProfit": [10.0], "AvgDiscount": [0.0], "TotalQuantity": [2]})
        with pytest.raises(ValueError, match="Insufficient customer observations"):
            prepare_features_for_clustering(single_row)

    def test_non_dataframe_raises(self):
        with pytest.raises(TypeError):
            prepare_features_for_clustering("not_a_df")


class TestKMeansClustering:
    """Tests for perform_kmeans_clustering."""

    def test_clustering_reproducibility(self, multi_customer_df):
        res1 = perform_kmeans_clustering(multi_customer_df, n_clusters=3, random_state=42)
        res2 = perform_kmeans_clustering(multi_customer_df, n_clusters=3, random_state=42)
        assert res1["inertia"] == res2["inertia"]
        assert res1["silhouette_score"] == res2["silhouette_score"]
        pd.testing.assert_series_equal(res1["clustered_df"]["Cluster"], res2["clustered_df"]["Cluster"])

    def test_invalid_n_clusters(self, multi_customer_df):
        with pytest.raises(ValueError, match="Cluster count must be >= 2"):
            perform_kmeans_clustering(multi_customer_df, n_clusters=1)

        with pytest.raises(ValueError, match="strictly less than customer count"):
            perform_kmeans_clustering(multi_customer_df, n_clusters=15)

    def test_pca_projection_output(self, multi_customer_df):
        res = perform_kmeans_clustering(multi_customer_df, n_clusters=3, random_state=42)
        pca_df = res["pca_df"]
        assert "PC1" in pca_df.columns
        assert "PC2" in pca_df.columns
        assert len(pca_df) == 10
        assert len(res["pca_variance_ratio"]) == 2
        assert sum(res["pca_variance_ratio"]) <= 100.0


class TestClusterDiagnosticsAndProfiling:
    """Tests for evaluation and profiling routines."""

    def test_evaluate_cluster_candidates(self, multi_customer_df):
        eval_df = evaluate_cluster_candidates(multi_customer_df, k_min=2, k_max=4, random_state=42)
        assert len(eval_df) == 3
        assert list(eval_df["k"]) == [2, 3, 4]
        assert "Inertia" in eval_df.columns
        assert "SilhouetteScore" in eval_df.columns
        # Inertia must decrease monotonically as k increases
        assert eval_df["Inertia"].is_monotonic_decreasing

    def test_generate_cluster_profiles(self, multi_customer_df):
        res = perform_kmeans_clustering(multi_customer_df, n_clusters=3, random_state=42)
        profile_df = generate_cluster_profiles(res["clustered_df"])
        assert len(profile_df) == 3
        assert profile_df["CustomerCount"].sum() == 10
        assert abs(profile_df["CustomerPct"].sum() - 100.0) < 0.5
        assert "DescriptivePersona" in profile_df.columns


class TestSegmentationVisualizations:
    """Smoke tests for Plotly visualization builders."""

    def test_chart_generation(self, multi_customer_df):
        eval_df = evaluate_cluster_candidates(multi_customer_df, k_min=2, k_max=4)
        res = perform_kmeans_clustering(multi_customer_df, n_clusters=3)
        profile_df = generate_cluster_profiles(res["clustered_df"])

        fig_diag = create_elbow_silhouette_chart(eval_df)
        fig_pca = create_pca_cluster_chart(res["pca_df"], res["pca_variance_ratio"])
        fig_bar = create_cluster_profile_bar_chart(profile_df)

        assert isinstance(fig_diag, go.Figure)
        assert isinstance(fig_pca, go.Figure)
        assert isinstance(fig_bar, go.Figure)


class TestBundledDatasetSegmentation:
    """Integration test verifying customer segmentation on the actual bundled 1,200-row CSV."""

    def test_bundled_data_segmentation(self):
        df = load_csv_data("data/sample_sales_data.csv")
        customer_df = aggregate_customer_features(df)
        assert len(customer_df) == 150

        # Cluster diagnostics from k=2 to k=6
        eval_df = evaluate_cluster_candidates(customer_df, k_min=2, k_max=6, random_state=42)
        assert len(eval_df) == 5

        # Fit model with k=4
        res = perform_kmeans_clustering(customer_df, n_clusters=4, random_state=42)
        assert res["n_clusters"] == 4
        assert res["silhouette_score"] is not None
        assert 0.2 < res["silhouette_score"] < 0.8

        profiles = generate_cluster_profiles(res["clustered_df"])
        assert len(profiles) == 4
        assert profiles["CustomerCount"].sum() == 150
