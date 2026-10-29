"""
Automated Test Suite for BizInsightIQ FastAPI REST API Layer.

Verifies health, dataset validation, exploratory data analysis, customer segmentation,
predictive modeling, and business decision support endpoints.
"""

import io
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


# Sample valid CSV string for isolated testing
SAMPLE_VALID_CSV = """CustomerID,OrderDate,Category,Region,Quantity,Discount,Sales,Profit
CUST-001,2024-01-15,Technology,East,4,0.05,500.0,120.0
CUST-001,2024-02-10,Furniture,East,2,0.10,300.0,-25.0
CUST-002,2024-01-20,Office Supplies,West,10,0.00,150.0,40.0
CUST-002,2024-03-05,Technology,West,1,0.20,800.0,160.0
CUST-003,2024-02-25,Technology,North,3,0.15,450.0,90.0
CUST-003,2024-03-12,Furniture,North,5,0.25,600.0,-50.0
"""

SAMPLE_INVALID_COLUMNS_CSV = """CustomerID,OrderDate,Category,Region,Quantity
CUST-001,2024-01-15,Technology,East,4
"""

SAMPLE_NEGATIVE_SALES_CSV = """CustomerID,OrderDate,Category,Region,Quantity,Discount,Sales,Profit
CUST-001,2024-01-15,Technology,East,4,0.05,-500.0,120.0
"""

SAMPLE_CORRUPT_DATES_CSV = """CustomerID,OrderDate,Category,Region,Quantity,Discount,Sales,Profit
CUST-001,invalid-date-token,Technology,East,4,0.05,500.0,120.0
"""


class TestHealthEndpoints:
    """Verifies service liveness and documentation root."""

    def test_health_check(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "UP"
        assert "BizInsightIQ" in data["service"]
        assert data["version"] == "1.0.0"

    def test_root_welcome(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "docs_url" in data
        assert data["docs_url"] == "/docs"


class TestDatasetValidationEndpoint:
    """Verifies POST /api/v1/datasets/validate endpoint."""

    def test_validate_valid_csv(self):
        file_bytes = io.BytesIO(SAMPLE_VALID_CSV.encode("utf-8"))
        response = client.post(
            "/api/v1/datasets/validate",
            files={"file": ("test_sales.csv", file_bytes, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["total_rows"] == 6
        assert len(data["errors"]) == 0

    def test_validate_missing_columns(self):
        file_bytes = io.BytesIO(SAMPLE_INVALID_COLUMNS_CSV.encode("utf-8"))
        response = client.post(
            "/api/v1/datasets/validate",
            files={"file": ("invalid.csv", file_bytes, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert len(data["missing_columns"]) > 0
        assert any("Missing required column" in err for err in data["errors"])

    def test_validate_negative_sales(self):
        file_bytes = io.BytesIO(SAMPLE_NEGATIVE_SALES_CSV.encode("utf-8"))
        response = client.post(
            "/api/v1/datasets/validate",
            files={"file": ("negative.csv", file_bytes, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert any("negative value" in err for err in data["errors"])

    def test_validate_corrupt_date(self):
        file_bytes = io.BytesIO(SAMPLE_CORRUPT_DATES_CSV.encode("utf-8"))
        response = client.post(
            "/api/v1/datasets/validate",
            files={"file": ("corrupt_dates.csv", file_bytes, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert any("OrderDate" in err for err in data["errors"])

    def test_validate_empty_file_rejected(self):
        file_bytes = io.BytesIO(b"")
        response = client.post(
            "/api/v1/datasets/validate",
            files={"file": ("empty.csv", file_bytes, "text/csv")},
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_validate_non_csv_extension_rejected(self):
        file_bytes = io.BytesIO(b"hello world")
        response = client.post(
            "/api/v1/datasets/validate",
            files={"file": ("data.txt", file_bytes, "text/plain")},
        )
        assert response.status_code == 400
        assert "csv" in response.json()["detail"].lower()


class TestAnalyticsEDAEndpoint:
    """Verifies POST /api/v1/analytics/eda endpoint."""

    def test_eda_default_dataset(self):
        response = client.post("/api/v1/analytics/eda")
        assert response.status_code == 200
        data = response.json()
        assert "kpis" in data
        assert data["kpis"]["total_sales"] > 0
        assert data["kpis"]["total_orders"] == 1200
        assert len(data["category_performance"]) > 0
        assert len(data["regional_performance"]) > 0
        assert len(data["trends"]) > 0
        assert "correlation_matrix" in data

    def test_eda_custom_uploaded_csv(self):
        file_bytes = io.BytesIO(SAMPLE_VALID_CSV.encode("utf-8"))
        response = client.post(
            "/api/v1/analytics/eda",
            files={"file": ("custom.csv", file_bytes, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["kpis"]["total_orders"] == 6
        assert data["kpis"]["unique_customers"] == 3

    def test_eda_invalid_csv_returns_400(self):
        file_bytes = io.BytesIO(SAMPLE_INVALID_COLUMNS_CSV.encode("utf-8"))
        response = client.post(
            "/api/v1/analytics/eda",
            files={"file": ("bad.csv", file_bytes, "text/csv")},
        )
        assert response.status_code == 400
        assert "validation failed" in response.json()["detail"]["message"].lower()


class TestCustomerSegmentationEndpoint:
    """Verifies POST /api/v1/segmentation endpoint."""

    def test_segmentation_default_bundled_dataset(self):
        response = client.post(
            "/api/v1/segmentation",
            data={"n_clusters": 4, "random_state": 42},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["n_clusters"] == 4
        assert 0.1 <= data["silhouette_score"] <= 1.0
        assert len(data["cluster_profiles"]) == 4
        assert len(data["pca_variance_ratio"]) == 2
        assert data["candidates_evaluation"] is not None
        assert data["customer_assignments"] is not None
        assert len(data["customer_assignments"]) > 0
        first_assign = data["customer_assignments"][0]
        assert "customer_id" in first_assign
        assert "cluster_id" in first_assign
        assert "recency" in first_assign
        assert "frequency" in first_assign
        assert "monetary_value" in first_assign
        assert "total_profit" in first_assign

    def test_segmentation_invalid_cluster_count(self):
        response = client.post(
            "/api/v1/segmentation",
            data={"n_clusters": 1},  # Must be >= 2
        )
        assert response.status_code == 422  # Pydantic validation error


class TestSalesPredictionEndpoint:
    """Verifies POST /api/v1/predictions/train and /predict endpoints."""

    def test_prediction_training_default_dataset(self):
        response = client.post(
            "/api/v1/predictions/train",
            data={"split_strategy": "chronological", "test_size": 0.2, "random_state": 42},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["comparison"]) == 3
        assert "linear_regression" in data["metrics"]
        assert "random_forest" in data["metrics"]
        assert "xgboost" in data["metrics"]
        assert data["metrics"]["random_forest"]["mae"] > 0
        assert data["metrics"]["random_forest"]["r2"] is not None
        assert data["metrics"]["xgboost"]["mae"] > 0
        assert data["metrics"]["xgboost"]["r2"] is not None

    def test_prediction_scenario_inference(self):
        payload = {
            "category": "Technology",
            "region": "East",
            "quantity": 5,
            "discount": 0.10,
            "month": 6,
            "quarter": 2,
            "day_of_week": 2,
        }
        response = client.post("/api/v1/predictions/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["predicted_sales"] > 0
        assert data["category"] == "Technology"
        assert data["quantity"] == 5

    def test_prediction_invalid_quantity_rejected(self):
        payload = {
            "category": "Technology",
            "region": "East",
            "quantity": -5,  # Invalid
            "discount": 0.10,
        }
        response = client.post("/api/v1/predictions/predict", json=payload)
        assert response.status_code == 422

    def test_prediction_invalid_discount_rejected(self):
        payload = {
            "category": "Technology",
            "region": "East",
            "quantity": 5,
            "discount": 1.5,  # Invalid (> 1.0)
        }
        response = client.post("/api/v1/predictions/predict", json=payload)
        assert response.status_code == 422

    def test_prediction_model_selection_linear_vs_random_forest(self):
        """Verifies prediction switching between Linear Regression, Random Forest, and XGBoost."""
        base_payload = {
            "category": "Technology",
            "region": "East",
            "quantity": 5,
            "discount": 0.10,
        }
        # Predict with Random Forest
        rf_res = client.post("/api/v1/predictions/predict", json={**base_payload, "model_type": "random_forest"})
        assert rf_res.status_code == 200
        rf_data = rf_res.json()
        assert "Random Forest" in rf_data["model_used"]
        assert rf_data["predicted_sales"] > 0

        # Predict with Linear Regression
        lr_res = client.post("/api/v1/predictions/predict", json={**base_payload, "model_type": "linear_regression"})
        assert lr_res.status_code == 200
        lr_data = lr_res.json()
        assert "Linear Regression" in lr_data["model_used"]
        assert lr_data["predicted_sales"] > 0

        # Predict with XGBoost
        xgb_res = client.post("/api/v1/predictions/predict", json={**base_payload, "model_type": "xgboost"})
        assert xgb_res.status_code == 200
        xgb_data = xgb_res.json()
        assert "XGBoost" in xgb_data["model_used"]
        assert xgb_data["predicted_sales"] > 0

    def test_prediction_custom_dataset_training_and_inference_isolation(self):
        """Verifies training registers custom dataset model and predict retrieves it."""
        import pathlib
        csv_path = pathlib.Path("data/test_sales_sample_valid.csv")
        assert csv_path.exists()
        
        dataset_id = "test_custom_ds_50"
        with open(csv_path, "rb") as f:
            train_res = client.post(
                "/api/v1/predictions/train",
                files={"file": ("test_sales.csv", f, "text/csv")},
                data={"dataset_id": dataset_id, "split_strategy": "chronological", "test_size": 0.2},
            )
        assert train_res.status_code == 200
        assert train_res.json()["dataset_id"] == dataset_id

        # Predict specifically using this dataset's trained model
        pred_res = client.post(
            "/api/v1/predictions/predict",
            json={
                "category": "Technology",
                "region": "East",
                "quantity": 5,
                "discount": 0.10,
                "dataset_id": dataset_id,
                "model_type": "random_forest",
            },
        )
        assert pred_res.status_code == 200
        pred_data = pred_res.json()
        assert pred_data["dataset_id"] == dataset_id
        assert pred_data["predicted_sales"] > 0

    def test_prediction_untrained_dataset_graceful_fallback(self):
        """Verifies querying an untrained dataset falls back gracefully to default benchmark."""
        pred_res = client.post(
            "/api/v1/predictions/predict",
            json={
                "category": "Technology",
                "region": "East",
                "quantity": 5,
                "discount": 0.10,
                "dataset_id": "nonexistent_ds_xyz",
            },
        )
        assert pred_res.status_code == 200
        pred_data = pred_res.json()
        assert "Fallback" in pred_data["model_used"]
        assert pred_data["predicted_sales"] > 0

    def test_prediction_explain_endpoint_random_forest(self):
        """Verifies SHAP explanation endpoint with Random Forest."""
        payload = {
            "category": "Technology",
            "region": "East",
            "quantity": 5,
            "discount": 0.10,
            "model_type": "random_forest",
        }
        res = client.post("/api/v1/predictions/explain", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["base_value"] > 0
        assert data["predicted_sales"] >= 0
        assert len(data["feature_contributions"]) == 7
        assert data["is_additive_exact"] is True
        assert any(fc["feature"] == "Category" for fc in data["feature_contributions"])

    def test_prediction_explain_endpoint_xgboost(self):
        """Verifies SHAP explanation endpoint with XGBoost."""
        payload = {
            "category": "Furniture",
            "region": "West",
            "quantity": 3,
            "discount": 0.20,
            "model_type": "xgboost",
        }
        res = client.post("/api/v1/predictions/explain", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert len(data["feature_contributions"]) == 7
        assert "XGBoost" in data["model_used"]

    def test_prediction_explain_endpoint_linear_regression(self):
        """Verifies SHAP explanation endpoint with Linear Regression."""
        payload = {
            "category": "Office Supplies",
            "region": "Central",
            "quantity": 10,
            "discount": 0.0,
            "model_type": "linear_regression",
        }
        res = client.post("/api/v1/predictions/explain", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert len(data["feature_contributions"]) == 7
        assert "Linear Regression" in data["model_used"]

    def test_prediction_explain_invalid_input_rejected(self):
        """Verifies invalid input triggers 422 Unprocessable Entity."""
        res = client.post("/api/v1/predictions/explain", json={"category": "Technology", "quantity": -1})
        assert res.status_code == 422

    def test_prediction_compare_endpoint_success(self):
        """Verifies POST /api/v1/predictions/compare with two valid scenarios."""
        payload = {
            "scenario_a": {
                "category": "Technology",
                "region": "East",
                "quantity": 5,
                "discount": 0.10,
            },
            "scenario_b": {
                "category": "Technology",
                "region": "East",
                "quantity": 5,
                "discount": 0.20,
            },
            "model_type": "random_forest",
        }
        res = client.post("/api/v1/predictions/compare", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["predicted_sales_a"] > 0
        assert data["predicted_sales_b"] > 0
        assert data["changed_features_count"] == 1
        assert "Random Forest" in data["model_used"]
        assert len(data["feature_comparisons"]) == 7

        # Check discount comparison
        discount_item = next(fc for fc in data["feature_comparisons"] if fc["feature"] == "Discount")
        assert discount_item["is_changed"] is True
        assert discount_item["scenario_a_value"] == "10%"
        assert discount_item["scenario_b_value"] == "20%"

    def test_prediction_compare_endpoint_xgboost_and_linear(self):
        """Verifies compare endpoint with XGBoost and Linear Regression."""
        base_payload = {
            "scenario_a": {
                "category": "Furniture",
                "region": "West",
                "quantity": 4,
                "discount": 0.05,
            },
            "scenario_b": {
                "category": "Furniture",
                "region": "West",
                "quantity": 8,
                "discount": 0.05,
            },
        }
        for m_type in ["xgboost", "linear_regression"]:
            res = client.post("/api/v1/predictions/compare", json={**base_payload, "model_type": m_type})
            assert res.status_code == 200
            data = res.json()
            assert data["success"] is True
            assert data["changed_features_count"] == 1

    def test_prediction_compare_invalid_input_rejected(self):
        """Verifies invalid scenario inputs return 422 Unprocessable Entity."""
        payload = {
            "scenario_a": {
                "category": "Technology",
                "region": "East",
                "quantity": 5,
                "discount": 0.10,
            },
            "scenario_b": {
                "category": "Technology",
                "region": "East",
                "quantity": 0,  # Invalid: quantity must be >= 1
                "discount": 0.20,
            },
        }
        res = client.post("/api/v1/predictions/compare", json=payload)
        assert res.status_code == 422



class TestBusinessInsightsEndpoint:
    """Verifies POST /api/v1/insights endpoint."""

    def test_insights_default_dataset(self):
        response = client.post("/api/v1/insights")
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["total_insights"] > 0
        assert len(data["insights"]) > 0
        # Verify structure of first insight
        first = data["insights"][0]
        assert "insight_id" in first
        assert "severity" in first
        assert "recommendation" in first
        assert "evidence" in first

    def test_insights_severity_filter(self):
        response = client.post(
            "/api/v1/insights",
            data={"severity": "CRITICAL"},
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["insights"]:
            assert item["severity"] == "critical"


class TestSecurityAndErrorHandling:
    """Verifies error responses do not leak sensitive internal server details."""

    def test_internal_error_sanitization(self):
        # Trigger validation failure on invalid custom file
        file_bytes = io.BytesIO(b"not,a,valid,csv\n1,2,3")
        response = client.post(
            "/api/v1/analytics/eda",
            files={"file": ("broken.csv", file_bytes, "text/csv")},
        )
        assert response.status_code == 400
        # Verify response is clean JSON without internal path disclosure
        detail = str(response.json())
        assert "C:\\" not in detail
        assert "D:\\" not in detail
