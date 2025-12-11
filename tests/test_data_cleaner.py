import datetime
from src.service.data_cleaner import DataCleaner


def test_cleaner_handles_missing_data():
    cleaner = DataCleaner()

    rows = [
        {"name": "Alice", "age": "20"},
        {"name": "", "age": "30"},           # empty name → None
        {"name": "   Bob   ", "age": "40"},   # trim whitespace
        {"name": None, "age": None},         # fully empty row → removed
    ]

    result = cleaner.clean(rows)
    assert len(result) == 3
    assert result[1]["name"] is None


def test_cleaner_converts_numbers():
    cleaner = DataCleaner()

    rows = [
        {"x": "10", "y": "3.14", "z": "hello"}
    ]

    result = cleaner.clean(rows)[0]

    assert result["x"] == 10
    assert result["y"] == 3.14
    assert result["z"] == "hello"


def test_cleaner_converts_dates():
    cleaner = DataCleaner()

    rows = [
        {"date1": "2024-01-01", "date2": "01/02/2024"}
    ]

    result = cleaner.clean(rows)[0]

    assert isinstance(result["date1"], datetime.date)
    assert isinstance(result["date2"], datetime.date)


def test_cleaner_removes_fully_empty_rows():
    cleaner = DataCleaner()

    rows = [
        {"a": "1"},
        {"a": ""},        # → cleaned to None
        {"a": None},      # fully empty row → removed
    ]

    result = cleaner.clean(rows)
    assert len(result) == 2
