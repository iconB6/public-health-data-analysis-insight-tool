from src.service.data_cleaner import DataCleaner
import datetime


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


def test_structured_output():
    cleaner = DataCleaner()

    rows = [
        {"data_source": "test", "country": "UK", "value": "12"}
    ]

    cleaned = cleaner.clean(rows)
    structured = cleaner.to_structured_records(cleaned)[0]

    assert structured["record_data"] == {"data_source": "test"}
    assert structured["dimensions"] == {"country": "UK"}
    assert structured["metrics"] == {"value": 12.0}
