"""
Customer Segmentation Router (K-Means & PCA).
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from api.schemas import SegmentationResponse
from api.deps import get_dataset_or_default
from src.validator import validate_dataset
from src.segmentation import (
    aggregate_customer_features,
    perform_kmeans_clustering,
    generate_cluster_profiles,
    evaluate_cluster_candidates,
)

router = APIRouter(prefix="/segmentation", tags=["Customer Segmentation"])


@router.post("", response_model=SegmentationResponse, summary="Execute K-Means Customer Clustering")
async def run_segmentation_endpoint(
    file: Optional[UploadFile] = File(None),
    n_clusters: int = Form(default=4, ge=2, le=7),
    random_state: int = Form(default=42),
    evaluate_candidates: bool = Form(default=True),
    include_assignments: bool = Form(default=True),
) -> SegmentationResponse:
    """
    Aggregates transaction data into customer RFM and behavioral metrics,
    applies StandardScaler, executes K-Means clustering ($k=2..7$), and projects
    clusters onto 2D PCA space with cluster persona profiles.
    """
    df = await get_dataset_or_default(file)
    validation = validate_dataset(df)
    if not validation.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Dataset validation failed.", "errors": validation.errors},
        )

    customer_df = aggregate_customer_features(df)
    if len(customer_df) < n_clusters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer count ({len(customer_df)}) is less than requested clusters ({n_clusters}).",
        )

    cluster_result = perform_kmeans_clustering(
        customer_df=customer_df,
        n_clusters=n_clusters,
        random_state=random_state,
    )
    profile_df = generate_cluster_profiles(cluster_result["clustered_df"])

    candidates_eval = None
    if evaluate_candidates:
        max_k = min(6, len(customer_df) - 1)
        if max_k >= 2:
            candidates_df = evaluate_cluster_candidates(
                customer_df=customer_df,
                k_min=2,
                k_max=max_k,
                random_state=random_state,
            )
            candidates_eval = candidates_df.to_dict(orient="records")

    customer_assignments = None
    if include_assignments and "clustered_df" in cluster_result:
        cdf = cluster_result["clustered_df"]
        customer_assignments = [
            {
                "customer_id": str(row["CustomerID"]),
                "cluster_id": int(row["Cluster"]),
                "recency": int(row["Recency"]),
                "frequency": int(row["Frequency"]),
                "monetary_value": round(float(row["MonetaryValue"]), 2),
                "total_profit": round(float(row["TotalProfit"]), 2),
            }
            for _, row in cdf.iterrows()
        ]

    return SegmentationResponse(
        n_clusters=cluster_result["n_clusters"],
        silhouette_score=float(cluster_result["silhouette_score"]),
        inertia=float(cluster_result["inertia"]),
        pca_variance_ratio=[float(v) for v in cluster_result["pca_variance_ratio"]],
        cluster_profiles=profile_df.to_dict(orient="records"),
        candidates_evaluation=candidates_eval,
        customer_assignments=customer_assignments,
    )
