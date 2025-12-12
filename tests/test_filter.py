import pytest
from datetime import datetime
from src.service.data_filter import DataFilter


class FakeRepository:
    def __init__(self, columns):
        self.columns = columns

    def get_columns(self):
        return self.columns

@pytest.fixture
def sample_records():
    return [
        {"country": "China", "date": "2024-01-10", "value": "10"},
        {"country": "China", "date": "2024-02-05", "value": "15"},
        {"country": "Japan", "date": "2024-03-01", "value": "20"},
        {"country": "USA", "date": "2023-12-31", "value": "12"},
    ]

@pytest.fixture
def data_filter():
    repo = FakeRepository(columns=["country", "date", "value"])
    return DataFilter(repository=repo)


def test_filter_by_fields(data_filter, sample_records):
    result = data_filter.filter_by_fields(sample_records, country="China")
    assert len(result) == 2
    assert all(r["country"] == "China" for r in result)


def test_filter_unknown_field_ignored(data_filter, sample_records):
    result = data_filter.filter_by_fields(sample_records, unknown="X")
    assert len(result) == 4  # unchanged


def test_filter_by_date_range_start(data_filter, sample_records):
    result = data_filter.filter_by_date_range(
        sample_records,
        date_field="date",
        start_date="2024-01-01"
    )
    assert len(result) == 3  # 3 after 2024-01-01


def test_filter_by_date_range_full(data_filter, sample_records):
    result = data_filter.filter_by_date_range(
        sample_records,
        date_field="date",
        start_date="2024-01-01",
        end_date="2024-02-28"
    )
    assert len(result) == 2
    assert all(r["country"] == "China" for r in result)


def test_filter_records_combined(data_filter, sample_records):
    """
    China + date >= 2024-02-01
    """
    result = data_filter.filter_records(
        sample_records,
        date_field="date",
        start_date="2024-02-01",
        country="China"
    )
    assert len(result) == 1
    assert result[0]["date"] == "2024-02-05"


def test_filter_no_filters_return_all(data_filter, sample_records):
    result = data_filter.filter_records(sample_records)
    assert len(result) == 4