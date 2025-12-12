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

    @abstractmethod
    def connect(self):
        """
        Establish connection to the data repository.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Close connection to the data repository.
        """
        pass

    @abstractmethod
    def execute(self, query: str, params: tuple = ()) -> Any:
        """
        Execute a single SQL statement and return the cursor/result.
        Implementations may return a DB-API cursor or driver-specific result.
        """
        pass

    @abstractmethod
    def executemany(self, query: str, params_list: List[tuple]) -> Any:
        """
        Execute the same SQL with a sequence of parameter tuples.
        """
        pass

    @abstractmethod
    def begin(self):
        """
        Begin a transaction context if the backend supports it.
        """
        pass

    @abstractmethod
    def commit(self):
        """
        Commit the current transaction.
        """
        pass

    @abstractmethod
    def rollback(self):
        """
        Roll back the current transaction.
        """
        pass

    @abstractmethod
    def __enter__(self):
        """
        Optional context-manager enter. Should return the repository/connection object.
        """
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Optional context-manager exit. Should commit on success or rollback on error.
        """
        pass
