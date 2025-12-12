from typing import List, Dict, Any
from src.interface.data_filter_interface import IDataFilter
from datetime import datetime


class DataFilter(IDataFilter):

    def __init__(self, repository=None):
        self.repository = repository

    def filter_by_fields(
        self,
        records: List[Dict[str, Any]],
        **field_filters
    ) -> List[Dict[str, Any]]:

        if not records:
            return []

        if self.repository:
            valid_fields = set(self.repository.get_columns())
        else:
            # infer valid fields from the first record
            valid_fields = set(records[0].keys()) if records else set()
        result = records

        for field, value in field_filters.items():
            if field not in valid_fields:
                continue
            if value is None:
                continue

            result = [
                r for r in result
                if r.get(field) == value
            ]

        return result

    def filter_by_date_range(
        self,
        records: List[Dict[str, Any]],
        date_field: str = "date",
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict[str, Any]]:

        if not records:
            return []

        if not (start_date or end_date):
            return records

        if self.repository:
            valid_fields = set(self.repository.get_columns())
        else:
            valid_fields = set(records[0].keys()) if records else set()

        if date_field not in valid_fields:
            return records

        def to_date(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d")
            except:
                return None

        start = to_date(start_date) if start_date else None
        end = to_date(end_date) if end_date else None

        result = []
        for r in records:
            v = to_date(r.get(date_field))
            if not v:
                continue
            if start and v < start:
                continue
            if end and v > end:
                continue

            result.append(r)

        return result

# combined filter
    def filter_records(
        self,
        records: List[Dict[str, Any]],
        date_field: str = None,
        start_date: str = None,
        end_date: str = None,
        **field_filters
    ) -> List[Dict[str, Any]]:

        result = self.filter_by_fields(records, **field_filters)

        if date_field:
            result = self.filter_by_date_range(result, date_field, start_date, end_date)

        return result
    

