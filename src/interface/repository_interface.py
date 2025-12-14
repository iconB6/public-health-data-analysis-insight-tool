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
        table: str,
        filters: Dict[str, Any],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generic query interface.

        Returns:
            List of rows as dicts
        """
        pass
