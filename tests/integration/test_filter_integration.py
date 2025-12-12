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
    structured = cleaner.to_structured_records(cleaned)

    assert len(structured) == len(cleaned)

    # ---------- 3. Store in SQLite ----------
    repo = SQLiteRepository(":memory:")
    storage = DataStorageService(repo)

    for record in structured:
        storage.save_full_record({
            "data_source": record["record_data"].get("data_source", "csv"),
            "dimensions": record["dimensions"],
            "metrics": record["metrics"]
        })

    # Must have stored all rows
    all_records = storage.get_all_records()
    assert len(all_records) == len(structured)

    # ---------- 4. Filter ----------
    filter_service = DataFilter()

    # Example filter: filter by dimension field
    filtered_by_country = filter_service.filter_records(
        all_records,
        dimension_filters={"country": "UK"}
    )
    assert all(r["dimensions"].get("country") == "UK" for r in filtered_by_country)

    # Example: date range filter (assuming sample.csv contains a "date" column)
    filtered_by_date = filter_service.filter_records(
        all_records,
        date_range={"start": "2020-01-01", "end": "2020-12-31"}
    )
    for r in filtered_by_date:
        assert "date" in r["dimensions"]

    # Example: metric filter (assuming metrics contain "cases")
    filtered_by_metrics = filter_service.filter_records(
        all_records,
        metric_filters={"cases": {">=": 100}}
    )
    for r in filtered_by_metrics:
        assert r["metrics"]["cases"] >= 100

    # If sample.csv doesn’t contain such fields, remove or adjust tests accordingly.
