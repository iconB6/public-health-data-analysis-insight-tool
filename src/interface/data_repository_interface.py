from abc import ABC, abstractmethod
from typing import Dict, Any, List


class IDataRepository(ABC):
    """
    Interface for saving records into a persistent storage.
    """

    @abstractmethod
    def save_record(self, record_data: Dict[str, Any]) -> int:
        """
        Save a single record.
        Should return the generated record_id.
        """
        pass

    @abstractmethod
    def save_dimensions(self, record_id: int, dimensions: Dict[str, str]) -> None:
        """
        Save key-value dimensional data.
        """
        pass

    @abstractmethod
    def save_metrics(self, record_id: int, metrics: Dict[str, float]) -> None:
        """
        Save metric key-value pairs.
        """
        pass

    @abstractmethod
    def get_record(self, record_id: int) -> Dict[str, Any]:
        """
        Load a record and its related dimensions/metrics.
        """
        pass
