from typing import Dict, Any
from src.interface.data_repository_interface import IDataRepository


class DataStorageService:

    def __init__(self, repository: IDataRepository):
        self.repository = repository

    def save_full_record(self, data: Dict[str, Any]) -> int:
        """
        {
            "data_source": "API",
            "dimensions": {"country": "UK", "age": "20-29"},
            "metrics": {"cases": 100, "deaths": 2}
        }
        """

        record_id = self.repository.save_record({
            "data_source": data["data_source"]
        })

        if "dimensions" in data and isinstance(data["dimensions"], dict):
            self.repository.save_dimensions(record_id, data["dimensions"])

        if "metrics" in data and isinstance(data["metrics"], dict):
            self.repository.save_metrics(record_id, data["metrics"])

        return record_id

    def get_record(self, record_id: int) -> Dict[str, Any]:
        """
        get record by id
        """
        return self.repository.get_record(record_id)
    
    def get_all_records(self):
        return self.repository.get_all_records()
