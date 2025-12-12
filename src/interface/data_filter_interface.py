from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IDataFilter(ABC):

    @abstractmethod
    def filter_by_fields(self, records: List[Dict[str, Any]], **filters) -> List[Dict[str, Any]]:
        """
        Filter records by given field=value pairs.
        """
        pass

    @abstractmethod
    def filter_by_date_range(
        self,
        records: List[Dict[str, Any]],
        date_field: str,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict[str, Any]]:
        """
        Filter records by date range.
        """
        pass

    @abstractmethod
    def filter_records(
        self,
        records: List[Dict[str, Any]],
        date_field: str = None,
        start_date: str = None,
        end_date: str = None,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Main filter method combining all filters.
        """
        pass
