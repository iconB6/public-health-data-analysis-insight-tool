import pytest
from src.service.summarizer_service import Summarizer


@pytest.fixture
def sample_records():
    return [
        {
            "record_id": 1,
            "data_source": "A",
            "dimensions": {"country": "USA", "date": "2023-01-01"},
            "metrics": {"population": 100}
        },
        {
            "record_id": 2,
            "data_source": "A",
            "dimensions": {"country": "USA", "date": "2023-02-01"},
            "metrics": {"population": 200}
        },
        {
            "record_id": 3,
            "data_source": "B",
            "dimensions": {"country": "Japan", "date": "2023-01-15"},
            "metrics": {"population": 150}
        },
    ]


def test_summary_stats(sample_records):
    s = Summarizer()
    summary = s.summary_stats(sample_records, "population")

    assert summary["count"] == 3
    assert summary["mean"] == 150
    assert summary["min"] == 100
    assert summary["max"] == 200


def test_trend_over_time(sample_records):
    s = Summarizer()
    trend = s.trend_over_time(sample_records, "date", "population")

    assert trend[0]["date"] == "2023-01-01"
    assert trend[-1]["date"] == "2023-02-01"
    assert trend[0]["population"] == 100


def test_group_by(sample_records):
    s = Summarizer()
    group = s.group_by(sample_records, "country", "population")

    assert group["USA"]["count"] == 2
    assert group["USA"]["mean"] == 150
    assert group["Japan"]["min"] == 150
