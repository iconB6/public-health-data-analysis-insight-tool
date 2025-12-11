from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IDataCleaner(ABC):
    """
    Interface for data cleaning and structuring.
    """

    @abstractmethod
    def clean(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Basic cleaning: missing values, types, etc.
        """
        pass

    @abstractmethod
    def to_structured_records(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert cleaned flat rows into:
        - record_data
        - dimensions
        - metrics
        """
        pass
