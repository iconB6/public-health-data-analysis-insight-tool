import pytest
import sqlite3
import datetime
from src.service.storage_service import DataStorageService

'''
DataStorageService should:
- accept List[Dict[str, Any]]
- infer column types automatically
- persist data into database
- return inserted record count (int)
'''

# ========== TEST DATA ==========

ROWS_NUMERIC = [
    {"AGE": 18},
    {"AGE": 20},
]

ROWS_NUMERIC_MIXED = [
    {"SCORE": 90},
    {"SCORE": 90.5},
]

ROWS_SEMANTIC_OVERRIDE = [
    {"YEAR": 2024},
    {"YEAR": 2023},
]

ROWS_MIXED_TYPES = [
    {
        "COUNT": 10,
        "RATE": 0.5,
        "NOTE": "abc",
        "DATE": datetime.date(2024, 1, 1),
        "EMPTY": None,
    }
]

ROWS_ALL_NULL_COLUMN = [
    {"A": None},
    {"A": None},
]

ROWS_EMPTY = []

# ========= EXPECTED RESULTS ==========

EXPECTED_NUMERIC_TYPE = "INTEGER"
EXPECTED_MIXED_NUMERIC_TYPE = "REAL"
EXPECTED_SEMANTIC_TYPE = "TEXT"

# ========= FIXTURES ==========

@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "storage_test.db"


@pytest.fixture
def storage_service(db_path):
    service = DataStorageService(str(db_path))
    service.connect()
    yield service
    try:
        service.disconnect()
    except Exception:
        pass


def get_schema(db_path, table="records"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    schema = {row[1]: row[2].upper() for row in cur.fetchall()}
    conn.close()
    return schema


def get_row_count(db_path, table="records"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    count = cur.fetchone()[0]
    conn.close()
    return count


# ========== Normal cases ==========

def test_storage_integer_inference(storage_service, db_path):
    with storage_service.transaction():
        inserted = storage_service.save_full_record(ROWS_NUMERIC)

    assert inserted == 2

    schema = get_schema(db_path)
    assert schema["AGE"] == EXPECTED_NUMERIC_TYPE


def test_storage_real_inference(storage_service, db_path):
    with storage_service.transaction():
        inserted = storage_service.save_full_record(ROWS_NUMERIC_MIXED)

    assert inserted == 2

    schema = get_schema(db_path)
    assert schema["SCORE"] == EXPECTED_MIXED_NUMERIC_TYPE


def test_storage_semantic_override(storage_service, db_path):
    with storage_service.transaction():
        inserted = storage_service.save_full_record(ROWS_SEMANTIC_OVERRIDE)

    assert inserted == 2

    schema = get_schema(db_path)
    assert schema["YEAR"] == EXPECTED_SEMANTIC_TYPE


# ========== Edge cases ==========

def test_storage_mixed_column_types(storage_service, db_path):
    with storage_service.transaction():
        inserted = storage_service.save_full_record(ROWS_MIXED_TYPES)

    assert inserted == 1

    schema = get_schema(db_path)

    assert schema["COUNT"] == "INTEGER"
    assert schema["RATE"] == "REAL"
    assert schema["NOTE"] == "TEXT"
    assert schema["DATE"] == "TEXT"

    # EMPTY should not appear (all None)
    assert "EMPTY" not in schema


def test_storage_all_null_column_not_created(storage_service, db_path):
    with storage_service.transaction():
        inserted = storage_service.save_full_record(ROWS_ALL_NULL_COLUMN)

    # rows are empty after clean → nothing to insert
    assert inserted == 0


def test_storage_empty_input_returns_zero(storage_service):
    with storage_service.transaction():
        inserted = storage_service.save_full_record(ROWS_EMPTY)

    assert inserted == 0


# ========== Invalid cases ==========

def test_storage_invalid_row_type(storage_service):
    with pytest.raises(TypeError):
        with storage_service.transaction():
            storage_service.save_full_record(["not a dict"])


# ========== Exception cases ==========

def test_storage_transaction_rollback(storage_service, db_path):
    with pytest.raises(RuntimeError):
        with storage_service.transaction():
            storage_service.save_full_record(ROWS_NUMERIC)
            raise RuntimeError("force rollback")

    # rollback must keep table empty
    assert get_row_count(db_path) == 0

