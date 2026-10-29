"""
Sales Prediction Router (Linear Regression vs. Random Forest).
Supports dataset-specific model registry, serialization, and model switching.
"""

from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from api.schemas import (
    PredictionTrainingResponse,
    RegressionMetrics,
    ScenarioPredictionRequest,
    ScenarioPredictionResponse,
    PredictionExplanationResponse,
    FeatureContributionItem,
    RawTransformedContributionItem,
    ScenarioComparisonRequest,
    ScenarioComparisonResponse,
    FeatureComparisonItem,
)
from api.deps import get_dataset_or_default, DEFAULT_SAMPLE_PATH
from src.validator import validate_dataset
from src.data_loader import load_csv_data
from src.prediction import (
    train_and_evaluate_models,
    predict_sales,
    explain_prediction,
    compare_scenarios_prediction,
    save_model,
    load_model,
)

router = APIRouter(prefix="/predictions", tags=["Sales Prediction"])

# Directory for serializing trained Scikit-learn pipelines
MODELS_DIR = Path("data/models")

# Thread-safe in-memory cache for registered models:
# Structure: { dataset_key: { "random_forest": Pipeline, "linear_regression": Pipeline } }
_MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register_trained_models(dataset_key: str, models: Dict[str, Any]) -> None:
    """Store trained models in-memory and serialize to data/models for persistence across restarts."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    _MODEL_REGISTRY[dataset_key] = models
    _MODEL_REGISTRY["latest"] = models

    for model_name, pipeline in models.items():
        try:
            safe_key = "".join(c for c in dataset_key if c.isalnum() or c in ("-", "_"))
            model_path = MODELS_DIR / f"{safe_key}_{model_name}.joblib"
            save_model(pipeline, model_path)
        except Exception:
            pass  # In-memory registry still serves even if disk write fails


def _get_model_display_name(mtype: str) -> str:
    if mtype == "linear_regression":
        return "Linear Regression"
    elif mtype == "xgboost":
        return "XGBoost Regressor"
    return "Random Forest Regressor"


def get_model_for_prediction(
    dataset_id: Optional[str] = None,
    model_type: Optional[str] = "random_forest",
) -> Tuple[Any, str, str]:
    """
    Retrieve fitted model for dataset and estimator type.
    Falls back gracefully to default benchmark model if custom model is not found.
    Returns: (model_pipeline, model_display_name, dataset_key_used)
    """
    model_type = (model_type or "random_forest").lower().strip()
    if model_type not in ("random_forest", "xgboost", "linear_regression"):
        model_type = "random_forest"

    target_key = dataset_id.strip() if dataset_id and dataset_id.strip() else "default"

    # 1. Check in-memory registry for target dataset
    if target_key in _MODEL_REGISTRY and model_type in _MODEL_REGISTRY[target_key]:
        model = _MODEL_REGISTRY[target_key][model_type]
        name = _get_model_display_name(model_type)
        return model, name, target_key

    # 2. Check disk for saved model matching target dataset
    safe_key = "".join(c for c in target_key if c.isalnum() or c in ("-", "_"))
    model_path = MODELS_DIR / f"{safe_key}_{model_type}.joblib"
    if model_path.exists():
        try:
            model = load_model(model_path)
            if target_key not in _MODEL_REGISTRY:
                _MODEL_REGISTRY[target_key] = {}
            _MODEL_REGISTRY[target_key][model_type] = model
            name = _get_model_display_name(model_type)
            return model, name, target_key
        except Exception:
            pass

    # 3. Check in-memory registry for default dataset
    default_key = "default"
    if default_key in _MODEL_REGISTRY and model_type in _MODEL_REGISTRY[default_key]:
        model = _MODEL_REGISTRY[default_key][model_type]
        name = _get_model_display_name(model_type)
        if target_key not in ("default", "33333333-3333-3333-3333-333333333333"):
            name += " (Fallback)"
        return model, name, "default"

    # 4. Check disk for default dataset model
    default_path = MODELS_DIR / f"default_{model_type}.joblib"
    if default_path.exists():
        try:
            model = load_model(default_path)
            if "default" not in _MODEL_REGISTRY:
                _MODEL_REGISTRY["default"] = {}
            _MODEL_REGISTRY["default"][model_type] = model
            name = _get_model_display_name(model_type)
            return model, name, "default"
        except Exception:
            pass

    # 5. Lazily train on bundled sample dataset
    if not DEFAULT_SAMPLE_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default sample dataset not found for model inference.",
        )
    df = load_csv_data(DEFAULT_SAMPLE_PATH)
    training_res = train_and_evaluate_models(df, split_strategy="chronological", test_size=0.2, random_state=42)
    register_trained_models("default", training_res["models"])
    register_trained_models("33333333-3333-3333-3333-333333333333", training_res["models"])

    model = _MODEL_REGISTRY["default"][model_type]
    name = _get_model_display_name(model_type)
    return model, name, "default"


@router.post("/train", response_model=PredictionTrainingResponse, summary="Train & Benchmark Regression Models")
async def train_models_endpoint(
    file: Optional[UploadFile] = File(None),
    dataset_id: Optional[str] = Form(default=None),
    split_strategy: str = Form(default="chronological"),
    test_size: float = Form(default=0.2, ge=0.05, le=0.5),
    random_state: int = Form(default=42),
) -> PredictionTrainingResponse:
    """
    Trains and compares Linear Regression (baseline), Random Forest Regressor, and XGBoost Regressor
    using chronological or random splitting. Reports MAE, RMSE, R² scores, and training durations.
    Registers trained models under the specified dataset_id for subsequent inference.
    Strictly excludes 'Profit' to prevent target leakage.
    """
    df = await get_dataset_or_default(file)
    validation = validate_dataset(df)
    if not validation.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Dataset validation failed.", "errors": validation.errors},
        )

    try:
        results = train_and_evaluate_models(
            df=df,
            split_strategy=split_strategy,
            test_size=test_size,
            random_state=random_state,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model training failed: {str(exc)}",
        )

    # Register trained models for inference
    key = dataset_id.strip() if dataset_id and dataset_id.strip() else ("custom" if file and file.filename else "default")
    register_trained_models(key, results["models"])
    if key == "default":
        register_trained_models("33333333-3333-3333-3333-333333333333", results["models"])

    eval_lr = results["evaluations"]["linear_regression"]
    eval_rf = results["evaluations"]["random_forest"]
    eval_xgb = results["evaluations"]["xgboost"]

    used_split_strategy = results["metadata"].get("split_strategy", split_strategy)
    metrics = {
        "linear_regression": RegressionMetrics(
            mae=float(eval_lr["mae"]),
            rmse=float(eval_lr["rmse"]),
            r2=float(eval_lr["r2"]),
            test_size=int(eval_lr["test_size"]),
            split_strategy=used_split_strategy,
            training_time=float(eval_lr.get("training_time", 0.0)),
        ),
        "random_forest": RegressionMetrics(
            mae=float(eval_rf["mae"]),
            rmse=float(eval_rf["rmse"]),
            r2=float(eval_rf["r2"]),
            test_size=int(eval_rf["test_size"]),
            split_strategy=used_split_strategy,
            training_time=float(eval_rf.get("training_time", 0.0)),
        ),
        "xgboost": RegressionMetrics(
            mae=float(eval_xgb["mae"]),
            rmse=float(eval_xgb["rmse"]),
            r2=float(eval_xgb["r2"]),
            test_size=int(eval_xgb["test_size"]),
            split_strategy=used_split_strategy,
            training_time=float(eval_xgb.get("training_time", 0.0)),
        ),
    }

    return PredictionTrainingResponse(
        comparison=results["comparison_df"].to_dict(orient="records"),
        metrics=metrics,
        metadata={
            "total_records": results["metadata"].get("total_records", 0),
            "train_size": results["metadata"].get("train_size", 0),
            "test_size": results["metadata"].get("test_size", 0),
            "split_strategy": results["metadata"].get("split_strategy", split_strategy),
            "train_period": results["metadata"].get("train_period", ""),
            "test_period": results["metadata"].get("test_period", ""),
            "numeric_features": results["metadata"].get("numeric_features", []),
            "categorical_features": results["metadata"].get("categorical_features", []),
        },
        dataset_id=key,
    )


@router.post("/predict", response_model=ScenarioPredictionResponse, summary="Predict Sales for a Transaction Scenario")
def predict_scenario_endpoint(payload: ScenarioPredictionRequest) -> ScenarioPredictionResponse:
    """
    Simulates a 'What-If' custom order scenario using the trained model.
    Predicts expected gross sales given category, region, quantity, discount rate,
    selected model architecture (Random Forest or Linear Regression), and dataset context.
    """
    model, model_display_name, dataset_key_used = get_model_for_prediction(
        dataset_id=payload.dataset_id,
        model_type=payload.model_type,
    )

    month = payload.month if payload.month is not None else 6
    quarter = payload.quarter if payload.quarter is not None else ((month - 1) // 3 + 1)
    day_of_week = payload.day_of_week if payload.day_of_week is not None else 2

    input_data = {
        "Category": payload.category,
        "Region": payload.region,
        "Quantity": payload.quantity,
        "Discount": payload.discount,
        "Month": month,
        "Quarter": quarter,
        "DayOfWeek": day_of_week,
    }

    try:
        predicted_sales = predict_sales(model, input_data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prediction failed: {str(exc)}",
        )

    return ScenarioPredictionResponse(
        predicted_sales=round(float(predicted_sales), 2),
        category=payload.category,
        region=payload.region,
        quantity=payload.quantity,
        discount=payload.discount,
        month=month,
        quarter=quarter,
        day_of_week=day_of_week,
        model_used=model_display_name,
        dataset_id=dataset_key_used,
    )


@router.post("/explain", response_model=PredictionExplanationResponse, summary="Explain Sales Prediction using SHAP Feature Attributions")
def explain_scenario_endpoint(payload: ScenarioPredictionRequest) -> PredictionExplanationResponse:
    """
    Computes exact SHAP (SHapley Additive exPlanations) values for a transaction quote scenario.
    Deconstructs the predicted sales into baseline expectation E[f(x)] and feature-level attributions.
    Supports Random Forest Regressor, XGBoost Regressor, and Linear Regression.
    """
    model, model_display_name, dataset_key_used = get_model_for_prediction(
        dataset_id=payload.dataset_id,
        model_type=payload.model_type,
    )

    month = payload.month if payload.month is not None else 6
    quarter = payload.quarter if payload.quarter is not None else ((month - 1) // 3 + 1)
    day_of_week = payload.day_of_week if payload.day_of_week is not None else 2

    input_data = {
        "Category": payload.category,
        "Region": payload.region,
        "Quantity": payload.quantity,
        "Discount": payload.discount,
        "Month": month,
        "Quarter": quarter,
        "DayOfWeek": day_of_week,
    }

    try:
        explanation = explain_prediction(model, input_data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SHAP explanation failed: {str(exc)}",
        )

    return PredictionExplanationResponse(
        predicted_sales=explanation["predicted_sales"],
        base_value=explanation["base_value"],
        model_used=model_display_name,
        dataset_id=dataset_key_used,
        success=explanation["success"],
        feature_contributions=[FeatureContributionItem(**item) for item in explanation["feature_contributions"]],
        raw_transformed_contributions=[RawTransformedContributionItem(**item) for item in explanation.get("raw_transformed_contributions", [])],
        additive_sum=explanation["additive_sum"],
        is_additive_exact=explanation["is_additive_exact"],
        explainer_type=explanation["explainer_type"],
    )


@router.post("/compare", response_model=ScenarioComparisonResponse, summary="Compare Two What-If Quote Scenarios Side by Side with SHAP")
def compare_scenarios_endpoint(payload: ScenarioComparisonRequest) -> ScenarioComparisonResponse:
    """
    Compares two transaction quote scenarios (Scenario A vs. Scenario B) using the same fitted model and SHAP explainer.
    Returns predicted sales amounts, absolute difference, percentage difference, and feature-by-feature SHAP shifts.
    Ensures identical model version, preprocessing bounds, and tenant isolation without retraining.
    """
    model, model_display_name, dataset_key_used = get_model_for_prediction(
        dataset_id=payload.dataset_id,
        model_type=payload.model_type,
    )

    def _build_input(item) -> Dict[str, Any]:
        month = item.month if item.month is not None else 6
        quarter = item.quarter if item.quarter is not None else ((month - 1) // 3 + 1)
        day_of_week = item.day_of_week if item.day_of_week is not None else 2
        return {
            "Category": item.category,
            "Region": item.region,
            "Quantity": item.quantity,
            "Discount": item.discount,
            "Month": month,
            "Quarter": quarter,
            "DayOfWeek": day_of_week,
        }

    input_a = _build_input(payload.scenario_a)
    input_b = _build_input(payload.scenario_b)

    try:
        comparison = compare_scenarios_prediction(model, input_a, input_b)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scenario comparison failed: {str(exc)}",
        )

    exp_a = comparison["scenario_a"]
    exp_b = comparison["scenario_b"]

    resp_a = PredictionExplanationResponse(
        predicted_sales=exp_a["predicted_sales"],
        base_value=exp_a["base_value"],
        model_used=model_display_name,
        dataset_id=dataset_key_used,
        success=exp_a["success"],
        feature_contributions=[FeatureContributionItem(**item) for item in exp_a["feature_contributions"]],
        raw_transformed_contributions=[RawTransformedContributionItem(**item) for item in exp_a.get("raw_transformed_contributions", [])],
        additive_sum=exp_a["additive_sum"],
        is_additive_exact=exp_a["is_additive_exact"],
        explainer_type=exp_a["explainer_type"],
    )

    resp_b = PredictionExplanationResponse(
        predicted_sales=exp_b["predicted_sales"],
        base_value=exp_b["base_value"],
        model_used=model_display_name,
        dataset_id=dataset_key_used,
        success=exp_b["success"],
        feature_contributions=[FeatureContributionItem(**item) for item in exp_b["feature_contributions"]],
        raw_transformed_contributions=[RawTransformedContributionItem(**item) for item in exp_b.get("raw_transformed_contributions", [])],
        additive_sum=exp_b["additive_sum"],
        is_additive_exact=exp_b["is_additive_exact"],
        explainer_type=exp_b["explainer_type"],
    )

    return ScenarioComparisonResponse(
        scenario_a=resp_a,
        scenario_b=resp_b,
        predicted_sales_a=comparison["predicted_sales_a"],
        predicted_sales_b=comparison["predicted_sales_b"],
        absolute_difference=comparison["absolute_difference"],
        percentage_difference=comparison["percentage_difference"],
        changed_features_count=comparison["changed_features_count"],
        feature_comparisons=[FeatureComparisonItem(**item) for item in comparison["feature_comparisons"]],
        is_difference_additive_exact=comparison["is_difference_additive_exact"],
        explainer_type=comparison["explainer_type"],
        base_value=comparison["base_value"],
        model_used=model_display_name,
        dataset_id=dataset_key_used,
        success=True,
        disclaimer=comparison["disclaimer"],
    )

