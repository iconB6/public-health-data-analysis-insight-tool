import pytest
from src.service.summary_service import SummaryService

"""
SummaryService tests verify table-level and filtered summaries.
It must count total records, compute value counts for categorical fields,
and calculate min/max/mean for numeric fields.
Null values are ignored, empty input is handled, and repository errors propagate.
"""


# ========== TEST DATA ==========

ROWS_NORMAL = [
    {"id": 1, "COUNTRY": "USA", "AGE": 30, "SCORE": 80.0},
    {"id": 2, "COUNTRY": "USA", "AGE": 40, "SCORE": 90.0},
    {"id": 3, "COUNTRY": "UK",  "AGE": 35, "SCORE": 85.0},
]

ROWS_WITH_NULLS = [
    {"id": 1, "COUNTRY": "USA", "AGE": None, "SCORE": 80.0},
    {"id": 2, "COUNTRY": None,  "AGE": 40,   "SCORE": None},
]

ROWS_EMPTY = []

SCHEMA = {
    "id": "INTEGER",
    "COUNTRY": "TEXT",
    "AGE": "INTEGER",
    "SCORE": "REAL",
}

# ========= EXPECTED RESULTS ==========

EXPECTED_META_NORMAL = {"total_records": 3}

EXPECTED_COUNTRY_COUNTS = {
    "USA": 2,
    "UK": 1,
}

EXPECTED_AGE_STATS = {
    "min": 30,
    "max": 40,
    "mean": 35,
}

# ========= FIXTURES ==========



class FakeRepository:
    def __init__(self, rows):
        self._rows = rows

    def query(self):
        return self._rows

    def get_schema(self, table_name="records"):
        return SCHEMA


@pytest.fixture
def summary_service_normal():
    return SummaryService(FakeRepository(ROWS_NORMAL))


@pytest.fixture
def summary_service_with_nulls():
    return SummaryService(FakeRepository(ROWS_WITH_NULLS))


@pytest.fixture
def summary_service_empty():
    return SummaryService(FakeRepository(ROWS_EMPTY))


# ========== Normal cases ==========

def test_summary_full_table(summary_service_normal):
    result = summary_service_normal.summarize()

    assert result["meta"] == EXPECTED_META_NORMAL

    country_counts = {
        item["value"]: item["count"]
        for item in result["categorical"]["COUNTRY"]
    }
    assert country_counts == EXPECTED_COUNTRY_COUNTS

    assert result["numeric"]["AGE"] == EXPECTED_AGE_STATS


def test_summary_from_filtered_rows(summary_service_normal):
    filtered = [
        {"id": 1, "COUNTRY": "USA", "AGE": 30, "SCORE": 80.0},
        {"id": 2, "COUNTRY": "USA", "AGE": 40, "SCORE": 90.0},
    ]

    result = summary_service_normal.summarize(filtered)

    assert result["meta"]["total_records"] == 2
    assert result["numeric"]["AGE"]["mean"] == 35


# ========== Edge cases ==========

def test_summary_ignores_null_values(summary_service_with_nulls):
    result = summary_service_with_nulls.summarize()

    assert result["meta"]["total_records"] == 2

    # COUNTRY: only one non-null
    country_counts = {
        item["value"]: item["count"]
        for item in result["categorical"]["COUNTRY"]
    }
    assert country_counts == {"USA": 1}

    # AGE: only one valid value
    assert result["numeric"]["AGE"]["min"] == 40
    assert result["numeric"]["AGE"]["max"] == 40


def test_summary_empty_table(summary_service_empty):
    result = summary_service_empty.summarize()

    assert result["meta"]["total_records"] == 0
    assert result["categorical"] == {}
    assert result["numeric"] == {}


# ========== Invalid cases ==========

def test_summary_invalid_rows_type(summary_service_normal):
    with pytest.raises(TypeError):
        summary_service_normal.summarize(rows="not a list")


# ========== Exception cases ==========

def test_repository_exception_propagates():
    class BrokenRepository:
        def query(self):
            raise RuntimeError("DB failure")

        def get_schema(self, table_name="records"):
            return SCHEMA

    service = SummaryService(BrokenRepository())

    with pytest.raises(RuntimeError):
        service.summarize()
