import pytest
import pandas as pd
from src.service.data_summarizer import DataSummarizer


@pytest.fixture
def sample_records():
    return [
        {"date": "2024-01-01", "value": 10, "category": "A"},
        {"date": "2024-01-02", "value": 20, "category": "A"},
        {"date": "2024-01-03", "value": 30, "category": "B"},
    ]


# ----------------------------------------------------------
# 1. Tests for summary_stats
# ----------------------------------------------------------
def test_summary_stats_valid(sample_records):
    summarizer = DataSummarizer()

    df = summarizer.summary_stats(sample_records)

    # Should contain the numeric column "value"
    assert "value" in df.index
    assert list(df.columns) == ["count", "mean", "min", "max"]

    assert df.loc["value", "count"] == 3
    assert df.loc["value", "mean"] == pytest.approx(20)
    assert df.loc["value", "min"] == 10
    assert df.loc["value", "max"] == 30


def test_summary_stats_empty():
    summarizer = DataSummarizer()

    with pytest.raises(ValueError, match="Records list is empty"):
        summarizer.summary_stats([])


def test_summary_stats_no_numeric():
    summarizer = DataSummarizer()
    records = [{"a": "x"}, {"a": "y"}]

    with pytest.raises(ValueError, match="No numeric columns"):
        summarizer.summary_stats(records)


# ----------------------------------------------------------
# 2. Tests for trend_over_time
# ----------------------------------------------------------
def test_trend_over_time_valid(sample_records):
    summarizer = DataSummarizer()

    df = summarizer.trend_over_time(
        sample_records, 
        date_field="date", 
        metric_field="value"
    )

    # Data should be sorted by date
    assert df["value"] == [10, 20, 30]


def test_trend_over_time_missing_date_field(sample_records):
    summarizer = DataSummarizer()

    with pytest.raises(ValueError, match="Date field 'wrong' not found"):
        summarizer.trend_over_time(sample_records, "wrong", "value")


def test_trend_over_time_missing_metric_field(sample_records):
    summarizer = DataSummarizer()

    with pytest.raises(ValueError, match="Metric field 'wrong' not found"):
        summarizer.trend_over_time(sample_records, "date", "wrong")


def test_trend_over_time_bad_date_format():
    summarizer = DataSummarizer()
    records = [{"date": "2024/01/01", "value": 10}]

    with pytest.raises(ValueError, match="Date format must be YYYY-MM-DD"):
        summarizer.trend_over_time(records, "date", "value")


# ----------------------------------------------------------
# 3. Tests for group_by
# ----------------------------------------------------------
def test_group_by_valid(sample_records):
    summarizer = DataSummarizer()

    df = summarizer.group_by(sample_records, "category", "value")

    assert "A" in df.index
    assert "B" in df.index

    assert df.loc["A", "count"] == 2
    assert df.loc["A", "mean"] == pytest.approx(15)
    assert df.loc["B", "mean"] == 30


def test_group_by_missing_group_field(sample_records):
    summarizer = DataSummarizer()

    with pytest.raises(ValueError, match="Group field 'wrong' not found"):
        summarizer.group_by(sample_records, "wrong", "value")


def test_group_by_missing_metric_field(sample_records):
    summarizer = DataSummarizer()

    with pytest.raises(ValueError, match="Metric field 'wrong' not found"):
        summarizer.group_by(sample_records, "category", "wrong")


def test_group_by_empty():
    summarizer = DataSummarizer()

    with pytest.raises(ValueError, match="Records list is empty"):
        summarizer.group_by([], "category", "value")
