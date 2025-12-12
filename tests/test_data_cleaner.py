from src.service.data_cleaner import DataCleaner
import datetime
import pandas as pd


def test_clean_basic_null_and_numbers():
    cleaner = DataCleaner()

    rows = [
        {"a": " 123 ", "b": "NA", "c": "1,234"},
        {"a": "3.14", "b": "None", "c": "  2024-01-02  "}
    ]

    cleaned = cleaner.clean(rows)

    assert cleaned[0]["a"] == 123
    assert cleaned[0]["b"] is None
    assert cleaned[0]["c"] == 1234.0

    assert cleaned[1]["a"] == 3.14
    assert cleaned[1]["b"] is None
    assert cleaned[1]["c"] == datetime.date(2024, 1, 2)


def test_clean_skips_empty_rows():
    cleaner = DataCleaner()
    rows = [
        {"a": None, "b": None},
        {"a": "", "b": ""}
    ]
    cleaned = cleaner.clean(rows)
    assert cleaned == []


def test_dataframe_output():
    cleaner = DataCleaner()

    rows = [
        {"country": "UK", "value_1": 100, "age": "20-29"},
        {"country": "US", "value_1": 200, "age": "30-39"},
    ]

    df = cleaner.to_dataframe_records(rows)

    # --- basic shape ---
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 3)

    # --- columns preserved ---
    assert list(df.columns) == ["country", "value_1", "age"]

    # --- values correct ---
    assert df.loc[0, "country"] == "UK"
    assert df.loc[1, "value_1"] == 200
