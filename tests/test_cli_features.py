import os
from src.service.data_loader import DataLoadingService
from src.service.data_cleaner import DataCleaner
from src.service.data_storage import DataStorageService
from src.infrastructure.sqlite_repository import SQLiteRepository
from presentation.visualization import groupby_fields, plot_time_series


def setup_storage_with_sample():
    loader = DataLoadingService()
    cleaner = DataCleaner()

    rows = loader.load_data("csv", os.path.join("tests", "data", "sample.csv"))
    cleaned = cleaner.clean(rows)

    repo = SQLiteRepository(":memory:")
    storage = DataStorageService(repo)
    storage.connect()
    with storage.transaction():
        storage.save_full_record(cleaned)

    return storage


def test_groupby_fields_basic():
    storage = setup_storage_with_sample()

    grouped = groupby_fields(storage, "records", ["country"], {"value_1": "mean"})

    assert grouped is not None
    # basic columns
    for col in ["count", "mean", "min", "max"]:
        assert col in grouped.columns
    # ensure at least one expected country present
    assert any(idx in ["BTN", "CHL", "CZE", "ESP"] for idx in grouped.index)


def test_plot_time_series_creates_file_and_cleans():
    storage = setup_storage_with_sample()

    out = plot_time_series(storage, "records", "date", "value_1")
    assert out is not None
    assert os.path.exists(out)

    # cleanup
    try:
        os.remove(out)
    except OSError:
        pass
