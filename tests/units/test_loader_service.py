import pytest
from src.service.loader_service import DataLoaderService

'''
responsible for loading data from the specified data source into memory 
in the form of List[Dict(str, Any)]
def load_data(self, source_type: str, source_path: str) -> List[Dict[str, Any]]
'''

# ========== TEST DATA ==========
CSV_VALID_BASIC = """country,date,value
UK,2023-01-01,10
UK,2023-02-01,20
FR,2023-01-01,15
"""
CSV_WITH_MISSING_VALUES = """country,date,value
UK,2023-01-01,
FR,,12
,2023-03-01,8
"""
CSV_EMPTY = """country,date,value
"""
CSV_WITH_MISSING_VALUES = """country,date,value
UK,2023-01-01"""
CSV_NO_HEADER = """USA,2020,100
UK,2021,200
"""
CSV_HEADER_ONLY = """country,year,value
"""
CSV_NOT_CSV = """<html>
<body>Not a CSV</body>
</html>
"""
# ========= EXPECTED RESULTS ==========
EXPECTED_BASIC_RESULT = [
    {"country": "UK", "date": "2023-01-01", "value": "10"},
    {"country": "UK", "date": "2023-02-01", "value": "20"},
    {"country": "FR", "date": "2023-01-01", "value": "15"},
]
EXPECTED_WITH_MISSING = [
    {"country": "UK", "date": "2023-01-01", "value": ""},
    {"country": "FR", "date": "", "value": "12"},
    {"country": "", "date": "2023-03-01", "value": "8"},
]
EXPECTED_EMPTY = []
EXPECTED_WITH_MISSING_VALUES = [
    {"country": "UK", "date": "2023-01-01", "value": ""},
]
# ========= FIXTURES ==========
@pytest.fixture
def csv_file_factory(tmp_path):
    """
    Create a temporary CSV file and return its file path.
    """
    def _create(content: str) -> str:
        file_path = tmp_path / "test.csv"
        file_path.write_text(content, encoding="utf-8")
        return str(file_path)
    return _create
# ========== Normal cases ==========
def test_load_csv_normal_case(csv_file_factory):
    service = DataLoaderService()
    file_path = csv_file_factory(CSV_VALID_BASIC)

    result = service.load_data("csv", file_path)

    assert isinstance(result, list)
    assert all(isinstance(row, dict) for row in result)
    assert result == EXPECTED_BASIC_RESULT
# ========== Edge cases ==========

def test_load_csv_missing_values(csv_file_factory):
    service = DataLoaderService()
    file_path = csv_file_factory(CSV_WITH_MISSING_VALUES)

    result = service.load_data("csv", file_path)

    assert isinstance(result, list)
    assert all(isinstance(row, dict) for row in result)
    assert result == EXPECTED_WITH_MISSING

def test_load_csv_empty_file(csv_file_factory):
    service = DataLoaderService()
    file_path = csv_file_factory(CSV_EMPTY)

    result = service.load_data("csv", file_path)

    assert isinstance(result, list)
    assert result == EXPECTED_EMPTY

def test_load_csv_null_file_path():
    service = DataLoaderService()
    with pytest.raises(ValueError):
        service.load_data("csv", None)

def test_load_csv_with_missing_values(csv_file_factory):
    service = DataLoaderService()
    file_path = csv_file_factory(CSV_WITH_MISSING_VALUES)

    result = service.load_data("csv", file_path)

    assert isinstance(result, list)
    assert all(isinstance(row, dict) for row in result)
    assert result == EXPECTED_WITH_MISSING_VALUES

# ========== Invalid cases ==========
def test_load_csv_without_header(csv_file_factory):
    service = DataLoaderService()
    file_path = csv_file_factory(CSV_NO_HEADER)

    with pytest.raises(ValueError):
        service.load_data("csv", file_path)

def test_load_csv_header_only(csv_file_factory):
    service = DataLoaderService()
    file_path = csv_file_factory(CSV_HEADER_ONLY)

    with pytest.raises(ValueError):
        service.load_data("csv", file_path)

# ========== Exception cases ==========
def test_load_csv_not_a_csv_file(csv_file_factory):
    service = DataLoaderService()
    file_path = csv_file_factory(CSV_NOT_CSV)

    with pytest.raises(ValueError):
        service.load_data("csv", file_path)
