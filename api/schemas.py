"""
Pydantic Request and Response Schemas for BizInsightIQ REST API.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Health Schemas
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "UP"})
    service: str = Field(..., json_schema_extra={"example": "BizInsightIQ AI/ML REST API"})
    version: str = Field(..., json_schema_extra={"example": "1.0.0"})


# ---------------------------------------------------------------------------
# Dataset Validation Schemas
# ---------------------------------------------------------------------------

class ValidationResponse(BaseModel):
    is_valid: bool
    total_rows: int
    total_columns: int
    columns_present: List[str]
    missing_columns: List[str]
    missing_values_by_column: Dict[str, int]
    duplicate_rows_count: int
    invalid_numeric_counts: Dict[str, int]
    invalid_date_count: int
    errors: List[str]
    warnings: List[str]


# ---------------------------------------------------------------------------
# EDA & Analytics Schemas
# ---------------------------------------------------------------------------

class BusinessKPIs(BaseModel):
    total_sales: float
    total_profit: float
    total_units: int
    unique_customers: int
    total_orders: int
    profit_margin_pct: float
    avg_order_value: float
    avg_discount_pct: float


class EDAResponse(BaseModel):
    kpis: BusinessKPIs
    trends: List[Dict[str, Any]]
    category_performance: List[Dict[str, Any]]
    regional_performance: List[Dict[str, Any]]
    discount_analysis: List[Dict[str, Any]]
    correlation_matrix: Dict[str, Dict[str, float]]


# ---------------------------------------------------------------------------
# Customer Segmentation Schemas
# ---------------------------------------------------------------------------

class ClusterProfile(BaseModel):
    Cluster: int
    CustomerCount: int
    CustomerPct: float
    Recency_Mean: float
    Frequency_Mean: float
    MonetaryValue_Mean: float
    TotalProfit_Mean: float
    AvgDiscount_Mean: float
    ProfitMarginPct_Mean: float
    DescriptivePersona: str


class CandidateEvaluation(BaseModel):
    k: int
    Inertia: float
    SilhouetteScore: float


class CustomerAssignment(BaseModel):
    customer_id: str
    cluster_id: int
    recency: int
    frequency: int
    monetary_value: float
    total_profit: float


class SegmentationResponse(BaseModel):
    n_clusters: int
    silhouette_score: float
    inertia: float
    pca_variance_ratio: List[float]
    cluster_profiles: List[Dict[str, Any]]
    candidates_evaluation: Optional[List[Dict[str, Any]]] = None
    customer_assignments: Optional[List[Dict[str, Any]]] = None


# ---------------------------------------------------------------------------
# Sales Prediction Schemas
# ---------------------------------------------------------------------------

class RegressionMetrics(BaseModel):
    mae: float
    rmse: float
    r2: float
    test_size: int
    split_strategy: str
    training_time: Optional[float] = None


class PredictionTrainingResponse(BaseModel):
    comparison: List[Dict[str, Any]]
    metrics: Dict[str, RegressionMetrics]
    metadata: Dict[str, Any]
    dataset_id: Optional[str] = None


class ScenarioPredictionRequest(BaseModel):
    category: str = Field(..., json_schema_extra={"example": "Technology"})
    region: str = Field(..., json_schema_extra={"example": "East"})
    quantity: int = Field(..., ge=1, le=1000, json_schema_extra={"example": 5})
    discount: float = Field(..., ge=0.0, le=1.0, json_schema_extra={"example": 0.10})
    month: Optional[int] = Field(default=6, ge=1, le=12, json_schema_extra={"example": 6})
    quarter: Optional[int] = Field(default=2, ge=1, le=4, json_schema_extra={"example": 2})
    day_of_week: Optional[int] = Field(default=2, ge=0, le=6, json_schema_extra={"example": 2})
    model_type: Optional[str] = Field(default="random_forest", description="Estimator type: 'random_forest', 'xgboost', or 'linear_regression'", json_schema_extra={"example": "random_forest"})
    dataset_id: Optional[str] = Field(default=None, description="Optional dataset ID associated with trained model", json_schema_extra={"example": "33333333-3333-3333-3333-333333333333"})


class ScenarioPredictionResponse(BaseModel):
    predicted_sales: float
    category: str
    region: str
    quantity: int
    discount: float
    month: int
    quarter: int
    day_of_week: int
    model_used: str = "Random Forest Regressor"
    dataset_id: Optional[str] = None


class FeatureContributionItem(BaseModel):
    feature: str
    input_value: str
    contribution: float
    direction: str  # "increased", "decreased", "neutral"
    interpretation: str
    percentage_impact: float


class RawTransformedContributionItem(BaseModel):
    feature: str
    contribution: float


class PredictionExplanationResponse(BaseModel):
    predicted_sales: float
    base_value: float
    model_used: str
    dataset_id: Optional[str] = None
    success: bool
    feature_contributions: List[FeatureContributionItem]
    raw_transformed_contributions: Optional[List[RawTransformedContributionItem]] = None
    additive_sum: float
    is_additive_exact: bool
    explainer_type: str
    disclaimer: str = (
        "SHAP feature attributions describe how the model calculated this prediction given its "
        "learned weights and training distributions. They reflect statistical model dependencies "
        "and do not constitute real-world causal guarantees."
    )


class SingleScenarioInput(BaseModel):
    category: str = Field(..., json_schema_extra={"example": "Technology"})
    region: str = Field(..., json_schema_extra={"example": "East"})
    quantity: int = Field(..., ge=1, le=1000, json_schema_extra={"example": 5})
    discount: float = Field(..., ge=0.0, le=1.0, json_schema_extra={"example": 0.10})
    month: Optional[int] = Field(default=6, ge=1, le=12, json_schema_extra={"example": 6})
    quarter: Optional[int] = Field(default=2, ge=1, le=4, json_schema_extra={"example": 2})
    day_of_week: Optional[int] = Field(default=2, ge=0, le=6, json_schema_extra={"example": 2})


class ScenarioComparisonRequest(BaseModel):
    scenario_a: SingleScenarioInput
    scenario_b: SingleScenarioInput
    model_type: Optional[str] = Field(default="random_forest", description="Estimator type: 'random_forest', 'xgboost', or 'linear_regression'", json_schema_extra={"example": "random_forest"})
    dataset_id: Optional[str] = Field(default=None, description="Optional dataset ID associated with trained model", json_schema_extra={"example": "33333333-3333-3333-3333-333333333333"})


class FeatureComparisonItem(BaseModel):
    feature: str
    scenario_a_value: str
    scenario_b_value: str
    is_changed: bool
    scenario_a_contribution: float
    scenario_b_contribution: float
    contribution_difference: float
    direction: str  # "increased", "decreased", "unchanged"
    interpretation: str


class ScenarioComparisonResponse(BaseModel):
    scenario_a: PredictionExplanationResponse
    scenario_b: PredictionExplanationResponse
    predicted_sales_a: float
    predicted_sales_b: float
    absolute_difference: float
    percentage_difference: float
    changed_features_count: int
    feature_comparisons: List[FeatureComparisonItem]
    is_difference_additive_exact: bool
    explainer_type: str
    base_value: float
    model_used: str
    dataset_id: Optional[str] = None
    success: bool = True
    disclaimer: str = (
        "Scenario comparisons quantify mathematical differences in model predictions and SHAP attributions. "
        "They do not prove real-world causality or guarantee that business interventions will produce observed changes."
    )


# ---------------------------------------------------------------------------
# Business Insights Schemas
# ---------------------------------------------------------------------------

class InsightItem(BaseModel):
    insight_id: str
    category: str
    severity: str
    title: str
    evidence: Dict[str, Any]
    recommendation: str
    limitations: str


class InsightsSummary(BaseModel):
    total_insights: int
    critical_count: int
    warning_count: int
    info_count: int


class InsightsResponse(BaseModel):
    summary: InsightsSummary
    insights: List[InsightItem]
