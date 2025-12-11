import pytest
import os
from src.service.data_loader import DataLoadingService


def test_load_csv_missing_file():
    service = DataLoadingService()

    with pytest.raises(ValueError):
        service.load_data("csv", "not_exist.csv")


def test_load_empty_csv(tmp_path):
    file_path = tmp_path / "empty.csv"
    file_path.write_text("")  # empty file

    service = DataLoadingService()

    with pytest.raises(ValueError):
        service.load_data("csv", str(file_path))


def test_load_csv_only_header(tmp_path):
    file_path = tmp_path / "header.csv"
    file_path.write_text("name,age\n")  # header only

    service = DataLoadingService()

    with pytest.raises(ValueError):
        service.load_data("csv", str(file_path))


def test_load_csv_valid(tmp_path):
    file_path = tmp_path / "valid.csv"
    file_path.write_text("name,age\nAlice,20\n")

    service = DataLoadingService()
    rows = service.load_data("csv", str(file_path))

    assert len(rows) == 1
    assert rows[0]["name"] == "Alice"
    assert rows[0]["age"] == "20"
