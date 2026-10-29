"""
Business Insights & Decision Support Router.
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from api.schemas import InsightsResponse, InsightsSummary, InsightItem
from api.deps import get_dataset_or_default
from src.validator import validate_dataset
from src.insights import (
    generate_all_insights,
    filter_insights,
    get_insights_summary,
)

router = APIRouter(prefix="/insights", tags=["Business Insights"])


@router.post("", response_model=InsightsResponse, summary="Generate Decision Support Insights & Recommendations")
async def generate_insights_endpoint(
    file: Optional[UploadFile] = File(None),
    severity: Optional[str] = Form(default=None),
    category: Optional[str] = Form(default=None),
) -> InsightsResponse:
    """
    Evaluates 12 deterministic heuristic business rules across four analytical pillars:
    Sales & Profitability, Promotional Discounting, Customer Segmentation, and Predictive Modeling.
    Provides structured recommendations, empirical evidence, and operational limitations.
    """
    df = await get_dataset_or_default(file)
    validation = validate_dataset(df)
    if not validation.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Dataset validation failed.", "errors": validation.errors},
        )

    all_insights = generate_all_insights(df)
    filtered = filter_insights(all_insights, severity=severity, category=category)
    summary_dict = get_insights_summary(all_insights)

    insight_items = [
        InsightItem(
            insight_id=ins.insight_id,
            category=ins.category,
            severity=ins.severity,
            title=ins.title,
            evidence=ins.evidence,
            recommendation=ins.recommendation,
            limitations=ins.limitations,
        )
        for ins in filtered
    ]

    return InsightsResponse(
        summary=InsightsSummary(
            total_insights=summary_dict.get("total", len(all_insights)),
            critical_count=summary_dict.get("by_severity", {}).get("critical", 0),
            warning_count=summary_dict.get("by_severity", {}).get("warning", 0),
            info_count=summary_dict.get("by_severity", {}).get("info", 0),
        ),
        insights=insight_items,
    )
