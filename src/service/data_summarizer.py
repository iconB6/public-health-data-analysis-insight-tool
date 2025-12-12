from src.interface.data_summarizer_interface import IDataSummarizer
from typing import List, Dict, Any
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


class DataSummarizer(IDataSummarizer):

    # ----------------------------------------------------------
    # 1. Summary statistics
    # ----------------------------------------------------------
    def summary_stats(self, records: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Compute summary stats (mean, min, max, count) for all numeric fields.
        Input: List[Dict]
        Output: pandas DataFrame
        """

        if not records:
            raise ValueError("Records list is empty.")

        df = pd.DataFrame(records)

        # Identify numeric columns
        numeric_cols = df.select_dtypes(include=["int64", "float64", "int32", "float32"]).columns

        if len(numeric_cols) == 0:
            raise ValueError("No numeric columns to summarize.")

        summary = df[numeric_cols].agg(["count", "mean", "min", "max"]).transpose()

        return summary

    # ----------------------------------------------------------
    # 2. Trend over time for a numeric field
    # ----------------------------------------------------------
    def trend_over_time(
    self,
    records: List[Dict[str, Any]],
    date_field: str,
    metric_field: str
) -> Dict[str, Any]:
        """
        Process and return time-series trend data without plotting.

        Returns:
            {
                "date": List[datetime],
                "value": List[float],
                "date_field": <str>,
                "metric_field": <str>,
                "dataframe": <pd.DataFrame>
            }
        """

        if not records:
            raise ValueError("Records list is empty.")

        df = pd.DataFrame(records)

        # Ensure fields exist
        if date_field not in df.columns:
            raise ValueError(f"Date field '{date_field}' not found.")

        if metric_field not in df.columns:
            raise ValueError(f"Metric field '{metric_field}' not found.")

        # Convert date
        try:
            df[date_field] = pd.to_datetime(df[date_field], format="%Y-%m-%d")
        except Exception:
            raise ValueError("Date format must be YYYY-MM-DD")

        # Convert metric to numeric
        df[metric_field] = pd.to_numeric(df[metric_field], errors="coerce")
        df = df.dropna(subset=[metric_field])

        # Sort chronologically
        df = df.sort_values(by=date_field)

        # Prepare data structure for visualization layer
        result = {
            "date": df[date_field].tolist(),
            "value": df[metric_field].tolist(),
            "date_field": date_field,
            "metric_field": metric_field,
            "dataframe": df[[date_field, metric_field]]
        }

        return result


    # ----------------------------------------------------------
    # 3. Group-by summary
    # ----------------------------------------------------------
    def group_by(
        self,
        records: List[Dict[str, Any]],
        group_field: str,
        metric_field: str
    ) -> pd.DataFrame:
        """
        Group by a categorical field and summarize a numeric field.
        Output: grouped pandas DataFrame
        """

        if not records:
            raise ValueError("Records list is empty.")

        df = pd.DataFrame(records)

        # Validate fields
        if group_field not in df.columns:
            raise ValueError(f"Group field '{group_field}' not found.")

        if metric_field not in df.columns:
            raise ValueError(f"Metric field '{metric_field}' not found.")

        # Ensure numeric metric
        df[metric_field] = pd.to_numeric(df[metric_field], errors="coerce")
        df = df.dropna(subset=[metric_field])

        grouped = df.groupby(group_field)[metric_field].agg(
            ["count", "mean", "min", "max"]
        )

        return grouped
