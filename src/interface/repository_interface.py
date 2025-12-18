from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import date


class IRepository(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def begin(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def ensure_table(self, table: str, schema: Dict[str, str]):
        """
        Create table if not exists using schema.
        """

    @abstractmethod
    def get_schema(self, table: str) -> Dict[str, str]:
        """
        Return schema mapping for a table: {column: TYPE}
        """

    @abstractmethod
    def insert_rows(
        self,
        table: str,
        rows: List[Dict[str, Any]],
        columns: List[str],
    ) -> int:
        """
        Insert rows and return inserted count.
        """
    
    @abstractmethod
    def query(
        self,
        *,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        conditions: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def query_for_trend(
        self,
        *,
        date_field: str,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        conditions: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch rows filtered by an arbitrary date field for trend computations.
        Implementations should return a list of dict rows where `date_field` values
        are either `datetime.date` or ISO date strings depending on implementation.
        """
        pass

