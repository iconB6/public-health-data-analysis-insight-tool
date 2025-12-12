import os
from src.service.data_loader import DataLoadingService
from src.service.data_cleaner import DataCleaner
from src.service.data_storage import DataStorageService
from src.service.data_filter import DataFilter
from src.infrastructure.sqlite_repository import SQLiteRepository


def test_integration_filter_pipeline():
    # ---------- 1. Load CSV ----------
    loader_service = DataLoadingService()
    csv_path = "tests/data/sample.csv"
    rows = loader_service.load_data("csv", csv_path)

    assert len(rows) > 0

    # ---------- 2. Clean ----------
    cleaner = DataCleaner()
    cleaned = cleaner.clean(rows)

    # ---------- 3. Store in SQLite ----------
    repo = SQLiteRepository(":memory:")
    storage = DataStorageService(repo)
    stored_count = storage.save_full_record(cleaned)

    # Must have stored all rows
    all_records = storage.get_all_records()
    assert len(all_records) == stored_count

    # ---------- 4. Filter ----------
    filter_service = DataFilter()

    # Example filter: filter by dimension field
    filtered_by_country = filter_service.filter_by_fields(all_records, country="UK")
    assert all(r["country"] == "UK" for r in filtered_by_country)

    # Example: date range filter (assuming sample.csv contains a "date" column)
    filtered_by_date = filter_service.filter_by_date_range(
        all_records, start_date="2024-04-01",
        end_date="2024-07-01"
    )
    assert len(filtered_by_date) == 4

