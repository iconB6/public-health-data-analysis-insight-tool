import datetime
from typing import Any, Dict, List

from src.interface.data_cleaner_interface import IDataCleaner


class DataCleaner(IDataCleaner):

    NULL_VALUES = {"", "na", "n/a", "null", "none", "-", "--"}

    DATE_FORMATS = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%d-%m-%Y",
    ]

    def clean(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean raw rows:
        - remove empty rows
        - normalize null values
        - convert numbers
        - convert dates
        """

        cleaned_rows = []

        for row in rows:
            cleaned = {}
            # skip fully empty rows
            if all(v in [None, ""] for v in row.values()):
                continue

            for key, value in row.items():
                cleaned[key] = self._clean_value(value)

            cleaned_rows.append(cleaned)

        return cleaned_rows

    # ---- Helpers ----

    def _clean_value(self, value: Any) -> Any:
        """Convert specific formats."""

        if value is None:
            return None

        # trim spaces
        if isinstance(value, str):
            value = value.strip()

        # check null-like values
        if isinstance(value, str) and value.lower() in self.NULL_VALUES:
            return None

        # detect numeric with thousand separators
        if isinstance(value, str) and value.replace(",", "").replace(".", "").isdigit():
            try:
                return float(value.replace(",", ""))
            except ValueError:
                pass

        # detect integer
        if isinstance(value, str) and value.isdigit():
            return int(value)

        # detect float
        try:
            return float(value)
        except (ValueError, TypeError):
            pass

        # detect dates
        if isinstance(value, str):
            for fmt in self.DATE_FORMATS:
                try:
                    return datetime.datetime.strptime(value, fmt).date()
                except ValueError:
                    continue

        return value

    # ---- Structured Output ----

    def to_structured_records(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert flat cleaned rows into:
        {
            "record_data": {...},
            "dimensions": {...},
            "metrics": {...}
        }
        """

        structured = []

        for row in rows:
            record_data = {}
            dimensions = {}
            metrics = {}

            for key, value in row.items():
                # record-level metadata (customizable)
                if key in ["data_source", "source", "provider"]:
                    record_data[key] = value
                    continue

                # numeric = metric
                if isinstance(value, (int, float)):
                    metrics[key] = value
                else:
                    dimensions[key] = value

            structured.append(
                {
                    "record_data": record_data,
                    "dimensions": dimensions,
                    "metrics": metrics,
                }
            )

        return structured