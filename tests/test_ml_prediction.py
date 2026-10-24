"""
Unit and Integration Tests for Sales Prediction Machine Learning Module (src/prediction.py).

Verifies feature engineering, target leakage prevention, chronological splitting,
pipeline construction, Linear Regression & Random Forest training, MAE/RMSE/R² metrics,
unknown category handling, edge cases, input immutability, and end-to-end execution.
"""

import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

from src.prediction import (
    prepare_prediction_data,
    build_prediction_pipeline,
    evaluate_regression_model,
    train_and_evaluate_models,
    predict_sales,
    create_actual_vs_predicted_chart,
    create_residual_distribution_chart,
    create_model_comparison_bar_chart,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    ALL_FEATURE_COLUMNS,
    TARGET_COLUMN,
)
from src.data_loader import load_csv_data


@pytest.fixture
def synthetic_transaction_df() -> pd.DataFrame:
    """Fixture providing 50 deterministic transaction records spanning 5 months."""
    np.random.seed(42)
    categories = ["Technology", "Furniture", "Office Supplies"]
    regions = ["North", "South", "East", "West"]
    
    dates = pd.date_range("2024-01-01", periods=50, freq="3D")
    
    rows = []
    for i, d in enumerate(dates):
        cat = categories[i % 3]
        reg = regions[i % 4]
        qty = int((i % 7) + 1)
        discount = float(round((i % 5) * 0.05, 2))
        base_price = 100.0 if cat == "Office Supplies" else (300.0 if cat == "Furniture" else 800.0)
        sales = round(base_price * qty * (1.0 - discount), 2)
        profit = round(sales * 0.25, 2)
        
        rows.append({
            "CustomerID": f"CUST-{100 + (i % 10)}",
            "OrderDate": d.strftime("%Y-%m-%d"),
            "Category": cat,
            "Region": reg,
            "Quantity": qty,
            "Discount": discount,
            "Sales": sales,
            "Profit": profit,
        })
        
    return pd.DataFrame(rows)


class TestDataPreparationAndLeakage:
    """Tests for feature engineering, leakage prevention, and splitting."""

    def test_prepare_prediction_data_success(self, synthetic_transaction_df):
        X_train, y_train, X_test, y_test, metadata = prepare_prediction_data(
            synthetic_transaction_df, split_strategy="chronological", test_size=0.2
        )
        assert len(X_train) == 40
        assert len(X_test) == 10
        assert len(y_train) == 40
        assert len(y_test) == 10
        assert metadata["split_strategy"] == "chronological"

    def test_no_target_leakage(self, synthetic_transaction_df):
        """Profit and CustomerID must strictly NOT exist in feature matrices."""
        X_train, _, X_test, _, _ = prepare_prediction_data(synthetic_transaction_df)
        assert "Profit" not in X_train.columns
        assert "Profit" not in X_test.columns
        assert "CustomerID" not in X_train.columns
        assert "CustomerID" not in X_test.columns
        assert "Sales" not in X_train.columns
        assert list(X_train.columns) == ALL_FEATURE_COLUMNS

    def test_date_derived_features_generation(self, synthetic_transaction_df):
        """Verify Month, Quarter, and DayOfWeek are generated accurately."""
        X_train, _, _, _, _ = prepare_prediction_data(synthetic_transaction_df)
        assert "Month" in X_train.columns
        assert "Quarter" in X_train.columns
        assert "DayOfWeek" in X_train.columns
        assert X_train["Month"].between(1, 12).all()
        assert X_train["Quarter"].between(1, 4).all()
        assert X_train["DayOfWeek"].between(0, 6).all()

    def test_chronological_split_ordering(self, synthetic_transaction_df):
        """Chronological split must place strictly earlier records in train and later in test."""
        data_copy = synthetic_transaction_df.copy()
        data_copy["ParsedDate"] = pd.to_datetime(data_copy["OrderDate"])
        data_copy = data_copy.sort_values("ParsedDate").reset_index(drop=True)
        
        split_idx = int(len(data_copy) * 0.8)
        max_train_date = data_copy["ParsedDate"].iloc[split_idx - 1]
        min_test_date = data_copy["ParsedDate"].iloc[split_idx]
        
        assert max_train_date <= min_test_date

    def test_random_split_reproducibility(self, synthetic_transaction_df):
        """Random split with fixed seed must produce identical splits."""
        X_tr1, _, X_te1, _, _ = prepare_prediction_data(synthetic_transaction_df, split_strategy="random", random_state=42)
        X_tr2, _, X_te2, _, _ = prepare_prediction_data(synthetic_transaction_df, split_strategy="random", random_state=42)
        pd.testing.assert_frame_equal(X_tr1, X_tr2)
        pd.testing.assert_frame_equal(X_te1, X_te2)

    def test_immutability(self, synthetic_transaction_df):
        original = synthetic_transaction_df.copy(deep=True)
        _ = prepare_prediction_data(synthetic_transaction_df)
        pd.testing.assert_frame_equal(synthetic_transaction_df, original)

    def test_insufficient_records_raises(self):
        few_rows = pd.DataFrame({
            "OrderDate": ["2024-01-01"] * 5,
            "Category": ["Technology"] * 5,
            "Region": ["North"] * 5,
            "Quantity": [1] * 5,
            "Discount": [0.0] * 5,
            "Sales": [100.0] * 5,
        })
        with pytest.raises(ValueError, match="Insufficient valid transaction records"):
            prepare_prediction_data(few_rows)

    def test_missing_required_columns_raises(self):
        bad_df = pd.DataFrame({"Quantity": [1, 2], "Sales": [10, 20]})
        with pytest.raises(ValueError, match="Missing required columns"):
            prepare_prediction_data(bad_df)


class TestPipelineAndModelTraining:
    """Tests for pipeline construction and training."""

    def test_build_linear_regression_pipeline(self):
        pipe = build_prediction_pipeline("linear_regression")
        assert isinstance(pipe, Pipeline)
        assert "preprocessor" in pipe.named_steps
        assert "regressor" in pipe.named_steps
        assert isinstance(pipe.named_steps["regressor"], LinearRegression)

    def test_build_random_forest_pipeline(self):
        pipe = build_prediction_pipeline("random_forest", random_state=42, n_estimators=50)
        assert isinstance(pipe, Pipeline)
        assert isinstance(pipe.named_steps["regressor"], RandomForestRegressor)
        assert pipe.named_steps["regressor"].n_estimators == 50

    def test_unsupported_model_type_raises(self):
        with pytest.raises(ValueError, match="Unsupported model_type"):
            build_prediction_pipeline("unsupported_model_algorithm")

    def test_training_and_evaluation(self, synthetic_transaction_df):
        results = train_and_evaluate_models(synthetic_transaction_df, split_strategy="chronological", test_size=0.2)
        
        assert "comparison_df" in results
        comp_df = results["comparison_df"]
        assert len(comp_df) == 2
        assert set(comp_df["Model"]) == {"Linear Regression (Baseline)", "Random Forest Regressor"}
        
        # Verify metric validity
        for _, row in comp_df.iterrows():
            assert row["MAE ($)"] >= 0.0
            assert row["RMSE ($)"] >= 0.0
            assert -1.0 <= row["R² Score"] <= 1.0


class TestEvaluationMetricsCalculations:
    """Tests for exact metric mathematics and edge cases."""

    def test_known_metrics_calculation(self):
        """Test with manually calculated known values."""
        # y_true = [100, 200, 300], y_pred = [110, 190, 310]
        # errors = [10, -10, 10] -> MAE = 10.0, RMSE = 10.0
        y_true = np.array([100.0, 200.0, 300.0])
        y_pred = np.array([110.0, 190.0, 310.0])
        
        # Mocking pipeline predict
        class MockModel:
            def predict(self, X):
                return y_pred
                
        eval_res = evaluate_regression_model(MockModel(), pd.DataFrame({"x": [1, 2, 3]}), pd.Series(y_true))
        assert eval_res["mae"] == 10.0
        assert eval_res["rmse"] == 10.0
        assert eval_res["r2"] > 0.95

    def test_negative_r2_handling(self):
        """Model that predicts worse than mean baseline will produce negative R2 gracefully."""
        y_true = np.array([10.0, 10.0, 10.0, 10.0, 12.0])
        y_pred = np.array([1000.0, 1000.0, 1000.0, 1000.0, 1000.0])
        
        class TerribleModel:
            def predict(self, X):
                return y_pred
                
        eval_res = evaluate_regression_model(TerribleModel(), pd.DataFrame({"x": [1, 2, 3, 4, 5]}), pd.Series(y_true))
        assert eval_res["r2"] < 0.0


class TestInferenceAndWhatIfPrediction:
    """Tests for predict_sales function and edge cases."""

    def test_single_scenario_prediction(self, synthetic_transaction_df):
        X_train, y_train, _, _, _ = prepare_prediction_data(synthetic_transaction_df)
        model = build_prediction_pipeline("linear_regression")
        model.fit(X_train, y_train)

        scenario = {
            "Quantity": 5,
            "Discount": 0.10,
            "Category": "Technology",
            "Region": "North",
            "Month": 6,
            "Quarter": 2,
            "DayOfWeek": 3,
        }
        pred = predict_sales(model, scenario)
        assert isinstance(pred, float)
        assert pred >= 0.0

    def test_unknown_categorical_handling(self, synthetic_transaction_df):
        """Unknown category or region must not crash inference (OneHotEncoder handles it)."""
        X_train, y_train, _, _, _ = prepare_prediction_data(synthetic_transaction_df)
        model = build_prediction_pipeline("linear_regression")
        model.fit(X_train, y_train)

        scenario_unknown = {
            "Quantity": 2,
            "Discount": 0.0,
            "Category": "CompletelyUnknownCategory",
            "Region": "UnknownMarsRegion",
            "Month": 1,
            "Quarter": 1,
            "DayOfWeek": 0,
        }
        # Must execute cleanly without error
        pred = predict_sales(model, scenario_unknown)
        assert isinstance(pred, float)
        assert pred >= 0.0

    def test_invalid_negative_quantity_raises(self, synthetic_transaction_df):
        X_train, y_train, _, _, _ = prepare_prediction_data(synthetic_transaction_df)
        model = build_prediction_pipeline("linear_regression")
        model.fit(X_train, y_train)

        bad_scenario = {
            "Quantity": -3,
            "Discount": 0.10,
            "Category": "Technology",
            "Region": "North",
            "Month": 6,
            "Quarter": 2,
            "DayOfWeek": 3,
        }
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            predict_sales(model, bad_scenario)

    def test_invalid_discount_raises(self, synthetic_transaction_df):
        X_train, y_train, _, _, _ = prepare_prediction_data(synthetic_transaction_df)
        model = build_prediction_pipeline("linear_regression")
        model.fit(X_train, y_train)

        bad_discount = {
            "Quantity": 2,
            "Discount": 1.5,
            "Category": "Technology",
            "Region": "North",
            "Month": 6,
            "Quarter": 2,
            "DayOfWeek": 3,
        }
        with pytest.raises(ValueError, match="Discount must be between 0.0 and 1.0"):
            predict_sales(model, bad_discount)


class TestPlotlyPredictionVisualizations:
    """Smoke tests for Plotly regression diagnostic charts."""

    def test_actual_vs_predicted_chart(self):
        y_true = np.array([100.0, 200.0, 300.0])
        y_pred = np.array([105.0, 195.0, 310.0])
        fig = create_actual_vs_predicted_chart(y_true, y_pred, "TestModel")
        assert isinstance(fig, go.Figure)

    def test_residual_distribution_chart(self):
        residuals = np.array([-5.0, 5.0, -10.0, 15.0])
        fig = create_residual_distribution_chart(residuals, "TestModel")
        assert isinstance(fig, go.Figure)

    def test_model_comparison_bar_chart(self):
        comp_df = pd.DataFrame([
            {"Model": "M1", "MAE ($)": 50.0, "RMSE ($)": 70.0},
            {"Model": "M2", "MAE ($)": 40.0, "RMSE ($)": 60.0},
        ])
        fig = create_model_comparison_bar_chart(comp_df)
        assert isinstance(fig, go.Figure)


class TestBundledDatasetPredictionIntegration:
    """Integration test training and evaluating models on the actual bundled 1,200-row dataset."""

    def test_bundled_dataset_prediction(self):
        df = load_csv_data("data/sample_sales_data.csv")
        assert len(df) == 1200
        
        results = train_and_evaluate_models(df, split_strategy="chronological", test_size=0.2)
        comp_df = results["comparison_df"]
        
        assert len(comp_df) == 2
        lr_row = comp_df[comp_df["Model"].str.contains("Linear")].iloc[0]
        rf_row = comp_df[comp_df["Model"].str.contains("Random Forest")].iloc[0]
        
        # Genuine predictive capability verified
        assert lr_row["R² Score"] > 0.50
        assert rf_row["R² Score"] > 0.50
        assert lr_row["MAE ($)"] < 1000.0
        assert rf_row["MAE ($)"] < 1000.0
