import pytest
from src.infrastructure.csv_loader import CSVLoader

def test_load_csv_missing_file():
    loader = CSVLoader("not_exist.csv")
    with pytest.raises(ValueError):
        loader.load()


def test_load_empty_csv(tmp_path):
    # completely empty file
    f = tmp_path / "empty.csv"
    f.write_text("")

    loader = CSVLoader(str(f))

    with pytest.raises(ValueError):
        loader.load()


def test_load_csv_only_header(tmp_path):
    f = tmp_path / "header.csv"
    f.write_text("name,age\n")

    loader = CSVLoader(str(f))

    with pytest.raises(ValueError):
        loader.load()


def test_load_csv_valid(tmp_path):
    f = tmp_path / "valid.csv"
    f.write_text("name,age\nAlice,20\n")

    loader = CSVLoader(str(f))
    rows = loader.load()

    assert len(rows) == 1
    assert rows[0]["name"] == "Alice"
    assert rows[0]["age"] == "20"