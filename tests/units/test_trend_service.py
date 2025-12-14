import pytest
import datetime
from src.service.trend_service import TrendService


'''
TrendService tests verify time-series aggregation over records.

The service must:
- query data via repository (no SQL)
- group records by date field
- aggregate numeric values using count / sum / mean
- respect date range filters
- return ordered date-value pairs
- validate input types and propagate repository errors
'''
# ========== TEST DATA ==========

ROWS_BASIC = [
    {"DATE": datetime.date(2024, 1, 1), "VALUE": 10},
    {"DATE": datetime.date(2024, 1, 1), "VALUE": 20},
    {"DATE": datetime.date(2024, 1, 2), "VALUE": 5},
]

ROWS_WITH_NULLS = [
    {"DATE": datetime.date(2024, 1, 1), "VALUE": None},
    {"DATE": datetime.date(2024, 1, 1), "VALUE": 10},
]

ROWS_EMPTY = []

# ========= EXPECTED RESULTS ==========

EXPECTED_COUNT = {
    "date": [datetime.date(2024, 1, 1), datetime.date(2024, 1, 2)],
    "value": [2, 1],
}

EXPECTED_SUM = {
    "date": [datetime.date(2024, 1, 1), datetime.date(2024, 1, 2)],
    "value": [30, 5],
}

EXPECTED_MEAN = {
    "date": [datetime.date(2024, 1, 1), datetime.date(2024, 1, 2)],
    "value": [15, 5],
}

# ========= FIXTURES ==========

class FakeRepository:
    def __init__(self, rows):
        self._rows = rows

    def query_for_trend(self, trend_data):
        return object()  

    def show(self, figure):
        pass

    def export(self, figure, path):
        pass


class BrokenRepository:
    def query_for_trend(self, **kwargs):
        raise RuntimeError("database error")


@pytest.fixture
def basic_service():
    return TrendService(FakeRepository(ROWS_BASIC))


@pytest.fixture
def null_service():
    return TrendService(FakeRepository(ROWS_WITH_NULLS))


@pytest.fixture
def empty_service():
    return TrendService(FakeRepository(ROWS_EMPTY))


@pytest.fixture
def broken_service():
    return TrendService(BrokenRepository())

# ========== Normal cases ==========

def test_trend_count(basic_service):
    result = basic_service.trend_over_time(
        date_field="DATE",
        metric_field="VALUE",
        agg="count",
    )

    assert result["date"] == EXPECTED_COUNT["date"]
    assert result["value"] == EXPECTED_COUNT["value"]


def test_trend_sum(basic_service):
    result = basic_service.trend_over_time(
        date_field="DATE",
        metric_field="VALUE",
        agg="sum",
    )

    assert result["value"] == EXPECTED_SUM["value"]


def test_trend_mean(basic_service):
    result = basic_service.trend_over_time(
        date_field="DATE",
        metric_field="VALUE",
        agg="mean",
    )

    assert result["value"] == EXPECTED_MEAN["value"]

# ========== Edge cases ==========

def test_trend_ignores_null_values(null_service):
    result = null_service.trend_over_time(
        date_field="DATE",
        metric_field="VALUE",
        agg="mean",
    )

    assert result["value"] == [10]


def test_trend_empty_result(empty_service):
    result = empty_service.trend_over_time(
        date_field="DATE",
        metric_field="VALUE",
        agg="count",
    )

    assert result["date"] == []
    assert result["value"] == []

# ========== Invalid cases ==========

def test_trend_invalid_date_field_type(basic_service):
    with pytest.raises(TypeError):
        basic_service.trend_over_time(
            date_field=123,
            metric_field="VALUE",
        )


def test_trend_invalid_metric_field_type(basic_service):
    with pytest.raises(TypeError):
        basic_service.trend_over_time(
            date_field="DATE",
            metric_field=456,
        )


def test_trend_invalid_aggregation(basic_service):
    with pytest.raises(ValueError):
        basic_service.trend_over_time(
            date_field="DATE",
            metric_field="VALUE",
            agg="median",
        )

# ========== Exception cases ==========

def test_repository_exception_propagates(broken_service):
    with pytest.raises(RuntimeError):
        broken_service.trend_over_time(
            date_field="DATE",
            metric_field="VALUE",
        )
