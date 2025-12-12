from src.service.data_storage import DataStorageService
from src.infrastructure.sqlite_repository import SQLiteRepository


def test_save_and_get_record():
    repo = SQLiteRepository(":memory:")
    service = DataStorageService(repo)

    data = [
        {"date": "2024-01-01", "country": "UK", "value_1": 123},
        {"date": "2024-01-02", "country": "US", "value_1": 456},
        {"date": "2024-01-03", "country": "JP", "value_1": 789},
    ]

    service.save_full_record(data)
    loaded = service.get_all_records()

    assert len(loaded) == 3

    # Check that dynamically created columns match
    expected_keys = {"record_id", "date", "country", "value_1"}

    assert set(loaded[0].keys()) == expected_keys

    # Verify content
    assert loaded[0]["date"] == "2024-01-01"
    assert loaded[1]["country"] == "US"
    assert loaded[2]["value_1"] == 789

    # Special check: record_id must auto-increment
    assert loaded[0]["record_id"] == 1
    assert loaded[1]["record_id"] == 2
    assert loaded[2]["record_id"] == 3

