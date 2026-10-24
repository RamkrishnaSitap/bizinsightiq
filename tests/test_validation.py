"""
Unit Tests for Data Loading and Data Validation Modules.

Uses pytest and small in-memory DataFrames to verify validation rules.
"""

import io
from pathlib import Path
import pytest
import pandas as pd

from src.data_loader import load_csv_data
from src.validator import validate_dataset, ValidationResult, REQUIRED_COLUMNS


@pytest.fixture
def valid_sample_df() -> pd.DataFrame:
    """Fixture providing a valid minimal business sales DataFrame."""
    return pd.DataFrame({
        "CustomerID": ["CUST-1001", "CUST-1002", "CUST-1003"],
        "OrderDate": ["2024-01-15", "2024-02-20", "2024-03-10"],
        "Category": ["Technology", "Furniture", "Office Supplies"],
        "Region": ["North", "South", "East"],
        "Quantity": [2, 5, 1],
        "Discount": [0.0, 0.1, 0.05],
        "Sales": [450.00, 1200.50, 45.20],
        "Profit": [112.50, 180.00, 15.30]
    })


class TestValidator:
    """Test suite for dataset validation logic."""

    def test_valid_dataset(self, valid_sample_df):
        """A properly formatted DataFrame should pass validation with zero errors."""
        result = validate_dataset(valid_sample_df)
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.total_rows == 3
        assert result.total_columns == 8
        assert result.missing_columns == []
        assert result.duplicate_rows_count == 0

    def test_missing_required_columns(self, valid_sample_df):
        """Dropping required columns must make is_valid False and identify missing columns."""
        df_incomplete = valid_sample_df.drop(columns=["Sales", "Profit"])
        result = validate_dataset(df_incomplete)
        assert result.is_valid is False
        assert "Sales" in result.missing_columns
        assert "Profit" in result.missing_columns
        assert any("Missing required column" in err for err in result.errors)

    def test_missing_values_warning(self, valid_sample_df):
        """Missing values should be detected and reported in missing_values_by_column."""
        df_with_nans = valid_sample_df.copy()
        df_with_nans.loc[0, "Region"] = None
        result = validate_dataset(df_with_nans)
        # Missing value generates warning, does not necessarily invalidate schema unless fatal
        assert "Region" in result.missing_values_by_column
        assert result.missing_values_by_column["Region"] == 1
        assert any("missing (NaN/null)" in warn for warn in result.warnings)

    def test_invalid_negative_sales_and_quantity(self, valid_sample_df):
        """Negative sales or negative quantity must produce validation errors."""
        df_negative = valid_sample_df.copy()
        df_negative.loc[0, "Quantity"] = -5
        df_negative.loc[1, "Sales"] = -100.0
        result = validate_dataset(df_negative)
        assert result.is_valid is False
        assert any("Quantity" in err and "negative" in err for err in result.errors)
        assert any("Sales" in err and "negative" in err for err in result.errors)

    def test_non_numeric_in_numeric_columns(self, valid_sample_df):
        """Strings placed into numeric columns must be flagged as errors."""
        df_bad_type = valid_sample_df.copy()
        df_bad_type["Sales"] = df_bad_type["Sales"].astype(object)
        df_bad_type.loc[0, "Sales"] = "not_a_number"
        result = validate_dataset(df_bad_type)
        assert result.is_valid is False
        assert any("non-numeric" in err for err in result.errors)
        assert "Sales" in result.invalid_numeric_counts

    def test_invalid_date_format(self, valid_sample_df):
        """Unparseable date strings in OrderDate must trigger an error."""
        df_bad_date = valid_sample_df.copy()
        df_bad_date.loc[0, "OrderDate"] = "not-a-real-date-string"
        result = validate_dataset(df_bad_date)
        assert result.is_valid is False
        assert result.invalid_date_count == 1
        assert any("invalid or unparseable date" in err for err in result.errors)

    def test_duplicate_rows_detection(self, valid_sample_df):
        """Duplicate rows should be counted and reported in warnings."""
        df_duplicated = pd.concat([valid_sample_df, valid_sample_df.iloc[[0]]], ignore_index=True)
        result = validate_dataset(df_duplicated)
        assert result.duplicate_rows_count == 1
        assert any("duplicate row" in warn for warn in result.warnings)

    def test_empty_dataframe(self):
        """An empty DataFrame should fail validation cleanly without raising an unhandled exception."""
        df_empty = pd.DataFrame()
        result = validate_dataset(df_empty)
        assert result.is_valid is False
        assert result.total_rows == 0
        assert any("empty" in err for err in result.errors)

    def test_immutability_of_input_dataframe(self, valid_sample_df):
        """Validation must not mutate the input DataFrame."""
        df_original_copy = valid_sample_df.copy(deep=True)
        _ = validate_dataset(valid_sample_df)
        pd.testing.assert_frame_equal(valid_sample_df, df_original_copy)

    def test_type_error_on_invalid_input(self):
        """Passing a non-DataFrame input should raise a TypeError."""
        with pytest.raises(TypeError):
            validate_dataset("not_a_dataframe")


class TestDataLoader:
    """Test suite for data loading module."""

    def test_load_valid_csv_file(self, tmp_path, valid_sample_df):
        """Valid CSV file on disk must load accurately."""
        csv_file = tmp_path / "test_sales.csv"
        valid_sample_df.to_csv(csv_file, index=False)
        loaded_df = load_csv_data(csv_file)
        assert isinstance(loaded_df, pd.DataFrame)
        assert len(loaded_df) == 3
        assert list(loaded_df.columns) == list(valid_sample_df.columns)

    def test_load_from_string_buffer(self, valid_sample_df):
        """Loading from an in-memory buffer (simulating Streamlit UploadedFile) should work."""
        buf = io.StringIO()
        valid_sample_df.to_csv(buf, index=False)
        buf.seek(0)
        loaded_df = load_csv_data(buf)
        assert len(loaded_df) == 3
        assert "CustomerID" in loaded_df.columns

    def test_load_non_existent_file(self):
        """Attempting to load a non-existent file must raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_csv_data("path/to/non_existent_sales_file.csv")

    def test_load_empty_file(self, tmp_path):
        """Loading a 0-byte file must raise ValueError."""
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")
        with pytest.raises(ValueError, match="empty"):
            load_csv_data(empty_file)

    def test_load_bundled_sample_dataset(self):
        """The bundled sample dataset in data/sample_sales_data.csv must load and validate."""
        sample_path = Path("data/sample_sales_data.csv")
        assert sample_path.exists(), "Sample dataset file must exist"
        df = load_csv_data(sample_path)
        assert len(df) == 1200
        result = validate_dataset(df)
        assert result.is_valid is True
        assert len(result.errors) == 0
