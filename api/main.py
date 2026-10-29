"""
BizInsightIQ FastAPI Application Entry Point.

Wires API routers, middleware, exception handlers, and documentation endpoints.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from api.routes import (
    health,
    validation,
    analytics,
    segmentation,
    prediction,
    insights,
)

logger = logging.getLogger("bizinsightiq.api")

app = FastAPI(
    title="BizInsightIQ AI/ML REST API",
    description=(
        "Enterprise REST API layer for BizInsightIQ. Exposes customer segmentation (K-Means), "
        "sales prediction (Random Forest & Linear Regression), exploratory data analysis (EDA), "
        "and explainable business insight engines for integration with Spring Boot and Next.js."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for future Next.js frontend and external client integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Safe Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches all unhandled exceptions and returns a sanitized error response,
    preventing internal filesystem paths, credentials, or stack traces from leaking.
    """
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please verify your request parameters."},
    )


# Mount routers under /api/v1
API_PREFIX = "/api/v1"
app.include_router(health.router)  # Mounted at /health
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(validation.router, prefix=API_PREFIX)
app.include_router(analytics.router, prefix=API_PREFIX)
app.include_router(segmentation.router, prefix=API_PREFIX)
app.include_router(prediction.router, prefix=API_PREFIX)
app.include_router(insights.router, prefix=API_PREFIX)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint welcoming clients and directing them to interactive Swagger documentation."""
    return {
        "service": "BizInsightIQ AI/ML REST API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": f"{API_PREFIX}/health",
    }
