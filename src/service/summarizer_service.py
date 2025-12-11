from typing import List, Dict, Any
from datetime import datetime
from src.interface.data_summarizer_interface import IDataSummarizer


class Summarizer(IDataSummarizer):

    # ----------------------------------------------------
    # summary statistics(min, max, mean, count)
    # ----------------------------------------------------
    def summary_stats(self, records: List[Dict[str, Any]], metric: str) -> Dict[str, Any]:
        values = [
            r["metrics"].get(metric)
            for r in records
            if metric in r["metrics"] and isinstance(r["metrics"][metric], (int, float))
        ]

        if not values:
            return {"count": 0, "mean": None, "min": None, "max": None}

        return {
            "count": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values)
        }

    # ----------------------------------------------------
    # trend over time
    # ----------------------------------------------------
    def trend_over_time(self, records: List[Dict[str, Any]], date_key: str, metric: str):
        """restrict: data_key must alive in dimensions, metric must be numeric"""

        items = []
        for r in records:
            date_str = r["dimensions"].get(date_key)
            metric_val = r["metrics"].get(metric)

            if not date_str or not isinstance(metric_val, (int, float)):
                continue

            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue

            items.append((dt, metric_val))

        # sort by date
        items.sort(key=lambda x: x[0])

        return [{"date": d.strftime("%Y-%m-%d"), metric: v} for d, v in items]

    # ----------------------------------------------------
    # group by dimension
    # ----------------------------------------------------
    def group_by(self, records: List[Dict[str, Any]], group_key: str, metric: str):
        groups = {}

        for r in records:
            dim_value = r["dimensions"].get(group_key)
            metric_value = r["metrics"].get(metric)

            if dim_value is None or not isinstance(metric_value, (int, float)):
                continue

            groups.setdefault(dim_value, []).append(metric_value)

        result = {}
        for key, vals in groups.items():
            result[key] = {
                "count": len(vals),
                "mean": sum(vals) / len(vals),
                "min": min(vals),
                "max": max(vals)
            }

        return result
