from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IDataLoader(ABC):
    """
    Interface for data loaders that load raw data
    from various sources (CSV, SQL, APIs, etc.).
    """

    @abstractmethod
    def load(self, source: str) -> List[Dict[str, Any]]:
        """
        Load raw data from a source.
        Return a list of dictionaries.
        Raise ValueError for invalid or empty data.
        """
        pass
