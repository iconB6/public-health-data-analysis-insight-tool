import pytest
from src.service.clean_service import DataCleanService
from datetime import date

'''
def clean(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
- remove empty rows
- normalize null values
- convert numbers
- convert dates
- normalize key strings
- handle inconsistent data
'''

# ========== TEST DATA ==========
RAW_ROWS_NORMAL = [
    {
        " Name ": " Alice ",
        "age": "18",
        "score": "90.5",
        "birth_date": "2006-01-01",
        "remark": ""
    }
]

RAW_ROWS_WITH_EMPTY = [
    {},
    {
        "name": "Bob",
        "age": None
    }
]

RAW_ROWS_EDGE = [
    {
        "NAME": "  ",
        "AGE": "0",
        "SCORE": "0.0",
        "DATE": "2020/01/01"
    }
]

RAW_ROWS_WITH_INVALID_KEYS = [
    {
        "\ufefffake": "z",
        "name": "Alice",
        "age": "18"
    }
]

RAW_ROWS_DETECT_NUMBER =[
    {
        "a": " 123 ", 
        "b": "NA", 
        "c": "1,234"
    }
]
# ========= EXPECTED RESULTS ==========
EXPECTED_NORMAL = [
    {
        "NAME": "Alice",
        "AGE": 18.0,
        "SCORE": 90.5,
        "BIRTH_DATE": date(2006, 1, 1),
        "REMARK": None
    }
]

EXPECTED_WITH_EMPTY = [
    {
        "NAME": "Bob",
        "AGE": None
    }
]

EXPECTED_EDGE = [
    {
        "NAME": None,
        "AGE": 0.0,
        "SCORE": 0.0,
        "DATE": date(2020, 1, 1)
    }
]

EXPECTED_ROWS_WITH_INVALID_KEYS = [
    {
        "FAKE": "z",
        "NAME": "Alice",
        "AGE": 18
    }
]

EXPECTED_ROWS_DETECT_NUMBER =[
    {
        "A": 123, 
        "B": None, 
        "C": 1234
    }
]
# ========= FIXTURES ==========
@pytest.fixture
def clean_service():
    return DataCleanService()
# ========== Normal cases ==========
def test_clean_normal_rows(clean_service):
    result = clean_service.clean(RAW_ROWS_NORMAL)

    assert result == EXPECTED_NORMAL
# ========== Edge cases ==========
def test_clean_removes_empty_rows(clean_service):
    result = clean_service.clean(RAW_ROWS_WITH_EMPTY)
    assert result == EXPECTED_WITH_EMPTY

def test_clean_edge_values(clean_service):
    result = clean_service.clean(RAW_ROWS_EDGE)
    assert result == EXPECTED_EDGE

def test_clean_BOM_values(clean_service):
    result = clean_service.clean(RAW_ROWS_WITH_INVALID_KEYS)
    assert result == EXPECTED_ROWS_WITH_INVALID_KEYS

def test_clean_detect_number(clean_service):
    result = clean_service.clean(RAW_ROWS_DETECT_NUMBER)
    assert result == EXPECTED_ROWS_DETECT_NUMBER

# ========== Exception cases ==========
def test_clean_with_none_input(clean_service):
    with pytest.raises(TypeError):
        clean_service.clean(None)
