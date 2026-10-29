"""
Dataset Validation Router.
"""

from fastapi import APIRouter, UploadFile, File
from api.schemas import ValidationResponse
from api.deps import parse_uploaded_csv
from src.validator import validate_dataset

router = APIRouter(prefix="/datasets", tags=["Dataset Management"])


@router.post("/validate", response_model=ValidationResponse, summary="Validate Uploaded CSV Dataset")
async def validate_dataset_endpoint(file: UploadFile = File(...)) -> ValidationResponse:
    """
    Accepts an uploaded CSV file, parses it into an immutable DataFrame, and executes
    the complete schema verification, numeric range checks, missing value detection,
    and date integrity checks using the existing validator module.
    """
    df = await parse_uploaded_csv(file)
    result = validate_dataset(df)
    return ValidationResponse(**result.to_dict())
