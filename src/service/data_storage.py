from typing import Dict, Any, List, Optional
from contextlib import contextmanager

from src.interface.data_repository_interface import IDataRepository
from src.infrastructure.sqlite_repository import SQLiteRepository


class DataStorageService:

    def __init__(self, db_path: str):
        self.repository: IDataRepository = SQLiteRepository(db_path)
        self.tables_created = False

    # --- Connection management ---
    def connect(self):
        """Establish or re-establish repository connection."""
        return self.repository.connect()

    def disconnect(self):
        """Close repository connection."""
        return self.repository.disconnect()

    # --- Transaction wrapper ---
    @contextmanager
    def transaction(self):
        self.repository.begin()
        try:
            yield
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            raise

    def get_columns(self) -> List[str]:
        return self.repository.get_columns()

    def save_full_record(self, rows: List[Dict[str, Any]]) -> int:

        if not rows:
            raise ValueError("Cannot store empty data list.")

        if not self.tables_created:
            self.repository.create_tables(rows)
            self.tables_created = True

        return self.repository.save_records(rows)
    
    def get_all_records(self) -> List[Dict[str, Any]]:
        return self.repository.get_all_records()
