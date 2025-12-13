from src.service.data_storage import DataStorageService
from src.infrastructure.sqlite_repository import SQLiteRepository


def test_save_and_get_record():
    service = DataStorageService(":memory:")

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

    # --- Test connect / disconnect behaviour ---
    # force close underlying connection and reconnect
    service.connect()
    assert getattr(repo, "conn") is not None
    service.disconnect()
    assert getattr(repo, "conn") is None

    # Recreate and ensure previous data still empty after reconnect
    service.connect()
    # for in-memory DB a fresh connection has no tables; reset flag so tables get created again
    service.tables_created = False

    # --- Test execute_query returns rows for SELECT ---
    # Insert initial data again to ensure table exists and rows present
    service.save_full_record(data)
    res = service.execute_query("SELECT country FROM records WHERE record_id = ?", (2,))
    assert isinstance(res, list)
    assert res[0]["country"] == "US"

    # --- Test transaction rollback on exception ---
    before_count = len(service.get_all_records())
    import pytest

    with pytest.raises(ValueError):
        with service.transaction():
            service.execute_query(
                "INSERT INTO records (date, country, value_1) VALUES (?,?,?)",
                ("2025-01-01", "CN", 111),
            )
            raise ValueError("force rollback")

    after_count = len(service.get_all_records())
    assert before_count == after_count

    # --- Test transaction commit ---
    with service.transaction():
        service.execute_query(
            "INSERT INTO records (date, country, value_1) VALUES (?,?,?)",
            ("2025-01-02", "CN", 222),
        )

    all_rows = service.get_all_records()
    # ensure a new row was committed
    assert any(r.get("country") == "CN" and r.get("value_1") == 222 for r in all_rows)

    # --- Test executemany through service ---
    params = [
        ("2025-02-01", "AA", 1),
        ("2025-02-02", "BB", 2),
    ]
    with service.transaction():
        service.executemany(
            "INSERT INTO records (date, country, value_1) VALUES (?,?,?)", params
        )

    # final count should have increased by 3 (one commit + two executemany)
    assert len(service.get_all_records()) >= before_count + 3

    # --- Test get_columns proxy ---
    cols = set(service.get_columns())
    assert {"record_id", "date", "country", "value_1"}.issubset(cols)

