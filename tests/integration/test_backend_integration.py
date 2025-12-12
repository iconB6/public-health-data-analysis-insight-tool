import os
from src.service.data_loader import DataLoadingService
from src.service.data_cleaner import DataCleaner
from src.service.data_storage import DataStorageService
from src.service.data_filter import DataFilter
from src.service.data_summarizer import DataSummarizer   # ⭐ 新增
from src.infrastructure.sqlite_repository import SQLiteRepository


def test_integration_full_pipeline_with_summarizer():
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

    all_records = storage.get_all_records()
    assert len(all_records) == stored_count

    # ---------- 4. Filter ----------
    filter_service = DataFilter()

    # Example filter: filter by dimension field
    filtered_by_country = filter_service.filter_by_fields(all_records, country="UK")
    assert all(r["country"] == "UK" for r in filtered_by_country)

    # Example: date range filter
    filtered_by_date = filter_service.filter_by_date_range(
        all_records,
        start_date="2024-04-01",
        end_date="2024-07-01",
    )
    assert len(filtered_by_date) == 4

    # ===============================================================
    # 5. Summarizer Integration Tests
    # ===============================================================

    summarizer = DataSummarizer()

    # ---------- 5.1 Summary Stats ----------
    stats_df = summarizer.summary_stats(all_records)

    # Ensure dataframe is created
    assert not stats_df.empty
    # Ensure required rows exist
    for stat in ["count", "mean", "min", "max"]:
        assert stat in stats_df.columns

    # ---------- 5.2 Trend Over Time ----------
    # Expect returned dataframe with date + metric
    trend_df = summarizer.trend_over_time(
        all_records,
        date_field="date",
        metric_field="value_1"  
    )

    assert set(trend_df.keys()) == {
            "date", "value", "date_field", "metric_field", "dataframe"
        }
    assert len(trend_df) > 0
    df = trend_df["dataframe"]
    assert list(df.columns) == ["date", "value_1"]

    # ---------- 5.3 Group By ----------
    group_df = summarizer.group_by(
        all_records,
        group_field="country",
        metric_field="value_1",  
    )

    assert not group_df.empty
    for col in ["count", "mean", "min", "max"]:
        assert col in group_df.columns

