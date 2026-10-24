"""
Data Validator Module for AI Business Intelligence & Predictive Analytics System.

Performs schema verification, numeric range checks, missing value detection,
date integrity validation, and duplicate row detection without modifying original data.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
import pandas as pd
import numpy as np


REQUIRED_COLUMNS = [
    "CustomerID",
    "OrderDate",
    "Category",
    "Region",
    "Quantity",
    "Discount",
    "Sales",
    "Profit",
]

NUMERIC_COLUMNS = ["Quantity", "Discount", "Sales", "Profit"]


@dataclass
class ValidationResult:
    """Stores the structured results of a dataset validation pass."""
    is_valid: bool
    total_rows: int
    total_columns: int
    columns_present: List[str]
    missing_columns: List[str]
    missing_values_by_column: Dict[str, int]
    duplicate_rows_count: int
    invalid_numeric_counts: Dict[str, int]
    invalid_date_count: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result object into a dictionary for UI display or reporting."""
        return {
            "is_valid": self.is_valid,
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
            "columns_present": self.columns_present,
            "missing_columns": self.missing_columns,
            "missing_values_by_column": self.missing_values_by_column,
            "duplicate_rows_count": self.duplicate_rows_count,
            "invalid_numeric_counts": self.invalid_numeric_counts,
            "invalid_date_count": self.invalid_date_count,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def validate_dataset(df: pd.DataFrame) -> ValidationResult:
    """
    Validate a business sales dataset against schema and business logic rules.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to inspect. The function does not modify this input.

    Returns
    -------
    ValidationResult
        Structured validation outcome containing validity flag, errors, and warnings.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, received {type(df).__name__}")

    errors: List[str] = []
    warnings: List[str] = []

    # 1. Check for empty DataFrame
    if df.empty:
        errors.append("Dataset is empty (0 rows).")
        return ValidationResult(
            is_valid=False,
            total_rows=0,
            total_columns=len(df.columns),
            columns_present=list(df.columns),
            missing_columns=REQUIRED_COLUMNS.copy(),
            missing_values_by_column={},
            duplicate_rows_count=0,
            invalid_numeric_counts={},
            invalid_date_count=0,
            errors=errors,
            warnings=warnings,
        )

    total_rows = len(df)
    total_columns = len(df.columns)
    columns_present = list(df.columns)

    # 2. Check required columns
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required column(s): {', '.join(missing_columns)}")

    # 3. Check missing / null values
    missing_values_by_column: Dict[str, int] = {}
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        if null_count > 0:
            missing_values_by_column[col] = null_count
            if col in REQUIRED_COLUMNS:
                warnings.append(
                    f"Column '{col}' contains {null_count} missing (NaN/null) values ({null_count / total_rows:.1%})."
                )

    # 4. Check duplicate rows
    duplicate_rows_count = int(df.duplicated().sum())
    if duplicate_rows_count > 0:
        warnings.append(
            f"Dataset contains {duplicate_rows_count} duplicate row(s)."
        )

    # 5. Check numeric integrity
    invalid_numeric_counts: Dict[str, int] = {}
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            # Check non-numeric entries
            converted = pd.to_numeric(df[col], errors="coerce")
            nan_from_conversion = int(converted.isnull().sum() - df[col].isnull().sum())
            if nan_from_conversion > 0:
                invalid_numeric_counts[col] = nan_from_conversion
                errors.append(f"Column '{col}' has {nan_from_conversion} non-numeric value(s).")

            # Check specific numeric range rules
            if col in ["Quantity", "Sales"]:
                negative_count = int((converted < 0).sum())
                if negative_count > 0:
                    errors.append(
                        f"Column '{col}' has {negative_count} negative value(s), which is invalid for {col}."
                    )
            elif col == "Discount":
                out_of_range = int(((converted < 0.0) | (converted > 1.0)).sum())
                if out_of_range > 0:
                    warnings.append(
                        f"Column 'Discount' has {out_of_range} value(s) outside standard range [0.0, 1.0]."
                    )

    # 6. Check date format integrity
    invalid_date_count = 0
    if "OrderDate" in df.columns:
        converted_dates = pd.to_datetime(df["OrderDate"], errors="coerce", format="mixed")
        invalid_date_count = int(converted_dates.isnull().sum() - df["OrderDate"].isnull().sum())
        if invalid_date_count > 0:
            errors.append(
                f"Column 'OrderDate' contains {invalid_date_count} invalid or unparseable date value(s)."
            )

    # Dataset is considered valid if there are zero blocking errors
    is_valid = len(errors) == 0

    return ValidationResult(
        is_valid=is_valid,
        total_rows=total_rows,
        total_columns=total_columns,
        columns_present=columns_present,
        missing_columns=missing_columns,
        missing_values_by_column=missing_values_by_column,
        duplicate_rows_count=duplicate_rows_count,
        invalid_numeric_counts=invalid_numeric_counts,
        invalid_date_count=invalid_date_count,
        errors=errors,
        warnings=warnings,
    )
