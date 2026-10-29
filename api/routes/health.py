"""
Health Check Endpoint.
"""

from fastapi import APIRouter
from api.schemas import HealthResponse

router = APIRouter(tags=["System Health"])


@router.get("/health", response_model=HealthResponse, summary="System Health Check")
def health_check() -> HealthResponse:
    """
    Returns the current liveness and health status of the BizInsightIQ API service.
    """
    return HealthResponse(
        status="UP",
        service="BizInsightIQ AI/ML REST API",
        version="1.0.0",
    )
