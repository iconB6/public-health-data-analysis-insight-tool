from typing import Dict, Any, List
from src.interface.data_repository_interface import IDataRepository


class DataStorageService:

    def __init__(self, repository: IDataRepository):
        self.repository = repository
        self.tables_created = False

    def save_full_record(self, rows: List[Dict[str, Any]]) -> int:

        if not rows:
            raise ValueError("Cannot store empty data list.")

        if not self.tables_created:
            self.repository.create_tables(rows)
            self.tables_created = True

        return self.repository.save_records(rows)
    
    def get_all_records(self) -> List[Dict[str, Any]]:
        return self.repository.get_all_records()
