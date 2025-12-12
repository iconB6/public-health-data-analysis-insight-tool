from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IDataRepository(ABC):
    """
    Abstract interface for a generic data repository.
    Concrete implementations: SQLiteRepository, MemoryRepository, etc.
    """

    @abstractmethod
    def create_tables(self, rows: List[Dict[str, Any]]) -> None:
        """
        Create database tables dynamically based on keys in row dictionaries.
        This must be called before saving records.
        """
        pass

    @abstractmethod
    def save_records(self, rows: List[Dict[str, Any]]) -> int:
        """
        Insert multiple records into storage.
        Should return the number of inserted rows.
        """
        pass

    @abstractmethod
    def get_all_records(self) -> List[Dict[str, Any]]:
        """
        Retrieve all stored records as List[Dict[str, Any]].
        """
        pass

    @abstractmethod
    def get_columns(self) -> List[str]:
        """
        Return all columns of the records table.
        """
        pass
