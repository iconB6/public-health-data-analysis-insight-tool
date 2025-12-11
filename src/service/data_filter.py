from typing import List, Dict, Any, Optional, Callable
from src.interface.data_filter_interface import IDataFilter
from datetime import datetime


class DataFilter(IDataFilter):

    def filter_records(
        self,
        records: List[Dict[str, Any]],
        dimension_filters: Optional[Dict[str, str]] = None,
        date_range: Optional[Dict[str, str]] = None,
        metric_filters: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> List[Dict[str, Any]]:

        result = records

        if dimension_filters:
            result = self._apply_dimension_filters(result, dimension_filters)

        if date_range:
            result = self._apply_date_range_filter(result, date_range)

        if metric_filters:
            result = self._apply_metric_filters(result, metric_filters)

        return result
    
    # -------------------------------------------------------------
    # dimension filters
    # -------------------------------------------------------------
    def _apply_dimension_filters(
        self, 
        records: List[Dict[str, Any]], 
        filters: Dict[str, str]
    ) -> List[Dict[str, Any]]:

        def match(record):
            dims = record.get("dimensions", {})
            return all(dims.get(key) == value for key, value in filters.items())

        return [r for r in records if match(r)]

    # -------------------------------------------------------------
    # date range filter：record["dimensions"]["date"] must be yyyy-mm-dd
    # -------------------------------------------------------------
    def _apply_date_range_filter(
        self,
        records: List[Dict[str, Any]],
        date_range: Dict[str, str]
    ) -> List[Dict[str, Any]]:

        start = (
            datetime.strptime(date_range["start"], "%Y-%m-%d")
            if "start" in date_range
            else None
        )
        end = (
            datetime.strptime(date_range["end"], "%Y-%m-%d")
            if "end" in date_range
            else None
        )

        def match(record):
            dims = record.get("dimensions", {})
            date_str = dims.get("date")
            if not date_str:
                return False

            try:
                record_date = datetime.strptime(date_str, "%Y-%m-%d")
            except:
                return False

            if start and record_date < start:
                return False
            if end and record_date > end:
                return False

            return True

        return [r for r in records if match(r)]

    # -------------------------------------------------------------
    # metric_filters example:{
    #    "cases": {">=": 1000},
    #    "deaths": {"<": 50}
    # }
    # -------------------------------------------------------------
    def _apply_metric_filters(
        self,
        records: List[Dict[str, Any]],
        metric_filters: Dict[str, Dict[str, float]]
    ) -> List[Dict[str, Any]]:

        ops: Dict[str, Callable[[float, float], bool]] = {
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b, 
        }

        def match(record):
            metrics = record.get("metrics", {})

            for metric_name, conditions in metric_filters.items():
                if metric_name not in metrics:
                    return False

                value = metrics[metric_name]

                for op_symbol, target in conditions.items():
                    if op_symbol not in ops:
                        raise ValueError(f"Unsupported operator: {op_symbol}")

                    if not ops[op_symbol](value, target):
                        return False

            return True

        return [r for r in records if match(r)]
    

