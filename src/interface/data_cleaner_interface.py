from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IDataCleaner(ABC):
    """
    Interface for data cleaning operations.
    """

    @abstractmethod
    def clean(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean raw loader output.
        - Handle missing or inconsistent data
        - Convert types (dates, numbers)
        - Produce normalized list of records
        """
        pass
