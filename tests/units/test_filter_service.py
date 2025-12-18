import datetime
import pytest

from src.service.filter_service import FilterService
from src.interface.repository_interface import IRepository

'''
FilterService requirements:
- Service-layer only; no SQL or DB-specific code.
- Uses IRepository for all data access.
- filter() accepts optional filters.
- Returns List[Dict[str, Any]].
- Caches latest results in memory.
- get_cached_results() returns last result.
- Invalid input raises error.
- Repository exceptions propagate.
'''

class FakeRepository(IRepository):
    def __init__(self, rows, schema):
        self.rows = rows
        self.schema = schema
        self.last_query = None

    def query(self, *, date_from=None, date_to=None, conditions=None):
        self.last_query = {
            "date_from": date_from,
            "date_to": date_to,
            "conditions": conditions,
        }
        return self.rows

    def query_for_trend(
        self,
        *,
        date_field: str,
        date_from=None,
        date_to=None,
        conditions=None,
    ):
        # For filter tests, trend queries can just reuse query behavior
        return self.query(date_from=date_from, date_to=date_to, conditions=conditions)

    # unused methods (empty implementations)
    def connect(self): pass
    def disconnect(self): pass
    def begin(self): pass
    def commit(self): pass
    def rollback(self): pass
    def ensure_table(self, table, schema): pass
    def insert_rows(self, table, rows): pass
    def get_schema(self, table): return self.schema


# ========== TEST DATA ==========

SCHEMA = {
    "COUNTRY": "TEXT",
    "AGE": "INTEGER",
    "SCORE": "REAL",
    "DATE": "TEXT",
}

ROWS = [
    {"COUNTRY": "USA", "AGE": 20, "SCORE": 88.5, "DATE": "2024-01-01"}
]


# ========== Normal cases ==========

def test_filter_numeric_and_text_conditions():
    repo = FakeRepository(ROWS, SCHEMA)
    service = FilterService(repo)

    result = service.filter(
        date_from=datetime.date(2024, 1, 1),
        conditions={
            "COUNTRY": {"eq": "USA"},
            "AGE": {"gt": 18},
        }
    )

    assert result == ROWS
    assert repo.last_query["conditions"]["AGE"]["gt"] == 18


# ========== Edge cases ==========

def test_filter_empty_result():
    repo = FakeRepository([], SCHEMA)
    service = FilterService(repo)

    result = service.filter(conditions={"AGE": {"gt": 100}})
    assert result == []


def test_cached_results():
    repo = FakeRepository(ROWS, SCHEMA)
    service = FilterService(repo)

    service.filter(conditions={"AGE": {"gt": 18}})
    assert service.get_cached_results() == ROWS


# ========== Invalid cases ==========

def test_invalid_operator_for_text_column():
    repo = FakeRepository(ROWS, SCHEMA)
    service = FilterService(repo)

    with pytest.raises(ValueError):
        service.filter(conditions={"COUNTRY": {"gt": "USA"}})


def test_unknown_column():
    repo = FakeRepository(ROWS, SCHEMA)
    service = FilterService(repo)

    with pytest.raises(ValueError):
        service.filter(conditions={"UNKNOWN": {"eq": 1}})


def test_invalid_date_type():
    repo = FakeRepository(ROWS, SCHEMA)
    service = FilterService(repo)

    with pytest.raises(TypeError):
        service.filter(date_from="2024-01-01")