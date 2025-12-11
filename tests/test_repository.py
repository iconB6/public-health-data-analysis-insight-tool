from src.service.data_storage import DataStorageService
from src.infrastructure.sqlite_repository import SQLiteRepository


def test_save_and_get_record():
    repo = SQLiteRepository(":memory:")
    service = DataStorageService(repo)

    data = {
        "data_source": "TestAPI",
        "dimensions": {"country": "UK", "year": "2023"},
        "metrics": {"cases": 10, "deaths": 1},
    }

    record_id = service.save_full_record(data)
    result = service.get_record(record_id)

    assert result["data_source"] == "TestAPI"
    assert result["dimensions"]["country"] == "UK"
    assert result["metrics"]["cases"] == 10

