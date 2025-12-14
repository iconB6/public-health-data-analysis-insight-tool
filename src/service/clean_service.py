import datetime
from typing import Any, Dict, List



class DataCleanService():

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
                clean_key = self._clean_key(key)
                cleaned[clean_key] = self._clean_value(value)

            cleaned_rows.append(cleaned)

        return cleaned_rows

    # ---- Helpers ----

    def _clean_key(self, key: str) -> str:
        """Normalize key strings."""
        if not isinstance(key, str):
            return key

        return (
            key
            .lstrip("\ufeff")          # BOM
            .replace("\u200b", "")     # zero-width space
            .replace("\xa0", " ")      # non-breaking space
            .strip()                   # leading/trailing spaces
            .upper()                   # normalize case
        )

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

        if isinstance(value, str):
            numeric = value.replace(",", "")

            # float
            if "." in numeric:
                try:
                    return float(numeric)
                except ValueError:
                    return None

            # int
            if numeric.isdigit():
                return int(numeric)


        # detect dates
        if isinstance(value, str):
            for fmt in self.DATE_FORMATS:
                try:
                    return datetime.datetime.strptime(value, fmt).date()
                except ValueError:
                    continue

        return value