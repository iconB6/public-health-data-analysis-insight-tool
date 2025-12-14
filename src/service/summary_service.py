from collections import Counter
from typing import Any, Dict, List, Optional
import statistics


class SummaryService:

    def __init__(self, repository):
        self._repo = repository

    def summarize(
        self,
        rows: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        
        if rows is not None:
            if not isinstance(rows, list):
                raise TypeError("rows must be a list of dict")

            for row in rows:
                if not isinstance(row, dict):
                    raise TypeError("each row must be a dict")

        if rows is None:
            rows = self._repo.query()

        if not rows:
            return {
                "meta": {"total_records": 0},
                "categorical": {},
                "numeric": {},
            }

        schema = self._repo.get_schema("records")

        result = {
            "meta": {"total_records": len(rows)},
            "categorical": {},
            "numeric": {},
        }

        for col, col_type in schema.items():
            values = [r[col] for r in rows if r.get(col) is not None]

            if not values:
                continue

            if col_type == "TEXT":
                counter = Counter(values)
                result["categorical"][col] = [
                    {"value": k, "count": v}
                    for k, v in counter.items()
                ]

            elif col_type in ("INTEGER", "REAL"):
                result["numeric"][col] = {
                    "min": min(values),
                    "max": max(values),
                    "mean": statistics.mean(values),
                }

        return result
