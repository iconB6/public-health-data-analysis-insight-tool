import os
from src.service.data_loader import DataLoadingService
from src.service.data_cleaner import DataCleaner
from src.service.data_storage import DataStorageService
from src.infrastructure.sqlite_repository import SQLiteRepository
from src.service.data_filter import DataFilter
from src.service.summarizer_service import Summarizer


def test_full_pipeline_integration():
    """
    Integration test:
    Load CSV -> Clean -> Structure -> Store -> Load All -> Filter -> Summarize
    """

    # -------------------------------
    # 1. Load CSV
    # -------------------------------
    loader_service = DataLoadingService()
    csv_path = "tests/data/sample.csv"     # Already exists in your repo
    rows = loader_service.load_data("csv", csv_path)

    assert len(rows) > 0

    # -------------------------------
    # 2. Clean data
    # -------------------------------
    cleaner = DataCleaner()
    cleaned_rows = cleaner.clean(rows)

    assert len(cleaned_rows) == len(rows)

    # -------------------------------
    # 3. Convert to structured format
    # -------------------------------
    structured = cleaner.to_structured_records(cleaned_rows)
    assert isinstance(structured, list)
    assert "record_data" in structured[0]
    assert "dimensions" in structured[0]
    assert "metrics" in structured[0]

    # -------------------------------
    # 4. Store into SQLite
    # -------------------------------
    repo = SQLiteRepository()   # in-memory DB
    storage = DataStorageService(repo)

    for item in structured:
        storage.save_full_record(item)

    # Confirm inserted
    all_records = repo.get_all_records()
    assert len(all_records) == len(structured)

    # -------------------------------
    # 5. Filter
    # -------------------------------
    data_filter = DataFilter()

    # try filter: dimension filter (if sample.csv has country column)
    filtered = data_filter.filter_records(
        all_records,
        dimension_filters={"country": "CZE"}  # adjust based on your CSV
    )

    # filtered may be empty depending on sample.csv, so no strict assert here
    assert isinstance(filtered, list)

    # -------------------------------
    # 6. Summaries
    # -------------------------------
    summarizer = Summarizer()

    # summary stats
    stats = summarizer.summary_stats(all_records, metric="value_1")  # adjust metric name
    assert "count" in stats and "mean" in stats

    # trend over time (if "date" exists)
    trend = summarizer.trend_over_time(all_records, date_key="date", metric="value_1")
    assert isinstance(trend, list)

    # group by (if "country" exists)
    grouped = summarizer.group_by(all_records, group_key="country", metric="value_1")
    assert isinstance(grouped, dict)

    # -------------------------------
    # Test successful
    # -------------------------------
    print("Integration test pipeline passed.")
