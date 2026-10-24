"""
Data Loader Module for AI Business Intelligence & Predictive Analytics System.

Handles loading CSV datasets safely from local paths or file buffers.
"""

from pathlib import Path
from typing import Union, BinaryIO, TextIO
import pandas as pd


def load_csv_data(source: Union[str, Path, BinaryIO, TextIO]) -> pd.DataFrame:
    """
    Load CSV data from a file path or file-like buffer.

    Parameters
    ----------
    source : str, Path, BinaryIO, or TextIO
        The file path or file-like buffer (e.g., Streamlit UploadedFile) to read.

    Returns
    -------
    pd.DataFrame
        Loaded pandas DataFrame (a copy, preserving original data).

    Raises
    ------
    FileNotFoundError
        If the given file path does not exist.
    ValueError
        If the file is empty or cannot be parsed as a CSV.
    TypeError
        If the source type is unsupported.
    """
    if isinstance(source, (str, Path)):
        file_path = Path(source)
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found at path: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"Path is not a regular file: {file_path}")
        if file_path.stat().st_size == 0:
            raise ValueError(f"Dataset file is empty (0 bytes): {file_path}")
        
        try:
            df = pd.read_csv(file_path)
        except pd.errors.EmptyDataError:
            raise ValueError(f"Dataset contains no data: {file_path}")
        except Exception as exc:
            raise ValueError(f"Failed to parse CSV file '{file_path}': {str(exc)}") from exc

    elif hasattr(source, "read"):
        # File-like object (e.g., Streamlit UploadedFile or io.StringIO/BytesIO)
        try:
            # Check for empty buffer if seekable
            if hasattr(source, "seek") and hasattr(source, "tell"):
                source.seek(0)
            df = pd.read_csv(source)
            if hasattr(source, "seek"):
                source.seek(0)
        except pd.errors.EmptyDataError:
            raise ValueError("Uploaded file contains no data.")
        except Exception as exc:
            raise ValueError(f"Failed to parse uploaded CSV: {str(exc)}") from exc
    else:
        raise TypeError(f"Unsupported data source type: {type(source).__name__}")

    if df.empty:
        raise ValueError("Loaded dataset is empty (0 rows).")

    return df.copy()
