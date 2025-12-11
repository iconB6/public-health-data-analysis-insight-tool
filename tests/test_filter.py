import pytest
from datetime import datetime
from src.service.data_filter import DataFilter


@pytest.fixture
def sample_records():
    return [
        {
            "record_id": 1,
            "data_source": "A",
            "dimensions": {
                "country": "USA",
                "date": "2023-01-10",
                "age_group": "20-29"
            },
            "metrics": {
                "population": 500,
                "growth": 1.2
            }
        },
        {
            "record_id": 2,
            "data_source": "A",
            "dimensions": {
                "country": "Japan",
                "date": "2023-02-15",
                "age_group": "30-39"
            },
            "metrics": {
                "population": 800,
                "growth": 0.9
            }
        },
        {
            "record_id": 3,
            "data_source": "B",
            "dimensions": {
                "country": "USA",
                "date": "2023-03-05",
                "age_group": "20-29"
            },
            "metrics": {
                "population": 300,
                "growth": 1.5
            }
        },
    ]


def test_filter_by_dimension(sample_records):
    f = DataFilter()

    result = f.filter_records(
        sample_records,
        dimension_filters={"country": "USA"}
    )

    assert len(result) == 2
    assert all(r["dimensions"]["country"] == "USA" for r in result)


def test_filter_by_multiple_dimensions(sample_records):
    f = DataFilter()

    result = f.filter_records(
        sample_records,
        dimension_filters={
            "country": "USA",
            "age_group": "20-29"
        }
    )

    assert len(result) == 2
    for r in result:
        assert r["dimensions"]["country"] == "USA"
        assert r["dimensions"]["age_group"] == "20-29"


def test_filter_by_date_range(sample_records):
    f = DataFilter()

    result = f.filter_records(
        sample_records,
        date_range={
            "start": "2023-02-01",
            "end": "2023-03-01"
        }
    )

    assert len(result) == 1
    assert result[0]["record_id"] == 2


def test_filter_combined_dimensions_and_date(sample_records):
    f = DataFilter()

    result = f.filter_records(
        sample_records,
        dimension_filters={"country": "USA"},
        date_range={"start": "2023-02-01", "end": "2023-04-01"}
    )

    assert len(result) == 1
    assert result[0]["record_id"] == 3


def test_filter_by_metric_greater_than(sample_records):
    f = DataFilter()

    result = f.filter_records(
        sample_records,
        metric_filters={"population": {">": 400}}
    )

    assert len(result) == 2
    assert {r["record_id"] for r in result} == {1, 2}


def test_filter_by_metric_less_than(sample_records):
    f = DataFilter()

    result = f.filter_records(
        sample_records,
        metric_filters={"growth": {"<": 1.0}}
    )

    assert len(result) == 1
    assert result[0]["record_id"] == 2


def test_filter_by_metric_equals(sample_records):
    f = DataFilter()

    result = f.filter_records(
        sample_records,
        metric_filters={"population": {"==": 300}}
    )

    assert len(result) == 1
    assert result[0]["record_id"] == 3


def test_combined_dimension_date_metric(sample_records):
    f = DataFilter()

    result = f.filter_records(
        sample_records,
        dimension_filters={"country": "USA"},
        date_range={"start": "2023-01-01", "end": "2023-02-01"},
        metric_filters={"population": {">": 400}}
    )

    assert len(result) == 1
    assert result[0]["record_id"] == 1


def test_no_filters_returns_all(sample_records):
    f = DataFilter()

    result = f.filter_records(sample_records)

    assert len(result) == 3
