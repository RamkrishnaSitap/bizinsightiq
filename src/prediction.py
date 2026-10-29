"""
Supervised Machine Learning Sales Prediction Module for BizInsightIQ.

Provides framework-agnostic data preprocessing, pipeline construction,
Linear Regression and Random Forest training, regression evaluation metrics,
what-if scenario inference, and Plotly diagnostic visualizations.
"""

import time
from pathlib import Path
from typing import Dict, Any, List, Tuple, Union, Optional
import pandas as pd
import numpy as np
import joblib
import shap
from xgboost import XGBRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import plotly.express as px
import plotly.graph_objects as go


NUMERIC_FEATURES = ["Quantity", "Discount", "Month", "Quarter", "DayOfWeek"]
CATEGORICAL_FEATURES = ["Category", "Region"]
ALL_FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN = "Sales"


def _validate_raw_prediction_columns(df: pd.DataFrame) -> None:
    """Ensure required raw columns exist in input DataFrame."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
    required = ["OrderDate", "Category", "Region", "Quantity", "Discount", "Sales"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for sales prediction: {', '.join(missing)}")


# ---------------------------------------------------------------------------
# 1. Feature Engineering & Chronological Train/Test Splitting
# ---------------------------------------------------------------------------

def prepare_prediction_data(
    df: pd.DataFrame,
    split_strategy: str = "chronological",
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, Dict[str, Any]]:
    """
    Prepare transaction features and split into training and evaluation sets.

    Engineering notes:
    - Derives calendar temporal features: Month, Quarter, DayOfWeek from OrderDate.
    - Explicitly excludes 'Profit' to eliminate target leakage.
    - Explicitly excludes 'CustomerID' to prevent arbitrary identifier bias.
    - Preserves input immutability via deep copy.

    Parameters
    ----------
    df : pd.DataFrame
        Sales dataset.
    split_strategy : str, default "chronological"
        'chronological' for time-ordered split or 'random' for standard shuffle split.
    test_size : float, default 0.2
        Fraction of data reserved for test set. Must be between 0.05 and 0.5.
    random_state : int, default 42
        Seed used if random split is selected.

    Returns
    -------
    Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, Dict[str, Any]]
        X_train, y_train, X_test, y_test, metadata
    """
    _validate_raw_prediction_columns(df)

    if not (0.05 <= test_size <= 0.5):
        raise ValueError(f"test_size must be between 0.05 and 0.5. Received: {test_size}")

    data = df.copy()

    # Parse dates safely
    data["ParsedDate"] = pd.to_datetime(data["OrderDate"], errors="coerce", format="mixed")
    data = data.dropna(subset=["ParsedDate", "Quantity", "Discount", "Sales", "Category", "Region"])

    if len(data) < 20:
        raise ValueError(f"Insufficient valid transaction records ({len(data)}) for regression modeling. Minimum 20 required.")

    # Sort chronologically by date
    data = data.sort_values("ParsedDate").reset_index(drop=True)

    # Derive calendar temporal features
    data["Month"] = data["ParsedDate"].dt.month.astype(int)
    data["Quarter"] = data["ParsedDate"].dt.quarter.astype(int)
    data["DayOfWeek"] = data["ParsedDate"].dt.day_of_week.astype(int)

    # Feature matrix X and Target vector y (Profit is strictly omitted)
    X = data[ALL_FEATURE_COLUMNS].copy()
    y = data[TARGET_COLUMN].copy()

    # Perform split
    n_total = len(data)
    if split_strategy == "chronological":
        split_idx = int(n_total * (1.0 - test_size))
        X_train = X.iloc[:split_idx].reset_index(drop=True)
        y_train = y.iloc[:split_idx].reset_index(drop=True)
        X_test = X.iloc[split_idx:].reset_index(drop=True)
        y_test = y.iloc[split_idx:].reset_index(drop=True)
        test_start_date = str(data["ParsedDate"].iloc[split_idx].date())
        test_end_date = str(data["ParsedDate"].iloc[-1].date())
        train_start_date = str(data["ParsedDate"].iloc[0].date())
        train_end_date = str(data["ParsedDate"].iloc[split_idx - 1].date())
    elif split_strategy == "random":
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, shuffle=True
        )
        X_train = X_train.reset_index(drop=True)
        y_train = y_train.reset_index(drop=True)
        X_test = X_test.reset_index(drop=True)
        y_test = y_test.reset_index(drop=True)
        train_start_date = str(data["ParsedDate"].min().date())
        train_end_date = str(data["ParsedDate"].max().date())
        test_start_date = train_start_date
        test_end_date = train_end_date
    else:
        raise ValueError(f"Unknown split_strategy: {split_strategy}. Choose 'chronological' or 'random'.")

    metadata = {
        "total_records": n_total,
        "train_size": len(X_train),
        "test_size": len(X_test),
        "split_strategy": split_strategy,
        "train_period": f"{train_start_date} to {train_end_date}",
        "test_period": f"{test_start_date} to {test_end_date}",
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
    }

    return X_train, y_train, X_test, y_test, metadata


# ---------------------------------------------------------------------------
# 2. Pipeline Construction (Preprocessing + Estimator)
# ---------------------------------------------------------------------------

def build_prediction_pipeline(
    model_type: str = "linear_regression",
    random_state: int = 42,
    **kwargs,
) -> Pipeline:
    """
    Construct a Scikit-learn Pipeline encapsulating preprocessing and model.

    Preprocessing:
    - Numeric features: StandardScaler()
    - Categorical features: OneHotEncoder(handle_unknown='ignore', sparse_output=False)

    Parameters
    ----------
    model_type : str
        'linear_regression' or 'random_forest'
    random_state : int, default 42
        Seed for stochastic models.
    **kwargs
        Hyperparameters passed directly to estimator.

    Returns
    -------
    Pipeline
        Unfitted Scikit-learn Pipeline.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
        ]
    )

    if model_type == "linear_regression":
        estimator = LinearRegression(**kwargs)
    elif model_type == "random_forest":
        default_rf_params = {
            "n_estimators": 100,
            "max_depth": 10,
            "random_state": random_state,
            "n_jobs": -1,
        }
        default_rf_params.update(kwargs)
        estimator = RandomForestRegressor(**default_rf_params)
    elif model_type == "xgboost":
        default_xgb_params = {
            "n_estimators": 100,
            "max_depth": 6,
            "learning_rate": 0.1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": random_state,
            "n_jobs": -1,
            "objective": "reg:squarederror",
        }
        default_xgb_params.update(kwargs)
        estimator = XGBRegressor(**default_xgb_params)
    else:
        raise ValueError(f"Unsupported model_type: '{model_type}'. Choose 'linear_regression', 'random_forest', or 'xgboost'.")

    return Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", estimator),
    ])


# ---------------------------------------------------------------------------
# 3. Model Evaluation & Comparison
# ---------------------------------------------------------------------------

def evaluate_regression_model(
    model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> Dict[str, Any]:
    """
    Evaluate trained regression pipeline on test dataset.

    Calculates:
    - Mean Absolute Error (MAE)
    - Root Mean Squared Error (RMSE)
    - Coefficient of Determination (R²)

    Parameters
    ----------
    model : Pipeline
        Fitted Scikit-learn regression pipeline.
    X_test : pd.DataFrame
        Test features.
    y_test : pd.Series
        Ground-truth test target.

    Returns
    -------
    Dict[str, Any]
        Dictionary of evaluation metrics and residuals.
    """
    if len(X_test) == 0:
        raise ValueError("Cannot evaluate model on empty test dataset.")

    y_pred = model.predict(X_test)
    y_true = np.asarray(y_test)

    # Clamping negative sales predictions at 0
    y_pred = np.maximum(y_pred, 0.0)

    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(root_mean_squared_error(y_true, y_pred))

    # Calculate R2 (handle edge cases like constant target)
    if np.var(y_true) == 0.0:
        r2 = 0.0
    else:
        r2 = float(r2_score(y_true, y_pred))

    residuals = y_true - y_pred

    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2": round(r2, 4),
        "test_size": len(y_test),
        "y_true": y_true,
        "y_pred": y_pred,
        "residuals": residuals,
    }


def train_and_evaluate_models(
    df: pd.DataFrame,
    split_strategy: str = "chronological",
    test_size: float = 0.2,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Train and evaluate both Linear Regression and Random Forest models on identical data splits.

    Parameters
    ----------
    df : pd.DataFrame
        Raw sales transactions.
    split_strategy : str, default 'chronological'
        Data split method.
    test_size : float, default 0.2
        Test set fraction.
    random_state : int, default 42
        Random seed.

    Returns
    -------
    Dict[str, Any]
        Comprehensive dictionary containing comparison table, trained models,
        evaluation dictionaries, and split metadata.
    """
    X_train, y_train, X_test, y_test, metadata = prepare_prediction_data(
        df, split_strategy=split_strategy, test_size=test_size, random_state=random_state
    )

    # 1. Train Linear Regression
    t0_lr = time.perf_counter()
    pipe_lr = build_prediction_pipeline("linear_regression")
    pipe_lr.fit(X_train, y_train)
    eval_lr = evaluate_regression_model(pipe_lr, X_test, y_test)
    eval_lr["training_time"] = round(time.perf_counter() - t0_lr, 4)

    # 2. Train Random Forest Regressor
    t0_rf = time.perf_counter()
    pipe_rf = build_prediction_pipeline("random_forest", random_state=random_state)
    pipe_rf.fit(X_train, y_train)
    eval_rf = evaluate_regression_model(pipe_rf, X_test, y_test)
    eval_rf["training_time"] = round(time.perf_counter() - t0_rf, 4)

    # 3. Train XGBoost Regressor
    t0_xgb = time.perf_counter()
    pipe_xgb = build_prediction_pipeline("xgboost", random_state=random_state)
    pipe_xgb.fit(X_train, y_train)
    eval_xgb = evaluate_regression_model(pipe_xgb, X_test, y_test)
    eval_xgb["training_time"] = round(time.perf_counter() - t0_xgb, 4)

    # Construct model comparison DataFrame
    comparison_df = pd.DataFrame([
        {
            "Model": "Linear Regression (Baseline)",
            "MAE ($)": eval_lr["mae"],
            "RMSE ($)": eval_lr["rmse"],
            "R² Score": eval_lr["r2"],
            "Training Time (s)": eval_lr["training_time"],
            "Test Samples": eval_lr["test_size"],
            "model": "Linear Regression (Baseline)",
            "mae": eval_lr["mae"],
            "rmse": eval_lr["rmse"],
            "r2": eval_lr["r2"],
            "training_time": eval_lr["training_time"],
            "test_size": eval_lr["test_size"],
        },
        {
            "Model": "Random Forest Regressor",
            "MAE ($)": eval_rf["mae"],
            "RMSE ($)": eval_rf["rmse"],
            "R² Score": eval_rf["r2"],
            "Training Time (s)": eval_rf["training_time"],
            "Test Samples": eval_rf["test_size"],
            "model": "Random Forest Regressor",
            "mae": eval_rf["mae"],
            "rmse": eval_rf["rmse"],
            "r2": eval_rf["r2"],
            "training_time": eval_rf["training_time"],
            "test_size": eval_rf["test_size"],
        },
        {
            "Model": "XGBoost Regressor",
            "MAE ($)": eval_xgb["mae"],
            "RMSE ($)": eval_xgb["rmse"],
            "R² Score": eval_xgb["r2"],
            "Training Time (s)": eval_xgb["training_time"],
            "Test Samples": eval_xgb["test_size"],
            "model": "XGBoost Regressor",
            "mae": eval_xgb["mae"],
            "rmse": eval_xgb["rmse"],
            "r2": eval_xgb["r2"],
            "training_time": eval_xgb["training_time"],
            "test_size": eval_xgb["test_size"],
        },
    ])

    return {
        "comparison_df": comparison_df,
        "models": {
            "linear_regression": pipe_lr,
            "random_forest": pipe_rf,
            "xgboost": pipe_xgb,
        },
        "evaluations": {
            "linear_regression": eval_lr,
            "random_forest": eval_rf,
            "xgboost": eval_xgb,
        },
        "metadata": metadata,
    }


# ---------------------------------------------------------------------------
# 4. What-If Scenario Prediction
# ---------------------------------------------------------------------------

def predict_sales(
    model: Pipeline,
    input_data: Union[Dict[str, Any], pd.DataFrame],
) -> Union[float, np.ndarray]:
    """
    Generate Sales prediction for a user-specified transaction scenario.

    Parameters
    ----------
    model : Pipeline
        Fitted Scikit-learn regression pipeline.
    input_data : Union[Dict[str, Any], pd.DataFrame]
        Input containing Quantity, Discount, Category, Region, Month, Quarter, DayOfWeek.

    Returns
    -------
    Union[float, np.ndarray]
        Predicted sales amount (in currency units, clamped >= 0).
    """
    if isinstance(input_data, dict):
        single_input = True
        input_df = pd.DataFrame([input_data])
    elif isinstance(input_data, pd.DataFrame):
        single_input = False
        input_df = input_data.copy()
    else:
        raise TypeError(f"input_data must be dict or DataFrame, received {type(input_data).__name__}")

    # Validate required features
    missing = [c for c in ALL_FEATURE_COLUMNS if c not in input_df.columns]
    if missing:
        raise ValueError(f"Input data missing required features: {', '.join(missing)}")

    # Verify non-negative quantity and valid discount range
    if (input_df["Quantity"] < 0).any():
        raise ValueError("Quantity cannot be negative.")
    if ((input_df["Discount"] < 0.0) | (input_df["Discount"] > 1.0)).any():
        raise ValueError("Discount must be between 0.0 and 1.0.")

    predictions = model.predict(input_df[ALL_FEATURE_COLUMNS])
    # Clamp negative estimates to 0
    predictions = np.maximum(predictions, 0.0).round(2)

    return float(predictions[0]) if single_input else predictions


def save_model(model: Pipeline, filepath: Union[str, Path]) -> str:
    """
    Serialize a trained Scikit-learn regression pipeline to disk using joblib.

    Parameters
    ----------
    model : Pipeline
        Fitted Scikit-learn regression pipeline.
    filepath : Union[str, Path]
        Target destination path for .joblib file.

    Returns
    -------
    str
        Absolute file path where the model was persisted.
    """
    if not isinstance(model, Pipeline):
        raise TypeError(f"Expected a Scikit-learn Pipeline instance, got {type(model).__name__}")

    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    return str(path.resolve())


def load_model(filepath: Union[str, Path]) -> Pipeline:
    """
    Deserialize and restore a trained Scikit-learn regression pipeline from disk.

    Parameters
    ----------
    filepath : Union[str, Path]
        Source .joblib model file path.

    Returns
    -------
    Pipeline
        Fitted Scikit-learn regression pipeline ready for inference.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Model file not found at: {path}")

    model = joblib.load(path)
    if not isinstance(model, Pipeline):
        raise TypeError(f"Loaded object is not a Scikit-learn Pipeline (got {type(model).__name__})")
    return model


# ---------------------------------------------------------------------------
# 5. Plotly Diagnostic Visualizations for Prediction
# ---------------------------------------------------------------------------

def create_actual_vs_predicted_chart(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str,
) -> go.Figure:
    """Create actual vs predicted scatter plot with reference 45-degree parity line."""
    if len(y_true) == 0:
        fig = go.Figure()
        fig.update_layout(title="No prediction data available")
        return fig

    max_val = max(float(np.max(y_true)), float(np.max(y_pred))) * 1.05

    fig = go.Figure()

    # Actual vs Predicted points
    fig.add_trace(
        go.Scatter(
            x=y_true,
            y=y_pred,
            mode="markers",
            name="Test Predictions",
            marker=dict(size=7, color="#3182ce", opacity=0.7),
            hovertemplate="Actual: $%{x:,.2f}<br>Predicted: $%{y:,.2f}<extra></extra>",
        )
    )

    # 45-degree Perfect Prediction Line
    fig.add_trace(
        go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode="lines",
            name="Ideal Parity (y = x)",
            line=dict(color="#e53e3e", dash="dash", width=2),
        )
    )

    fig.update_layout(
        title=f"<b>Actual vs. Predicted Sales ({model_name})</b>",
        xaxis_title="Actual Test Sales ($)",
        yaxis_title="Predicted Sales ($)",
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def create_residual_distribution_chart(
    residuals: np.ndarray,
    model_name: str,
) -> go.Figure:
    """Create histogram of prediction residuals (Actual - Predicted)."""
    if len(residuals) == 0:
        fig = go.Figure()
        fig.update_layout(title="No residual data available")
        return fig

    fig = px.histogram(
        x=residuals,
        nbins=35,
        title=f"<b>Prediction Residuals Distribution ({model_name})</b>",
        labels={"x": "Residual Error ($) = Actual - Predicted"},
        template="plotly_white",
        color_discrete_sequence=["#4a5568"],
    )
    fig.add_vline(x=0, line_dash="dash", line_color="#e53e3e", annotation_text="Zero Residual")
    fig.update_layout(margin=dict(l=40, r=40, t=50, b=40), yaxis_title="Record Count")
    return fig


def create_model_comparison_bar_chart(comparison_df: pd.DataFrame) -> go.Figure:
    """Create grouped bar chart comparing MAE and RMSE across candidate models."""
    if comparison_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No comparison data available")
        return fig

    fig = go.Figure(
        data=[
            go.Bar(name="MAE ($ - Lower is better)", x=comparison_df["Model"], y=comparison_df["MAE ($)"], marker_color="#3182ce"),
            go.Bar(name="RMSE ($ - Lower is better)", x=comparison_df["Model"], y=comparison_df["RMSE ($)"], marker_color="#e53e3e"),
        ]
    )
    fig.update_layout(
        barmode="group",
        title="<b>Model Error Comparison (MAE vs. RMSE)</b>",
        yaxis_title="Error ($)",
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


# ---------------------------------------------------------------------------
# 6. Explainable AI (SHAP Feature Attributions)
# ---------------------------------------------------------------------------

def explain_prediction(
    model: Pipeline,
    input_data: Union[Dict[str, Any], pd.DataFrame],
    background_data: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Deconstruct an individual sales prediction using SHAP (SHapley Additive exPlanations).

    Respects the full Scikit-learn Pipeline (preprocessing + estimator).
    Dynamically selects TreeExplainer for tree ensembles (RandomForest, XGBoost)
    and LinearExplainer for Linear Regression. Aggregates one-hot encoded categories
    back to their original business entities while preserving mathematical additivity:
        Expected Base Value + Sum(SHAP Values) == Predicted Sales

    Parameters
    ----------
    model : Pipeline
        Fitted Scikit-learn regression pipeline.
    input_data : Union[Dict[str, Any], pd.DataFrame]
        Input scenario features (Category, Region, Quantity, Discount, Month, Quarter, DayOfWeek).
    background_data : Optional[pd.DataFrame], default None
        Optional reference dataset used as background distribution for baseline expectations.

    Returns
    -------
    Dict[str, Any]
        Dictionary of attributions, baseline expectation, verification metrics, and interpretations.
    """
    if not isinstance(model, Pipeline):
        raise TypeError(f"Expected a Scikit-learn Pipeline instance, got {type(model).__name__}")

    if "preprocessor" not in model.named_steps or "regressor" not in model.named_steps:
        raise ValueError("Pipeline must contain 'preprocessor' and 'regressor' named steps.")

    if isinstance(input_data, dict):
        input_df = pd.DataFrame([input_data])
    elif isinstance(input_data, pd.DataFrame):
        input_df = input_data.copy()
    else:
        raise TypeError(f"input_data must be dict or DataFrame, received {type(input_data).__name__}")

    # Validate required features
    missing = [c for c in ALL_FEATURE_COLUMNS if c not in input_df.columns]
    if missing:
        raise ValueError(f"Input data missing required features: {', '.join(missing)}")

    preprocessor = model.named_steps["preprocessor"]
    regressor = model.named_steps["regressor"]

    # Transform input scenario features through fitted preprocessor
    X_trans = preprocessor.transform(input_df[ALL_FEATURE_COLUMNS])
    transformed_feature_names = list(preprocessor.get_feature_names_out())

    # Raw model prediction
    raw_pred = float(regressor.predict(X_trans)[0])
    clamped_pred = round(max(raw_pred, 0.0), 2)

    # Initialize SHAP explainer based on model architecture
    if isinstance(regressor, (RandomForestRegressor, XGBRegressor)):
        explainer = shap.TreeExplainer(regressor)
        shap_res = explainer(X_trans)
        shap_vals = shap_res.values[0]
        base_val = explainer.expected_value
        if isinstance(base_val, (list, np.ndarray)):
            base_val = float(base_val[0])
        else:
            base_val = float(base_val)
        explainer_type = f"TreeExplainer ({type(regressor).__name__})"
    elif isinstance(regressor, LinearRegression):
        if background_data is not None and len(background_data) > 0:
            bg_df = background_data[ALL_FEATURE_COLUMNS] if isinstance(background_data, pd.DataFrame) else pd.DataFrame(background_data)
            bg_trans = preprocessor.transform(bg_df.iloc[:100])
        else:
            # Baseline is mean of standardized features (zeros for numeric)
            bg_trans = np.zeros((1, len(transformed_feature_names)))
        explainer = shap.LinearExplainer(regressor, bg_trans)
        shap_res = explainer(X_trans)
        shap_vals = shap_res.values[0]
        base_val = float(explainer.expected_value)
        explainer_type = "LinearExplainer (LinearRegression)"
    else:
        # General Explainer fallback
        if background_data is not None and len(background_data) > 0:
            bg_trans = preprocessor.transform(background_data[ALL_FEATURE_COLUMNS].iloc[:50])
        else:
            bg_trans = np.zeros((1, len(transformed_feature_names)))
        explainer = shap.Explainer(regressor.predict, bg_trans)
        shap_res = explainer(X_trans)
        shap_vals = shap_res.values[0]
        base_val = float(explainer.expected_value if hasattr(explainer, "expected_value") else raw_pred)
        explainer_type = f"GeneralExplainer ({type(regressor).__name__})"

    # 1. Capture raw transformed feature contributions
    raw_contributions = []
    for name, val in zip(transformed_feature_names, shap_vals):
        raw_contributions.append({
            "feature": name,
            "contribution": round(float(val), 2),
        })

    # 2. Map one-hot encoded and scaled features back to original business features
    grouped_shap: Dict[str, float] = {}
    for name, val in zip(transformed_feature_names, shap_vals):
        clean = name.replace("num__", "").replace("cat__", "")
        if clean.startswith("Category_"):
            orig = "Category"
        elif clean.startswith("Region_"):
            orig = "Region"
        else:
            orig = clean
        grouped_shap[orig] = grouped_shap.get(orig, 0.0) + float(val)

    # 3. Build user-friendly feature explanations
    total_abs_impact = sum(abs(v) for v in grouped_shap.values()) or 1.0
    feature_contributions = []
    for feat_name, contrib in grouped_shap.items():
        inp_val = input_df[feat_name].iloc[0] if feat_name in input_df.columns else ""
        if feat_name == "Discount":
            display_val = f"{float(inp_val) * 100:.0f}%"
        elif feat_name == "Quantity":
            display_val = f"{int(inp_val)} units"
        else:
            display_val = str(inp_val)

        if contrib > 0.01:
            direction = "increased"
            interpretation = f"Pushed sales prediction ${abs(contrib):,.2f} above baseline"
        elif contrib < -0.01:
            direction = "decreased"
            interpretation = f"Pulled sales prediction ${abs(contrib):,.2f} below baseline"
        else:
            direction = "neutral"
            interpretation = "Negligible impact on sales prediction relative to baseline"

        feature_contributions.append({
            "feature": feat_name,
            "input_value": display_val,
            "contribution": round(float(contrib), 2),
            "direction": direction,
            "interpretation": interpretation,
            "percentage_impact": round((abs(contrib) / total_abs_impact) * 100.0, 1),
        })

    # Sort contributions by absolute impact (highest driver first)
    feature_contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)

    additive_sum = round(base_val + sum(grouped_shap.values()), 2)
    is_additive_exact = abs(additive_sum - raw_pred) < 0.10

    return {
        "predicted_sales": clamped_pred,
        "base_value": round(base_val, 2),
        "feature_contributions": feature_contributions,
        "raw_transformed_contributions": raw_contributions,
        "additive_sum": additive_sum,
        "is_additive_exact": is_additive_exact,
        "explainer_type": explainer_type,
        "success": True,
    }


def create_shap_waterfall_chart(
    base_value: float,
    feature_contributions: List[Dict[str, Any]],
    predicted_sales: float,
    model_name: str = "Trained Model",
) -> go.Figure:
    """
    Create Plotly Waterfall diagram showing step-by-step SHAP attributions from base to prediction.
    """
    if not feature_contributions:
        fig = go.Figure()
        fig.update_layout(title="No SHAP attribution data available")
        return fig

    # Top drivers (up to 7)
    top_features = feature_contributions[:7]
    names = ["Baseline Expectation"] + [f"{f['feature']} ({f['input_value']})" for f in top_features] + ["Final Prediction"]
    measures = ["absolute"] + ["relative"] * len(top_features) + ["total"]
    values = [base_value] + [f["contribution"] for f in top_features] + [predicted_sales]

    fig = go.Figure(
        go.Waterfall(
            name="SHAP Attribution",
            orientation="v",
            measure=measures,
            x=names,
            y=values,
            textposition="outside",
            text=[f"${v:,.2f}" for v in values],
            connector={"line": {"color": "#a0aec0"}},
            decreasing={"marker": {"color": "#e53e3e"}},
            increasing={"marker": {"color": "#38a169"}},
            totals={"marker": {"color": "#3182ce"}},
        )
    )

    fig.update_layout(
        title=f"<b>SHAP Prediction Waterfall Attribution ({model_name})</b>",
        yaxis_title="Sales Impact ($)",
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig


def compare_scenarios_prediction(
    model: Pipeline,
    scenario_a: Union[Dict[str, Any], pd.DataFrame],
    scenario_b: Union[Dict[str, Any], pd.DataFrame],
    background_data: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Compares two business scenarios side by side using the same fitted regression model and SHAP explainer.

    Evaluates:
    - Predicted sales for Scenario A and Scenario B.
    - Absolute difference (y_hat_B - y_hat_A) and percentage difference.
    - Feature-by-feature input changes and SHAP attribution shifts (Delta phi_i = phi_{B, i} - phi_{A, i}).
    - Verifies exact additivity of the difference: sum(Delta phi_i) == Delta y_hat.
    """
    exp_a = explain_prediction(model, scenario_a, background_data=background_data)
    exp_b = explain_prediction(model, scenario_b, background_data=background_data)

    pred_a = float(exp_a["predicted_sales"])
    pred_b = float(exp_b["predicted_sales"])
    abs_diff = round(pred_b - pred_a, 2)
    pct_diff = round(((pred_b - pred_a) / pred_a) * 100.0, 2) if abs(pred_a) > 1e-6 else 0.0

    # Build feature-level comparison
    a_dict = {item["feature"]: item for item in exp_a["feature_contributions"]}
    b_dict = {item["feature"]: item for item in exp_b["feature_contributions"]}

    all_features = ["Category", "Region", "Quantity", "Discount", "Month", "Quarter", "DayOfWeek"]
    for k in list(a_dict.keys()) + list(b_dict.keys()):
        if k not in all_features:
            all_features.append(k)

    feature_comparisons = []
    changed_count = 0
    diff_sum = 0.0

    for feat in all_features:
        item_a = a_dict.get(feat, {"input_value": "-", "contribution": 0.0})
        item_b = b_dict.get(feat, {"input_value": "-", "contribution": 0.0})

        val_a = str(item_a["input_value"])
        val_b = str(item_b["input_value"])
        is_changed = (val_a != val_b)
        if is_changed:
            changed_count += 1

        contrib_a = float(item_a["contribution"])
        contrib_b = float(item_b["contribution"])
        diff_contrib = round(contrib_b - contrib_a, 2)
        diff_sum += diff_contrib

        if diff_contrib > 0.01:
            direction = "increased"
            if is_changed:
                interpretation = f"Changing {feat} from {val_a} to {val_b} increased sales attribution by +${abs(diff_contrib):,.2f}"
            else:
                interpretation = f"Feature {feat} attribution shifted by +${abs(diff_contrib):,.2f} due to model non-linear interactions"
        elif diff_contrib < -0.01:
            direction = "decreased"
            if is_changed:
                interpretation = f"Changing {feat} from {val_a} to {val_b} reduced sales attribution by -${abs(diff_contrib):,.2f}"
            else:
                interpretation = f"Feature {feat} attribution shifted by -${abs(diff_contrib):,.2f} due to model non-linear interactions"
        else:
            direction = "unchanged"
            if is_changed:
                interpretation = f"{feat} changed from {val_a} to {val_b} with negligible shift in sales attribution"
            else:
                interpretation = f"Unchanged ({val_a}), yielding identical attribution in both scenarios"

        feature_comparisons.append({
            "feature": feat,
            "scenario_a_value": val_a,
            "scenario_b_value": val_b,
            "is_changed": is_changed,
            "scenario_a_contribution": round(contrib_a, 2),
            "scenario_b_contribution": round(contrib_b, 2),
            "contribution_difference": diff_contrib,
            "direction": direction,
            "interpretation": interpretation,
        })

    # Sort comparisons: changed features first, then by absolute contribution difference descending
    feature_comparisons.sort(key=lambda x: (not x["is_changed"], -abs(x["contribution_difference"])))

    is_diff_additive = abs(diff_sum - abs_diff) < 0.15

    return {
        "scenario_a": exp_a,
        "scenario_b": exp_b,
        "predicted_sales_a": pred_a,
        "predicted_sales_b": pred_b,
        "absolute_difference": abs_diff,
        "percentage_difference": pct_diff,
        "changed_features_count": changed_count,
        "feature_comparisons": feature_comparisons,
        "is_difference_additive_exact": is_diff_additive,
        "explainer_type": exp_a["explainer_type"],
        "base_value": exp_a["base_value"],
        "success": True,
        "disclaimer": (
            "Scenario comparisons quantify mathematical differences in model predictions and SHAP attributions. "
            "They do not prove real-world causality or guarantee that business interventions will produce observed changes."
        ),
    }


