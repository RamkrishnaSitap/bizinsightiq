"""
Exploratory Data Analysis (EDA) & Analytics Router.
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from api.schemas import EDAResponse, BusinessKPIs
from api.deps import get_dataset_or_default
from src.validator import validate_dataset
from src.eda import (
    compute_business_kpis,
    compute_sales_profit_trends,
    compute_category_performance,
    compute_regional_performance,
    compute_discount_profitability_analysis,
    compute_correlation_matrix,
)

router = APIRouter(prefix="/analytics", tags=["Exploratory Data Analysis"])


@router.post("/eda", response_model=EDAResponse, summary="Compute Business KPIs & EDA Aggregations")
async def run_eda_endpoint(file: Optional[UploadFile] = File(None)) -> EDAResponse:
    """
    Computes business performance metrics, sales/profit trends, category breakdown,
    regional breakdown, discount elasticity, and feature correlation matrix.
    If no file is uploaded, analyzes the verified bundled sample sales dataset.
    """
    df = await get_dataset_or_default(file)
    validation = validate_dataset(df)
    if not validation.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Dataset validation failed.", "errors": validation.errors},
        )

    kpis_dict = compute_business_kpis(df)
    trends_df = compute_sales_profit_trends(df)
    cat_df = compute_category_performance(df)
    reg_df = compute_regional_performance(df)
    discount_df = compute_discount_profitability_analysis(df)
    corr_df = compute_correlation_matrix(df)

    return EDAResponse(
        kpis=BusinessKPIs(**kpis_dict),
        trends=trends_df.to_dict(orient="records"),
        category_performance=cat_df.to_dict(orient="records"),
        regional_performance=reg_df.to_dict(orient="records"),
        discount_analysis=discount_df.to_dict(orient="records"),
        correlation_matrix=corr_df.to_dict(orient="dict"),
    )
