import os
from unittest.mock import MagicMock
from src.service.data_loader import DataLoadingService
from src.service.data_cleaner import DataCleaner
from src.service.data_storage import DataStorageService


def test_full_integration_pipeline():
    """
    Integration test:
    loader → cleaner → structured → storage
    """

    # --- 1. Load data from CSV ---
    loader = DataLoadingService()

    csv_path = os.path.join("tests", "data", "sample.csv")
    raw_rows = loader.load_data("csv", csv_path)

    assert isinstance(raw_rows, list)
    assert len(raw_rows) > 0

    # --- 2. Clean data ---
    cleaner = DataCleaner()
    cleaned = cleaner.clean(raw_rows)

    assert len(cleaned) == len(raw_rows)
    assert all(isinstance(r, dict) for r in cleaned)

    # --- 3. Convert to structured records ---
    structured = cleaner.to_structured_records(cleaned)

    assert isinstance(structured, list)
    assert len(structured) == len(cleaned)
    assert "dimensions" in structured[0]
    assert "metrics" in structured[0]

    # --- 4. Save using mocked repository ---
    mock_repo = MagicMock()
    mock_repo.save_record.return_value = 1  # simulate auto-increment id

    storage = DataStorageService(mock_repo)

    for record in structured:
        record_id = storage.save_full_record(record)
        assert record_id == 1

    # repo interactions check
    assert mock_repo.save_record.call_count == len(structured)
    assert mock_repo.save_dimensions.call_count == len(structured)
    assert mock_repo.save_metrics.call_count == len(structured)