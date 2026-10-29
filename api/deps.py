"""
Dependency and Utility Functions for BizInsightIQ REST API.
"""

from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
import pandas as pd

from src.data_loader import load_csv_data

DEFAULT_SAMPLE_PATH = Path("data/sample_sales_data.csv")
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


async def parse_uploaded_csv(file: UploadFile) -> pd.DataFrame:
    """
    Safely read and parse an uploaded CSV file from FastAPI UploadFile.
    Enforces upload file size limit and handles empty/corrupt files.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only CSV files are supported.",
        )

    # Read bytes and check size
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded CSV file is empty (0 bytes).",
        )
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB.",
        )

    # Use existing data_loader safely via BytesIO / file buffer
    from io import BytesIO
    buffer = BytesIO(content)
    try:
        df = load_csv_data(buffer)
        return df
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV data: {str(exc)}",
        )


async def get_dataset_or_default(file: Optional[UploadFile] = None) -> pd.DataFrame:
    """
    Retrieve DataFrame from uploaded file if provided, otherwise load the bundled sample sales dataset.
    """
    if file is not None and file.filename:
        return await parse_uploaded_csv(file)

    if not DEFAULT_SAMPLE_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bundled default sample dataset is not available on the server.",
        )

    try:
        return load_csv_data(DEFAULT_SAMPLE_PATH)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading default dataset: {str(exc)}",
        )
