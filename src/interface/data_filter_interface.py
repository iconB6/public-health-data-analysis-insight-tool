from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IDataFilter(ABC):
    @abstractmethod
    def filter(
        self, rows: List[Dict[str, Any]], criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Filter rows based on criteria.
        :param rows: list of dict records
        :param criteria: e.g. {"country": "USA", "year": 2024}
        """
        pass
