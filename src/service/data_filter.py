from typing import List, Dict, Any
from src.interface.data_filter_interface import IDataFilter
from datetime import datetime, date


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

        field_map = {f.upper(): f for f in valid_fields}

        result = records
        matched_any_field = False

        for raw_field, value in field_filters.items():
            if value is None:
                continue

            key_upper = raw_field.strip().upper()

            if key_upper not in field_map:
                continue  

            matched_any_field = True
            field = field_map[key_upper]  

            result = [
                r for r in result
                if (
                    isinstance(r.get(field), str)
                    and isinstance(value, str)
                    and r.get(field).strip().upper() == value.strip().upper()
                ) or r.get(field) == value
            ]
        # if no fields matched, raise exception
        if not matched_any_field:
            raise Exception("[Empty dataset] No valid filter fields matched.")

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

        def normalize(s: str) -> str:
            return (
                s.lstrip("\ufeff")
                .strip()
                .upper()
            )

        normalized_map = {normalize(f): f for f in valid_fields}
        target = normalize(date_field)

        if target not in normalized_map:
            raise ValueError(
                f"Date field '{date_field}' not found. "
                f"Available fields: {valid_fields}"
            )

        real_field = normalized_map[target]

        def to_date(v):
            if v is None:
                return None

            if isinstance(v, datetime):
                return v
            if isinstance(v, date):
                return datetime.combine(v, datetime.min.time())

            if isinstance(v, str):
                v = v.strip()
                for fmt in (
                    "%Y-%m-%d",
                    "%Y/%m/%d",
                    "%d-%m-%Y",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y%m%d",
                ):
                    try:
                        return datetime.strptime(v, fmt)
                    except ValueError:
                        continue
            return None

        start = to_date(start_date) if start_date else None
        end = to_date(end_date) if end_date else None

        if start_date and not start:
            raise ValueError(f"Invalid start_date: {start_date}")
        if end_date and not end:
            raise ValueError(f"Invalid end_date: {end_date}")

        if start and end and start > end:
            raise ValueError(
                f"Invalid date range: start_date ({start_date}) "
                f"is later than end_date ({end_date})"
            )

        # ---------- filtering ----------
        result = []
        for r in records:
            v = to_date(r.get(real_field))
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
    

