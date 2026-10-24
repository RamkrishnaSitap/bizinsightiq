"""
Supervised Machine Learning Sales Prediction Module for BizInsightIQ.

Provides framework-agnostic data preprocessing, pipeline construction,
Linear Regression and Random Forest training, regression evaluation metrics,
what-if scenario inference, and Plotly diagnostic visualizations.
"""

from typing import Dict, Any, List, Tuple, Union, Optional
import pandas as pd
import numpy as np
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
    else:
        raise ValueError(f"Unsupported model_type: '{model_type}'. Choose 'linear_regression' or 'random_forest'.")

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
    pipe_lr = build_prediction_pipeline("linear_regression")
    pipe_lr.fit(X_train, y_train)
    eval_lr = evaluate_regression_model(pipe_lr, X_test, y_test)

    # 2. Train Random Forest Regressor
    pipe_rf = build_prediction_pipeline("random_forest", random_state=random_state)
    pipe_rf.fit(X_train, y_train)
    eval_rf = evaluate_regression_model(pipe_rf, X_test, y_test)

    # Construct model comparison DataFrame
    comparison_df = pd.DataFrame([
        {
            "Model": "Linear Regression (Baseline)",
            "MAE ($)": eval_lr["mae"],
            "RMSE ($)": eval_lr["rmse"],
            "R² Score": eval_lr["r2"],
            "Test Samples": eval_lr["test_size"],
        },
        {
            "Model": "Random Forest Regressor",
            "MAE ($)": eval_rf["mae"],
            "RMSE ($)": eval_rf["rmse"],
            "R² Score": eval_rf["r2"],
            "Test Samples": eval_rf["test_size"],
        },
    ])

    return {
        "comparison_df": comparison_df,
        "models": {
            "linear_regression": pipe_lr,
            "random_forest": pipe_rf,
        },
        "evaluations": {
            "linear_regression": eval_lr,
            "random_forest": eval_rf,
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
