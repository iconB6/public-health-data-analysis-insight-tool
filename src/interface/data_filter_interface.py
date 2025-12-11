from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class IDataFilter(ABC):
    @abstractmethod
    def filter_records(
        self,
        records: List[Dict[str, Any]],
        dimension_filters: Optional[Dict[str, str]] = None,
        date_range: Optional[Dict[str, str]] = None,
        metric_filters: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> List[Dict[str, Any]]:
        pass
