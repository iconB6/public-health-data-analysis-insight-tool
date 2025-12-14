from datetime import date
import pytest

from src.service.filter_service import FilterService
from src.interface.repository_interface import IRepository

'''
FilterService requirements:
- Service-layer only; no SQL or DB-specific code.
- Uses IDataRepository for all data access.
- filter() accepts table name and optional filters.
- Returns List[Dict[str, Any]].
- Caches latest results in memory.
- get_cached_results() returns last result.
- Invalid input raises error.
- Repository exceptions propagate.
'''

# ========== TEST DATA ==========
TABLE_NAME = "records"

DATASET = [
    {"country": "UK", "date": "2020-01-01", "value": 100},
    {"country": "UK", "date": "2021-01-01", "value": 200},
    {"country": "US", "date": "2020-01-01", "value": 300},
]


# ========= EXPECTED RESULTS ==========
UK_ONLY = [
    {"country": "UK", "date": "2020-01-01", "value": 100},
    {"country": "UK", "date": "2021-01-01", "value": 200},
]

UK_2020_ONLY = [
    {"country": "UK", "date": "2020-01-01", "value": 100},
]


# ========= FIXTURES ==========
class FakeRepository(IRepository):
    def __init__(self, data):
        self.data = data
        self.last_query = None

    def query(self, table, filters, start_date=None, end_date=None):
        self.last_query = {
            "table": table,
            "filters": filters,
            "start_date": start_date,
            "end_date": end_date,
        }

        results = self.data

        if "country" in filters:
            results = [r for r in results if r["country"] == filters["country"]]

        if start_date:
            results = [r for r in results if r["date"] >= start_date.isoformat()]

        if end_date:
            results = [r for r in results if r["date"] <= end_date.isoformat()]

        return results

@pytest.fixture
def repository():
    return FakeRepository(DATASET)


@pytest.fixture
def filter_service(repository):
    return FilterService(repository)

# ========== Normal cases ==========
def test_filter_by_country(filter_service):
    results = filter_service.filter(
        table=TABLE_NAME,
        country="UK"
    )

    assert results == UK_ONLY

def test_filter_by_country_and_date_range(filter_service):
    results = filter_service.filter(
        table=TABLE_NAME,
        country="UK",
        start_date=date(2020, 1, 1),
        end_date=date(2020, 12, 31),
    )

    assert results == UK_2020_ONLY


# ========== Edge cases ==========
def test_filter_without_any_conditions(filter_service):
    results = filter_service.filter(table=TABLE_NAME)
    assert results == DATASET

def test_filter_returns_empty_list(filter_service):
    results = filter_service.filter(
        table=TABLE_NAME,
        country="CN"
    )

    assert results == []

def test_cached_results_after_filter(filter_service):
    filter_service.filter(
        table=TABLE_NAME,
        country="UK"
    )

    cached = filter_service.get_cached_results()
    assert cached == UK_ONLY

# ========== Invalid cases ==========
def test_filter_with_invalid_table_type(filter_service):
    with pytest.raises(TypeError):
        filter_service.filter(
            table=None,   # type: ignore
            country="UK"
        )

def test_filter_with_invalid_date_type(filter_service):
    with pytest.raises(AttributeError):
        filter_service.filter(
            table=TABLE_NAME,
            start_date="2020-01-01"  # type: ignore
        )


# ========== Exception cases ==========
class BrokenRepository(IRepository):
    def query(self, *args, **kwargs):
        raise RuntimeError("DB error")


def test_repository_exception_propagates():
    service = FilterService(BrokenRepository())

    with pytest.raises(RuntimeError):
        service.filter(table=TABLE_NAME)

