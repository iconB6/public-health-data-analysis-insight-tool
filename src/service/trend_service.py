import datetime
from collections import defaultdict
from typing import Any, Dict, Optional
from src.utils.logger import get_logger


class TrendService:

    def __init__(self, repository):
        self._repo = repository
        self.logger = get_logger(self.__class__.__name__)

    def trend_over_time(
        self,
        *,
        date_field: str,
        metric_field: str,
        agg: str = "count",
        date_from=None,
        date_to=None,
        conditions=None,
    ) -> dict:
        
        self.logger.info(
            "Computing trend over time: %s (%s)",
            metric_field, agg
        )

        
        # ---------- validation ----------
        if not isinstance(date_field, str):
            raise TypeError("date_field must be str")

        if not isinstance(metric_field, str):
            raise TypeError("metric_field must be str")

        if agg not in {"count", "sum", "mean"}:
            raise ValueError("agg must be one of: count, sum, mean")

        # ---------- fetch data ----------
        rows = self._repo.query_for_trend(
            date_field=date_field,
            date_from=date_from,
            date_to=date_to,
            conditions=conditions,
        )


        if not rows:
            self.logger.warning("Trend query returned no rows")
            return {
                "date": [],
                "value": [],
                "date_field": date_field,
                "metric_field": metric_field,
                "aggregation": agg,
            }

        # ---------- group by date ----------
        grouped = defaultdict(list)

        for row in rows:
            date = row.get(date_field)
            value = row.get(metric_field)

            if date is None:
                continue

            grouped[date].append(value)

        # ---------- aggregate ----------
        dates = sorted(grouped.keys())
        values = []

        for d in dates:
            vals = [v for v in grouped[d] if isinstance(v, (int, float))]

            if agg == "count":
                values.append(len(vals))
            elif agg == "sum":
                values.append(sum(vals))
            elif agg == "mean":
                values.append(sum(vals) / len(vals) if vals else 0)

        return {
            "date": dates,
            "value": values,
            "date_field": date_field,
            "metric_field": metric_field,
            "aggregation": agg,
        }
